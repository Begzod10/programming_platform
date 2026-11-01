using System.Text.Json;
using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class BackendProtocolTests
{
    private static readonly Uri Base = new("https://lms.example.uz/api/v1");

    [Theory]
    [InlineData("https://lms.example.uz/api/v1", "https://lms.example.uz/api/v1/pc/login")]
    [InlineData("https://lms.example.uz/api/v1/", "https://lms.example.uz/api/v1/pc/login")]
    [InlineData("http://10.0.0.5:8000/api/v1", "http://10.0.0.5:8000/api/v1/pc/login")]
    public void EndpointKeepsBasePath(string baseUrl, string expected)
        => Assert.Equal(expected, BackendProtocol.Endpoint(new Uri(baseUrl), "pc/login").AbsoluteUri);

    [Theory]
    [InlineData("https://lms.example.uz/api/v1", "wss://lms.example.uz/api/v1/pc/ws?token=")]
    [InlineData("http://10.0.0.5:8000/api/v1/", "ws://10.0.0.5:8000/api/v1/pc/ws?token=")]
    public void WebSocketUriSwapsScheme(string baseUrl, string prefix)
    {
        var u = BackendProtocol.WebSocketUri(new Uri(baseUrl), "a.b+c/=");
        Assert.Equal(prefix + "a.b%2Bc%2F%3D", u.AbsoluteUri);
    }

    [Fact]
    public void WebSocketUriRejectsOtherSchemes()
        => Assert.Throws<ArgumentException>(() => BackendProtocol.WebSocketUri(new Uri("ftp://x/api"), "t"));

    [Fact]
    public void LoginBodyHasWireNames()
    {
        using var d = JsonDocument.Parse(BackendProtocol.LoginBody("ali", "p\"w", "LAB-01", "key-123456"));
        var r = d.RootElement;
        Assert.Equal("ali", r.GetProperty("username").GetString());
        Assert.Equal("p\"w", r.GetProperty("password").GetString());
        Assert.Equal("LAB-01", r.GetProperty("hostname").GetString());
        Assert.Equal("key-123456", r.GetProperty("machine_key").GetString());
    }

    [Theory]
    [InlineData(401, "bad_credentials")]
    [InlineData(422, "bad_credentials")]
    [InlineData(403, "not_a_student")]
    [InlineData(429, "rate_limited")]
    [InlineData(500, "offline")]
    [InlineData(503, "offline")]
    [InlineData(404, "offline")]
    public void LoginErrorCodes(int status, string code) => Assert.Equal(code, BackendProtocol.LoginErrorCode(status));

    [Fact]
    public void ParsesLoginResponse()
    {
        var (token, state) = BackendProtocol.ParseLoginResponse(
            "{\"token\":\"tok\",\"state\":{\"locked\":true,\"reason\":\"quota\",\"remaining\":2,\"student\":{\"full_name\":\"Ali\"},\"allowlist\":[{\"exe\":\"code.exe\"}],\"browser_hosts\":[\"lms.example.uz\"]}}");
        Assert.Equal("tok", token);
        Assert.True(state.Locked);
        Assert.Equal("quota", state.Reason);
        Assert.Equal("Ali", state.StudentName);
        Assert.Equal(new[] { "lms.example.uz" }, state.BrowserHosts);
    }

    [Theory]
    [InlineData("{}")]
    [InlineData("{\"token\":\"\",\"state\":{\"locked\":true}}")]
    [InlineData("{\"token\":\"t\"}")]
    [InlineData("{\"token\":\"t\",\"state\":5}")]
    [InlineData("{\"token\":\"t\",\"state\":{}}")]
    [InlineData("not json")]
    [InlineData("[]")]
    public void BadLoginResponseThrowsFormatException(string body)
        => Assert.Throws<FormatException>(() => BackendProtocol.ParseLoginResponse(body));

    [Fact]
    public void UsageBodyUsesIsoWithOffsetAndWireNames()
    {
        var e = new UsageEvent("code.exe",
            new DateTimeOffset(2026, 10, 23, 9, 0, 1, 250, TimeSpan.FromHours(5)),
            new DateTimeOffset(2026, 10, 23, 9, 5, 0, TimeSpan.FromHours(5)), true);
        var body = BackendProtocol.UsageBody(new[] { e });
        using var d = JsonDocument.Parse(body);
        var ev = d.RootElement.GetProperty("events")[0];
        Assert.Equal("code.exe", ev.GetProperty("app_name").GetString());
        Assert.Equal("2026-10-23T09:00:01.250+05:00", ev.GetProperty("started_at").GetString());
        Assert.Equal("2026-10-23T09:05:00.000+05:00", ev.GetProperty("ended_at").GetString());
        Assert.True(ev.GetProperty("was_locked").GetBoolean());
    }

    [Fact]
    public void UsageBodyRejectsMoreThan500()
        => Assert.Throws<ArgumentException>(() => BackendProtocol.UsageBody(
            Enumerable.Range(0, 501).Select(_ => new UsageEvent("a", DateTimeOffset.UnixEpoch, DateTimeOffset.UnixEpoch.AddSeconds(1), false)).ToList()));

    [Theory]
    [InlineData(200, UsageOutcome.Ok)]
    [InlineData(204, UsageOutcome.Ok)]
    [InlineData(422, UsageOutcome.DropBatch)]
    [InlineData(400, UsageOutcome.DropBatch)]
    [InlineData(413, UsageOutcome.DropBatch)]
    [InlineData(401, UsageOutcome.TokenDead)]
    [InlineData(403, UsageOutcome.TokenDead)]
    [InlineData(429, UsageOutcome.Retry)]
    [InlineData(408, UsageOutcome.Retry)]
    [InlineData(500, UsageOutcome.Retry)]
    [InlineData(502, UsageOutcome.Retry)]
    public void ClassifiesUsageResponses(int status, UsageOutcome outcome)
        => Assert.Equal(outcome, BackendProtocol.ClassifyUsage(status));

    [Fact]
    public void HeartbeatFrame()
    {
        using var a = JsonDocument.Parse(BackendProtocol.Heartbeat("code.exe"));
        Assert.Equal("hb", a.RootElement.GetProperty("type").GetString());
        Assert.Equal("code.exe", a.RootElement.GetProperty("app").GetString());
        using var b = JsonDocument.Parse(BackendProtocol.Heartbeat(null));
        Assert.Equal(JsonValueKind.Null, b.RootElement.GetProperty("app").ValueKind);
    }

    [Fact]
    public void ParsesStateFrame()
    {
        var f = BackendProtocol.ParseServerFrame("{\"type\":\"state\",\"locked\":false,\"reason\":\"quota_met\",\"remaining\":0,\"student\":null,\"allowlist\":[],\"browser_hosts\":[]}");
        Assert.Equal(ServerFrameKind.State, f.Kind);
        Assert.NotNull(f.State);
        Assert.False(f.State!.Locked);
    }

    [Fact]
    public void ParsesPongAndMessageFrames()
    {
        Assert.Equal(ServerFrameKind.Pong, BackendProtocol.ParseServerFrame("{\"type\":\"pong\"}").Kind);
        var m = BackendProtocol.ParseServerFrame("{\"type\":\"message\",\"text\":\"Salom\"}");
        Assert.Equal(ServerFrameKind.Message, m.Kind);
        Assert.Equal("Salom", m.Text);
    }

    [Theory]
    [InlineData("{\"type\":\"other\"}")]
    [InlineData("{\"type\":\"message\"}")]
    [InlineData("{\"type\":\"message\",\"text\":5}")]
    [InlineData("{}")]
    public void UnknownOrIncompleteFramesAreIgnored(string json)
        => Assert.Equal(ServerFrameKind.Unknown, BackendProtocol.ParseServerFrame(json).Kind);

    [Theory]
    [InlineData("nope")]
    [InlineData("[1]")]
    [InlineData("{\"type\":\"state\"}")]
    public void MalformedFramesThrowFormatException(string json)
        => Assert.Throws<FormatException>(() => BackendProtocol.ParseServerFrame(json));
}
