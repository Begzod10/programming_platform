using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class SignedOutRulesTests
{
    [Fact]
    public void SignedOutIsLockedNoStudentButKeepsAllowlistAndHosts()
    {
        var allow = new[] { new AllowEntry("code.exe", null) };
        var cached = new PcRules(false, "quota_met", 0, "Ali", allow, new[] { "lms.uz" });
        var r = SessionRules.SignedOut(cached);
        Assert.True(r.Locked);
        Assert.Equal("no_student", r.Reason);
        Assert.Equal(0, r.Remaining);
        Assert.Null(r.StudentName);
        Assert.Same(allow, r.Allowlist);
        Assert.Equal(new[] { "lms.uz" }, r.BrowserHosts);
    }

    [Fact]
    public void SignedOutWithEmptyAllowlistUsesDefaults()
    {
        var r = SessionRules.SignedOut(new PcRules(false, "x", 0, null, Array.Empty<AllowEntry>(), Array.Empty<string>()));
        Assert.Equal(Defaults.Allowlist, r.Allowlist);
    }

    [Fact]
    public void ToStateMessageMapsFields()
    {
        var m = SessionRules.ToStateMessage(new PcRules(true, "quota", 3, "Ali", Defaults.Allowlist, Array.Empty<string>()));
        Assert.Equal(new StateMessage(true, "quota", 3, "Ali"), m);
    }
}

public class ShellLaunchPolicyTests
{
    private static readonly DateTimeOffset Now = new(2026, 10, 23, 10, 0, 0, TimeSpan.Zero);

    private static ShellAction D(double? missingFor, double? sinceLaunch = null, bool console = true, bool running = false, double? sinceSnapshot = null, double? sinceAlive = null)
        => ShellLaunchPolicy.Decide(Now,
            missingFor is { } m ? Now.AddSeconds(-m) : null,
            sinceLaunch is { } l ? Now.AddSeconds(-l) : null,
            console, running,
            sinceSnapshot is { } s ? Now.AddSeconds(-s) : null,
            sinceAlive is { } a ? Now.AddSeconds(-a) : null);

    [Fact] public void NothingWhenShellPresent() => Assert.Equal(ShellAction.None, D(null));
    [Fact] public void NothingBeforeSixSeconds() => Assert.Equal(ShellAction.None, D(5.9));
    [Fact] public void LaunchAfterSixSeconds() => Assert.Equal(ShellAction.Launch, D(6));
    [Fact] public void NothingWithoutConsoleSession() => Assert.Equal(ShellAction.None, D(60, console: false));
    [Fact] public void AtMostOnceEvery15Seconds() => Assert.Equal(ShellAction.None, D(60, sinceLaunch: 14));
    [Fact] public void LaunchAgainAfter15Seconds() => Assert.Equal(ShellAction.Launch, D(60, sinceLaunch: 15));
    [Fact] public void FutureLaunchTimeDoesNotBlockForever() => Assert.Equal(ShellAction.Launch, D(60, sinceLaunch: -3600));
    [Fact] public void RunningShellIsGivenTimeToConnect() => Assert.Equal(ShellAction.None, D(60, sinceLaunch: 20, running: true));
    [Fact] public void RunningButSilentFor30SecondsIsKilled() => Assert.Equal(ShellAction.KillHung, D(60, sinceLaunch: 40, running: true, sinceSnapshot: 30));
    [Fact] public void RecentSnapshotKeepsRunningShell() => Assert.Equal(ShellAction.None, D(10, running: true, sinceSnapshot: 10));
    [Fact] public void RunningShellNeverLaunchedButSilentIsKilled() => Assert.Equal(ShellAction.KillHung, D(31, running: true));

    // "alive" frames from a shell that deliberately sends no snapshots (non-Default input desktop)
    [Fact] public void RecentAliveKeepsSilentRunningShell() => Assert.Equal(ShellAction.None, D(120, sinceLaunch: 120, running: true, sinceSnapshot: 120, sinceAlive: 29.9));
    [Fact] public void AliveExactly30sOldIsHung() => Assert.Equal(ShellAction.KillHung, D(120, sinceLaunch: 120, running: true, sinceSnapshot: 120, sinceAlive: 30));
    [Fact] public void StaleAliveAndStaleSnapshotStillKilled() => Assert.Equal(ShellAction.KillHung, D(120, sinceLaunch: 120, running: true, sinceSnapshot: 90, sinceAlive: 60));
    [Fact] public void AliveNeverMeansLaunchWhenNotRunning() => Assert.Equal(ShellAction.Launch, D(60, running: false, sinceAlive: 1));
}

public class AliveDoesNotFreshenSnapshotTests
{
    [Fact]
    public void PlannerIgnoresAlive_StaleSnapshotStillMeansShellMissingAndFallback()
    {
        var now = new DateTimeOffset(2026, 10, 23, 10, 0, 0, TimeSpan.Zero);
        var rules = new PcRules(true, "no_student", 0, null, Defaults.Allowlist, Array.Empty<string>());
        var plan = EnforcementPlanner.Plan(rules, new Snapshot(Array.Empty<WindowedProc>(), null, Array.Empty<BrowserWindow>()),
            now.AddSeconds(-7), now, Array.Empty<RunningProcess>());
        Assert.True(plan.ShellMissing);
        Assert.True(plan.UsedFallback);
    }
}
