using System.Security.AccessControl;
using System.Security.Principal;
using PcGuard.Core;

namespace PcGuard.Setup;

/// <summary>Thin Windows-only reader: collects the ACEs of the package root, dist\ and the required files for <see cref="PackageAclPolicy"/>.</summary>
internal static class PackageAcl
{
    public static List<AceInfo> Read(string packageRoot)
    {
        var dist = Path.Combine(packageRoot, "dist");
        var aces = new List<AceInfo>();
        AddDirectory(aces, packageRoot);
        AddDirectory(aces, dist);
        foreach (var f in new[] { "PcGuard.Service.exe", "PcGuard.Shell.exe", "appsettings.json" })
            AddFile(aces, Path.Combine(dist, f));
        return aces;
    }

    private static void AddDirectory(List<AceInfo> aces, string path) =>
        Add(aces, path, new DirectoryInfo(path).GetAccessControl(AccessControlSections.Access));

    private static void AddFile(List<AceInfo> aces, string path) =>
        Add(aces, path, new FileInfo(path).GetAccessControl(AccessControlSections.Access));

    private static void Add(List<AceInfo> aces, string path, FileSystemSecurity sec)
    {
        foreach (FileSystemAccessRule r in sec.GetAccessRules(true, true, typeof(SecurityIdentifier)))
        {
            aces.Add(new AceInfo(path, ((SecurityIdentifier)r.IdentityReference).Value,
                r.AccessControlType == AccessControlType.Allow, (AceRights)(uint)r.FileSystemRights));
        }
    }
}
