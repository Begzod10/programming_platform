using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class BrowserHostRuleTests
{
    private static readonly string[] Allowed = { "example.uz" };

    [Fact]
    public void EmptyAllowedListDisablesRule() =>
        Assert.True(BrowserHostRule.IsAllowed("youtube.com", Array.Empty<string>()));

    [Fact]
    public void NullHostIsAllowed() => Assert.True(BrowserHostRule.IsAllowed(null, Allowed));

    [Fact]
    public void EmptyHostIsAllowed() => Assert.True(BrowserHostRule.IsAllowed("", Allowed));

    [Fact]
    public void ExactHostAllowed() => Assert.True(BrowserHostRule.IsAllowed("example.uz", Allowed));

    [Fact]
    public void SubdomainAllowed() => Assert.True(BrowserHostRule.IsAllowed("platform.example.uz", Allowed));

    [Fact]
    public void WwwAllowedViaSuffixRule() => Assert.True(BrowserHostRule.IsAllowed("www.example.uz", Allowed));

    [Fact]
    public void LookalikeSuffixNotAllowed() => Assert.False(BrowserHostRule.IsAllowed("evilexample.uz", Allowed));

    [Fact]
    public void UnrelatedHostNotAllowed() => Assert.False(BrowserHostRule.IsAllowed("youtube.com", Allowed));

    [Fact]
    public void AllowedHostAsPrefixOfOtherDomainNotAllowed() =>
        Assert.False(BrowserHostRule.IsAllowed("example.uz.evil.com", Allowed));

    [Fact]
    public void UppercaseHostAllowed() => Assert.True(BrowserHostRule.IsAllowed("Platform.EXAMPLE.uz", Allowed));

    [Fact]
    public void TrailingDotAllowed() => Assert.True(BrowserHostRule.IsAllowed("example.uz.", Allowed));

    [Fact]
    public void AllowedHostInUpperCase() =>
        Assert.True(BrowserHostRule.IsAllowed("platform.example.uz", new[] { "EXAMPLE.UZ" }));

    [Fact]
    public void AnyAllowedEntryMatches() =>
        Assert.True(BrowserHostRule.IsAllowed("docs.other.uz", new[] { "example.uz", "other.uz" }));

    [Theory]
    [InlineData("chrome.exe", true)]
    [InlineData("MSEdge.exe", true)]
    [InlineData("firefox.exe", false)]
    public void IsBrowser(string exe, bool expected) => Assert.Equal(expected, BrowserHostRule.IsBrowser(exe));

    [Fact]
    public void EmptyAndWhitespaceEntriesAreSkipped() =>
        Assert.False(BrowserHostRule.IsAllowed("youtube.com", new[] { "", "  ", "example.uz" }));

    [Fact]
    public void AllEmptyEntriesMeanRuleDisabled() =>
        Assert.True(BrowserHostRule.IsAllowed("youtube.com", new[] { "", "   " }));

    [Fact]
    public void AllowedEntriesAreNormalized() =>
        Assert.True(BrowserHostRule.IsAllowed("platform.example.uz", new[] { "  Example.UZ. " }));

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    public void IsBrowserNullOrEmptyIsFalse(string? exe) => Assert.False(BrowserHostRule.IsBrowser(exe));
}
