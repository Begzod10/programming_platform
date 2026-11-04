namespace PcGuard.Core;

/// <summary>Why the startup grace ended.</summary>
public enum StartupGraceEnd
{
    /// <summary>The first shell connected (and reported) within the window.</summary>
    ShellConnected,
    /// <summary>The window passed without any shell: name-only enforcement from now on.</summary>
    Expired,
}

/// <summary>One evaluation of the grace: whether it is active now, and (exactly once) how it ended.</summary>
public readonly record struct StartupGraceState(bool Active, StartupGraceEnd? JustEnded);

/// <summary>
/// Startup grace: right after the service process starts, the shell is not running yet, so the planner
/// is in its name-only fallback and would kill every non-allowlisted user process (AnyDesk, Telegram,
/// OneDrive, even Setup) seconds before the lock screen can appear. Until the first shell has connected
/// or <see cref="Window"/> has passed, whichever comes first, the fallback's kills are held back
/// (<see cref="Apply"/>); the shell is still launched as usual (ShellMissing/UsedFallback unchanged).
///
/// It applies ONLY to "no shell ever connected since this service process started": once a shell has
/// connected the grace is over for good, so killing or hanging a running shell later gains nothing.
/// Elapsed time is measured on a MONOTONIC source (<see cref="MonotonicClock"/> by default), never the
/// wall clock; a reading earlier than the start ends the grace (fail closed). Thread-safe.
/// </summary>
public sealed class StartupGrace
{
    public static readonly TimeSpan Window = TimeSpan.FromSeconds(30);

    private readonly Func<TimeSpan> _monotonic;
    private readonly TimeSpan _startedAt;
    private readonly object _lock = new();
    private bool _shellConnected;
    private bool _ended;

    public StartupGrace() : this(MonotonicClock.Now) { }

    public StartupGrace(Func<TimeSpan> monotonic)
    {
        _monotonic = monotonic ?? throw new ArgumentNullException(nameof(monotonic));
        _startedAt = _monotonic();
    }

    /// <summary>Pure rule: active while no shell has connected and less than <see cref="Window"/> has
    /// passed since <paramref name="serviceStartedAt"/> (both monotonic).</summary>
    public static bool IsActive(TimeSpan serviceStartedAt, TimeSpan now, bool shellEverConnected)
    {
        if (shellEverConnected) return false;
        var elapsed = now - serviceStartedAt;
        return elapsed >= TimeSpan.Zero && elapsed < Window;
    }

    /// <summary>Records that a verified shell connected. Latched: the grace never comes back.</summary>
    public void MarkShellConnected()
    {
        lock (_lock) _shellConnected = true;
    }

    /// <summary>Evaluates the grace now. Once it is over it stays over; the end is reported once.</summary>
    public StartupGraceState Evaluate()
    {
        lock (_lock)
        {
            if (_ended) return new StartupGraceState(false, null);
            if (IsActive(_startedAt, _monotonic(), _shellConnected)) return new StartupGraceState(true, null);
            _ended = true;
            return new StartupGraceState(false, _shellConnected ? StartupGraceEnd.ShellConnected : StartupGraceEnd.Expired);
        }
    }

    /// <summary>While the grace is active, a name-only (fallback) plan kills and closes nothing; its
    /// ShellMissing/UsedFallback flags are kept so the shell is still launched. Any other plan is
    /// returned unchanged.</summary>
    public static EnforcementPlan Apply(EnforcementPlan plan, bool graceActive)
        => graceActive && plan.UsedFallback
            ? plan with { KillPids = Array.Empty<int>(), CloseWindows = Array.Empty<long>() }
            : plan;
}
