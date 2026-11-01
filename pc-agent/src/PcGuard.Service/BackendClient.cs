using System.Net;
using System.Net.Http.Headers;
using System.Net.WebSockets;
using System.Text;
using PcGuard.Core;

namespace PcGuard.Service;

public sealed record LoginResult(bool Ok, string? Error, string? Token, PcRules? State);

public enum WsEnd { TokenDead, Stopped }

/// <summary>Callbacks of one WebSocket session. Invoked on the socket's receive loop.</summary>
public sealed class WsHandlers
{
    public required Func<string?> ForegroundApp { get; init; }
    public required Action<PcRules> OnState { get; init; }
    public required Action<string> OnMessage { get; init; }
    public required Action OnPong { get; init; }
    public Action<bool>? OnConnectedChanged { get; init; }
}

/// <summary>
/// HTTP + WebSocket client for the backend's /pc API (base URL includes /api/v1). Stateless with
/// respect to the session: the caller holds the token (memory only) and passes it in.
/// SECURITY: never logs request/response bodies, passwords, tokens or the WebSocket URI (it carries
/// the token in its query string). No IHttpClientFactory logging handler is used for the same reason.
/// </summary>
public sealed class BackendClient : IDisposable
{
    private const int MaxFrameBytes = 1024 * 1024;
    private static readonly TimeSpan HeartbeatEvery = TimeSpan.FromSeconds(30);
    private static readonly MediaTypeHeaderValue Json = new("application/json") { CharSet = "utf-8" };

    private readonly Uri _base;
    private readonly HttpClient _http;
    private readonly ILogger _log;

    public BackendClient(Uri baseUrl, ILogger log)
    {
        if (baseUrl.Scheme is not ("https" or "http")) throw new ArgumentException("Backend:BaseUrl must be http(s)", nameof(baseUrl));
        _base = baseUrl;
        _log = log;
        _http = new HttpClient(new SocketsHttpHandler
        {
            PooledConnectionLifetime = TimeSpan.FromMinutes(5),
            AllowAutoRedirect = false, // never replay credentials to another location
        })
        {
            Timeout = TimeSpan.FromSeconds(15),
        };
    }

    public void Dispose() => _http.Dispose();

    /// <summary>The password lives only in this call's locals and the request content; it is never logged.</summary>
    public async Task<LoginResult> LoginAsync(string username, string password, string hostname, string machineKey, CancellationToken ct)
    {
        try
        {
            using var content = new StringContent(BackendProtocol.LoginBody(username, password, hostname, machineKey), Encoding.UTF8);
            content.Headers.ContentType = Json;
            using var resp = await _http.PostAsync(BackendProtocol.Endpoint(_base, "pc/login"), content, ct).ConfigureAwait(false);
            if (!resp.IsSuccessStatusCode)
            {
                _log.LogInformation("Login refused with HTTP {Status}", (int)resp.StatusCode);
                return new LoginResult(false, BackendProtocol.LoginErrorCode((int)resp.StatusCode), null, null);
            }
            var body = await resp.Content.ReadAsStringAsync(ct).ConfigureAwait(false);
            var (token, state) = BackendProtocol.ParseLoginResponse(body);
            return new LoginResult(true, null, token, state);
        }
        catch (OperationCanceledException) when (ct.IsCancellationRequested)
        {
            throw;
        }
        catch (Exception e)
        {
            // never let an unexpected exception bubble out of login: the shell must always get a result
            _log.LogWarning("Login failed: {Error}", e.GetType().Name);
            return new LoginResult(false, "offline", null, null);
        }
    }

    /// <summary>Best effort; returns false on any failure.</summary>
    public async Task<bool> LogoutAsync(string token, CancellationToken ct)
    {
        try
        {
            using var req = new HttpRequestMessage(HttpMethod.Post, BackendProtocol.Endpoint(_base, "pc/logout"));
            req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
            using var resp = await _http.SendAsync(req, ct).ConfigureAwait(false);
            if (!resp.IsSuccessStatusCode) _log.LogInformation("Logout returned HTTP {Status}", (int)resp.StatusCode);
            return resp.IsSuccessStatusCode;
        }
        catch (Exception e) when (e is HttpRequestException or TaskCanceledException)
        {
            if (ct.IsCancellationRequested) throw;
            _log.LogWarning("Logout failed: {Error}", e.GetType().Name);
            return false;
        }
    }

