namespace PcGuard.Core;

/// <summary>Error codes of <see cref="AdminResultMessage"/> (maintenance code redemption).</summary>
public static class AdminErrors
{
    /// <summary>Wrong, expired, already used or malformed code (the backend does not say which).</summary>
    public const string InvalidCode = "invalid_code";
    /// <summary>Too many local failures (or attempts closer than 1 s): RetrySeconds says when to try again.</summary>
    public const string LockedOut = "locked_out";
    /// <summary>The backend refused with 429: retry later.</summary>
    public const string RateLimited = "rate_limited";
    /// <summary>The backend could not be reached.</summary>
    public const string Offline = "offline";
    /// <summary>Anything else (unexpected answer, internal failure).</summary>
    public const string Error = "error";
}

/// <summary>The one-time maintenance code a teacher issues in the console: exactly six ASCII digits.</summary>
public static class MaintenanceCode
{
    public const int Length = 6;

    /// <summary>
    /// True only for exactly six characters '0'..'9' (the contract <c>^[0-9]{6}$</c>, checked without a
    /// regex: .NET's <c>$</c> also matches before a trailing newline, and char.IsDigit accepts
    /// non-ASCII digits).
    /// </summary>
    public static bool IsWellFormed(string? code)
    {
        if (code is null || code.Length != Length) return false;
        foreach (var c in code)
            if (c is < '0' or > '9') return false;
        return true;
    }

    /// <summary>What a code input box keeps of typed or pasted text: ASCII digits only, at most six.</summary>
    public static string FilterInput(string? input)
    {
        if (string.IsNullOrEmpty(input)) return "";
        var chars = new char[Length];
        var n = 0;
        foreach (var c in input)
        {
            if (c is < '0' or > '9') continue;
            chars[n++] = c;
            if (n == Length) break;
        }
        return new string(chars, 0, n);
    }
}

public enum MaintenanceRedeemStatus { Ok, InvalidCode, RateLimited, Offline, Error }

/// <summary>Typed outcome of <c>POST /pc/maintenance/redeem</c>. Minutes is set (15, 60 or 240) only for Ok.</summary>
public sealed record MaintenanceRedeemResult(MaintenanceRedeemStatus Status, int Minutes = 0)
{
    public static MaintenanceRedeemResult Ok(int minutes) => new(MaintenanceRedeemStatus.Ok, minutes);
    public static readonly MaintenanceRedeemResult InvalidCode = new(MaintenanceRedeemStatus.InvalidCode);
    public static readonly MaintenanceRedeemResult RateLimited = new(MaintenanceRedeemStatus.RateLimited);
    public static readonly MaintenanceRedeemResult Offline = new(MaintenanceRedeemStatus.Offline);
    public static readonly MaintenanceRedeemResult Error = new(MaintenanceRedeemStatus.Error);
}

/// <summary>
/// Pure decision logic around one maintenance code redemption; the backend call happens between
/// <see cref="Precheck"/> and <see cref="Complete"/> in the service. Order: local lockout / 1 s
/// spacing first (a locked-out attempt never reaches the backend, even with a valid code), then the
/// code shape (six ASCII digits; anything else is invalid_code without a network call). Only
/// invalid_code counts toward the local lockout (5 failures -> 10 minutes); rate_limited, offline and
/// error do not. Never sees or keeps the code beyond the shape check.
/// Not thread-safe: the service runs redemptions one at a time on its command loop.
/// </summary>
public sealed class MaintenanceCodeGate
{
    private readonly MaintenanceMode _mode;
    private readonly AdminAttemptLimiter _limiter;

    public MaintenanceCodeGate(MaintenanceMode mode, AdminAttemptLimiter limiter)
    {
        _mode = mode;
        _limiter = limiter;
    }

    /// <summary>Consecutive invalid_code failures so far (for the audit log).</summary>
    public int ConsecutiveFailures => _limiter.ConsecutiveFailures;

    /// <summary>Null: call the backend. Otherwise answer the shell with this and do NOT call it.</summary>
    public AdminResultMessage? Precheck(DateTimeOffset now, string? code)
    {
        var d = _limiter.Check(now);
        if (d.Kind != AdminAttemptKind.Allowed) return new AdminResultMessage(false, AdminErrors.LockedOut, d.RetrySeconds);
        if (!MaintenanceCode.IsWellFormed(code)) return Fail(now);
        return null;
    }

    public AdminResultMessage Complete(DateTimeOffset now, MaintenanceRedeemResult result)
    {
        switch (result.Status)
        {
            case MaintenanceRedeemStatus.Ok:
                // never trust an arbitrary duration: anything outside {15, 60, 240} does not activate
                if (!_mode.Activate(now, result.Minutes)) return new AdminResultMessage(false, AdminErrors.Error, 0);
                _limiter.RecordSuccess();
                return new AdminResultMessage(true, null, 0);
            case MaintenanceRedeemStatus.InvalidCode:
                return Fail(now);
            case MaintenanceRedeemStatus.RateLimited:
                return new AdminResultMessage(false, AdminErrors.RateLimited, 0);
            case MaintenanceRedeemStatus.Offline:
                return new AdminResultMessage(false, AdminErrors.Offline, 0);
            default:
                return new AdminResultMessage(false, AdminErrors.Error, 0);
        }
    }

    private AdminResultMessage Fail(DateTimeOffset now)
    {
        _limiter.RecordFailure(now);
        var d = _limiter.Check(now);
        return d.Kind == AdminAttemptKind.LockedOut
            ? new AdminResultMessage(false, AdminErrors.LockedOut, d.RetrySeconds)
            : new AdminResultMessage(false, AdminErrors.InvalidCode, 0);
    }
}

public enum MaintenanceEndReason { Expired, EndedOnPc, ServiceStopped }

/// <summary>
/// Texts of the maintenance audit entries in the Windows Application event log (these log lines are
/// the PC's whole audit trail). None of them takes the code: it can never end up in a log.
/// </summary>
public static class MaintenanceAudit
{
    public static string Started(int minutes, DateTimeOffset until)
        => $"Maintenance mode started for {minutes.ToString(System.Globalization.CultureInfo.InvariantCulture)} minutes (until "
           + until.UtcDateTime.ToString("yyyy-MM-dd HH:mm", System.Globalization.CultureInfo.InvariantCulture)
           + " UTC), redeemed with teacher code";

    public static string Ended(MaintenanceEndReason reason) => "Maintenance mode ended (" + reason switch
    {
        MaintenanceEndReason.EndedOnPc => "ended on the PC",
        MaintenanceEndReason.ServiceStopped => "service stopped",
        _ => "expired",
    } + ")";

    public static string Rejected(int consecutiveFailures)
        => $"Maintenance code rejected ({consecutiveFailures} of {AdminAttemptLimiter.MaxFailures} consecutive failures)";

    public static string LockedOut()
        => $"Maintenance code attempts locked out for {(int)AdminAttemptLimiter.Lockout.TotalMinutes} minutes after {AdminAttemptLimiter.MaxFailures} consecutive failures";

    public static string RefusedLockedOut(int retrySeconds)
        => $"Maintenance code attempt refused: locked out for another {retrySeconds} s";

    /// <param name="error">One of <see cref="AdminErrors"/> other than invalid_code.</param>
    public static string NotChecked(string error) => "Maintenance code could not be checked: " + error;

    /// <summary>The service refused to send a code because the backend base URL is not https.</summary>
    public static string RefusedInsecureTransport()
        => "Maintenance code not sent: the backend URL is not https (plain http could be forged on the LAN)";
}
