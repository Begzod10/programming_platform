using PcGuard.Core;
using Xunit;

namespace PcGuard.Core.Tests;

public class StateParserTests
{
    private const string Full = """
    {"locked": true, "reason": "quota_pending", "remaining": 2, "completed": 0, "required": 2,
     "student": {"id": 5, "full_name": "Ali Valiyev"},
     "allowlist": [{"exe": "code.exe", "publisher": null}, {"exe": "chrome.exe", "publisher": "Google LLC"}],
     "browser_hosts": ["example.uz"], "server_time": "2026-10-23T10:00:00+00:00"}
    """;

    [Fact]
    public void FullObject()
    {
        var r = StateParser.Parse(Full);
        Assert.True(r.Locked);
        Assert.Equal("quota_pending", r.Reason);
        Assert.Equal(2, r.Remaining);
        Assert.Equal("Ali Valiyev", r.StudentName);
        Assert.Equal(new[] { new AllowEntry("code.exe", null), new AllowEntry("chrome.exe", "Google LLC") }, r.Allowlist.ToArray());
        Assert.Equal(new[] { "example.uz" }, r.BrowserHosts.ToArray());
    }

    [Fact]
    public void StateFrameWithType()
    {
        var r = StateParser.Parse("""{"type":"state","locked":false,"reason":"ok","remaining":0,"student":null,"allowlist":[],"browser_hosts":[]}""");
        Assert.False(r.Locked);
        Assert.Equal("ok", r.Reason);
    }

    [Fact]
    public void StudentNull_AndNullFullName()
    {
        Assert.Null(StateParser.Parse("""{"locked":true,"student":null}""").StudentName);
        Assert.Null(StateParser.Parse("""{"locked":true,"student":{"id":1,"full_name":null}}""").StudentName);
    }

    [Fact]
    public void MissingOptionalKeys()
    {
        var r = StateParser.Parse("""{"locked":true}""");
        Assert.Equal("unknown", r.Reason);
        Assert.Equal(0, r.Remaining);
        Assert.Null(r.StudentName);
        Assert.Empty(r.Allowlist);
        Assert.Empty(r.BrowserHosts);
    }

    [Fact]
    public void Normalizes()
    {
        var r = StateParser.Parse("""{"locked":false,"allowlist":[{"exe":"  Code.EXE ","publisher":"  "},{"exe":"X.exe","publisher":""}],"browser_hosts":[" Example.UZ ","  ",""]}""");
        Assert.Equal(new[] { new AllowEntry("code.exe", null), new AllowEntry("x.exe", null) }, r.Allowlist.ToArray());
        Assert.Equal(new[] { "example.uz" }, r.BrowserHosts.ToArray());
    }

    [Theory]
    [InlineData("not json")]
    [InlineData("[1,2]")]
    [InlineData("""{"reason":"x"}""")]
    [InlineData("""{"locked":"true"}""")]
    public void Invalid_ThrowsFormatException(string json)
        => Assert.Throws<FormatException>(() => StateParser.Parse(json));
}
