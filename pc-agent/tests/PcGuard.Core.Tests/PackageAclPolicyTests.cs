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

    private static PackageScan Scan(IEnumerable<AceInfo> aces, int count, IEnumerable<string>? reparse = null) =>
        new(aces.ToList(), (reparse ?? Array.Empty<string>()).ToList(), count);

    [Fact]
    public void Unsafe_grant_on_nested_file_is_found()
    {
        var aces = new[]
        {
            Allow(Admins, AceRights.FullControl, @"C:\P\dist"),
            Allow(Users, AceRights.Modify, @"C:\P\dist\sub\evil.dll"),
        };
        var v = PackageAclPolicy.Evaluate(Scan(aces, 3));
        Assert.False(v.IsSafe);
        Assert.Equal(new UnsafeGrant(@"C:\P\dist\sub\evil.dll", Users, "Users"), Assert.Single(v.Grants));
    }

    [Fact]
    public void Reparse_point_inside_dist_is_unsafe()
    {
        var v = PackageAclPolicy.Evaluate(Scan(Array.Empty<AceInfo>(), 2, new[] { @"C:\P\dist\link" }));
        Assert.False(v.IsSafe);
        Assert.Equal(new[] { @"C:\P\dist\link" }, v.ReparsePaths);
    }

    [Fact]
    public void More_than_the_entry_limit_is_unsafe()
    {
        var v = PackageAclPolicy.Evaluate(Scan(Array.Empty<AceInfo>(), PackageAclPolicy.MaxEntries + 1));
        Assert.False(v.IsSafe);
        Assert.True(v.TooLarge);
    }

    [Fact]
    public void Exactly_the_entry_limit_with_safe_entries_passes()
    {
        var aces = Enumerable.Range(0, PackageAclPolicy.MaxEntries)
            .Select(i => Allow(i % 2 == 0 ? Admins : Users, i % 2 == 0 ? AceRights.FullControl : AceRights.ReadAndExecute, @"C:\P\dist" + i));
        var v = PackageAclPolicy.Evaluate(Scan(aces, PackageAclPolicy.MaxEntries));
        Assert.True(v.IsSafe);
        Assert.False(v.TooLarge);
        Assert.Empty(v.Grants);
        Assert.Empty(v.ReparsePaths);
    }

    [Fact]
    public void Entry_limit_is_5000()
    {
        Assert.Equal(5000, PackageAclPolicy.MaxEntries);
    }

    [Fact]
    public void Describe_lists_up_to_five_then_counts_the_rest()
    {
        var grants = Enumerable.Range(1, 8).Select(i => new UnsafeGrant(@"C:\P\f" + i, Users, "Users")).ToList();
        var lines = PackageAclPolicy.DescribeGrants(grants);
        Assert.Equal(new[]
        {
            @"Users can modify: C:\P\f1", @"Users can modify: C:\P\f2", @"Users can modify: C:\P\f3",
            @"Users can modify: C:\P\f4", @"Users can modify: C:\P\f5", "and 3 more.",
        }, lines);
    }

    [Fact]
    public void Describe_with_five_or_fewer_has_no_more_line()
    {
        var grants = new[] { new UnsafeGrant(@"C:\P\a", Everyone, "Everyone") };
        Assert.Equal(new[] { @"Everyone can modify: C:\P\a" }, PackageAclPolicy.DescribeGrants(grants));
    }

    [Fact]
    public void Remedy_text_contains_the_exact_icacls_command()
    {
        Assert.Contains(
            "icacls C:\\PcGuardSetup /inheritance:r /grant:r \"*S-1-5-32-544:(OI)(CI)F\" \"*S-1-5-18:(OI)(CI)F\"",
            PackageAclPolicy.RemedyLines);
    }
}
