using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class ShellSecurityTests
{
    private const string UserSid = "S-1-5-21-111-222-333-1001";

    [Fact]
    public void DefaultDaclGrantsSystemAndAdminsFullControl()
    {
        var sddl = ShellSecurity.DefaultDaclSddl(UserSid);
        Assert.Contains("(A;;GA;;;SY)", sddl);
        Assert.Contains("(A;;GA;;;BA)", sddl);
    }

    [Fact]
    public void DefaultDaclHasEmptyOwnerRightsAce()
    {
        // suppresses the implicit READ_CONTROL/WRITE_DAC the owning (interactive) user would otherwise
        // hold, so the student cannot rewrite the DACL and grant themselves terminate/suspend.
        Assert.Contains("(A;;0x0;;;OW)", ShellSecurity.DefaultDaclSddl(UserSid));
    }

    [Fact]
    public void DefaultDaclGivesUserOnlyTheReadRights()
    {
        var sddl = ShellSecurity.DefaultDaclSddl(UserSid);
        Assert.Contains($"(A;;0x121400;;;{UserSid})", sddl);
    }

    [Fact]
    public void DefaultDaclNeverGrantsUserTerminateOrInject()
    {
        var sddl = ShellSecurity.DefaultDaclSddl(UserSid);
        foreach (var mask in UserAllowMasks(sddl, UserSid))
        {
            Assert.Equal(0u, mask & 0x0001); // PROCESS/THREAD_TERMINATE
            Assert.Equal(0u, mask & 0x0002); // CREATE_THREAD
            Assert.Equal(0u, mask & 0x0800); // SUSPEND_RESUME
        }
    }

    [Fact]
    public void ProcessSddlIsAdminOwnedAndDeniesUserTerminateFirst()
    {
        var sddl = ShellSecurity.ProcessSddl(UserSid);
        Assert.StartsWith("O:BAG:BA", sddl);
        // the deny ACE must precede the user's allow ACE
        var deny = sddl.IndexOf($"(D;;0x82B;;;{UserSid})", StringComparison.Ordinal);
        var allow = sddl.IndexOf($"(A;;0x121400;;;{UserSid})", StringComparison.Ordinal);
        Assert.True(deny >= 0 && allow > deny);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    public void BlankSidIsRejected(string sid)
    {
        Assert.Throws<ArgumentException>(() => ShellSecurity.DefaultDaclSddl(sid));
        Assert.Throws<ArgumentException>(() => ShellSecurity.ProcessSddl(sid));
    }

    // Masks of every allow ACE in the SDDL that applies to the user SID.
    private static IEnumerable<uint> UserAllowMasks(string sddl, string userSid)
    {
        foreach (var ace in sddl.Split('(', ')'))
        {
            var parts = ace.Split(';');
            if (parts.Length != 6 || parts[0] != "A") continue;
            if (parts[5] != userSid) continue;
            var mask = parts[2];
            if (mask.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
                yield return Convert.ToUInt32(mask[2..], 16);
        }
    }
}
