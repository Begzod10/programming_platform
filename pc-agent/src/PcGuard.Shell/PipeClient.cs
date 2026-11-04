using System.IO;
using System.IO.Pipes;
using System.Text;
using Microsoft.Win32.SafeHandles;
using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>
/// Client of the guard service pipe. Connects with retry/backoff (the service may not have pinned
/// this process yet on the first attempts, or may restart), reads one JSON object per line
/// (bounded), and writes with a timeout. Everything runs on thread-pool threads, never the UI thread;
/// events are raised on those threads.
///
/// Every connection's server is checked first (<c>verifyServer</c>: GetNamedPipeServerProcessId
/// against the SCM's process id of PcGuard). A server that is provably not the service (a pipe-name
/// squatter while the service is down) is disconnected at once and never heard; one that cannot be
/// checked is heard, and each message carries that <see cref="PipeServerTrust"/> so the app can refuse
/// "released" from it. After every ended or failed connection <c>shouldGiveUp</c> is asked (the
/// service is stopped AND disabled, as after a recovery release); then <see cref="GaveUp"/> is raised
/// and the loop ends instead of reconnecting forever.
/// </summary>
internal sealed class PipeClient : IDisposable
{
    public const string PipeName = "PcGuard.Pipe";
    private static readonly TimeSpan ConnectTimeout = TimeSpan.FromSeconds(2);
    private static readonly TimeSpan WriteTimeout = TimeSpan.FromSeconds(2);
    private static readonly TimeSpan StableAfter = TimeSpan.FromSeconds(5);

    private readonly CancellationTokenSource _cts = new();
    private readonly SemaphoreSlim _writeLock = new(1, 1);
    private readonly object _gate = new();
    private readonly Func<SafePipeHandle, PipeServerTrust>? _verifyServer;
    private readonly Func<bool>? _shouldGiveUp;
    private NamedPipeClientStream? _stream;
    private Task? _loop;

    public PipeClient(Func<SafePipeHandle, PipeServerTrust>? verifyServer = null, Func<bool>? shouldGiveUp = null)
    {
        _verifyServer = verifyServer;
        _shouldGiveUp = shouldGiveUp;
    }

    public event Action<bool>? ConnectionChanged;
    /// <summary>A message and the trust of the server that sent it.</summary>
    public event Action<PipeMessage, PipeServerTrust>? MessageReceived;
    /// <summary>The service is stopped and disabled: the loop ended for good.</summary>
    public event Action? GaveUp;

    public bool IsConnected
    {
        get { lock (_gate) return _stream is { IsConnected: true }; }
    }

    public void Start() => _loop ??= Task.Run(() => RunAsync(_cts.Token));

