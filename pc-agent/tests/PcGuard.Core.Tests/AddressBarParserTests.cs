using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class AddressBarParserTests
{
    [Theory]
    [InlineData("https://Example.COM/path?q=1", "example.com")]
    [InlineData("example.com", "example.com")]
    [InlineData("  example.com/a/b  ", "example.com")]
    [InlineData("http://example.com:8080/x", "example.com")]
    [InlineData("https://user:pw@example.com/", "example.com")]
    [InlineData("example.com.", "example.com")]
    [InlineData("https://example.com./", "example.com")]
    [InlineData("www.youtube.com/watch?v=1", "www.youtube.com")]
    [InlineData("localhost:3000", "localhost")]
    [InlineData("http://192.168.0.1/", "192.168.0.1")]
    [InlineData("https://[::1]:8080/", "::1")]
    [InlineData("//example.com/x", "example.com")]
    [InlineData("LOCALHOST", "localhost")]
    public void ExtractsBareHost(string raw, string expected)
        => Assert.Equal(expected, AddressBarParser.ExtractHost(raw));

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("about:blank")]
    [InlineData("about:newtab")]
    [InlineData("chrome://settings")]
    [InlineData("edge://newtab")]
    [InlineData("file:///C:/x.html")]
    [InlineData("chrome-extension://abc/page.html")]
    [InlineData("view-source:https://example.com")]
    [InlineData("data:text/html,hi")]
    [InlineData("javascript:alert(1)")]
    [InlineData("hello world")]
    [InlineData("search for cats")]
    [InlineData("https://")]
    [InlineData("http://exa mple.com")]
    [InlineData("/")]
    [InlineData("google")]
    [InlineData("yout")]
    [InlineData("intranet/page")]
    public void ReturnsNullForNonHosts(string? raw)
        => Assert.Null(AddressBarParser.ExtractHost(raw));
}
