namespace PcGuard.Core;

/// <summary>
/// The PcGuard service as the SCM reports it to the shell (read-only access, which standard users
/// have): QueryServiceStatusEx (current state and process id, 0 when not running) and
/// QueryServiceConfig (start type).
/// </summary>
public sealed record ServiceProbe(uint State, uint StartType, int ProcessId);

/// <summary>Whether the process serving \\.\pipe\PcGuard.Pipe is the PcGuard service.</summary>
public enum PipeServerTrust
{
    /// <summary>The pipe server's process id is the service's process id.</summary>
    Verified,
    /// <summary>Provably not the service (another process, or the service is not running): a squatter.</summary>
    Mismatch,
    /// <summary>The check could not be made (API failure): keep the connection but never exit on "released".</summary>
    Unknown,
}

/// <summary>
/// Pure decisions of the shell about the service it talks to (the Win32 calls are in the shell's
/// Native class):
/// <list type="bullet">
/// <item><see cref="ClassifyServer"/>: GetNamedPipeServerProcessId compared with the SCM's process id
/// of PcGuard. A standard user can create a pipe of the same name while the service is down (SCM
/// restart window, boot); such a server is a <see cref="PipeServerTrust.Mismatch"/>.</item>
/// <item><see cref="HonourReleased"/>: "released" makes the shell exit, so only a verified server may send it.</item>
/// <item><see cref="ShouldExit"/>: after a recovery release the service is Disabled and stopped; a shell
/// that missed "released" (write failed, other session) then exits instead of reconnecting forever.
/// A crashed service (stopped, but Automatic) is restarted by the SCM, so the shell keeps waiting.</item>
/// </list>
/// </summary>
public static class ShellServiceCheck
{
    public const string ServiceName = "PcGuard";

    // SERVICE_STATUS_PROCESS.dwCurrentState
    public const uint Stopped = 1;
    public const uint StartPending = 2;
    public const uint StopPending = 3;
    public const uint Running = 4;

    // QUERY_SERVICE_CONFIG.dwStartType
    public const uint AutoStart = 2;
    public const uint DemandStart = 3;
    public const uint Disabled = 4;

    public static PipeServerTrust ClassifyServer(int? serverPid, ServiceProbe? service)
    {
        if (serverPid is null || service is null) return PipeServerTrust.Unknown;
        if (service.ProcessId == 0 || serverPid.Value != service.ProcessId) return PipeServerTrust.Mismatch;
        return PipeServerTrust.Verified;
    }

    public static bool HonourReleased(PipeServerTrust trust) => trust == PipeServerTrust.Verified;

    public static bool ShouldExit(ServiceProbe? service)
        => service is { State: Stopped, StartType: Disabled };
}
