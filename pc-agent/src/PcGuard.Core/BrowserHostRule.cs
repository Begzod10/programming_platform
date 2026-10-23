namespace PcGuard.Core;

public static class BrowserHostRule
{
    public static readonly ISet<string> Browsers =
        new HashSet<string>(StringComparer.OrdinalIgnoreCase) { "chrome.exe", "msedge.exe" };

    public static bool IsBrowser(string exe) => Browsers.Contains(exe);

    public static bool IsAllowed(string? host, IReadOnlyList<string> allowedHosts)
    {
        if (allowedHosts.Count == 0) return true;
        if (string.IsNullOrEmpty(host)) return true;
        var h = host.TrimEnd('.');
        foreach (var a in allowedHosts)
        {
            if (h.Equals(a, StringComparison.OrdinalIgnoreCase) ||
                h.EndsWith("." + a, StringComparison.OrdinalIgnoreCase))
                return true;
        }
        return false;
    }
}
