using System.Diagnostics.CodeAnalysis;

namespace PcGuard.Core;

/// <summary>
/// A Windows account name typed into the administrator maintenance dialog, split for LogonUser.
/// Accepted forms:
/// - <c>user</c> and <c>.\user</c>: a LOCAL account (Domain ".", the local account database only);
/// - <c>MACHINE\user</c> or <c>DOMAIN\user</c>: down-level logon name (Domain = the part before the backslash);
/// - <c>user@domain.tld</c>: user principal name (Domain null, User = the whole UPN, as LogonUser requires).
/// Rejected: null/empty/whitespace, control characters, more than <see cref="MaxLength"/> characters,
/// empty parts, more than one separator and characters Windows forbids in account names.
/// Case is preserved and never compared here: Windows treats account names case-insensitively, and
/// the service decides membership by SID, never by comparing names.
/// </summary>
public sealed record AdminAccountName(string? Domain, string User)
{
    public const int MaxLength = 256;

    // characters Windows does not allow in user or group names (the separators are handled separately)
    private static readonly char[] Forbidden = { '"', '/', '[', ']', ':', ';', '|', '=', ',', '+', '*', '?', '<', '>' };

    public static AdminAccountName Parse(string input)
        => TryParse(input, out var n) ? n : throw new FormatException("Not a usable Windows account name");

    public static bool TryParse(string? input, [NotNullWhen(true)] out AdminAccountName? name)
    {
        name = null;
        if (string.IsNullOrWhiteSpace(input) || input.Length > MaxLength) return false;
        if (input.Any(char.IsControl)) return false;
        var s = input.Trim();

        var slash = s.IndexOf('\\');
        if (slash >= 0)
        {
            if (s.IndexOf('\\', slash + 1) >= 0) return false;
            var domain = s[..slash].Trim();
            var user = s[(slash + 1)..].Trim();
            if (!ValidPart(domain) || !ValidPart(user) || user.Contains('@') || domain.Contains('@')) return false;
            name = new AdminAccountName(domain, user);
            return true;
        }

        var at = s.IndexOf('@');
        if (at >= 0)
        {
            if (s.IndexOf('@', at + 1) >= 0) return false;
            var user = s[..at];
            var suffix = s[(at + 1)..];
            if (!ValidPart(user) || !ValidPart(suffix) || user != user.Trim() || suffix.Any(char.IsWhiteSpace)) return false;
            name = new AdminAccountName(null, s);
            return true;
        }

        if (!ValidPart(s)) return false;
        name = new AdminAccountName(".", s);
        return true;
    }

    private static bool ValidPart(string p) => p.Length > 0 && p.IndexOfAny(Forbidden) < 0;

    public override string ToString() => Domain is null ? User : Domain + "\\" + User;
}
