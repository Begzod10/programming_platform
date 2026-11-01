namespace PcGuard.Core;

/// <summary>
/// Strips .NET runtime hijacking variables from an environment block before it is handed to a child
/// process. A standard user can set HKCU\Environment, so variables such as DOTNET_STARTUP_HOOKS,
/// CORECLR_ENABLE_PROFILING / CORECLR_PROFILER_PATH and COMPlus_* would otherwise load student code
/// into the trusted shell started by the service. Everything whose NAME begins with one of the
/// blocked prefixes (case-insensitive) is removed; nothing is added back.
/// </summary>
public static class EnvironmentFilter
{
    private static readonly string[] BlockedPrefixes = { "DOTNET_", "COMPLUS_", "CORECLR_", "COR_" };

    /// <param name="entry">An environment entry in "NAME=VALUE" form.</param>
    public static bool IsBlocked(string entry)
    {
        if (string.IsNullOrEmpty(entry)) return false;
        var eq = entry.IndexOf('=');
        var name = eq < 0 ? entry : entry[..eq];
        if (name.Length == 0) return false; // e.g. the "=C:=..." drive-current-dir pseudo-variables
        foreach (var prefix in BlockedPrefixes)
            if (name.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
                return true;
        return false;
    }

    public static IReadOnlyList<string> Strip(IEnumerable<string> entries)
        => entries.Where(e => !IsBlocked(e)).ToList();
}
