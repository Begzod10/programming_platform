using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class PackageAclPolicyTests
{
    private const string Users = "S-1-5-32-545";
    private const string AuthUsers = "S-1-5-11";
    private const string Everyone = "S-1-1-0";
    private const string Interactive = "S-1-5-4";
    private const string Admins = "S-1-5-32-544";
    private const string System = "S-1-5-18";
    private const string CreatorOwner = "S-1-3-0";

    private static AceInfo Allow(string sid, AceRights r, string path = @"C:\P") => new(path, sid, true, r);

    [Fact]
    public void Writable_users_is_unsafe()
    {
        var g = PackageAclPolicy.FindUnsafeGrants(new[] { Allow(Users, AceRights.Write, @"C:\P\dist") });
        var one = Assert.Single(g);
        Assert.Equal(new UnsafeGrant(@"C:\P\dist", Users, "Users"), one);
    }

    [Fact]
    public void Read_only_users_is_safe()
    {
        Assert.Empty(PackageAclPolicy.FindUnsafeGrants(new[]
        {
            Allow(Users, AceRights.Read | AceRights.ReadAndExecute), Allow(Everyone, AceRights.ReadAndExecute),
        }));
    }

    [Fact]
    public void Administrators_and_system_may_write()
    {
        Assert.Empty(PackageAclPolicy.FindUnsafeGrants(new[]
        {
            Allow(Admins, AceRights.FullControl), Allow(System, AceRights.FullControl),
        }));
    }

    [Fact]
    public void Deny_ace_is_ignored()
    {
        Assert.Empty(PackageAclPolicy.FindUnsafeGrants(new[] { new AceInfo(@"C:\P", Users, false, AceRights.FullControl) }));
    }

    [Fact]
    public void Everyone_full_control_is_unsafe()
    {
        var one = Assert.Single(PackageAclPolicy.FindUnsafeGrants(new[] { Allow(Everyone, AceRights.FullControl) }));
        Assert.Equal(new UnsafeGrant(@"C:\P", Everyone, "Everyone"), one);
    }

    [Fact]
    public void Creator_owner_is_ignored()
    {
        Assert.Empty(PackageAclPolicy.FindUnsafeGrants(new[] { Allow(CreatorOwner, AceRights.FullControl) }));
    }

    [Theory]
    [InlineData(AceRights.WriteData)]
    [InlineData(AceRights.AppendData)]
    [InlineData(AceRights.Delete)]
    [InlineData(AceRights.DeleteSubdirectoriesAndFiles)]
    [InlineData(AceRights.ChangePermissions)]
    [InlineData(AceRights.TakeOwnership)]
    [InlineData(AceRights.Modify)]
    [InlineData(AceRights.GenericWrite)]
    [InlineData(AceRights.GenericAll)]
    public void Each_dangerous_right_is_unsafe(AceRights r)
    {
        Assert.Single(PackageAclPolicy.FindUnsafeGrants(new[] { Allow(AuthUsers, r) }));
    }

    [Fact]
    public void Group_names_are_reported()
    {
        var g = PackageAclPolicy.FindUnsafeGrants(new[]
        {
            Allow(AuthUsers, AceRights.Modify, "a"), Allow(Interactive, AceRights.WriteData, "b"),
        });
        Assert.Equal(new[] { "Authenticated Users", "INTERACTIVE" }, g.Select(x => x.Group));
    }

    [Fact]
    public void Write_attributes_alone_is_not_flagged()
    {
        Assert.Empty(PackageAclPolicy.FindUnsafeGrants(new[] { Allow(Users, AceRights.WriteAttributes | AceRights.Synchronize) }));
    }
}
