namespace PcGuard.Core;

/// <summary>Monotonic time for deadlines: never stepped by NTP, w32time or an administrator setting the clock.</summary>
public static class MonotonicClock
{
    /// <summary>Time since boot (Environment.TickCount64, GetTickCount64 on Windows: keeps counting
    /// during sleep, so a window also expires while the PC sleeps).</summary>
    public static TimeSpan Now() => TimeSpan.FromMilliseconds(Environment.TickCount64);
}

/// <summary>
/// Maintenance mode (teacher code) — the one deliberate EXCEPTION to "the agent never unlocks itself".
/// A teacher issues a one-time code for this PC in the console; when the backend accepts it, the
/// service suspends enforcement for a fixed, short time. It is:
/// - time-limited: exactly 15, 60 or 240 minutes (<see cref="AllowedMinutes"/>), the duration the
///   teacher chose and the backend returned; nothing else activates it;
/// - tracked on a MONOTONIC clock (injected; <see cref="MonotonicClock"/> by default), so setting the
///   wall clock back or forward neither ends it early nor extends it. The wall-clock time passed to
///   <see cref="Activate"/> only gives <see cref="Until"/>, for display and the audit log;
/// - IN MEMORY ONLY: never persisted, so a service restart always re-locks;
/// - ended at expiry or from the PC (admin_end, the banner's End button). There is no remote end yet.
/// Thread-safe. Audit logging is the caller's job.
/// </summary>
public sealed class MaintenanceMode
{
    public static readonly IReadOnlyList<int> AllowedMinutes = new[] { 15, 60, 240 };

    private readonly Func<TimeSpan> _monotonic;
    private readonly object _lock = new();
    private TimeSpan? _start;    // monotonic
    private TimeSpan? _deadline; // monotonic
    private DateTimeOffset? _until; // wall clock, display only

    public MaintenanceMode() : this(MonotonicClock.Now) { }

    public MaintenanceMode(Func<TimeSpan> monotonic)
    {
        _monotonic = monotonic ?? throw new ArgumentNullException(nameof(monotonic));
    }

    public static bool IsAllowedDuration(int minutes) => AllowedMinutes.Contains(minutes);

    /// <summary>Wall-clock end of the current window, for display and the audit log only (the
    /// deadline itself is monotonic); null when none was activated (or it ended).</summary>
    public DateTimeOffset? Until
    {
        get { lock (_lock) return _until; }
    }

    /// <summary>Starts (or replaces) a window of <paramref name="minutes"/> monotonic minutes from now.
    /// <paramref name="wallNow"/> only sets <see cref="Until"/>. False, and no change, for any duration
    /// outside <see cref="AllowedMinutes"/>.</summary>
    public bool Activate(DateTimeOffset wallNow, int minutes)
    {
        if (!IsAllowedDuration(minutes)) return false;
        var length = TimeSpan.FromMinutes(minutes);
        lock (_lock)
        {
            var now = _monotonic();
            _start = now;
            _deadline = now + length;
            _until = wallNow + length;
        }
        return true;
    }

    /// <summary>Ends maintenance. Returns true when a window had been activated (and not yet cleared).</summary>
    public bool End()
    {
        lock (_lock)
        {
            var was = _deadline is not null;
            Clear();
            return was;
        }
    }

    /// <summary>Active only inside [start, deadline) on the monotonic clock; a reading before the start
    /// (which a real monotonic clock never gives) counts as inactive.</summary>
    public bool IsActive()
    {
        lock (_lock) return Inside(_monotonic());
    }

    /// <summary>Clears a window that is no longer active (expired). Returns true exactly once, when it did so.</summary>
    public bool TryExpire()
    {
        lock (_lock)
        {
            if (_deadline is null) return false;
            if (Inside(_monotonic())) return false;
            Clear();
            return true;
        }
    }

    private bool Inside(TimeSpan now) => _start is { } s && _deadline is { } d && now >= s && now < d;

    private void Clear()
    {
        _start = null;
        _deadline = null;
        _until = null;
    }
}
