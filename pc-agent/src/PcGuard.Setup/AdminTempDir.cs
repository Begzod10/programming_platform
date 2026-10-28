using System.Security.AccessControl;
using System.Security.Principal;

namespace PcGuard.Setup;

/// <summary>
/// A freshly created folder that only SYSTEM and Administrators can use. The ACL is applied in the same call
/// that creates the folder (no window in which it has inherited permissions) and inheritance is removed.
/// The folder sits directly under %ProgramData% (not inside %ProgramData%\PcGuard, which belongs to the service).
/// </summary>
internal sealed class AdminTempDir
{
    public string Path { get; }

    private AdminTempDir(string path) => Path = path;

    public static AdminTempDir Create()
    {
        var programData = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
        if (string.IsNullOrWhiteSpace(programData))
            throw new InvalidOperationException("Cannot find %ProgramData%.");

        // 128-bit random name: nobody can pre-create it.
        var path = System.IO.Path.Combine(programData, "PcGuard-setup-" + Guid.NewGuid().ToString("N"));
        if (Directory.Exists(path) || File.Exists(path))
            throw new IOException("Setup folder already exists; refusing to reuse it.");

        var security = new DirectorySecurity();
        security.SetAccessRuleProtection(isProtected: true, preserveInheritance: false);
        var inherit = InheritanceFlags.ContainerInherit | InheritanceFlags.ObjectInherit;
        foreach (var sidType in new[] { WellKnownSidType.LocalSystemSid, WellKnownSidType.BuiltinAdministratorsSid })
        {
            var sid = new SecurityIdentifier(sidType, null);
            security.AddAccessRule(new FileSystemAccessRule(
                sid, FileSystemRights.FullControl, inherit, PropagationFlags.None, AccessControlType.Allow));
        }

        var info = new DirectoryInfo(path);
        info.Create(security);
        var dir = new AdminTempDir(path);
        try
        {
            dir.Verify();
        }
        catch
        {
            dir.TryDelete();
            throw;
        }
        return dir;
    }

    /// <summary>Asserts the created folder is a real directory (no reparse point) with a protected DACL holding only SYSTEM and Administrators.</summary>
    private void Verify()
    {
        var info = new DirectoryInfo(Path);
        if (!info.Exists || (info.Attributes & FileAttributes.ReparsePoint) != 0)
            throw new InvalidOperationException("Setup folder is not a plain directory; refusing to use it.");

        var sec = info.GetAccessControl(AccessControlSections.Access);
        if (!sec.AreAccessRulesProtected)
            throw new InvalidOperationException("Setup folder inherits permissions; refusing to use it.");

        var allowed = new[]
        {
            new SecurityIdentifier(WellKnownSidType.LocalSystemSid, null),
            new SecurityIdentifier(WellKnownSidType.BuiltinAdministratorsSid, null),
        };
        foreach (FileSystemAccessRule rule in sec.GetAccessRules(true, true, typeof(SecurityIdentifier)))
        {
            if (!allowed.Contains((SecurityIdentifier)rule.IdentityReference))
                throw new InvalidOperationException("Setup folder has an unexpected permission entry; refusing to use it.");
        }
    }

    /// <summary>Deletes the folder; returns false (and leaves it) if that is impossible.</summary>
    public bool TryDelete()
    {
        for (var attempt = 0; attempt < 5; attempt++)
        {
            try
            {
                if (!Directory.Exists(Path)) return true;
                Directory.Delete(Path, recursive: true);
                return true;
            }
            catch (Exception e) when (e is IOException or UnauthorizedAccessException)
            {
                Thread.Sleep(200);
            }
        }
        return !Directory.Exists(Path);
    }
}
