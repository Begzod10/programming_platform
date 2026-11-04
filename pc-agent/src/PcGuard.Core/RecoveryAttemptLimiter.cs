using System.Globalization;

namespace PcGuard.Core;

/// <summary>What the service found when it read %ProgramData%\PcGuard\recovery.attempts.</summary>
public enum RecoveryAttemptFileStatus
{
    /// <summary>No file: nothing failed since the last success (or an administrator deleted it).</summary>
    Missing,
    /// <summary>A regular, small file with the SYSTEM/Administrators-only owner and ACL (same rules as recovery.hash).</summary>
    Ok,
    /// <summary>A link, too large, wrong owner or ACL, or unreadable.</summary>
    Untrusted,
}

/// <summary>Storage of recovery.attempts (the service implements it on the admin-only data folder).</summary>
public interface IRecoveryAttemptStore
{
    /// <summary>Reads the file; <paramref name="text"/> is set only for <see cref="RecoveryAttemptFileStatus.Ok"/>. Never throws.</summary>
    RecoveryAttemptFileStatus Read(out string? text);

    /// <summary>Replaces the file with <paramref name="text"/> (admin-only, atomic). False on any failure. Never throws.</summary>
    bool Write(string text);

    /// <summary>Removes the file (missing counts as success). False on failure. Never throws.</summary>
    bool Delete();
}

/// <summary>Persisted limiter state: consecutive failures, lockouts started so far (the escalation level) and the lockout end.</summary>
public sealed record RecoveryAttemptState(int Failures, int Lockouts, DateTimeOffset? LockedUntilUtc)
{
    public const int MaxLockouts = 1000;
    private const long MaxUnixSeconds = 253_402_300_799; // 9999-12-31

    /// <summary><c>v1;failures=N;lockouts=N;until=UNIXSECONDS</c> (0 = no lockout). ASCII, one line.</summary>
    public string Format()
    {
        var until = LockedUntilUtc is { } u ? u.ToUnixTimeSeconds() : 0;
        return "v1;failures=" + Failures.ToString(CultureInfo.InvariantCulture)
               + ";lockouts=" + Lockouts.ToString(CultureInfo.InvariantCulture)
               + ";until=" + until.ToString(CultureInfo.InvariantCulture);
    }

    /// <summary>The state, or null when the text is not exactly the format (corrupt). Never throws.</summary>
    public static RecoveryAttemptState? Parse(string? text)
    {
        if (text is null || text.Length > 128) return null;
        var parts = text.Trim().Split(';');
        if (parts.Length != 4 || parts[0] != "v1") return null;
        if (!Field(parts[1], "failures=", out var failures) || failures > RecoveryAttemptLimiter.MaxFailures) return null;
        if (!Field(parts[2], "lockouts=", out var lockouts) || lockouts > MaxLockouts) return null;
        if (!Field(parts[3], "until=", out var until) || until > MaxUnixSeconds) return null;
        if (failures >= RecoveryAttemptLimiter.MaxFailures && until == 0) return null; // never written: a lockout always has an end
        return new RecoveryAttemptState((int)failures, (int)lockouts,
            until == 0 ? null : DateTimeOffset.FromUnixTimeSeconds(until));
    }

    private static bool Field(string part, string name, out long value)
    {
        value = 0;
        if (!part.StartsWith(name, StringComparison.Ordinal)) return false;
        var digits = part.AsSpan(name.Length);
        if (digits.Length is 0 or > 15 || (digits.Length > 1 && digits[0] == '0')) return false;
        foreach (var c in digits)
            if (c is < '0' or > '9') return false;
        return long.TryParse(digits, NumberStyles.None, CultureInfo.InvariantCulture, out value);
    }
}

/// <summary>
/// Brute-force protection of the offline recovery code, persisted so that neither a service restart
/// nor a reboot (which a standard user can cause) resets it:
/// <list type="bullet">
/// <item>at least <see cref="MinSpacing"/> between attempts (memory only; a reboot takes far longer);</item>
/// <item><see cref="MaxFailures"/> consecutive failures start a lockout of 10 minutes, then 1 hour, then
/// 24 hours for every further one (<see cref="LockoutFor"/>); only a successful release (or an
/// administrator deleting recovery.attempts and restarting the service) resets the escalation;</item>
/// <item>every attempt is written to the store as a failure BEFORE the code is verified
/// (<see cref="BeginAttempt"/>), so cutting the power during the check still counts; an attempt that
/// cannot be written is refused;</item>
/// <item>the file is read once, at construction (service start). Missing = fresh start. Untrusted or
/// corrupt = locked out for 24 hours (<see cref="LoadProblem"/> says why), and that state is written
/// back. While running, memory is authoritative: a file that disappears never shortens a lockout.</item>
/// </list>
/// A wall-clock step back never makes the current lockout longer than its own length. Pure apart
/// from the store; the caller supplies "now". Not thread-safe (the service serialises calls).
/// </summary>
public sealed class RecoveryAttemptLimiter
{
    public static readonly TimeSpan MinSpacing = TimeSpan.FromSeconds(1);
    public const int MaxFailures = 5;
    private static readonly TimeSpan[] Steps = { TimeSpan.FromMinutes(10), TimeSpan.FromHours(1), TimeSpan.FromHours(24) };

