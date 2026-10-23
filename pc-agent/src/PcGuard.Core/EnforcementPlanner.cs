namespace PcGuard.Core;

/// <summary>What the service does in one enforcement tick.</summary>
/// <param name="KillPids">Processes to terminate: de-duplicated, ascending.</param>
/// <param name="CloseWindows">Browser windows the shell should close: de-duplicated, ascending.</param>
/// <param name="ShellMissing">No fresh snapshot: the shell is dead, hung or not started.</param>
/// <param name="UsedFallback">Enforcement ran in name-only mode (no window information).</param>
public record EnforcementPlan(IReadOnlyList<int> KillPids, IReadOnlyList<long> CloseWindows, bool ShellMissing, bool UsedFallback);

/// <summary>
/// Pure decision logic for the guard service's 2 s tick. The snapshot from the shell is only used
/// as a report of which pids have visible windows and which browser windows show which host; process
/// identity (exe, publisher, system ownership) always comes from the service's own enumeration.
/// </summary>
public static class EnforcementPlanner
{
    public static readonly TimeSpan SnapshotMaxAge = TimeSpan.FromSeconds(6);

    private static readonly EnforcementPlan Empty = new(Array.Empty<int>(), Array.Empty<long>(), false, false);

    /// <param name="exemptPids">Pids never killed (the service itself, the verified shell).</param>
    public static EnforcementPlan Plan(
        PcRules rules,
        Snapshot? snapshot,
        DateTimeOffset snapshotAt,
        DateTimeOffset now,
        IReadOnlyList<RunningProcess> userSessionProcesses,
        IReadOnlyCollection<int>? exemptPids = null)
    {
        var age = now - snapshotAt;
        var fresh = snapshot is not null && age >= TimeSpan.Zero && age <= SnapshotMaxAge;
        var shellMissing = !fresh;

        if (!rules.Locked) return Empty with { ShellMissing = shellMissing };

        var exempt = exemptPids is null ? new HashSet<int>() : new HashSet<int>(exemptPids);
        var candidates = userSessionProcesses.Where(p => !exempt.Contains(p.Pid));

        IEnumerable<ProcInfo> infos;
        if (fresh)
        {
            var windowed = new HashSet<int>(snapshot!.Windowed.Select(w => w.Pid));
            infos = candidates.Select(p => new ProcInfo(p.Pid, p.Exe, windowed.Contains(p.Pid), p.Publisher));
        }
        else
        {
            // name-only fallback: no window information, so every non-system user process counts as visible
            infos = candidates.Where(p => !p.IsSystemOwned)
                .Select(p => new ProcInfo(p.Pid, p.Exe, true, p.Publisher));
        }

        var kill = ProcessPolicy.FindViolators(infos, rules)
            .Select(v => v.Pid).Distinct().OrderBy(pid => pid).ToList();

        var close = new List<long>();
        if (fresh)
        {
            var exeByPid = new Dictionary<int, string>();
            foreach (var p in userSessionProcesses) exeByPid.TryAdd(p.Pid, p.Exe);
            close = snapshot!.Browsers
                .Where(b => exeByPid.TryGetValue(b.Pid, out var exe)
                            && BrowserHostRule.IsBrowser(exe)
                            && !BrowserHostRule.IsAllowed(b.Host, rules.BrowserHosts))
                .Select(b => b.Hwnd).Distinct().OrderBy(h => h).ToList();
        }

        return new EnforcementPlan(kill, close, shellMissing, UsedFallback: !fresh);
    }
}
