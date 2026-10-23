using System.Security.AccessControl;
using System.Security.Principal;

namespace PcGuard.Service;

/// <summary>
/// %ProgramData%\PcGuard: the service's private data folder (machine key, rule cache, usage queue).
/// ACL: SYSTEM and Administrators full control, inheritance from ProgramData removed. WINDOWS ONLY.
/// Standard users may create folders under ProgramData, so a pre-existing folder that is not owned
/// by SYSTEM/Administrators or grants anyone else access is moved aside (never trusted) and a fresh
/// one is created.
/// </summary>
internal sealed class SecureStore
{
    private static readonly SecurityIdentifier System = new(WellKnownSidType.LocalSystemSid, null);
    private static readonly SecurityIdentifier Admins = new(WellKnownSidType.BuiltinAdministratorsSid, null);

    private readonly ILogger _log;

    public string Dir { get; }
    public string MachineKeyPath => Path.Combine(Dir, "machine.key");
    public string RulesPath => Path.Combine(Dir, "rules.json");
    public string UsageQueuePath => Path.Combine(Dir, "usage.queue");

    public SecureStore(ILogger log)
    {
        _log = log;
        Dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "PcGuard");
    }

    public void EnsureDirectory()
    {
        var di = new DirectoryInfo(Dir);
        if (di.Exists && !IsSecure(di))
        {
            var quarantine = Dir + ".untrusted-" + Guid.NewGuid().ToString("N");
            _log.LogError("Data folder has an unexpected owner or ACL; moving it aside to {Quarantine}", quarantine);
            Directory.Move(Dir, quarantine);
            di = new DirectoryInfo(Dir);
        }
        if (!di.Exists)
        {
            di.Create(BuildSecurity());
        }
        else
        {
            di.SetAccessControl(BuildSecurity()); // re-assert (cheap, idempotent)
        }
    }

    /// <summary>Reads the machine key, creating it (random GUID) on first start. Never logged.</summary>
    public string LoadOrCreateMachineKey()
    {
        try
        {
            if (File.Exists(MachineKeyPath) && Guid.TryParse(File.ReadAllText(MachineKeyPath).Trim(), out var existing))
                return existing.ToString("D");
        }
        catch (IOException e)
        {
            _log.LogWarning("Could not read machine key ({Error}); generating a new one", e.GetType().Name);
        }

        var key = Guid.NewGuid().ToString("D");
        var tmp = MachineKeyPath + ".tmp";
        File.WriteAllText(tmp, key); // inherits the folder ACL
        File.Move(tmp, MachineKeyPath, overwrite: true);
        _log.LogInformation("Generated a new machine key");
        return key;
    }

    private static DirectorySecurity BuildSecurity()
    {
        var sec = new DirectorySecurity();
        sec.SetOwner(Admins);
        sec.SetAccessRuleProtection(isProtected: true, preserveInheritance: false);
        const InheritanceFlags inherit = InheritanceFlags.ContainerInherit | InheritanceFlags.ObjectInherit;
        sec.AddAccessRule(new FileSystemAccessRule(System, FileSystemRights.FullControl, inherit, PropagationFlags.None, AccessControlType.Allow));
        sec.AddAccessRule(new FileSystemAccessRule(Admins, FileSystemRights.FullControl, inherit, PropagationFlags.None, AccessControlType.Allow));
        return sec;
    }

    private static bool IsSecure(DirectoryInfo di)
    {
        try
        {
            var sec = di.GetAccessControl(AccessControlSections.Owner | AccessControlSections.Access);
            var owner = sec.GetOwner(typeof(SecurityIdentifier)) as SecurityIdentifier;
            if (owner is null || !(owner.Equals(System) || owner.Equals(Admins))) return false;
            foreach (FileSystemAccessRule r in sec.GetAccessRules(includeExplicit: true, includeInherited: true, typeof(SecurityIdentifier)))
            {
                if (r.AccessControlType == AccessControlType.Deny) continue;
                if (r.IdentityReference is not SecurityIdentifier sid || !(sid.Equals(System) || sid.Equals(Admins))) return false;
            }
            return true;
        }
        catch (Exception e) when (e is UnauthorizedAccessException or IOException or InvalidOperationException)
        {
            return false;
        }
    }
}