    private async Task RunAsync(CancellationToken ct)
    {
        var attempt = 0;
        while (!ct.IsCancellationRequested)
        {
            var connectedAt = DateTimeOffset.MinValue;
            NamedPipeClientStream? s = null;
            try
            {
                s = new NamedPipeClientStream(".", PipeName, PipeDirection.InOut, PipeOptions.Asynchronous);
                await s.ConnectAsync((int)ConnectTimeout.TotalMilliseconds, ct).ConfigureAwait(false);
                var trust = VerifyServer(s);
                if (trust == PipeServerTrust.Mismatch)
                {
                    // not the PcGuard service: never read from it or write to it
                    ShellLog.Info("Pipe server is not the PcGuard service: disconnected");
                }
                else
                {
                    lock (_gate) _stream = s;
                    connectedAt = DateTimeOffset.UtcNow;
                    if (trust == PipeServerTrust.Unknown) ShellLog.Info("Pipe server could not be verified: 'released' will be ignored on this connection");
                    Raise(true);

                    var reader = new BoundedLineReader(s, BoundedLineReader.DefaultMaxLineBytes);
                    while (!ct.IsCancellationRequested)
                    {
                        var line = await reader.ReadLineAsync(ct).ConfigureAwait(false);
                        if (line is null) break; // service closed the pipe (restart, or rejected us)
                        if (line.Length == 0) continue;
                        PipeMessage msg;
                        try { msg = PipeMessage.Parse(line); }
                        catch (FormatException) { continue; }
                        try { MessageReceived?.Invoke(msg, trust); }
                        catch (Exception e) { ShellLog.Error("MessageReceived handler", e); }
                    }
                }
            }
            catch (OperationCanceledException) when (ct.IsCancellationRequested)
            {
                break;
            }
            catch (Exception e)
            {
                // not connectable yet / connection dropped / anything unexpected: the loop must never
                // end. Log the type only, then fall through to the backoff.
                if (e is not (IOException or TimeoutException or UnauthorizedAccessException
                              or ObjectDisposedException or InvalidOperationException))
                    ShellLog.Info("Pipe loop error: " + e.GetType().FullName);
            }
            finally
            {
                var wasConnected = false;
                lock (_gate)
                {
                    if (ReferenceEquals(_stream, s)) { _stream = null; wasConnected = true; }
                }
                try { s?.Dispose(); } catch (IOException) { }
                if (wasConnected) Raise(false);
            }

            // A connection that died within seconds (e.g. the service rejected us because the pin was
            // not set yet) keeps counting up, so we do not hammer the service; a stable one resets.
            attempt = connectedAt != DateTimeOffset.MinValue && DateTimeOffset.UtcNow - connectedAt > StableAfter ? 1 : attempt + 1;
            if (ServiceIsGone())
            {
                try { GaveUp?.Invoke(); }
                catch (Exception e) { ShellLog.Error("GaveUp handler", e); }
                break;
            }
            try { await Task.Delay(Backoff.NextDelay(attempt), ct).ConfigureAwait(false); }
            catch (OperationCanceledException) { break; }
        }
    }

    private PipeServerTrust VerifyServer(NamedPipeClientStream s)
    {
        if (_verifyServer is null) return PipeServerTrust.Unknown;
        try { return _verifyServer(s.SafePipeHandle); }
        catch (Exception e)
        {
            ShellLog.Error("Pipe server check", e);
            return PipeServerTrust.Unknown;
        }
    }

    private bool ServiceIsGone()
    {
        if (_shouldGiveUp is null) return false;
        try { return _shouldGiveUp(); }
        catch (Exception e)
        {
            ShellLog.Error("Service state check", e);
            return false;
        }
    }

    /// <summary>Sends one message; false when not connected or the write failed/timed out.</summary>
    public async Task<bool> SendAsync(PipeMessage message)
    {
        NamedPipeClientStream? s;
        lock (_gate) s = _stream;
        if (s is null) return false;
        byte[]? bytes = null;
        try
        {
            bytes = Encoding.UTF8.GetBytes(PipeMessage.Serialize(message) + "\n");
            if (!await _writeLock.WaitAsync(WriteTimeout).ConfigureAwait(false)) return false;
            try
            {
                using var cts = new CancellationTokenSource(WriteTimeout);
                await s.WriteAsync(bytes, cts.Token).ConfigureAwait(false);
                await s.FlushAsync(cts.Token).ConfigureAwait(false);
                return true;
            }
            finally
            {
                _writeLock.Release();
            }
        }
        catch (Exception e) when (e is IOException or OperationCanceledException or ObjectDisposedException or InvalidOperationException)
        {
            try { s.Dispose(); } catch (IOException) { } // forces the read loop to end => reconnect
            return false;
        }
        finally
        {
            if (bytes is not null) Array.Clear(bytes, 0, bytes.Length); // may hold a password
        }
    }

    private void Raise(bool connected)
    {
        try { ConnectionChanged?.Invoke(connected); }
        catch (Exception e) { ShellLog.Error("ConnectionChanged handler", e); }
    }

    public void Dispose()
    {
        _cts.Cancel();
        lock (_gate) { try { _stream?.Dispose(); } catch (IOException) { } }
    }
}
