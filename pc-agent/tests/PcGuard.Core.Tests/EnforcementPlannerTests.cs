using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class EnforcementPlannerTests
{
    private static readonly DateTimeOffset Now = new(2026, 10, 23, 10, 0, 0, TimeSpan.Zero);

    private static PcRules Rules(bool locked, IReadOnlyList<string>? hosts = null, params AllowEntry[] allow)
        => new(locked, locked ? "quota" : "ok", 2, "Ali", allow.Length > 0 ? allow : Defaults.Allowlist, hosts ?? Array.Empty<string>());

    // svc = token user is SYSTEM/LOCAL SERVICE/NETWORK SERVICE or undetermined; img = image under %SystemRoot% owned by TI/SYSTEM/Admins
    private static RunningProcess P(int pid, string exe, bool svc = false, bool img = false, string? pub = null) => new(pid, exe, pub, svc, img);

    private static Snapshot Snap(IEnumerable<int> windowedPids, IReadOnlyList<RunningProcess> procs, params BrowserWindow[] browsers)
        => new(windowedPids.Select(pid => new WindowedProc(pid, procs.First(p => p.Pid == pid).Exe)).ToList(), null, browsers);

    private static readonly RunningProcess[] Procs =
    {
        P(100, "explorer.exe", img: true),
        P(101, "code.exe"),
        P(102, "game.exe"),
        P(103, "steam.exe"),          // background, no window
        P(104, "chrome.exe"),
        P(105, "svchost.exe", svc: true),
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
    public void SystemOwnedWindowedProcessIsNeverKilledInFreshPath()
    {
        // a system-owned process with a window and a non-allowlisted name must not be killed
        var procs = new[] { P(300, "svcwindow.exe", svc: true), P(301, "game.exe") };
        var plan = EnforcementPlanner.Plan(Rules(true), Snap(new[] { 300, 301 }, procs), Now, Now, procs);
        Assert.Equal(new[] { 301 }, plan.KillPids);
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

    // ---- service-owned vs system-image split (inbox apps such as Notepad) ----

    private static readonly RunningProcess Notepad = P(400, "notepad.exe", img: true); // System32, student token

    [Fact]
    public void UserTokenSystemImageAppIsViolatorInFreshMode()
    {
        var procs = new[] { Notepad };
        var plan = EnforcementPlanner.Plan(Rules(true), Snap(new[] { 400 }, procs), Now, Now, procs);
        Assert.Equal(new[] { 400 }, plan.KillPids);
    }

    [Fact]
    public void UserTokenSystemImageAppSurvivesFallback()
    {
        var procs = new[] { Notepad };
        var plan = EnforcementPlanner.Plan(Rules(true), null, Now, Now, procs);
        Assert.True(plan.UsedFallback);
        Assert.Empty(plan.KillPids);
    }

    [Fact]
    public void ServiceOwnedWindowedProcessIsNeverAViolator()
    {
        var procs = new[] { P(401, "svcui.exe", svc: true) };
        Assert.Empty(EnforcementPlanner.Plan(Rules(true), Snap(new[] { 401 }, procs), Now, Now, procs).KillPids);
        Assert.Empty(EnforcementPlanner.Plan(Rules(true), null, Now, Now, procs).KillPids);
    }

    [Fact]
    public void UndeterminedOwnerProcessIsNeverAViolator()
    {
        // the enumerator reports an undetermined token owner as IsServiceOwned = true (conservative)
        var procs = new[] { P(402, "mystery.exe", svc: true) };
        Assert.Empty(EnforcementPlanner.Plan(Rules(true), Snap(new[] { 402 }, procs), Now, Now, procs).KillPids);
        Assert.Empty(EnforcementPlanner.Plan(Rules(true), null, Now, Now, procs).KillPids);
    }

    [Fact]
    public void ProtectedNamesAreNeverViolatorsInEitherMode()
    {
        var procs = new[] { P(403, "dwm.exe"), P(404, "explorer.exe", img: true) };
        Assert.Empty(EnforcementPlanner.Plan(Rules(true), Snap(new[] { 403, 404 }, procs), Now, Now, procs).KillPids);
        Assert.Empty(EnforcementPlanner.Plan(Rules(true), null, Now, Now, procs).KillPids);
    }

    [Fact]
    public void AllowlistedAppsAreNeverViolatorsInEitherMode()
    {
        var procs = new[] { P(405, "code.exe"), P(406, "cmd.exe", img: true) };
        Assert.Empty(EnforcementPlanner.Plan(Rules(true), Snap(new[] { 405, 406 }, procs), Now, Now, procs).KillPids);
        Assert.Empty(EnforcementPlanner.Plan(Rules(true), null, Now, Now, procs).KillPids);
    }

    [Fact]
    public void FallbackKillsAllowlistedBrowserWhenHostRuleActive()
    {
        // no snapshot => cannot read the address bar, so a host-restricted browser is a loophole: kill it
        var plan = EnforcementPlanner.Plan(Rules(true, new[] { "platform.uz" }), null, Now, Now, Procs);
        Assert.Contains(104, plan.KillPids); // chrome.exe, allowlisted, killed anyway
        Assert.Equal(new[] { 102, 103, 104 }, plan.KillPids);
    }

    [Fact]
    public void FallbackDoesNotKillBrowserWhenNoHostRule()
    {
        var plan = EnforcementPlanner.Plan(Rules(true, Array.Empty<string>()), null, Now, Now, Procs);
        Assert.DoesNotContain(104, plan.KillPids); // chrome stays: no host restriction
        Assert.Equal(new[] { 102, 103 }, plan.KillPids);
    }

    [Fact]
    public void FallbackBrowserKillIgnoresSystemOwnedBrowser()
    {
        var procs = new[] { P(1, "chrome.exe", svc: true), P(2, "game.exe") };
        var plan = EnforcementPlanner.Plan(Rules(true, new[] { "platform.uz" }), null, Now, Now, procs);
        Assert.Equal(new[] { 2 }, plan.KillPids);
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
    public void UnreadableBrowserWindowIsClosedWhenLockedWithHostList()
    {
        var plan = PlanBrowsers(Rules(true, Hosts), new BrowserWindow(9, 104, null, false), new BrowserWindow(3, 104, null, true));
        Assert.Equal(new long[] { 9 }, plan.CloseWindows);
    }

    [Fact]
    public void UnreadableBrowserWindowIgnoredWhenHostListEmpty()
        => Assert.Empty(PlanBrowsers(Rules(true, Array.Empty<string>()), new BrowserWindow(9, 104, null, false)).CloseWindows);

    [Fact]
    public void UnreadableBrowserWindowIgnoredWhenNotLocked()
        => Assert.Empty(PlanBrowsers(Rules(false, Hosts), new BrowserWindow(9, 104, null, false)).CloseWindows);

    [Fact]
    public void ReadableNullHostIsAllowed()
        => Assert.Empty(PlanBrowsers(Rules(true, Hosts), new BrowserWindow(9, 104, null, true)).CloseWindows);

    [Fact]
    public void UnreadableNonBrowserPidIgnored()
        => Assert.Empty(PlanBrowsers(Rules(true, Hosts), new BrowserWindow(9, 4242, null, false)).CloseWindows);

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
