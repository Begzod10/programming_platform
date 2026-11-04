using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class MaintenanceCodeTests
{
    [Theory]
    [InlineData("123456")]
    [InlineData("000000")]
    [InlineData("999999")]
    public void SixAsciiDigitsAreWellFormed(string code) => Assert.True(MaintenanceCode.IsWellFormed(code));

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("12345")]
    [InlineData("1234567")]
    [InlineData("12345a")]
    [InlineData(" 123456")]
    [InlineData("123456 ")]
    [InlineData("123456\n")] // a regex "$" would accept this
    [InlineData("12 456")]
    [InlineData("-12345")]
    [InlineData("١٢٣٤٥٦")] // Arabic-Indic digits: char.IsDigit is true, but they are not [0-9]
    [InlineData("１２３４５６")] // full-width digits
    public void AnythingElseIsRejected(string? code) => Assert.False(MaintenanceCode.IsWellFormed(code));

    [Theory]
    [InlineData("123456", "123456")]
    [InlineData("12 34 56", "123456")]
    [InlineData("1234567890", "123456")]
    [InlineData("a1b2c3", "123")]
    [InlineData("١٢٣", "")]
    [InlineData("", "")]
    [InlineData(null, "")]
    public void FilterInputKeepsAtMostSixAsciiDigits(string? input, string expected)
        => Assert.Equal(expected, MaintenanceCode.FilterInput(input));
}

public class MaintenanceCodeGateTests
{
    private static readonly DateTimeOffset T0 = new(2026, 10, 23, 10, 0, 0, TimeSpan.Zero);

    private static (MaintenanceCodeGate Gate, MaintenanceMode Mode, AdminAttemptLimiter Limiter) New()
    {
        var mode = new MaintenanceMode();
        var limiter = new AdminAttemptLimiter();
        return (new MaintenanceCodeGate(mode, limiter), mode, limiter);
    }

    [Fact]
    public void ErrorCodesExact()
    {
        Assert.Equal("invalid_code", AdminErrors.InvalidCode);
        Assert.Equal("locked_out", AdminErrors.LockedOut);
        Assert.Equal("rate_limited", AdminErrors.RateLimited);
        Assert.Equal("offline", AdminErrors.Offline);
        Assert.Equal("error", AdminErrors.Error);
    }

    [Fact]
    public void WellFormedCodeProceeds()
    {
        var (g, _, limiter) = New();
        Assert.Null(g.Precheck(T0, "123456"));
        Assert.Equal(0, limiter.ConsecutiveFailures);
    }

    [Theory]
    [InlineData("")]
    [InlineData("12345")]
    [InlineData("abcdef")]
    [InlineData("1234567")]
    public void MalformedCodeIsInvalidCodeBeforeAnyNetworkCallAndCounts(string code)
    {
        var (g, mode, limiter) = New();
        Assert.Equal(new AdminResultMessage(false, "invalid_code", 0), g.Precheck(T0, code));
        Assert.Equal(1, limiter.ConsecutiveFailures);
        Assert.False(mode.IsActive());
    }

    [Theory]
    [InlineData(15)]
    [InlineData(60)]
    [InlineData(240)]
    public void SuccessActivatesForTheServersMinutesAndResetsFailures(int minutes)
    {
        var (g, mode, limiter) = New();
        limiter.RecordFailure(T0.AddSeconds(-10));
        Assert.Equal(new AdminResultMessage(true, null, 0), g.Complete(T0, MaintenanceRedeemResult.Ok(minutes)));
        Assert.True(mode.IsActive());
        Assert.Equal(T0.AddMinutes(minutes), mode.Until);
        Assert.Equal(0, limiter.ConsecutiveFailures);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(30)]
    [InlineData(100000)]
    [InlineData(-15)]
    public void AnOkWithAnUnexpectedDurationNeverActivatesAndIsAGenericError(int minutes)
    {
        var (g, mode, limiter) = New();
        Assert.Equal(new AdminResultMessage(false, "error", 0), g.Complete(T0, new MaintenanceRedeemResult(MaintenanceRedeemStatus.Ok, minutes)));
        Assert.False(mode.IsActive());
        Assert.Equal(0, limiter.ConsecutiveFailures);
    }

    [Fact]
    public void InvalidCodeCounts()
    {
        var (g, mode, limiter) = New();
        Assert.Equal(new AdminResultMessage(false, "invalid_code", 0), g.Complete(T0, MaintenanceRedeemResult.InvalidCode));
        Assert.Equal(1, limiter.ConsecutiveFailures);
        Assert.False(mode.IsActive());
    }

    [Theory]
    [InlineData(MaintenanceRedeemStatus.RateLimited, "rate_limited")]
    [InlineData(MaintenanceRedeemStatus.Offline, "offline")]
    [InlineData(MaintenanceRedeemStatus.Error, "error")]
    public void OtherFailuresMapToTheirCodeAndDoNotCount(MaintenanceRedeemStatus status, string code)
    {
        var (g, mode, limiter) = New();
        Assert.Equal(new AdminResultMessage(false, code, 0), g.Complete(T0, new MaintenanceRedeemResult(status)));
        Assert.Equal(0, limiter.ConsecutiveFailures);
        Assert.False(mode.IsActive());
    }

    [Fact]
    public void SecondAttemptWithinOneSecondIsRefusedWithRetry()
    {
        var (g, _, _) = New();
        g.Complete(T0, MaintenanceRedeemResult.InvalidCode);
        Assert.Equal(new AdminResultMessage(false, "locked_out", 1), g.Precheck(T0.AddMilliseconds(300), "123456"));
        Assert.Null(g.Precheck(T0.AddSeconds(1), "123456"));
    }

