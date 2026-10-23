using System.IO.Pipes;
using System.Security.AccessControl;
using System.Security.Principal;
using System.Text;
using PcGuard.Core;

namespace PcGuard.Service;

/// <summary>
/// Named pipe "PcGuard.Pipe" between the service and the shell. WINDOWS ONLY.
///
/// SECURITY
/// - ACL: AuthenticatedUsers read/write, SYSTEM full control, NETWORK denied (no remote clients).
///   Nobody but SYSTEM may create further instances, and the first instance is created with
///   FirstPipeInstance, so the name cannot be squatted while the service runs. A listening instance
///   is always kept open before the previous one is dropped, so the name is never released.
/// - A connected client is accepted only if its process image is exactly the installed shell
///   (&lt;service dir&gt;\PcGuard.Shell.exe, case-insensitive full path) and it runs in the active console
///   session; otherwise it is disconnected at once. Without this, any student could run a fake shell
///   that reports an empty window list and escape enforcement.
///   Residual risk (accepted): code injected into the genuine shell process by the same user can
///   still speak on its connection; pid reuse between connect and the check is not handled.
/// - One active client at a time: a newly accepted client replaces the old one.
/// - Lines are limited to 1 MiB; malformed lines are ignored; nothing received is logged verbatim.
/// </summary>
internal sealed class PipeServer
{
    public const string PipeName = "PcGuard.Pipe";
    private static readonly TimeSpan WriteTimeout = TimeSpan.FromSeconds(2);

    private sealed class Client
    {
        public required NamedPipeServerStream Stream { get; init; }
        public required int Pid { get; init; }
        public SemaphoreSlim WriteLock { get; } = new(1, 1);
    }

    private readonly string _shellPath;
    private readonly ShellPin _pin;
    private readonly ILogger _log;
    private readonly object _gate = new();
    private Client? _active;

    /// <summary>Raised for every well-formed message from the accepted client (on a pipe thread).</summary>
    public event Func<PipeMessage, int, Task>? MessageReceived;

    /// <summary>Raised after a client was accepted (argument: client pid).</summary>
    public event Func<int, Task>? ClientConnected;

    /// <summary>Raised when the accepted client went away (argument: client pid).</summary>
    public event Action<int>? ClientDisconnected;

    public PipeServer(string installedShellPath, ShellPin pin, ILogger log)
    {
        _shellPath = Path.GetFullPath(installedShellPath);
        _pin = pin;
        _log = log;
    }

    public int? ActiveClientPid
    {
        get { lock (_gate) return _active?.Pid; }
    }

    public async Task RunAsync(CancellationToken ct)
    {
        NamedPipeServerStream? listener = null;
        var first = true;
        while (!ct.IsCancellationRequested)
        {
            try
            {
                listener ??= Create(first);
                first = false;
                await listener.WaitForConnectionAsync(ct).ConfigureAwait(false);
                var connected = listener;
                listener = Create(firstInstance: false); // keep the name owned before handling the new one
                _ = HandleAsync(connected, ct);
            }
            catch (OperationCanceledException) when (ct.IsCancellationRequested)
            {
                break;
            }
            catch (Exception e) when (e is IOException or UnauthorizedAccessException)
            {
                // e.g. FirstPipeInstance failed: someone else owns the name (squatting) — retry
                _log.LogError("Pipe server error: {Error} {Message}", e.GetType().Name, e.Message);
                listener?.Dispose();
                listener = null;
                try { await Task.Delay(TimeSpan.FromSeconds(2), ct).ConfigureAwait(false); }
                catch (OperationCanceledException) { break; }
            }
        }
        listener?.Dispose();
        Client? last;
        lock (_gate) { last = _active; _active = null; }
        last?.Stream.Dispose();
    }

    /// <summary>Sends to the accepted client; false when there is none or the write failed/timed out.</summary>
    public async Task<bool> SendAsync(PipeMessage message)
    {
        Client? c;
        lock (_gate) c = _active;
        if (c is null) return false;
        var bytes = Encoding.UTF8.GetBytes(PipeMessage.Serialize(message) + "\n");
        if (!await c.WriteLock.WaitAsync(WriteTimeout).ConfigureAwait(false)) return false;
        try
        {
            using var cts = new CancellationTokenSource(WriteTimeout);
            await c.Stream.WriteAsync(bytes, cts.Token).ConfigureAwait(false);
            await c.Stream.FlushAsync(cts.Token).ConfigureAwait(false);
            return true;
        }
        catch (Exception e) when (e is IOException or OperationCanceledException or ObjectDisposedException or InvalidOperationException)
        {
            _log.LogDebug("Pipe write failed ({Error}); dropping client", e.GetType().Name);
            Drop(c);
            return false;
        }
        finally
        {
            c.WriteLock.Release();
        }
    }

