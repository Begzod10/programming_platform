namespace PcGuard.Core;

public static class ProcessPolicy
{
    public static readonly ISet<string> Protected = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
    {
        "explorer.exe", "dwm.exe", "csrss.exe", "winlogon.exe", "ctfmon.exe", "sihost.exe",
        "taskhostw.exe", "runtimebroker.exe", "shellexperiencehost.exe", "searchhost.exe",
        "startmenuexperiencehost.exe", "textinputhost.exe", "conhost.exe",
        "pcguard.shell.exe", "pcguard.service.exe",
        // host of UWP frames; the real app pid is reported by the shell via its CoreWindow
        "applicationframehost.exe",
    };

    public static IReadOnlyList<ProcInfo> FindViolators(IEnumerable<ProcInfo> running, PcRules rules)
    {
        if (!rules.Locked) return Array.Empty<ProcInfo>();
        return running
            .Where(p => p.HasVisibleWindow && !Protected.Contains(p.Exe) && !IsAllowed(p, rules.Allowlist))
            .ToList();
    }

    private static bool IsAllowed(ProcInfo p, IReadOnlyList<AllowEntry> allow) =>
        allow.Any(e =>
            string.Equals(e.Exe, p.Exe, StringComparison.OrdinalIgnoreCase) &&
            (e.Publisher is null ||
             (p.Publisher is not null && p.Publisher.Contains(e.Publisher, StringComparison.OrdinalIgnoreCase))));
}
