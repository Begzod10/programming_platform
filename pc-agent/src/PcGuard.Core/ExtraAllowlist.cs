namespace PcGuard.Core;

/// <summary>
/// PC-local "extra allowed apps" (<c>Allowlist:ExtraApps</c> in the installed appsettings.json, written
/// by install.ps1; the folder is writable by administrators only). The service merges them into the
/// EFFECTIVE allowlist in every state (signed out, defaults, student rules, offline cache, fail-closed)
/// as publisher-free entries. They are never stored in the rule cache and never sent anywhere.
/// Protected-process and browser-host handling is unchanged: an extra app is treated exactly like an
/// allowlisted app.
/// </summary>
public static class ExtraAllowlist
{
    public const int MaxEntries = 16;
    public const int MinLength = 5;
    public const int MaxLength = 64;

    public const string Rule =
        "a bare exe file name ending in .exe, 5-64 characters, only letters A-Z, digits, '.', '-' and '_' (no path, spaces or wildcards)";

    /// <summary>A bare file name ending in <c>.exe</c>, 5-64 chars of ASCII letters, digits, '.', '-', '_'.</summary>
    public static bool IsValidName(string? name)
    {
        if (name is null || name.Length < MinLength || name.Length > MaxLength) return false;
        if (!name.EndsWith(".exe", StringComparison.OrdinalIgnoreCase)) return false;
        foreach (var c in name)
        {
            var ok = c is >= 'a' and <= 'z' or >= 'A' and <= 'Z' or >= '0' and <= '9' or '.' or '-' or '_';
            if (!ok) return false;
        }
        return true;
    }

    /// <summary>
    /// Splits configured entries into valid names (lower-cased, case-insensitively de-duplicated, at most
    /// <see cref="MaxEntries"/>, in order) and rejected entries (invalid, or valid but beyond the limit).
    /// Duplicates are dropped silently. Entries are not trimmed.
    /// </summary>
    public static (IReadOnlyList<string> Valid, IReadOnlyList<string> Rejected) Parse(IEnumerable<string?>? entries)
    {
        var valid = new List<string>();
        var rejected = new List<string>();
        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var e in entries ?? Array.Empty<string?>())
        {
            if (!IsValidName(e)) { rejected.Add(e ?? ""); continue; }
            var n = e!.ToLowerInvariant();
            if (seen.Contains(n)) continue;
            if (valid.Count >= MaxEntries) { rejected.Add(e); continue; }
            seen.Add(n);
            valid.Add(n);
        }
        return (valid, rejected);
    }

    /// <summary>
    /// The rule allowlist plus each extra as <c>AllowEntry(name, null)</c>. An extra is skipped when the
    /// rules (or an earlier extra) already hold a publisher-free entry with the same name (ignoring case);
    /// next to a publisher-bound entry it is still added, so the app is allowed whatever its metadata says.
    /// Returns <paramref name="rules"/> itself when nothing is added.
    /// </summary>
    public static IReadOnlyList<AllowEntry> Merge(IReadOnlyList<AllowEntry> rules, IReadOnlyList<string> extras)
    {
        if (extras.Count == 0) return rules;
        var present = new HashSet<string>(
            rules.Where(r => r.Publisher is null && r.Exe is not null).Select(r => r.Exe), StringComparer.OrdinalIgnoreCase);
        List<AllowEntry>? merged = null;
        foreach (var x in extras)
        {
            if (!present.Add(x)) continue;
            merged ??= new List<AllowEntry>(rules);
            merged.Add(new AllowEntry(x, null));
        }
        return merged is null ? rules : merged.AsReadOnly();
    }

    /// <summary><paramref name="rules"/> with the extras merged into its allowlist; everything else unchanged.</summary>
    public static PcRules Apply(PcRules rules, IReadOnlyList<string> extras)
    {
        var merged = Merge(rules.Allowlist, extras);
        return ReferenceEquals(merged, rules.Allowlist) ? rules : rules with { Allowlist = merged };
    }

    /// <summary>
    /// Install-time check (Setup-PcGuard.exe): any invalid name, or more than <see cref="MaxEntries"/>
    /// distinct names, refuses the whole list with an error. Otherwise the normalised, de-duplicated names.
    /// </summary>
    public static (IReadOnlyList<string> Names, string? Error) ValidateForInstall(IEnumerable<string> names)
    {
        var (valid, rejected) = Parse(names);
        var invalid = rejected.Where(r => !IsValidName(r)).ToList();
        if (invalid.Count > 0)
            return (Array.Empty<string>(), $"Invalid extra app name '{invalid[0]}': it must be {Rule}.");
        if (rejected.Count > 0)
            return (Array.Empty<string>(), $"Too many extra apps: at most {MaxEntries} are allowed.");
        return (valid, null);
    }

    /// <summary>Comma separated input (interactive Setup question): pieces trimmed, empty pieces dropped.</summary>
    public static IReadOnlyList<string> SplitList(string? input)
        => string.IsNullOrWhiteSpace(input)
            ? Array.Empty<string>()
            : input.Split(',').Select(p => p.Trim()).Where(p => p.Length > 0).ToList();
}
