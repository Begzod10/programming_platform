namespace PcGuard.Core;

/// <summary>Outcome of <see cref="BackendUrlValidator.Validate"/>. <c>Warning</c> is set only when <c>Ok</c> is true.</summary>
public sealed record BackendUrlResult(bool Ok, string? Normalized, string? Error, string? Warning);

/// <summary>Checks the backend base URL typed into the setup wrapper (rules mirror install.ps1: https unless loopback).</summary>
public static class BackendUrlValidator
{
    private static BackendUrlResult Fail(string error) => new(false, null, error, null);

    public static BackendUrlResult Validate(string? input)
    {
        var s = input?.Trim();
        if (string.IsNullOrEmpty(s))
            return Fail("The backend URL is empty.");
        if (s.Length > 2048)
            return Fail("The backend URL is too long.");

        // "://" check first: on Unix "/api/v1" would otherwise parse as an absolute file path.
        if (!s.Contains("://", StringComparison.Ordinal) || !Uri.TryCreate(s, UriKind.Absolute, out var uri))
            return Fail("The backend URL must be an absolute URL such as https://host/api/v1.");

        foreach (var ch in s)
        {
            if (ch > '~' && !char.IsWhiteSpace(ch) && !char.IsControl(ch))
                return Fail("The backend URL contains non-ASCII characters. Use the punycode (xn--) form of the domain name.");
            if (char.IsWhiteSpace(ch) || char.IsControl(ch) || ch > '~' || "\"'`<>\\".IndexOf(ch) >= 0)
                return Fail("The backend URL contains characters that are not allowed.");
        }

        var isHttps = uri.Scheme == Uri.UriSchemeHttps;
        var isHttp = uri.Scheme == Uri.UriSchemeHttp;
        if (!isHttps && !(isHttp && IsLoopback(uri.Host)))
            return Fail("Only https URLs are allowed (http is allowed only for localhost).");

        if (uri.UserInfo.Length > 0)
            return Fail("The backend URL must not contain a user name or password.");

        if (s.Contains('?') || s.Contains('#'))
            return Fail("The backend URL must not contain a query string or fragment.");

        foreach (var seg in uri.OriginalString.Split('/'))
        {
            if (seg == ".." || seg == ".")
                return Fail("The backend URL must not contain . or .. path segments.");
        }

        var path = uri.AbsolutePath.TrimEnd('/');
        var normalized = uri.GetLeftPart(UriPartial.Authority) + path;
        string? warning = path.EndsWith("/api/v1", StringComparison.OrdinalIgnoreCase)
            ? null
            : "The URL does not end with /api/v1. Continue only if this is intended.";
        return new BackendUrlResult(true, normalized, null, warning);
    }

    private static bool IsLoopback(string host) =>
        host == "localhost" || host == "127.0.0.1" || host == "[::1]";
}
