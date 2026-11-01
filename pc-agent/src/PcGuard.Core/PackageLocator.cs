namespace PcGuard.Core;

/// <summary>Checks that the folder next to Setup-PcGuard.exe holds the published agent files.</summary>
public static class PackageLocator
{
    private static readonly string[] RequiredInDist =
    {
        "PcGuard.Service.exe", "PcGuard.Shell.exe", "appsettings.json",
    };

    /// <summary>Returns the required files that are missing, as display paths like <c>dist\PcGuard.Service.exe</c>.</summary>
    public static IReadOnlyList<string> Check(Func<string, bool> fileExists, string root)
    {
        var missing = new List<string>();
        foreach (var name in RequiredInDist)
        {
            if (!fileExists(Path.Combine(root, "dist", name)))
                missing.Add(@"dist\" + name);
        }
        return missing;
    }
}