    /// <summary>GET /pc/state. Status null = network failure.</summary>
    public async Task<(int? Status, PcRules? State)> GetStateAsync(string token, CancellationToken ct)
    {
        try
        {
            using var req = new HttpRequestMessage(HttpMethod.Get, BackendProtocol.Endpoint(_base, "pc/state"));
            req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
            using var resp = await _http.SendAsync(req, ct).ConfigureAwait(false);
            if (!resp.IsSuccessStatusCode) return ((int)resp.StatusCode, null);
            var body = await resp.Content.ReadAsStringAsync(ct).ConfigureAwait(false);
            return ((int)resp.StatusCode, StateParser.Parse(body));
        }
        catch (Exception e) when (e is HttpRequestException or TaskCanceledException or FormatException)
        {
            if (ct.IsCancellationRequested) throw;
            _log.LogDebug("State poll failed: {Error}", e.GetType().Name);
            return (null, null);
        }
    }

    /// <summary>POST /pc/usage with at most 500 events. Network errors map to Retry.</summary>
    public async Task<UsageOutcome> UploadUsageAsync(string token, IReadOnlyList<UsageEvent> events, CancellationToken ct)
    {
        try
        {
            using var req = new HttpRequestMessage(HttpMethod.Post, BackendProtocol.Endpoint(_base, "pc/usage"));
            req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
            req.Content = new StringContent(BackendProtocol.UsageBody(events), Encoding.UTF8);
            req.Content.Headers.ContentType = Json;
            using var resp = await _http.SendAsync(req, ct).ConfigureAwait(false);
            var outcome = BackendProtocol.ClassifyUsage((int)resp.StatusCode);
            if (outcome != UsageOutcome.Ok)
                _log.LogInformation("Usage upload of {Count} events: HTTP {Status} -> {Outcome}", events.Count, (int)resp.StatusCode, outcome);
            return outcome;
        }
        catch (Exception e) when (e is HttpRequestException or TaskCanceledException)
        {
            if (ct.IsCancellationRequested) throw;
            _log.LogDebug("Usage upload failed: {Error}", e.GetType().Name);
            return UsageOutcome.Retry;
        }
    }

    /// <summary>
    /// Keeps a WebSocket to /pc/ws open until <paramref name="ct"/> is cancelled or the token dies
    /// (handshake rejected with 401/403, or close code 4001). Other drops reconnect with Backoff.
    /// Sends {"type":"hb","app":...} every 30 s.
    /// </summary>
    public async Task<WsEnd> RunWebSocketAsync(string token, WsHandlers handlers, CancellationToken ct)
    {
        var attempt = 0;
        while (!ct.IsCancellationRequested)
        {
            var outcome = await RunOnceAsync(token, handlers, ct).ConfigureAwait(false);
            handlers.OnConnectedChanged?.Invoke(false);
            if (outcome.TokenDead) return WsEnd.TokenDead;
            if (ct.IsCancellationRequested) break;
            attempt = outcome.ReceivedAny ? 1 : attempt + 1;
            var delay = Backoff.NextDelay(attempt);
            _log.LogInformation("WebSocket down ({Reason}); reconnecting in {Delay}s", outcome.Reason, delay.TotalSeconds);
            try { await Task.Delay(delay, ct).ConfigureAwait(false); }
            catch (OperationCanceledException) { break; }
        }
        return WsEnd.Stopped;
    }

    private readonly record struct Attempt(bool TokenDead, bool ReceivedAny, string Reason);

