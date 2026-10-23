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

    public bool Matches(int pid, long? createdAt)
    {
        if (createdAt is null) return false;
        lock (_lock)
        {
            return _set && pid == _pid && createdAt.Value == _createdAt;
        }
    }
}