    private readonly IRecoveryAttemptStore _store;
    private DateTimeOffset? _lastAttempt;
    private DateTimeOffset? _lockedUntil;

    public RecoveryAttemptLimiter(IRecoveryAttemptStore store, DateTimeOffset now)
    {
        _store = store ?? throw new ArgumentNullException(nameof(store));
        var status = store.Read(out var text);
        switch (status)
        {
            case RecoveryAttemptFileStatus.Missing:
                return;
            case RecoveryAttemptFileStatus.Ok when RecoveryAttemptState.Parse(text) is { } state:
                ConsecutiveFailures = state.Failures;
                Lockouts = state.Lockouts;
                _lockedUntil = state.LockedUntilUtc;
                if (_lockedUntil is { } until && until <= now)
                {
                    // that lockout is over: counting starts again (the escalation level stays)
                    _lockedUntil = null;
                    ConsecutiveFailures = 0;
                }
                if (Lockouts == 0 && _lockedUntil is not null) Lockouts = 1;
                return;
            default:
                LoadProblem = status == RecoveryAttemptFileStatus.Untrusted ? "untrusted or unreadable" : "corrupt";
                Lockouts = Steps.Length; // the next one is the longest too
                ConsecutiveFailures = 0;
                _lockedUntil = now + Steps[^1];
                Persist();
                return;
        }
    }

    /// <summary>Non-null when recovery.attempts was untrusted or corrupt at start (attempts locked out for 24 h).</summary>
    public string? LoadProblem { get; }

    public int ConsecutiveFailures { get; private set; }

    /// <summary>Lockouts started since the last success (the escalation level).</summary>
    public int Lockouts { get; private set; }

    /// <summary>Length of the lockout in force (or the last one started); 10 minutes when there was none.</summary>
    public TimeSpan CurrentLockout => LockoutFor(Math.Max(0, Lockouts - 1));

    /// <summary>Length of the lockout number <paramref name="index"/> + 1: 10 min, 1 h, then 24 h.</summary>
    public static TimeSpan LockoutFor(int index) => Steps[Math.Clamp(index, 0, Steps.Length - 1)];

    public AdminAttemptDecision Check(DateTimeOffset now)
    {
        if (_lockedUntil is { } until)
        {
            var cap = CurrentLockout;
            var left = until - now;
            if (left > cap)
            {
                // clock set back during a lockout: keep it, but never longer than its own length
                _lockedUntil = now + cap;
                left = cap;
            }
            if (left > TimeSpan.Zero) return new AdminAttemptDecision(AdminAttemptKind.LockedOut, Seconds(left));
            _lockedUntil = null;
            _lastAttempt = null;
            ConsecutiveFailures = 0;
        }

        if (_lastAttempt is { } last)
        {
            var since = now - last;
            // a negative gap (clock set back) does not block: changing the clock needs administrator rights
            if (since >= TimeSpan.Zero && since < MinSpacing)
                return new AdminAttemptDecision(AdminAttemptKind.Wait, Seconds(MinSpacing - since));
        }
        return new AdminAttemptDecision(AdminAttemptKind.Allowed, 0);
    }

    /// <summary>
    /// Counts this attempt as a failure (starting the next lockout at the 5th) and writes that to the
    /// store BEFORE the caller verifies the code. False when locked out or when the write failed: then
    /// the code must NOT be verified (the attempt still counts in memory).
    /// </summary>
    public bool BeginAttempt(DateTimeOffset now)
    {
        if (Check(now).Kind == AdminAttemptKind.LockedOut) return false;
        _lastAttempt = now;
        ConsecutiveFailures++;
        if (ConsecutiveFailures >= MaxFailures)
        {
            _lockedUntil = now + LockoutFor(Lockouts);
            Lockouts++;
        }
        return Persist();
    }

    /// <summary>The code was right: everything is reset and recovery.attempts deleted. False when the delete failed.</summary>
    public bool RecordSuccess()
    {
        ConsecutiveFailures = 0;
        Lockouts = 0;
        _lastAttempt = null;
        _lockedUntil = null;
        return _store.Delete();
    }

    private bool Persist() => _store.Write(new RecoveryAttemptState(ConsecutiveFailures, Lockouts, _lockedUntil).Format());

    private static int Seconds(TimeSpan t) => Math.Max(1, (int)Math.Ceiling(t.TotalSeconds));
}
