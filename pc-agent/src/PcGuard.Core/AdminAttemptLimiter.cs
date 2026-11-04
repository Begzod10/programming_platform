namespace PcGuard.Core;

public enum AdminAttemptKind { Allowed, Wait, LockedOut }

/// <param name="RetrySeconds">Seconds until another attempt is accepted (rounded up, at least 1); 0 when allowed.</param>
public sealed record AdminAttemptDecision(AdminAttemptKind Kind, int RetrySeconds);

/// <summary>
/// Brute-force protection for the administrator maintenance unlock (in memory only, reset by a service
/// restart): at least <see cref="MinSpacing"/> between attempts, and <see cref="MaxFailures"/>
/// consecutive failures lock attempts out for <see cref="Lockout"/>. A success resets the counter; so
/// does the end of a lockout. Pure (the caller supplies "now"); not thread-safe — the service uses it
/// from its single admin worker only.
/// </summary>
public sealed class AdminAttemptLimiter
{
    public static readonly TimeSpan MinSpacing = TimeSpan.FromSeconds(1);
    public const int MaxFailures = 5;
    public static readonly TimeSpan Lockout = TimeSpan.FromMinutes(10);

    private DateTimeOffset? _lastFailure;
    private DateTimeOffset? _lockedUntil;

    public int ConsecutiveFailures { get; private set; }

    public AdminAttemptDecision Check(DateTimeOffset now)
    {
        if (_lockedUntil is { } until)
        {
            var left = until - now;
            if (left > Lockout)
            {
                // clock set back during a lockout: keep it, but never longer than one full lockout
                _lockedUntil = now + Lockout;
                left = Lockout;
            }
            if (left > TimeSpan.Zero) return new AdminAttemptDecision(AdminAttemptKind.LockedOut, Seconds(left));
            // lockout over: start counting again
            _lockedUntil = null;
            _lastFailure = null;
            ConsecutiveFailures = 0;
        }

        if (_lastFailure is { } last)
        {
            var since = now - last;
            // a negative gap (clock set back) does not block: changing the clock needs administrator rights
            if (since >= TimeSpan.Zero && since < MinSpacing)
                return new AdminAttemptDecision(AdminAttemptKind.Wait, Seconds(MinSpacing - since));
        }
        return new AdminAttemptDecision(AdminAttemptKind.Allowed, 0);
    }

    public bool IsLockedOut(DateTimeOffset now) => Check(now).Kind == AdminAttemptKind.LockedOut;

    public void RecordFailure(DateTimeOffset now)
    {
        _lastFailure = now;
        if (_lockedUntil is not null) return; // already locked out: never extend it
        ConsecutiveFailures++;
        if (ConsecutiveFailures >= MaxFailures) _lockedUntil = now + Lockout;
    }

    public void RecordSuccess()
    {
        ConsecutiveFailures = 0;
        _lastFailure = null;
        _lockedUntil = null;
    }

    private static int Seconds(TimeSpan t) => Math.Max(1, (int)Math.Ceiling(t.TotalSeconds));
}