    private static NamedPipeServerStream Create(bool firstInstance)
    {
        var sec = new PipeSecurity();
        sec.AddAccessRule(new PipeAccessRule(new SecurityIdentifier(WellKnownSidType.NetworkSid, null),
            PipeAccessRights.FullControl, AccessControlType.Deny));
        sec.AddAccessRule(new PipeAccessRule(new SecurityIdentifier(WellKnownSidType.AuthenticatedUserSid, null),
            PipeAccessRights.ReadWrite, AccessControlType.Allow));
        sec.AddAccessRule(new PipeAccessRule(new SecurityIdentifier(WellKnownSidType.LocalSystemSid, null),
            PipeAccessRights.FullControl, AccessControlType.Allow));
        var options = PipeOptions.Asynchronous | (firstInstance ? PipeOptions.FirstPipeInstance : PipeOptions.None);
        return NamedPipeServerStreamAcl.Create(PipeName, PipeDirection.InOut, maxNumberOfServerInstances: 3,
            PipeTransmissionMode.Byte, options, inBufferSize: 64 * 1024, outBufferSize: 64 * 1024, sec);
    }

    private async Task HandleAsync(NamedPipeServerStream stream, CancellationToken ct)
    {
        Client? client = null;
        try
        {
            var pid = Verify(stream);
            if (pid is null)
            {
                stream.Dispose();
                return;
            }

            client = new Client { Stream = stream, Pid = pid.Value };
            Client? old;
            lock (_gate) { old = _active; _active = client; }
            if (old is not null)
            {
                old.Stream.Dispose();
                ClientDisconnected?.Invoke(old.Pid);
            }
            _log.LogInformation("Shell connected (pid {Pid})", client.Pid);
            if (ClientConnected is { } onConnected) await onConnected(client.Pid).ConfigureAwait(false);

            var reader = new BoundedLineReader(stream, BoundedLineReader.DefaultMaxLineBytes);
            while (!ct.IsCancellationRequested)
            {
                var line = await reader.ReadLineAsync(ct).ConfigureAwait(false);
                if (line is null) break;
                if (line.Length == 0) continue;
                PipeMessage msg;
                try { msg = PipeMessage.Parse(line); }
                catch (FormatException) { _log.LogDebug("Ignoring malformed pipe line"); continue; }
                if (MessageReceived is { } onMessage)
                {
                    try { await onMessage(msg, client.Pid).ConfigureAwait(false); }
                    catch (Exception e) when (e is not OperationCanceledException)
                    {
                        _log.LogError("Pipe message handler failed: {Error}", e.GetType().Name);
                    }
                }
            }
        }
        catch (Exception e) when (e is IOException or ObjectDisposedException or OperationCanceledException or InvalidOperationException)
        {
            // client went away or was replaced
        }
        finally
        {
            if (client is not null) Drop(client);
            else stream.Dispose();
        }
    }

    private int? Verify(NamedPipeServerStream stream)
    {
        var pid = Native.TryGetPipeClientProcessId(stream.SafePipeHandle);
        if (pid is null)
        {
            _log.LogWarning("Rejected pipe client: cannot resolve its process id");
            return null;
        }

        // PRIMARY GATE: the client must be the exact process instance (pid + creation time) that
        // ShellSupervisor launched. This defeats a fake shell, the genuine exe started by hand, and
        // PID reuse. We never fall back to "newest client wins" or an image-path string match.
        var createdAt = Native.TryGetProcessCreationTime(pid.Value);
        if (!_pin.Matches(pid.Value, createdAt))
        {
            _log.LogWarning("Rejected pipe client pid {Pid}: not the shell instance this service launched", pid);
            return null;
        }

        // SECONDARY sanity check only (never the sole gate): the image should be the installed shell.
        // Compared via file identity, with a normalised-path fallback, so an 8.3 short path or a
        // symlink cannot lock out the genuine shell. A mismatch is logged but the pin already decided.
        var image = Native.TryGetImagePath(pid.Value);
        if (image is null || !SameFile(image, _shellPath))
            _log.LogWarning("Pinned shell pid {Pid} has an unexpected image path ({Image}); accepting on the pin",
                pid, image is null ? "unknown" : Path.GetFileName(image));

        return pid;
    }

    private static bool SameFile(string a, string b)
    {
        try
        {
            if (string.Equals(Path.GetFullPath(a), Path.GetFullPath(b), StringComparison.OrdinalIgnoreCase)) return true;
            return Native.SameFileIdentity(a, b);
        }
        catch (Exception e) when (e is ArgumentException or IOException or NotSupportedException)
        {
            return false;
        }
    }

    private void Drop(Client c)
    {
        bool wasActive;
        lock (_gate)
        {
            wasActive = ReferenceEquals(_active, c);
            if (wasActive) _active = null;
        }
        try { c.Stream.Dispose(); } catch (IOException) { }
        if (wasActive)
        {
            _log.LogInformation("Shell disconnected (pid {Pid})", c.Pid);
            ClientDisconnected?.Invoke(c.Pid);
        }
    }
}
