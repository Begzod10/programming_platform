using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class AdminAccountNameTests
{
    [Theory]
    [InlineData("admin", ".", "admin")]
    [InlineData("  admin  ", ".", "admin")]
    [InlineData(@".\admin", ".", "admin")]
    [InlineData(@"PC-01\Admin", "PC-01", "Admin")]
    [InlineData(@"CORP\j.doe", "CORP", "j.doe")]
    [InlineData(@"corp.example.uz\jdoe", "corp.example.uz", "jdoe")]
    [InlineData("jdoe@corp.example.uz", null, "jdoe@corp.example.uz")]
    [InlineData("John.Doe@outlook.com", null, "John.Doe@outlook.com")]
    [InlineData("Ali Valiyev", ".", "Ali Valiyev")]
    public void ParsesSupportedForms(string input, string? domain, string user)
    {
        var n = AdminAccountName.Parse(input);
        Assert.Equal(domain, n.Domain);
        Assert.Equal(user, n.User);
        Assert.True(AdminAccountName.TryParse(input, out var t));
        Assert.Equal(n, t);
    }

    [Fact]
    public void CaseIsPreservedForWindowsWhichComparesCaseInsensitively()
    {
        Assert.Equal("ADMIN", AdminAccountName.Parse("ADMIN").User);
        Assert.Equal("pc-01", AdminAccountName.Parse(@"pc-01\admin").Domain);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("\t")]
    [InlineData("ad\nmin")]
    [InlineData("ad\0min")]
    [InlineData("admin\u0007")]
    [InlineData(@"\admin")]
    [InlineData(@"PC\")]
    [InlineData(@"\")]
    [InlineData(@"a\b\c")]
    [InlineData(@" \admin")]
    [InlineData("@corp.uz")]
    [InlineData("jdoe@")]
    [InlineData("a@b@c")]
    [InlineData("jdoe@corp uz")]
    [InlineData(@"PC\jdoe@corp.uz@x")]
    [InlineData("ad/min")]
    [InlineData("ad:min")]
    [InlineData("ad*min")]
    [InlineData("ad?min")]
    [InlineData("ad<min>")]
    [InlineData("ad|min")]
    [InlineData("ad\"min")]
    [InlineData("ad[min]")]
    [InlineData("ad=min")]
    [InlineData("ad,min")]
    [InlineData("ad+min")]
    [InlineData("ad;min")]
    [InlineData(@"P*C\admin")]
    public void RejectsInvalidInput(string? input)
    {
        Assert.False(AdminAccountName.TryParse(input, out var n));
        Assert.Null(n);
        Assert.Throws<FormatException>(() => AdminAccountName.Parse(input!));
    }

    [Fact]
    public void LengthLimitIs256Characters()
    {
        Assert.Equal(256, AdminAccountName.MaxLength);
        Assert.True(AdminAccountName.TryParse(new string('a', 256), out _));
        Assert.False(AdminAccountName.TryParse(new string('a', 257), out _));
    }

    [Fact]
    public void ToStringShowsTheQualifiedName()
    {
        Assert.Equal(@".\admin", AdminAccountName.Parse("admin").ToString());
        Assert.Equal(@"CORP\jdoe", AdminAccountName.Parse(@"CORP\jdoe").ToString());
        Assert.Equal("jdoe@corp.uz", AdminAccountName.Parse("jdoe@corp.uz").ToString());
    }
}
