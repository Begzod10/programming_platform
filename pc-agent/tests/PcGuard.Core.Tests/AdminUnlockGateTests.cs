using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class AdminUnlockGateTests
{
    private static readonly DateTimeOffset T0 = new(2026, 10, 23, 10, 0, 0, TimeSpan.Zero);

    private static (AdminUnlockGate Gate, MaintenanceMode Mode, AdminAttemptLimiter Limiter) New()
    {
        var mode = new MaintenanceMode();
        var limiter = new AdminAttemptLimiter();
        return (new AdminUnlockGate(mode, limiter), mode, limiter);
    }

    [Fact]
    public void ErrorCodesExact()
    {
        Assert.Equal("bad_credentials", AdminErrors.BadCredentials);
        Assert.Equal("not_admin", AdminErrors.NotAdmin);
        Assert.Equal("locked_out", AdminErrors.LockedOut);
        Assert.Equal("invalid_duration", AdminErrors.InvalidDuration);
        Assert.Equal("error", AdminErrors.Error);
    }

    [Fact]
    public void ValidRequestProceedsWithParsedAccount()
    {
        var (g, _, _) = New();
        var p = g.Precheck(T0, @"PC\admin", 8, 60);
        Assert.Null(p.Reply);
        Assert.Equal(new AdminAccountName("PC", "admin"), p.Account);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(30)]
    [InlineData(int.MaxValue)]
    [InlineData(-60)]
    public void InvalidDurationIsRejectedBeforeAuthenticationAndIsNotAFailure(int minutes)
    {
        var (g, mode, limiter) = New();
        var p = g.Precheck(T0, "admin", 8, minutes);
        Assert.Equal(new AdminResultMessage(false, "invalid_duration", 0), p.Reply);
        Assert.Null(p.Account);
        Assert.Equal(0, limiter.ConsecutiveFailures);
        Assert.False(mode.IsActive(T0));
    }

    [Theory]
    [InlineData("", 8)]
    [InlineData("  ", 8)]
    [InlineData("ad\nmin", 8)]
    [InlineData("admin", 0)]
    [InlineData("admin", 257)]
    public void UnusableNameOrPasswordIsBadCredentialsAndCountsAsFailure(string user, int pwLen)
    {
        var (g, _, limiter) = New();
        var p = g.Precheck(T0, user, pwLen, 15);
        Assert.Equal(new AdminResultMessage(false, "bad_credentials", 0), p.Reply);
        Assert.Null(p.Account);
        Assert.Equal(1, limiter.ConsecutiveFailures);
    }

    [Fact]
    public void PasswordOf256CharactersIsAccepted()
    {
        Assert.Equal(256, AdminUnlockGate.MaxPasswordLength);
        var (g, _, _) = New();
        Assert.Null(g.Precheck(T0, "admin", 256, 15).Reply);
    }

    [Fact]
    public void SuccessActivatesMaintenanceForTheRequestedMinutesAndResetsFailures()
    {
        var (g, mode, limiter) = New();
        limiter.RecordFailure(T0.AddSeconds(-10));
        var r = g.Complete(T0, 15, AdminAuthResult.Ok);
        Assert.Equal(new AdminResultMessage(true, null, 0), r);
        Assert.True(mode.IsActive(T0));
        Assert.Equal(T0.AddMinutes(15), mode.Until);
        Assert.Equal(0, limiter.ConsecutiveFailures);
    }

    [Fact]
    public void SuccessWithAnInvalidDurationNeverActivates()
    {
        var (g, mode, _) = New();
        Assert.Equal(new AdminResultMessage(false, "invalid_duration", 0), g.Complete(T0, 100000, AdminAuthResult.Ok));
        Assert.False(mode.IsActive(T0));
    }

    [Theory]
    [InlineData(AdminAuthResult.BadCredentials, "bad_credentials")]
    [InlineData(AdminAuthResult.NotAdmin, "not_admin")]
    [InlineData(AdminAuthResult.Error, "error")]
    public void FailuresMapToTheirCodeAndCount(AdminAuthResult result, string code)
    {
        var (g, mode, limiter) = New();
        Assert.Equal(new AdminResultMessage(false, code, 0), g.Complete(T0, 60, result));
        Assert.Equal(1, limiter.ConsecutiveFailures);
        Assert.False(mode.IsActive(T0));
    }

    [Fact]
    public void SecondAttemptWithinOneSecondIsRefusedWithRetry()
    {
        var (g, _, _) = New();
        g.Complete(T0, 60, AdminAuthResult.BadCredentials);
        Assert.Equal(new AdminResultMessage(false, "locked_out", 1), g.Precheck(T0.AddMilliseconds(300), "admin", 8, 60).Reply);
        Assert.Null(g.Precheck(T0.AddSeconds(1), "admin", 8, 60).Reply);
    }

    [Fact]
    public void FifthFailureRepliesLockedOutAndTheRightPasswordIsRefusedDuringLockout()
    {
        var (g, mode, _) = New();
        var t = T0;
        for (var i = 0; i < 4; i++)
        {
            Assert.Null(g.Precheck(t, "admin", 8, 60).Reply);
            Assert.Equal("bad_credentials", g.Complete(t, 60, AdminAuthResult.BadCredentials).Error);
            t = t.AddSeconds(2);
        }
        Assert.Null(g.Precheck(t, "admin", 8, 60).Reply);
        Assert.Equal(new AdminResultMessage(false, "locked_out", 600), g.Complete(t, 60, AdminAuthResult.BadCredentials));

        // during the lockout the request never reaches authentication
        var during = g.Precheck(t.AddMinutes(9), "admin", 8, 60);
        Assert.Equal(new AdminResultMessage(false, "locked_out", 60), during.Reply);
        Assert.Null(during.Account);
        Assert.False(mode.IsActive(t.AddMinutes(9)));

        // after it, a correct password works again
        var after = t.AddMinutes(10);
        Assert.Null(g.Precheck(after, "admin", 8, 60).Reply);
        Assert.True(g.Complete(after, 60, AdminAuthResult.Ok).Ok);
        Assert.True(mode.IsActive(after));
    }

    [Fact]
    public void LockoutIsCheckedBeforeDuration()
    {
        var (g, _, limiter) = New();
        for (var i = 0; i < 5; i++) limiter.RecordFailure(T0);
        Assert.Equal("locked_out", g.Precheck(T0, "admin", 8, 9999).Reply!.Error);
    }
}
