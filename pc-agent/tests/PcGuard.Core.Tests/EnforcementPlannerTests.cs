using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class EnforcementPlannerTests
{
    private static readonly DateTimeOffset Now = new(2026, 10, 23, 10, 0, 0, TimeSpan.Zero);

    private static PcRules Rules(bool locked, IReadOnlyList<string>? hosts = null, params AllowEntry[] allow)
        => new(locked, locked ? "quota" : "ok", 2, "Ali", allow.Length > 0 ? allow : Defaults.Allowlist, hosts ?? Array.Empty<string>());

    private static RunningProcess P(int pid, string exe, bool system = false, string? pub = null) => new(pid, exe, pub, system);

    private static Snapshot Snap(IEnumerable<int> windowedPids, IReadOnlyList<RunningProcess> procs, params BrowserWindow[] browsers)
        => new(windowedPids.Select(pid => new WindowedProc(pid, procs.First(p => p.Pid == pid).Exe)).ToList(), null, browsers);

    private static readonly RunningProcess[] Procs =
    {
        P(100, "explorer.exe", system: true),
        P(101, "code.exe"),
        P(102, "game.exe"),
        P(103, "steam.exe"),          // background, no window
        P(104, "chrome.exe"),
        P(105, "svchost.exe", system: true),
        P(106, "dwm.exe"),            // protected by name
        P(107, "pcguard.shell.exe"),
    };

    [Fact]
    public void UnlockedYieldsEmptyPlan()
    {
        var plan = EnforcementPlanner.Plan(Rules(false), Snap(new[] { 102 }, Procs), Now, Now, Procs);
        Assert.Empty(plan.KillPids);
        Assert.Empty(plan.CloseWindows);
        Assert.False(plan.ShellMissing);
        Assert.False(plan.UsedFallback);
    }

    [Fact]
    public void UnlockedStillReportsShellMissing()
    {
        var plan = EnforcementPlanner.Plan(Rules(false), null, Now, Now, Procs);
        Assert.Empty(plan.KillPids);
        Assert.True(plan.ShellMissing);
        Assert.False(plan.UsedFallback);
    }

    [Fact]
    public void LockedKillsWindowedNonAllowlistedOnly()
    {
        var plan = EnforcementPlanner.Plan(Rules(true), Snap(new[] { 100, 101, 102, 104, 106, 107 }, Procs), Now.AddSeconds(-2), Now, Procs);
        Assert.Equal(new[] { 102 }, plan.KillPids);
        Assert.False(plan.ShellMissing);
        Assert.False(plan.UsedFallback);
    }

    [Fact]
    public void BackgroundProcessWithoutWindowIsNotKilledWhenSnapshotFresh()
    {
        var plan = EnforcementPlanner.Plan(Rules(true), Snap(Array.Empty<int>(), Procs), Now, Now, Procs);
        Assert.Empty(plan.KillPids);
    }

    [Fact]
    public void WindowedPidNotInServiceEnumerationIsIgnored()
    {
        var snap = new Snapshot(new[] { new WindowedProc(999, "game.exe") }, null, Array.Empty<BrowserWindow>());
        Assert.Empty(EnforcementPlanner.Plan(Rules(true), snap, Now, Now, Procs).KillPids);
    }

    [Fact]
    public void ExeNameComesFromServiceNotFromSnapshot()
    {
        // the shell claims pid 102 is code.exe; the service's own enumeration says game.exe
        var snap = new Snapshot(new[] { new WindowedProc(102, "code.exe") }, null, Array.Empty<BrowserWindow>());
        Assert.Equal(new[] { 102 }, EnforcementPlanner.Plan(Rules(true), snap, Now, Now, Procs).KillPids);
    }

    [Fact]
    public void PublisherRestrictionIsApplied()
    {
        var procs = new[] { P(1, "code.exe", pub: "Evil Corp"), P(2, "code.exe", pub: "Microsoft Corporation") };
        var rules = Rules(true, null, new AllowEntry("code.exe", "Microsoft"));
        var plan = EnforcementPlanner.Plan(rules, Snap(new[] { 1, 2 }, procs), Now, Now, procs);
        Assert.Equal(new[] { 1 }, plan.KillPids);
    }

    [Fact]
    public void SnapshotExactlySixSecondsOldIsFresh()
    {
        var plan = EnforcementPlanner.Plan(Rules(true), Snap(Array.Empty<int>(), Procs), Now.AddSeconds(-6), Now, Procs);
        Assert.False(plan.UsedFallback);
        Assert.False(plan.ShellMissing);
    }

    [Fact]
    public void StaleSnapshotUsesFallback()
    {
        var plan = EnforcementPlanner.Plan(Rules(true), Snap(Array.Empty<int>(), Procs), Now.AddSeconds(-6.5), Now, Procs);
        Assert.True(plan.UsedFallback);
        Assert.True(plan.ShellMissing);
    }

    [Fact]
    public void FutureSnapshotTimestampIsTreatedAsStale()
    {
        var plan = EnforcementPlanner.Plan(Rules(true), Snap(Array.Empty<int>(), Procs), Now.AddSeconds(1), Now, Procs);
        Assert.True(plan.UsedFallback);
        Assert.True(plan.ShellMissing);
    }

    [Fact]
    public void MissingSnapshotUsesFallback()
    {
        var plan = EnforcementPlanner.Plan(Rules(true), null, Now, Now, Procs);
        Assert.True(plan.UsedFallback);
        Assert.True(plan.ShellMissing);
    }

    [Fact]
    public void FallbackKillsEveryNonAllowlistedUserProcessIncludingBackground()
    {
        var plan = EnforcementPlanner.Plan(Rules(true), null, Now, Now, Procs);
        // 102 game (windowless or not), 103 steam (background); not explorer/svchost (system),
        // dwm/pcguard.shell (protected), code/chrome (allowlisted)
        Assert.Equal(new[] { 102, 103 }, plan.KillPids);
        Assert.Empty(plan.CloseWindows);
    }

    [Fact]
    public void FallbackHonoursPublisherAllowlist()
    {
        var procs = new[] { P(1, "code.exe", pub: "Evil"), P(2, "code.exe", pub: "Microsoft Corporation") };
        var plan = EnforcementPlanner.Plan(Rules(true, null, new AllowEntry("code.exe", "Microsoft")), null, Now, Now, procs);
        Assert.Equal(new[] { 1 }, plan.KillPids);
    }

    [Fact]
    public void ExemptPidsAreNeverKilled()
    {
        var plan = EnforcementPlanner.Plan(Rules(true), null, Now, Now, Procs, exemptPids: new[] { 102 });
        Assert.Equal(new[] { 103 }, plan.KillPids);
        var fresh = EnforcementPlanner.Plan(Rules(true), Snap(new[] { 102 }, Procs), Now, Now, Procs, exemptPids: new[] { 102 });
        Assert.Empty(fresh.KillPids);
    }

    [Fact]
    public void KillPidsAreDeduplicatedAndSorted()
    {
        var procs = new[] { P(30, "b.exe"), P(10, "a.exe"), P(30, "b.exe"), P(20, "c.exe") };
        var snap = new Snapshot(new[] { new WindowedProc(30, "b.exe"), new WindowedProc(10, "a.exe"), new WindowedProc(30, "b.exe"), new WindowedProc(20, "c.exe") },
            null, Array.Empty<BrowserWindow>());
        Assert.Equal(new[] { 10, 20, 30 }, EnforcementPlanner.Plan(Rules(true), snap, Now, Now, procs).KillPids);
        Assert.Equal(new[] { 10, 20, 30 }, EnforcementPlanner.Plan(Rules(true), null, Now, Now, procs).KillPids);
    }

    // ---- browser host rule ----

    private static readonly string[] Hosts = { "platform.uz" };

    private static EnforcementPlan PlanBrowsers(PcRules rules, params BrowserWindow[] windows)
        => EnforcementPlanner.Plan(rules, Snap(new[] { 104 }, Procs, windows), Now, Now, Procs);

    [Fact]
    public void AllowedHostIsNotClosed()
    {
        var plan = PlanBrowsers(Rules(true, Hosts), new BrowserWindow(1, 104, "platform.uz"), new BrowserWindow(2, 104, "app.platform.uz"));
        Assert.Empty(plan.CloseWindows);
        Assert.Empty(plan.KillPids); // the browser itself is never killed for this
    }

    [Fact]
    public void DisallowedHostWindowIsClosed()
    {
        var plan = PlanBrowsers(Rules(true, Hosts), new BrowserWindow(1, 104, "youtube.com"), new BrowserWindow(2, 104, "platform.uz"));
        Assert.Equal(new long[] { 1 }, plan.CloseWindows);
        Assert.Empty(plan.KillPids);
    }

    [Fact]
    public void NullHostIsNotClosed()
        => Assert.Empty(PlanBrowsers(Rules(true, Hosts), new BrowserWindow(1, 104, null)).CloseWindows);

    [Fact]
    public void EmptyHostListDisablesRule()
        => Assert.Empty(PlanBrowsers(Rules(true, Array.Empty<string>()), new BrowserWindow(1, 104, "youtube.com")).CloseWindows);

    [Fact]
    public void NonBrowserProcessIsIgnored()
    {
        // the shell reports a code.exe window as a "browser": the service checks the real exe
        var plan = PlanBrowsers(Rules(true, Hosts), new BrowserWindow(1, 101, "youtube.com"));
        Assert.Empty(plan.CloseWindows);
    }

    [Fact]
    public void BrowserWindowOfUnknownPidIsIgnored()
        => Assert.Empty(PlanBrowsers(Rules(true, Hosts), new BrowserWindow(1, 4242, "youtube.com")).CloseWindows);

    [Fact]
    public void BrowserRuleNotAppliedWhenUnlocked()
        => Assert.Empty(PlanBrowsers(Rules(false, Hosts), new BrowserWindow(1, 104, "youtube.com")).CloseWindows);

    [Fact]
    public void CloseWindowsAreDeduplicated()
    {
        var plan = PlanBrowsers(Rules(true, Hosts), new BrowserWindow(5, 104, "a.com"), new BrowserWindow(5, 104, "a.com"), new BrowserWindow(3, 104, "b.com"));
        Assert.Equal(new long[] { 3, 5 }, plan.CloseWindows);
    }
}
