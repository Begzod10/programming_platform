using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class StartupGraceTests
{
    private static readonly TimeSpan T0 = TimeSpan.FromMinutes(5); // monotonic time at service start
    private static readonly DateTimeOffset Now = new(2026, 10, 23, 14, 50, 9, TimeSpan.Zero);

    private static readonly RunningProcess[] Procs =
    {
        new(200, "anydesk.exe", null, false, false),
        new(201, "telegram.exe", null, false, false),
        new(202, "notepad.exe", null, false, true),
        new(203, "chrome.exe", null, false, false),
    };

    private static PcRules Locked(params string[] hosts)
        => new(true, "quota", 0, null, Defaults.Allowlist, hosts);

    // ---------------- pure IsActive ----------------

    [Fact]
    public void WindowIsThirtySeconds() => Assert.Equal(TimeSpan.FromSeconds(30), StartupGrace.Window);

    [Fact]
    public void ActiveRightAfterStartWithoutShell()
        => Assert.True(StartupGrace.IsActive(T0, T0, shellEverConnected: false));

    [Fact]
    public void ActiveJustBeforeThirtySeconds()
        => Assert.True(StartupGrace.IsActive(T0, T0 + TimeSpan.FromSeconds(29.999), false));

    [Fact]
    public void EndsAtThirtySeconds()
        => Assert.False(StartupGrace.IsActive(T0, T0 + TimeSpan.FromSeconds(30), false));

    [Fact]
    public void InactiveOnceAShellConnected()
        => Assert.False(StartupGrace.IsActive(T0, T0 + TimeSpan.FromSeconds(1), shellEverConnected: true));

    [Fact]
    public void MonotonicTimeBeforeStartIsNotAGrace() // impossible on a monotonic source: fail closed
        => Assert.False(StartupGrace.IsActive(T0, T0 - TimeSpan.FromSeconds(1), false));

    // ---------------- stateful tracker ----------------

    private sealed class FakeClock
    {
        public TimeSpan Value = T0;
        public TimeSpan Read() => Value;
    }

    [Fact]
    public void TrackerIsActiveFromConstruction()
    {
        var clock = new FakeClock();
        var g = new StartupGrace(clock.Read);
        var e = g.Evaluate();
        Assert.True(e.Active);
        Assert.Null(e.JustEnded);
    }

    [Fact]
    public void TrackerElapsedUsesMonotonicStartNotZero()
    {
        var clock = new FakeClock { Value = TimeSpan.FromHours(10) }; // long uptime before the service started
        var g = new StartupGrace(clock.Read);
        clock.Value += TimeSpan.FromSeconds(10);
        Assert.True(g.Evaluate().Active);
    }

    [Fact]
    public void TrackerExpiresOnceWithoutShell()
    {
        var clock = new FakeClock();
        var g = new StartupGrace(clock.Read);
        clock.Value += TimeSpan.FromSeconds(29);
        Assert.True(g.Evaluate().Active);
        clock.Value += TimeSpan.FromSeconds(1);
        var e = g.Evaluate();
        Assert.False(e.Active);
        Assert.Equal(StartupGraceEnd.Expired, e.JustEnded);
        clock.Value += TimeSpan.FromSeconds(2);
        var again = g.Evaluate();
        Assert.False(again.Active);
        Assert.Null(again.JustEnded); // reported exactly once
    }

    [Fact]
    public void TrackerEndsOnceWhenShellConnects()
    {
        var clock = new FakeClock();
        var g = new StartupGrace(clock.Read);
        clock.Value += TimeSpan.FromSeconds(7);
        g.MarkShellConnected();
        var e = g.Evaluate();
        Assert.False(e.Active);
        Assert.Equal(StartupGraceEnd.ShellConnected, e.JustEnded);
        Assert.Null(g.Evaluate().JustEnded);
    }

    [Fact]
    public void ShellConnectingAfterExpiryDoesNotChangeTheEnd()
    {
        var clock = new FakeClock();
        var g = new StartupGrace(clock.Read);
        clock.Value += TimeSpan.FromSeconds(31);
        Assert.Equal(StartupGraceEnd.Expired, g.Evaluate().JustEnded);
        g.MarkShellConnected();
        var e = g.Evaluate();
        Assert.False(e.Active);
        Assert.Null(e.JustEnded);
    }

    [Fact]
    public void ShellConnectedBeforeAnyEvaluateEndsWithShellConnected()
    {
        var clock = new FakeClock();
        var g = new StartupGrace(clock.Read);
        g.MarkShellConnected();
        clock.Value += TimeSpan.FromSeconds(40); // tick came late: the shell still connected first
        Assert.Equal(StartupGraceEnd.ShellConnected, g.Evaluate().JustEnded);
    }

    [Fact]
    public void NeverActiveAgainAfterShellDisconnects()
    {
        // a shell that connected and later died/hung gets no grace: there is no way to "un-connect"
        var clock = new FakeClock();
        var g = new StartupGrace(clock.Read);
        g.MarkShellConnected();
        g.Evaluate();
        clock.Value += TimeSpan.FromSeconds(1);
        Assert.False(g.Evaluate().Active);
    }

    [Fact]
    public void BackwardMonotonicReadingEndsTheGrace()
    {
        var clock = new FakeClock();
        var g = new StartupGrace(clock.Read);
        clock.Value -= TimeSpan.FromSeconds(1);
        var e = g.Evaluate();
        Assert.False(e.Active);
        Assert.Equal(StartupGraceEnd.Expired, e.JustEnded);
        clock.Value = T0; // even back in range: latched
        Assert.False(g.Evaluate().Active);
    }

    [Fact]
    public void NullClockThrows() => Assert.Throws<ArgumentNullException>(() => new StartupGrace(null!));

    // ---------------- applying to a plan ----------------

    [Fact]
    public void ActiveGraceStripsKillsFromAFallbackPlanButKeepsFlags()
    {
        var plan = EnforcementPlanner.Plan(Locked(), null, Now, Now, Procs);
        Assert.NotEmpty(plan.KillPids); // precondition: the fallback alone would kill
        var held = StartupGrace.Apply(plan, graceActive: true);
        Assert.Empty(held.KillPids);
        Assert.Empty(held.CloseWindows);
        Assert.True(held.ShellMissing);   // the supervisor still launches the shell
        Assert.True(held.UsedFallback);
    }

    [Fact]
    public void ActiveGraceAlsoHoldsTheBrowserHostFallbackKill()
    {
        var plan = EnforcementPlanner.Plan(Locked("example.com"), null, Now, Now, Procs);
        Assert.Contains(203, plan.KillPids);
        Assert.Empty(StartupGrace.Apply(plan, true).KillPids);
    }

    [Fact]
    public void InactiveGraceLeavesTheFallbackPlanUnchanged()
    {
        var plan = EnforcementPlanner.Plan(Locked(), null, Now, Now, Procs);
        Assert.Same(plan, StartupGrace.Apply(plan, graceActive: false));
    }

    [Fact]
    public void GraceNeverTouchesAWindowAwarePlan()
    {
        var snap = new Snapshot(new[] { new WindowedProc(200, "anydesk.exe") }, null,
            new[] { new BrowserWindow(9, 203, "evil.com", true) });
        var plan = EnforcementPlanner.Plan(Locked("example.com"), snap, Now, Now, Procs);
        Assert.False(plan.UsedFallback);
        Assert.NotEmpty(plan.KillPids);
        Assert.Same(plan, StartupGrace.Apply(plan, graceActive: true));
    }

    [Fact]
    public void UnlockedPlanStaysEmptyUnderGrace()
    {
        var unlocked = Locked() with { Locked = false };
        var plan = EnforcementPlanner.Plan(unlocked, null, Now, Now, Procs);
        var held = StartupGrace.Apply(plan, true);
        Assert.Empty(held.KillPids);
        Assert.True(held.ShellMissing);
        Assert.False(held.UsedFallback);
    }
}