    private async Task<Attempt> RunOnceAsync(string token, WsHandlers h, CancellationToken ct)
    {
        using var ws = new ClientWebSocket();
        ws.Options.CollectHttpResponseDetails = true;
        ws.Options.KeepAliveInterval = TimeSpan.FromSeconds(20);
        try
        {
            using var connectCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
            connectCts.CancelAfter(TimeSpan.FromSeconds(15));
            await ws.ConnectAsync(BackendProtocol.WebSocketUri(_base, token), connectCts.Token).ConfigureAwait(false);
        }
        catch (Exception e) when (e is WebSocketException or HttpRequestException or OperationCanceledException)
        {
            if (ct.IsCancellationRequested) return new Attempt(false, false, "stopped");
            // the backend closes before accept for a bad/closed session, which the handshake reports as 403
            if (ws.HttpStatusCode is HttpStatusCode.Forbidden or HttpStatusCode.Unauthorized)
                return new Attempt(true, false, "handshake rejected");
            return new Attempt(false, false, "connect failed: " + e.GetType().Name);
        }

        h.OnConnectedChanged?.Invoke(true);
        using var loopCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        var lastReceived = new long[] { Environment.TickCount64 };
        var hb = HeartbeatLoopAsync(ws, h, lastReceived, loopCts.Token);
        var receivedAny = false;
        try
        {
            var buffer = new byte[16 * 1024];
            using var frame = new MemoryStream();
            while (ws.State == WebSocketState.Open && !ct.IsCancellationRequested)
            {
                frame.SetLength(0);
                WebSocketReceiveResult r;
                var tooBig = false;
                do
                {
                    r = await ws.ReceiveAsync(buffer, ct).ConfigureAwait(false);
                    if (r.MessageType == WebSocketMessageType.Close) break;
                    if (frame.Length + r.Count > MaxFrameBytes) tooBig = true;
                    else frame.Write(buffer, 0, r.Count);
                } while (!r.EndOfMessage);

                if (r.MessageType == WebSocketMessageType.Close)
                {
                    var code = (int?)ws.CloseStatus;
                    if (code == 4001) return new Attempt(true, receivedAny, "closed 4001");
                    return new Attempt(false, receivedAny, "closed " + (code?.ToString() ?? "?"));
                }
                if (tooBig || r.MessageType != WebSocketMessageType.Text) continue;

                ServerFrame f;
                try { f = BackendProtocol.ParseServerFrame(Encoding.UTF8.GetString(frame.GetBuffer(), 0, (int)frame.Length)); }
                catch (FormatException) { _log.LogDebug("Ignoring malformed server frame"); continue; }
                receivedAny = true;
                Interlocked.Exchange(ref lastReceived[0], Environment.TickCount64);
                switch (f.Kind)
                {
                    case ServerFrameKind.State: h.OnState(f.State!); break;
                    case ServerFrameKind.Pong: h.OnPong(); break;
                    case ServerFrameKind.Message: h.OnMessage(f.Text!); break;
                }
            }
            if (ws.CloseStatus is { } cs && (int)cs == 4001) return new Attempt(true, receivedAny, "closed 4001");
            return new Attempt(false, receivedAny, "socket " + ws.State);
        }
        catch (Exception e) when (e is WebSocketException or OperationCanceledException or IOException or ObjectDisposedException)
        {
            return new Attempt(false, receivedAny, ct.IsCancellationRequested ? "stopped" : "receive failed: " + e.GetType().Name);
        }
        finally
        {
            loopCts.Cancel();
            try { await hb.ConfigureAwait(false); } catch (OperationCanceledException) { }
            if (ws.State == WebSocketState.Open)
            {
                try
                {
                    using var closeCts = new CancellationTokenSource(TimeSpan.FromSeconds(2));
                    await ws.CloseOutputAsync(WebSocketCloseStatus.NormalClosure, null, closeCts.Token).ConfigureAwait(false);
                }
                catch (Exception e) when (e is WebSocketException or OperationCanceledException or IOException) { }
            }
        }
    }

    // The server answers every heartbeat with a pong; silence for this long means a dead connection
    // (.NET 8 keep-alive pings do not detect an unresponsive peer).
    private static readonly TimeSpan SilenceLimit = HeartbeatEvery * 2 + TimeSpan.FromSeconds(15);

    private async Task HeartbeatLoopAsync(ClientWebSocket ws, WsHandlers h, long[] lastReceived, CancellationToken ct)
    {
        try
        {
            using var timer = new PeriodicTimer(HeartbeatEvery);
            while (await timer.WaitForNextTickAsync(ct).ConfigureAwait(false))
            {
                if (ws.State != WebSocketState.Open) return;
                if (Environment.TickCount64 - Interlocked.Read(ref lastReceived[0]) > (long)SilenceLimit.TotalMilliseconds)
                {
                    _log.LogInformation("WebSocket silent for too long; aborting it");
                    ws.Abort();
                    return;
                }
                var bytes = Encoding.UTF8.GetBytes(BackendProtocol.Heartbeat(h.ForegroundApp()));
                await ws.SendAsync(bytes, WebSocketMessageType.Text, endOfMessage: true, ct).ConfigureAwait(false);
            }
        }
        catch (Exception e) when (e is WebSocketException or IOException or ObjectDisposedException)
        {
            _log.LogDebug("Heartbeat send failed: {Error}", e.GetType().Name);
            ws.Abort(); // wake the receive loop so it reconnects
        }
    }
}
