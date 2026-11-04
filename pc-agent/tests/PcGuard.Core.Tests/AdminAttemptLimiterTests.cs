using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class AdminAttemptLimiterTests
{
    private static readonly DateTimeOffset T0 = new(2026, 10, 23, 10, 0, 0, TimeSpan.Zero);

    [Fact]
    public void ConstantsAreExact()
    {
        Assert.Equal(TimeSpan.FromSeconds(1), AdminAttemptLimiter.MinSpacing);
        Assert.Equal(5, AdminAttemptLimiter.MaxFailures);
        Assert.Equal(TimeSpan.FromMinutes(10), AdminAttemptLimiter.Lockout);
    }

    [Fact]
    public void FreshLimiterAllows()
        => Assert.Equal(new AdminAttemptDecision(AdminAttemptKind.Allowed, 0), new AdminAttemptLimiter().Check(T0));

    [Fact]
    public void AttemptWithinOneSecondOfAFailureMustWait()
    {
        var l = new AdminAttemptLimiter();
        l.RecordFailure(T0);
        Assert.Equal(new AdminAttemptDecision(AdminAttemptKind.Wait, 1), l.Check(T0));
        Assert.Equal(new AdminAttemptDecision(AdminAttemptKind.Wait, 1), l.Check(T0.AddMilliseconds(999)));
        Assert.Equal(new AdminAttemptDecision(AdminAttemptKind.Allowed, 0), l.Check(T0.AddSeconds(1)));
    }

    [Fact]
    public void FourFailuresDoNotLockOut()
    {
        var l = new AdminAttemptLimiter();
        for (var i = 0; i < 4; i++) l.RecordFailure(T0.AddSeconds(2 * i));
        Assert.False(l.IsLockedOut(T0.AddSeconds(10)));
        Assert.Equal(AdminAttemptKind.Allowed, l.Check(T0.AddSeconds(10)).Kind);
    }

    [Fact]
    public void FiveConsecutiveFailuresLockOutForTenMinutes()
    {
        var l = new AdminAttemptLimiter();
        for (var i = 0; i < 5; i++) l.RecordFailure(T0.AddSeconds(2 * i));
        var last = T0.AddSeconds(8);
        Assert.True(l.IsLockedOut(last));
        Assert.Equal(new AdminAttemptDecision(AdminAttemptKind.LockedOut, 600), l.Check(last));
        Assert.Equal(new AdminAttemptDecision(AdminAttemptKind.LockedOut, 540), l.Check(last.AddMinutes(1)));
        Assert.Equal(new AdminAttemptDecision(AdminAttemptKind.LockedOut, 1), l.Check(last.AddMinutes(10).AddMilliseconds(-1)));
    }

    [Fact]
    public void RetrySecondsRoundUp()
    {
        var l = new AdminAttemptLimiter();
        for (var i = 0; i < 5; i++) l.RecordFailure(T0);
        Assert.Equal(600, l.Check(T0.AddMilliseconds(500)).RetrySeconds); // 599.5 s -> 600
    }

    [Fact]
    public void LockoutExpiryResetsTheCounter()
    {
        var l = new AdminAttemptLimiter();
        for (var i = 0; i < 5; i++) l.RecordFailure(T0);
        var after = T0.AddMinutes(10);
        Assert.Equal(new AdminAttemptDecision(AdminAttemptKind.Allowed, 0), l.Check(after));
        Assert.Equal(0, l.ConsecutiveFailures);
        // a single new failure does not lock out again
        l.RecordFailure(after);
        Assert.False(l.IsLockedOut(after.AddSeconds(2)));
        Assert.Equal(AdminAttemptKind.Allowed, l.Check(after.AddSeconds(2)).Kind);
    }

    [Fact]
    public void SuccessResetsTheCounter()
    {
        var l = new AdminAttemptLimiter();
        for (var i = 0; i < 4; i++) l.RecordFailure(T0.AddSeconds(2 * i));
        l.RecordSuccess();
        Assert.Equal(0, l.ConsecutiveFailures);
        for (var i = 0; i < 4; i++) l.RecordFailure(T0.AddSeconds(20 + 2 * i));
        Assert.Equal(AdminAttemptKind.Allowed, l.Check(T0.AddSeconds(40)).Kind);
    }

    [Fact]
    public void FailuresDuringLockoutDoNotExtendIt()
    {
        var l = new AdminAttemptLimiter();
        for (var i = 0; i < 5; i++) l.RecordFailure(T0);
        l.RecordFailure(T0.AddMinutes(5));
        Assert.Equal(new AdminAttemptDecision(AdminAttemptKind.LockedOut, 300), l.Check(T0.AddMinutes(5)));
    }

    [Fact]
    public void ClockSetBackDuringLockoutKeepsItBoundedToTenMinutes()
    {
        var l = new AdminAttemptLimiter();
        for (var i = 0; i < 5; i++) l.RecordFailure(T0);
        var back = T0.AddHours(-3);
        Assert.Equal(new AdminAttemptDecision(AdminAttemptKind.LockedOut, 600), l.Check(back));
        Assert.Equal(AdminAttemptKind.Allowed, l.Check(back.AddMinutes(10)).Kind);
    }

    [Fact]
    public void ClockSetBackAfterAFailureDoesNotBlockForever()
    {
        var l = new AdminAttemptLimiter();
        l.RecordFailure(T0);
        Assert.Equal(AdminAttemptKind.Allowed, l.Check(T0.AddHours(-1)).Kind);
    }
}
