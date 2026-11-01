using System.Text.RegularExpressions;

namespace PcGuard.Core;

/// <summary>
/// Normalises the text read from a browser's address bar to a bare lower-case host (punycode for IDN
/// names), or null when it is not a web host. The result feeds <see cref="BrowserHostRule"/>.
/// PRIVACY: the raw text is a URL; callers must never log or persist it.
/// </summary>
public static partial class AddressBarParser
{
    [GeneratedRegex(@"^([A-Za-z][A-Za-z0-9+.\-]*)://")]
    private static partial Regex SchemeWithSlashes();

    // "host:port" or "[v6]..." typed without a scheme (Chrome hides "https://" in the omnibox).
    [GeneratedRegex(@"^(\[[0-9A-Fa-f:.]+\]|[^/:?#\s]+)(:\d+)?([/?#]|$)")]
    private static partial Regex SchemelessAuthority();

    public static string? ExtractHost(string? raw)
    {
        if (raw is null) return null;
        var s = raw.Trim();
        if (s.Length == 0) return null;
        foreach (var c in s) if (char.IsWhiteSpace(c) || char.IsControl(c)) return null;

        string candidate;
        var m = SchemeWithSlashes().Match(s);
        if (m.Success)
        {
            var scheme = m.Groups[1].Value.ToLowerInvariant();
            if (scheme != "http" && scheme != "https") return null; // file:, chrome:, edge:, extension schemes...
            candidate = s;
        }
        else if (s.StartsWith("//", StringComparison.Ordinal))
        {
            candidate = "https:" + s;
        }
        else if (SchemelessAuthority().IsMatch(s))
        {
            candidate = "https://" + s;
        }
        else
        {
            return null; // about:blank, javascript:, data:, view-source:, user:pw@host, "/" ...
        }

        if (!Uri.TryCreate(candidate, UriKind.Absolute, out var uri)) return null;
        var host = uri.IdnHost.TrimEnd('.').ToLowerInvariant();
        if (host.Length == 0) return null;
        if (Uri.CheckHostName(host.Trim('[', ']')) == UriHostNameType.Unknown) return null;
        // A bare word (no dot) is almost certainly text being typed into the omnibox ("goo", "google"),
        // not a navigated site; closing a window over it would be wrong. localhost and IPs are real hosts.
        if (!host.Contains('.') && !host.Contains(':') && host != "localhost") return null;
        return host;
    }
}
