using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class BackendUrlValidatorTests
{
    [Fact]
    public void Valid_https_url_is_accepted_without_warning()
    {
        var r = BackendUrlValidator.Validate("https://example.uz/api/v1");
        Assert.True(r.Ok);
        Assert.Equal("https://example.uz/api/v1", r.Normalized);
        Assert.Null(r.Error);
        Assert.Null(r.Warning);
    }

    [Fact]
    public void Input_is_trimmed_and_trailing_slash_removed()
    {
        var r = BackendUrlValidator.Validate("  https://example.uz/api/v1/  ");
        Assert.True(r.Ok);
        Assert.Equal("https://example.uz/api/v1", r.Normalized);
        Assert.Null(r.Warning);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void Empty_is_rejected(string? input)
    {
        var r = BackendUrlValidator.Validate(input);
        Assert.False(r.Ok);
        Assert.Null(r.Normalized);
        Assert.Equal("The backend URL is empty.", r.Error);
    }

    [Theory]
    [InlineData("example.uz/api/v1")]
    [InlineData("/api/v1")]
    [InlineData("not a url")]
    public void Not_an_absolute_url_is_rejected(string input)
    {
        var r = BackendUrlValidator.Validate(input);
        Assert.False(r.Ok);
        Assert.Equal("The backend URL must be an absolute URL such as https://host/api/v1.", r.Error);
    }

    [Theory]
    [InlineData("ftp://example.uz/api/v1")]
    [InlineData("file:///c:/x")]
    public void Other_schemes_are_rejected(string input)
    {
        var r = BackendUrlValidator.Validate(input);
        Assert.False(r.Ok);
        Assert.Equal("Only https URLs are allowed (http is allowed only for localhost).", r.Error);
    }

    [Fact]
    public void Http_to_a_remote_host_is_rejected()
    {
        var r = BackendUrlValidator.Validate("http://example.uz/api/v1");
        Assert.False(r.Ok);
        Assert.Equal("Only https URLs are allowed (http is allowed only for localhost).", r.Error);
    }

    [Theory]
    [InlineData("http://localhost:8000/api/v1", "http://localhost:8000/api/v1")]
    [InlineData("http://127.0.0.1:8000/api/v1", "http://127.0.0.1:8000/api/v1")]
    [InlineData("http://[::1]:8000/api/v1", "http://[::1]:8000/api/v1")]
    [InlineData("HTTP://LOCALHOST/api/v1", "http://localhost/api/v1")]
    public void Http_to_loopback_is_accepted(string input, string expected)
    {
        var r = BackendUrlValidator.Validate(input);
        Assert.True(r.Ok);
        Assert.Equal(expected, r.Normalized);
    }

    [Theory]
    [InlineData("https://user@example.uz/api/v1")]
    [InlineData("https://user:pw@example.uz/api/v1")]
    public void Userinfo_is_rejected(string input)
    {
        var r = BackendUrlValidator.Validate(input);
        Assert.False(r.Ok);
        Assert.Equal("The backend URL must not contain a user name or password.", r.Error);
    }

    [Theory]
    [InlineData("https://example.uz/api/v1?x=1")]
    [InlineData("https://example.uz/api/v1#frag")]
    [InlineData("https://example.uz/api/v1?")]
    public void Query_and_fragment_are_rejected(string input)
    {
        var r = BackendUrlValidator.Validate(input);
        Assert.False(r.Ok);
        Assert.Equal("The backend URL must not contain a query string or fragment.", r.Error);
    }

    [Theory]
    [InlineData("https://example.uz/api/v1\"")]
    [InlineData("https://example.uz/a b/api/v1")]
    public void Quotes_and_inner_whitespace_are_rejected(string input)
    {
        var r = BackendUrlValidator.Validate(input);
        Assert.False(r.Ok);
        Assert.Equal("The backend URL contains characters that are not allowed.", r.Error);
    }

    [Theory]
    [InlineData("https://example.uz", "https://example.uz")]
    [InlineData("https://example.uz/", "https://example.uz")]
    [InlineData("https://example.uz/api", "https://example.uz/api")]
    [InlineData("https://example.uz/v1/api/v1x", "https://example.uz/v1/api/v1x")]
    public void Url_not_ending_in_api_v1_is_accepted_with_warning(string input, string expected)
    {
        var r = BackendUrlValidator.Validate(input);
        Assert.True(r.Ok);
        Assert.Equal(expected, r.Normalized);
        Assert.Equal("The URL does not end with /api/v1. Continue only if this is intended.", r.Warning);
    }

    [Fact]
    public void Host_is_lowercased_and_default_port_dropped()
    {
        var r = BackendUrlValidator.Validate("https://EXAMPLE.uz:443/api/v1");
        Assert.True(r.Ok);
        Assert.Equal("https://example.uz/api/v1", r.Normalized);
    }
}
