namespace PcGuard.Core;

/// <summary>
/// Administrator maintenance unlock (emergency) — the one deliberate EXCEPTION to "the agent never
/// unlocks itself". A local Windows administrator, authenticated by the SYSTEM service, can suspend
/// enforcement for a fixed, short time. It is:
/// - time-limited: exactly 15, 60 or 240 minutes (<see cref="AllowedMinutes"/>); nothing else activates it;
/// - IN MEMORY ONLY: never persisted, so a service restart always re-locks;
/// - ended at expiry, by the administrator (admin_end), or when the clock is set back before its start.
/// Pure and thread-safe; the caller supplies "now" (injected clock). Audit logging is the caller's job.
/// </summary>
public sealed class MaintenanceMode
{
    public static readonly IReadOnlyList<int> AllowedMinutes = new[] { 15, 60, 240 };

    private readonly object _lock = new();
    private DateTimeOffset? _start;
    private DateTimeOffset? _until;

    public static bool IsAllowedDuration(int minutes) => AllowedMinutes.Contains(minutes);

    /// <summary>When the current maintenance window ends; null when none was activated (or it ended).</summary>
    public DateTimeOffset? Until
    {
        get { lock (_lock) return _until; }
    }

    /// <summary>Starts (or replaces) the window [now, now + minutes). False, and no change, for any
    /// duration outside <see cref="AllowedMinutes"/>.</summary>
    public bool Activate(DateTimeOffset now, int minutes)
    {
        if (!IsAllowedDuration(minutes)) return false;
        lock (_lock)
        {
            _start = now;
            _until = now.AddMinutes(minutes);
        }
        return true;
    }

    /// <summary>Ends maintenance. Returns true when a window had been activated (and not yet cleared).</summary>
    public bool End()
    {
        lock (_lock)
        {
            var was = _until is not null;
            _start = null;
            _until = null;
            return was;
        }
    }

    /// <summary>Active only inside [start, until): a time before the start (clock set back) is inactive.</summary>
    public bool IsActive(DateTimeOffset now)
    {
        lock (_lock) return _start is { } s && _until is { } u && now >= s && now < u;
    }

    /// <summary>Clears a window that is no longer active at <paramref name="now"/> (expired, or the
    /// clock went back before its start). Returns true exactly once, when it did so.</summary>
    public bool TryExpire(DateTimeOffset now)
    {
        lock (_lock)
        {
            if (_start is not { } s || _until is not { } u) return false;
            if (now >= s && now < u) return false;
            _start = null;
            _until = null;
            return true;
        }
    }
}
