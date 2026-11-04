namespace PcGuard.Core;

/// <summary>Error codes of <see cref="AdminResultMessage"/>.</summary>
public static class AdminErrors
{
    public const string BadCredentials = "bad_credentials";
    public const string NotAdmin = "not_admin";
    public const string LockedOut = "locked_out";
    public const string InvalidDuration = "invalid_duration";
    public const string Error = "error";
}

/// <summary>Outcome of the Windows check (LogonUser + local Administrators membership).</summary>
public enum AdminAuthResult { Ok, BadCredentials, NotAdmin, Error }

/// <param name="Reply">Non-null: answer the shell with this and do NOT authenticate.</param>
/// <param name="Account">Non-null (and Reply null): authenticate this account.</param>
public sealed record AdminPrecheck(AdminResultMessage? Reply, AdminAccountName? Account);

/// <summary>
/// Pure decision logic around one administrator maintenance unlock attempt; the Windows calls
/// happen between <see cref="Precheck"/> and <see cref="Complete"/> in the service. Order:
/// lockout / spacing first (a locked-out request never reaches LogonUser, even with the right
/// password), then the fixed duration set, then the account name and password shape.
/// Not thread-safe: the service runs attempts one at a time on its admin worker.
/// </summary>
public sealed class AdminUnlockGate
{
    /// <summary>Windows passwords are limited to 256 characters (PWLEN); anything longer cannot be right.</summary>
    public const int MaxPasswordLength = 256;

    private readonly MaintenanceMode _mode;
    private readonly AdminAttemptLimiter _limiter;

    public AdminUnlockGate(MaintenanceMode mode, AdminAttemptLimiter limiter)
    {
        _mode = mode;
        _limiter = limiter;
    }

    public AdminPrecheck Precheck(DateTimeOffset now, string username, int passwordLength, int minutes)
    {
        var d = _limiter.Check(now);
        if (d.Kind != AdminAttemptKind.Allowed)
            return new AdminPrecheck(new AdminResultMessage(false, AdminErrors.LockedOut, d.RetrySeconds), null);

        if (!MaintenanceMode.IsAllowedDuration(minutes))
            return new AdminPrecheck(new AdminResultMessage(false, AdminErrors.InvalidDuration, 0), null);

        if (passwordLength <= 0 || passwordLength > MaxPasswordLength || !AdminAccountName.TryParse(username, out var account))
            return new AdminPrecheck(Fail(now, AdminErrors.BadCredentials), null);

        return new AdminPrecheck(null, account);
    }

    public AdminResultMessage Complete(DateTimeOffset now, int minutes, AdminAuthResult result)
    {
        switch (result)
        {
            case AdminAuthResult.Ok:
                if (!_mode.Activate(now, minutes)) return new AdminResultMessage(false, AdminErrors.InvalidDuration, 0);
                _limiter.RecordSuccess();
                return new AdminResultMessage(true, null, 0);
            case AdminAuthResult.BadCredentials:
                return Fail(now, AdminErrors.BadCredentials);
            case AdminAuthResult.NotAdmin:
                return Fail(now, AdminErrors.NotAdmin);
            default:
                return Fail(now, AdminErrors.Error); // fail closed: an error counts like a wrong password
        }
    }

    private AdminResultMessage Fail(DateTimeOffset now, string code)
    {
        _limiter.RecordFailure(now);
        var d = _limiter.Check(now);
        return d.Kind == AdminAttemptKind.LockedOut
            ? new AdminResultMessage(false, AdminErrors.LockedOut, d.RetrySeconds)
            : new AdminResultMessage(false, code, 0);
    }
}
