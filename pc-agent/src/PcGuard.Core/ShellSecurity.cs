using System.Globalization;

namespace PcGuard.Core;

/// <summary>
/// Builds the SDDL strings that harden the service-launched shell. Pure so the exact ACE layout is
/// unit-testable; the Windows project converts and applies them.
/// </summary>
public static class ShellSecurity
{
    /// <summary>Rights the interactive user keeps on the shell's process and objects:
    /// PROCESS/THREAD_QUERY_INFORMATION (0x0400), QUERY_LIMITED_INFORMATION (0x1000),
    /// READ_CONTROL (0x00020000), SYNCHRONIZE (0x00100000). No terminate (0x0001), suspend (0x0800)
    /// or inject (0x0002/0x0008/0x0020).</summary>
    public const uint UserAllowedRights = 0x1000 | 0x0400 | 0x00100000 | 0x00020000; // 0x00121400

    /// <summary>Process-object rights DENIED to the interactive user: PROCESS_TERMINATE (0x0001),
    /// PROCESS_CREATE_THREAD (0x0002), PROCESS_VM_OPERATION (0x0008), PROCESS_VM_WRITE (0x0020),
    /// PROCESS_SUSPEND_RESUME (0x0800).</summary>
    public const uint ProcessDeniedRights = 0x0001 | 0x0002 | 0x0008 | 0x0020 | 0x0800; // 0x082B

    /// <summary>
    /// Default DACL for the DUPLICATED primary token, so THREADS and other kernel objects the shell
    /// creates are not grantable to the user for terminate/suspend/inject.
    /// Covered: SYSTEM and Administrators get full control; the interactive user gets only
    /// <see cref="UserAllowedRights"/>. The OWNER RIGHTS ACE (S-1-3-4 / alias OW) with ZERO rights is
    /// REQUIRED: these objects take the token's default owner (the interactive user), who would
    /// otherwise implicitly hold READ_CONTROL and WRITE_DAC and could rewrite the DACL to grant
    /// themselves terminate/suspend. The empty OWNER RIGHTS ACE suppresses that implicit owner power.
    /// NOT covered: SYSTEM and elevated administrators keep full control (by design).
    /// </summary>
    public static string DefaultDaclSddl(string userSid)
    {
        if (string.IsNullOrWhiteSpace(userSid)) throw new ArgumentException("A user SID is required", nameof(userSid));
        return $"D:(A;;GA;;;SY)(A;;GA;;;BA)(A;;0x0;;;OW)(A;;0x{UserAllowedRights.ToString("X", CultureInfo.InvariantCulture)};;;{userSid})";
    }

    /// <summary>
    /// Security descriptor for the shell PROCESS object: owner/group Administrators (so a standard
    /// user cannot rewrite the DACL), a deny ACE for <see cref="ProcessDeniedRights"/> first, then the
    /// user's <see cref="UserAllowedRights"/>, then SYSTEM and Administrators full control.
    /// </summary>
    public static string ProcessSddl(string userSid)
    {
        if (string.IsNullOrWhiteSpace(userSid)) throw new ArgumentException("A user SID is required", nameof(userSid));
        var denied = ProcessDeniedRights.ToString("X", CultureInfo.InvariantCulture);
        var allowed = UserAllowedRights.ToString("X", CultureInfo.InvariantCulture);
        return $"O:BAG:BAD:(D;;0x{denied};;;{userSid})(A;;0x{allowed};;;{userSid})(A;;GA;;;SY)(A;;GA;;;BA)";
    }
}
