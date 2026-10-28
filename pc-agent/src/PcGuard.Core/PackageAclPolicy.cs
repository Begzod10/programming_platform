namespace PcGuard.Core;

/// <summary>File access rights; numeric values equal System.Security.AccessControl.FileSystemRights / the Win32 masks.</summary>
[Flags]
public enum AceRights : uint
{
    None = 0,
    ReadData = 0x1,
    WriteData = 0x2,
    AppendData = 0x4,
    ReadExtendedAttributes = 0x8,
    WriteExtendedAttributes = 0x10,
    ExecuteFile = 0x20,
    DeleteSubdirectoriesAndFiles = 0x40,
    ReadAttributes = 0x80,
    WriteAttributes = 0x100,
    Delete = 0x10000,
    ReadPermissions = 0x20000,
    ChangePermissions = 0x40000,
    TakeOwnership = 0x80000,
    Synchronize = 0x100000,
    Write = 0x116,
    Read = 0x20089,
    ReadAndExecute = 0x200A9,
    Modify = 0x301BF,
    FullControl = 0x1F01FF,
    GenericAll = 0x10000000,
    GenericWrite = 0x40000000,
}

/// <summary>One access-control entry of a package path (path, trustee SID string, allow/deny, rights).</summary>
public sealed record AceInfo(string Path, string Sid, bool Allow, AceRights Rights);

public sealed record UnsafeGrant(string Path, string Sid, string Group);

/// <summary>Decides whether a package folder can be modified by standard users (then an elevated install must refuse it).</summary>
public static class PackageAclPolicy
{
    private static readonly Dictionary<string, string> LowPrivilegeGroups = new()
    {
        ["S-1-5-32-545"] = "Users",
        ["S-1-5-11"] = "Authenticated Users",
        ["S-1-1-0"] = "Everyone",
        ["S-1-5-4"] = "INTERACTIVE",
    };

    private const AceRights Dangerous =
        AceRights.WriteData | AceRights.AppendData | AceRights.DeleteSubdirectoriesAndFiles | AceRights.Delete
        | AceRights.ChangePermissions | AceRights.TakeOwnership | AceRights.GenericAll | AceRights.GenericWrite;

    /// <summary>Allow entries for Users, Authenticated Users, Everyone or INTERACTIVE that grant write-like rights. Deny entries are ignored.</summary>
    public static IReadOnlyList<UnsafeGrant> FindUnsafeGrants(IEnumerable<AceInfo> aces)
    {
        var result = new List<UnsafeGrant>();
        foreach (var a in aces)
        {
            if (!a.Allow) continue;
            if (!LowPrivilegeGroups.TryGetValue(a.Sid, out var name)) continue;
            if ((a.Rights & Dangerous) != 0)
                result.Add(new UnsafeGrant(a.Path, a.Sid, name));
        }
        return result;
    }
}
