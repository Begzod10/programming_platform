namespace PcGuard.Core;

public static class BrowserHostRule
{
    public static readonly ISet<string> Browsers =
        new HashSet<string>(StringComparer.OrdinalIgnoreCase) { "chrome.exe", "msedge.exe" };

    public static bool IsBrowser(string? exe) => !string.IsNullOrEmpty(exe) && Browsers.Contains(exe);

    /// <summary>
    /// The caller must pass a BARE host (no scheme, port, userinfo or path). For IDN hosts both
    /// <paramref name="host"/> and the allowed entries must be punycode (ASCII).
    /// Allowed entries are trimmed, stripped of a trailing dot, lower-cased; empty entries are skipped.
    /// If there are no non-empty entries the rule is DISABLED (returns true), same as an empty list.
    /// A null/empty host (address bar unreadable) returns true.
    /// </summary>
    public static bool IsAllowed(string? host, IReadOnlyList<string> allowedHosts)
    {
        var allowed = allowedHosts
            .Select(a => a?.Trim().TrimEnd('.').ToLowerInvariant() ?? "")
            .Where(a => a.Length > 0)
            .ToList();
        if (allowed.Count == 0) return true;
        if (string.IsNullOrEmpty(host)) return true;
        var h = host.TrimEnd('.').ToLowerInvariant();
        return allowed.Any(a => h == a || h.EndsWith("." + a, StringComparison.Ordinal));
    }
}
