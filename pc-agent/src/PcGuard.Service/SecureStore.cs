using PcGuard.Core;
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
    /// <summary>The recovery code hash written by install.ps1 (never the code itself).</summary>
    public string RecoveryHashPath => Path.Combine(Dir, "recovery.hash");

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

    public enum RecoveryHashStatus { Ok, Missing, Untrusted, Malformed }

    /// <summary>
    /// Reads recovery.hash fresh (so an install or -ClearRecoveryCode needs no restart). Trusted only if
    /// it is a regular file (not a link), small, owned by SYSTEM or Administrators and granting no one
    /// else any access, and its content (surrounding whitespace ignored) is the stored hash form.
    /// Never logs or returns the content on failure.
    /// </summary>
    public RecoveryHashStatus TryReadRecoveryHash(out string? stored)
    {
        stored = null;
        try
        {
            var fi = new FileInfo(RecoveryHashPath);
            if (!fi.Exists) return RecoveryHashStatus.Missing;
            if ((fi.Attributes & FileAttributes.ReparsePoint) != 0 || fi.Length > RecoveryCode.MaxStoredLength + 8)
                return RecoveryHashStatus.Untrusted;
            if (!IsTrusted(fi.GetAccessControl(AccessControlSections.Owner | AccessControlSections.Access)))
                return RecoveryHashStatus.Untrusted;
            var text = File.ReadAllText(fi.FullName, global::System.Text.Encoding.ASCII).Trim();
            if (!RecoveryCode.IsWellFormedStored(text)) return RecoveryHashStatus.Malformed;
            stored = text;
            return RecoveryHashStatus.Ok;
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or InvalidOperationException
                                      or global::System.Security.SecurityException or ArgumentException)
        {
            return RecoveryHashStatus.Untrusted;
        }
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
            return IsTrusted(di.GetAccessControl(AccessControlSections.Owner | AccessControlSections.Access));
        }
        catch (Exception e) when (e is UnauthorizedAccessException or IOException or InvalidOperationException)
        {
            return false;
        }
    }

    // Owner SYSTEM or Administrators, and every Allow ACE (explicit or inherited) for SYSTEM or Administrators only.
    private static bool IsTrusted(FileSystemSecurity sec)
    {
        var owner = sec.GetOwner(typeof(SecurityIdentifier)) as SecurityIdentifier;
        if (owner is null || !(owner.Equals(System) || owner.Equals(Admins))) return false;
        foreach (FileSystemAccessRule r in sec.GetAccessRules(includeExplicit: true, includeInherited: true, typeof(SecurityIdentifier)))
        {
            if (r.AccessControlType == AccessControlType.Deny) continue;
            if (r.IdentityReference is not SecurityIdentifier sid || !(sid.Equals(System) || sid.Equals(Admins))) return false;
        }
        return true;
    }
}
