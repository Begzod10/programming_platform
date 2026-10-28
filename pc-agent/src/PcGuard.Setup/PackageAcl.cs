using System.Security.AccessControl;
using System.Security.Principal;
using PcGuard.Core;

namespace PcGuard.Setup;

/// <summary>
/// Thin Windows-only reader for <see cref="PackageAclPolicy"/>: collects the ACEs of the package root and of every folder and
/// file under dist\ (install.ps1 copies all of dist\ and the service loads DLLs from it). Reparse points are never followed:
/// they are only reported. The walk stops after <see cref="PackageAclPolicy.MaxEntries"/> entries.
/// </summary>
internal static class PackageAcl
{
    public static PackageScan Read(string packageRoot)
    {
        var aces = new List<AceInfo>();
        var reparse = new List<string>();
        var count = 0;

        AddAces(aces, packageRoot, new DirectoryInfo(packageRoot).GetAccessControl(AccessControlSections.Access));

        var stack = new Stack<DirectoryInfo>();
        stack.Push(new DirectoryInfo(Path.Combine(packageRoot, "dist")));
        while (stack.Count > 0)
        {
            var dir = stack.Pop();
            if ((dir.Attributes & FileAttributes.ReparsePoint) != 0)
            {
                reparse.Add(dir.FullName);
                continue;
            }
            if (++count > PackageAclPolicy.MaxEntries) break;
            AddAces(aces, dir.FullName, dir.GetAccessControl(AccessControlSections.Access));

            foreach (var child in dir.EnumerateFileSystemInfos())
            {
                if (child is DirectoryInfo d)
                {
                    stack.Push(d);
                    continue;
                }
                if ((child.Attributes & FileAttributes.ReparsePoint) != 0)
                {
                    reparse.Add(child.FullName);
                    continue;
                }
                if (++count > PackageAclPolicy.MaxEntries) break;
                AddAces(aces, child.FullName, ((FileInfo)child).GetAccessControl(AccessControlSections.Access));
            }
            if (count > PackageAclPolicy.MaxEntries) break;
        }
        return new PackageScan(aces, reparse, count);
    }

    private static void AddAces(List<AceInfo> aces, string path, FileSystemSecurity sec)
    {
        foreach (FileSystemAccessRule r in sec.GetAccessRules(true, true, typeof(SecurityIdentifier)))
        {
            aces.Add(new AceInfo(path, ((SecurityIdentifier)r.IdentityReference).Value,
                r.AccessControlType == AccessControlType.Allow, (AceRights)(uint)r.FileSystemRights));
        }
    }
}
