using PcGuard.Core;

namespace PcGuard.Service;

/// <summary>
/// The exact shell process instance the service itself launched: its pid plus creation time
/// (FILETIME ticks). The pipe server accepts a client only when it matches this pin, so a student
/// running a fake shell (even a copy of PcGuard.Shell.exe placed elsewhere, or the genuine exe
/// started by hand) is rejected before any message is read, and PID reuse is defeated by the
/// creation-time component. Shared between the guard loop (ShellSupervisor sets it) and the pipe
/// server (reads it); all access is locked. WINDOWS semantics, but the type itself is portable.
/// </summary>
internal sealed class ShellPin
{
    private readonly object _lock = new();
    private int _pid;
    private long _createdAt;
    private bool _set;

    public void Set(int pid, long createdAt)
    {
        lock (_lock)
        {
            _pid = pid;
            _createdAt = createdAt;
            _set = true;
        }
    }

    /// <summary>Forget the pin (e.g. the console session changed): the next client must be a freshly
    /// launched, re-pinned shell.</summary>
    public void Clear()
    {
        lock (_lock) _set = false;
    }

    public bool Matches(int pid, long? createdAt) => Check(pid, createdAt, out _) == PinCheck.Match;

    /// <summary>Why a client does or does not match the pin (for the rejection log line);
    /// <paramref name="pinnedPid"/> is the pinned pid (0 when no pin is set). The creation times are
    /// never logged.</summary>
    public PinCheck Check(int pid, long? createdAt, out int pinnedPid)
    {
        lock (_lock)
        {
            pinnedPid = _set ? _pid : 0;
            return PinCheckRules.Classify(_set, _pid, _createdAt, pid, createdAt);
        }
    }
}
