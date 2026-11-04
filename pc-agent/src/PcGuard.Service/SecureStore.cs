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
    /// <summary>The recovery code limiter's persisted state (<see cref="RecoveryAttemptLimiter"/>).</summary>
    public string RecoveryAttemptsPath => Path.Combine(Dir, "recovery.attempts");
    private const int MaxAttemptsFileBytes = 256;

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
            if ((fi.Attributes & FileAttributes.ReparsePoint) != 0 || fi.Length > RecoveryCode.MaxStoredFileBytes)
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

    /// <summary>
    /// Reads recovery.attempts under the same trust rules as recovery.hash (regular file, small, owner
    /// SYSTEM or Administrators, no Allow ACE for anyone else). Never throws, never logs the content.
    /// </summary>
    public RecoveryAttemptFileStatus ReadRecoveryAttempts(out string? text)
    {
        text = null;
        try
        {
            var fi = new FileInfo(RecoveryAttemptsPath);
            if (!fi.Exists)
                return Directory.Exists(RecoveryAttemptsPath) ? RecoveryAttemptFileStatus.Untrusted : RecoveryAttemptFileStatus.Missing;
            if ((fi.Attributes & FileAttributes.ReparsePoint) != 0 || fi.Length > MaxAttemptsFileBytes)
                return RecoveryAttemptFileStatus.Untrusted;
            if (!IsTrusted(fi.GetAccessControl(AccessControlSections.Owner | AccessControlSections.Access)))
                return RecoveryAttemptFileStatus.Untrusted;
            text = File.ReadAllText(fi.FullName, global::System.Text.Encoding.ASCII);
            return RecoveryAttemptFileStatus.Ok;
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or InvalidOperationException
                                      or global::System.Security.SecurityException or ArgumentException)
        {
            return RecoveryAttemptFileStatus.Untrusted;
        }
    }

    /// <summary>Replaces recovery.attempts (temp file with an explicit admin-only ACL, then an atomic move). False on any failure.</summary>
    public bool WriteRecoveryAttempts(string text)
    {
        var tmp = RecoveryAttemptsPath + ".tmp";
        try
        {
            if (File.Exists(tmp)) File.Delete(tmp);
            File.WriteAllText(tmp, text, global::System.Text.Encoding.ASCII);
            new FileInfo(tmp).SetAccessControl(BuildFileSecurity());
            File.Move(tmp, RecoveryAttemptsPath, overwrite: true);
            return true;
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or InvalidOperationException
                                      or global::System.Security.SecurityException or ArgumentException or NotSupportedException)
        {
            _log.LogError("Could not write recovery.attempts ({Error})", e.GetType().Name);
            try { if (File.Exists(tmp)) File.Delete(tmp); } catch (Exception) { /* best effort */ }
            return false;
        }
    }

    /// <summary>Deletes recovery.attempts; true when it is gone.</summary>
    public bool DeleteRecoveryAttempts()
    {
        try
        {
            if (File.Exists(RecoveryAttemptsPath)) File.Delete(RecoveryAttemptsPath);
            return !File.Exists(RecoveryAttemptsPath);
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or ArgumentException)
        {
            _log.LogError("Could not delete recovery.attempts ({Error})", e.GetType().Name);
            return false;
        }
    }

    /// <summary>
    /// The recovery code was used: makes it unusable (single use). A regular recovery.hash is
    /// overwritten with zeros and deleted; a link is deleted without writing through it. True when no
    /// recovery.hash is left; otherwise <paramref name="error"/> is the exception type.
    /// </summary>
    public bool TryBurnRecoveryHash(out string? error)
    {
        error = null;
        try
        {
            var fi = new FileInfo(RecoveryHashPath);
            if (!fi.Exists) return true;
            if ((fi.Attributes & FileAttributes.ReparsePoint) == 0 && fi.Length <= RecoveryCode.MaxStoredFileBytes)
            {
                using var fs = new FileStream(fi.FullName, FileMode.Open, FileAccess.Write, FileShare.None);
                fs.Write(new byte[fs.Length]);
                fs.Flush(flushToDisk: true);
            }
            fi.Delete();
            return !File.Exists(RecoveryHashPath);
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or ArgumentException
                                      or global::System.Security.SecurityException or NotSupportedException)
        {
            error = e.GetType().Name;
            return false;
        }
    }

    private static FileSecurity BuildFileSecurity()
    {
        var sec = new FileSecurity();
        sec.SetOwner(Admins);
        sec.SetAccessRuleProtection(isProtected: true, preserveInheritance: false);
        sec.AddAccessRule(new FileSystemAccessRule(System, FileSystemRights.FullControl, AccessControlType.Allow));
        sec.AddAccessRule(new FileSystemAccessRule(Admins, FileSystemRights.FullControl, AccessControlType.Allow));
        return sec;
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

/// <summary>recovery.attempts in the secured data folder, for <see cref="RecoveryAttemptLimiter"/>.</summary>
internal sealed class RecoveryAttemptFileStore : IRecoveryAttemptStore
{
    private readonly SecureStore _store;

    public RecoveryAttemptFileStore(SecureStore store) => _store = store;

    public RecoveryAttemptFileStatus Read(out string? text) => _store.ReadRecoveryAttempts(out text);
    public bool Write(string text) => _store.WriteRecoveryAttempts(text);
    public bool Delete() => _store.DeleteRecoveryAttempts();
}

/// <summary>Used when the data folder could not be secured: recovery attempts are refused before the limiter anyway.</summary>
internal sealed class NoRecoveryAttemptStore : IRecoveryAttemptStore
{
    public RecoveryAttemptFileStatus Read(out string? text)
    {
        text = null;
        return RecoveryAttemptFileStatus.Missing;
    }

    public bool Write(string text) => false;
    public bool Delete() => true;
}