    [Fact]
    public void FifthFailureRepliesLockedOutAndAValidCodeIsRefusedDuringLockout()
    {
        var (g, mode, _) = New();
        var t = T0;
        for (var i = 0; i < 4; i++)
        {
            Assert.Null(g.Precheck(t, "111111"));
            Assert.Equal("invalid_code", g.Complete(t, MaintenanceRedeemResult.InvalidCode).Error);
            t = t.AddSeconds(2);
        }
        Assert.Null(g.Precheck(t, "111111"));
        Assert.Equal(new AdminResultMessage(false, "locked_out", 600), g.Complete(t, MaintenanceRedeemResult.InvalidCode));

        // during the lockout the request never reaches the backend, even with a well-formed code
        Assert.Equal(new AdminResultMessage(false, "locked_out", 60), g.Precheck(t.AddMinutes(9), "222222"));
        Assert.False(mode.IsActive());

        var after = t.AddMinutes(10);
        Assert.Null(g.Precheck(after, "222222"));
        Assert.True(g.Complete(after, MaintenanceRedeemResult.Ok(15)).Ok);
        Assert.True(mode.IsActive());
    }

    [Fact]
    public void FiveMalformedCodesLockOutToo()
    {
        var (g, _, _) = New();
        var t = T0;
        AdminResultMessage? last = null;
        for (var i = 0; i < 5; i++, t = t.AddSeconds(2)) last = g.Precheck(t, "x");
        Assert.Equal("locked_out", last!.Error);
        Assert.Equal("locked_out", g.Precheck(t, "123456")!.Error);
    }

    [Fact]
    public void LockoutIsCheckedBeforeTheCodeShape()
    {
        var (g, _, limiter) = New();
        for (var i = 0; i < 5; i++) limiter.RecordFailure(T0);
        Assert.Equal("locked_out", g.Precheck(T0, "bad")!.Error);
        Assert.Equal(5, limiter.ConsecutiveFailures); // a refused attempt does not count again
    }

    [Fact]
    public void RateLimitedOfflineAndErrorNeverLockOut()
    {
        var (g, _, _) = New();
        var t = T0;
        var cycle = new[] { MaintenanceRedeemStatus.RateLimited, MaintenanceRedeemStatus.Offline, MaintenanceRedeemStatus.Error };
        for (var i = 0; i < 20; i++, t = t.AddSeconds(2))
        {
            Assert.Null(g.Precheck(t, "123456"));
            g.Complete(t, new MaintenanceRedeemResult(cycle[i % cycle.Length]));
        }
        Assert.Null(g.Precheck(t, "123456"));
    }
}

public class MaintenanceRulesTests
{
    private static readonly PcRules Locked = new(true, "quota", 3, "Ali", Defaults.Allowlist, new[] { "example.uz" });

    [Fact]
    public void ActiveMaintenanceUnlocksAndKeepsTheRest()
    {
        var r = SessionRules.WithMaintenance(Locked, active: true);
        Assert.False(r.Locked);
        Assert.Equal("maintenance", r.Reason);
        Assert.Equal("Ali", r.StudentName);
        Assert.Equal(Locked.Allowlist, r.Allowlist);
    }

    [Fact]
    public void InactiveMaintenanceChangesNothing()
        => Assert.Same(Locked, SessionRules.WithMaintenance(Locked, active: false));

    [Fact]
    public void SignedOutDuringMaintenanceIsUnlocked()
        => Assert.False(SessionRules.WithMaintenance(SessionRules.SignedOut(Locked), active: true).Locked);

    [Fact]
    public void PlannerKillsAndClosesNothingDuringMaintenanceEvenWithoutASnapshot()
    {
        var rules = SessionRules.WithMaintenance(SessionRules.SignedOut(Locked), active: true);
        var procs = new[] { new RunningProcess(42, "game.exe", null, false, false) };
        var plan = EnforcementPlanner.Plan(rules, null, DateTimeOffset.MinValue, DateTimeOffset.UtcNow, procs);
        Assert.Empty(plan.KillPids);
        Assert.Empty(plan.CloseWindows);
        Assert.False(plan.UsedFallback);
        // and the same input without maintenance does kill (sanity check of the test itself)
        var locked = EnforcementPlanner.Plan(SessionRules.SignedOut(Locked), null, DateTimeOffset.MinValue, DateTimeOffset.UtcNow, procs);
        Assert.Contains(42, locked.KillPids);
    }
}

public class MaintenanceAuditTests
{
    [Fact]
    public void StartedTextExact()
        => Assert.Equal("Maintenance mode started for 15 minutes (until 2026-10-23 10:15 UTC), redeemed with teacher code",
            MaintenanceAudit.Started(15, new DateTimeOffset(2026, 10, 23, 15, 15, 0, TimeSpan.FromHours(5))));

    [Theory]
    [InlineData(MaintenanceEndReason.Expired, "Maintenance mode ended (expired)")]
    [InlineData(MaintenanceEndReason.EndedOnPc, "Maintenance mode ended (ended on the PC)")]
    [InlineData(MaintenanceEndReason.ServiceStopped, "Maintenance mode ended (service stopped)")]
    public void EndedTextExact(MaintenanceEndReason reason, string expected)
        => Assert.Equal(expected, MaintenanceAudit.Ended(reason));

    [Fact]
    public void FailureTexts()
    {
        Assert.Equal("Maintenance code rejected (2 of 5 consecutive failures)", MaintenanceAudit.Rejected(2));
        Assert.Equal("Maintenance code attempts locked out for 10 minutes after 5 consecutive failures", MaintenanceAudit.LockedOut());
        Assert.Equal("Maintenance code attempt refused: locked out for another 60 s", MaintenanceAudit.RefusedLockedOut(60));
        Assert.Equal("Maintenance code could not be checked: offline", MaintenanceAudit.NotChecked("offline"));
    }
}
