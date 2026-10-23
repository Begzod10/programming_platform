using System.Text.Json;
using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class PipeProtocolTests
{
    private static T RoundTrip<T>(T msg) where T : PipeMessage
    {
        var line = PipeMessage.Serialize(msg);
        Assert.DoesNotContain('\n', line);
        Assert.DoesNotContain('\r', line);
        return Assert.IsType<T>(PipeMessage.Parse(line));
    }

    [Fact]
    public void LoginRoundTrips()
    {
        var m = RoundTrip(new LoginMessage("ali", "p@ss\nword"));
        Assert.Equal("login", m.T);
        Assert.Equal("ali", m.Username);
        Assert.Equal("p@ss\nword", m.Password);
    }

    [Fact]
    public void LoginToStringNeverContainsPassword()
    {
        var m = new LoginMessage("ali", "s3cret-pass");
        Assert.DoesNotContain("s3cret-pass", m.ToString());
        Assert.Contains("ali", m.ToString());
    }

    [Fact]
    public void LogoutRoundTrips() => Assert.Equal("logout", RoundTrip(new LogoutMessage()).T);

    [Fact]
    public void SnapshotRoundTrips()
    {
        var snap = new Snapshot(
            new[] { new WindowedProc(10, "code.exe"), new WindowedProc(11, "chrome.exe") },
            "chrome.exe",
            new[] { new BrowserWindow(0x1234_5678_9ABCL, 11, "platform.uz"), new BrowserWindow(7, 11, null) });
        var m = RoundTrip(new SnapshotMessage(snap));
        Assert.Equal("snapshot", m.T);
        Assert.Equal(snap.Windowed, m.Snapshot.Windowed);
        Assert.Equal("chrome.exe", m.Snapshot.Foreground);
        Assert.Equal(snap.Browsers, m.Snapshot.Browsers);
    }

    [Fact]
    public void SnapshotWithNullForegroundRoundTrips()
    {
        var m = RoundTrip(new SnapshotMessage(new Snapshot(Array.Empty<WindowedProc>(), null, Array.Empty<BrowserWindow>())));
        Assert.Null(m.Snapshot.Foreground);
        Assert.Empty(m.Snapshot.Windowed);
        Assert.Empty(m.Snapshot.Browsers);
    }

    [Fact]
    public void SnapshotUsesSnakeCaseWireFormat()
    {
        var line = PipeMessage.Serialize(new SnapshotMessage(new Snapshot(
            new[] { new WindowedProc(1, "a.exe") }, null, new[] { new BrowserWindow(2, 1, "x.uz") })));
        using var doc = JsonDocument.Parse(line);
        var r = doc.RootElement;
        Assert.Equal("snapshot", r.GetProperty("t").GetString());
        Assert.Equal(1, r.GetProperty("windowed")[0].GetProperty("pid").GetInt32());
        Assert.Equal("a.exe", r.GetProperty("windowed")[0].GetProperty("exe").GetString());
        Assert.Equal(JsonValueKind.Null, r.GetProperty("foreground").ValueKind);
        Assert.Equal(2, r.GetProperty("browsers")[0].GetProperty("hwnd").GetInt64());
        Assert.Equal("x.uz", r.GetProperty("browsers")[0].GetProperty("host").GetString());
    }

    [Fact]
    public void LoginResultRoundTrips()
    {
        var ok = RoundTrip(new LoginResultMessage(true, null));
        Assert.True(ok.Ok);
        Assert.Null(ok.Error);
        var bad = RoundTrip(new LoginResultMessage(false, "bad_credentials"));
        Assert.False(bad.Ok);
        Assert.Equal("bad_credentials", bad.Error);
    }

    [Fact]
    public void StateRoundTrips()
    {
        var m = RoundTrip(new StateMessage(true, "quota", 3, "Ali Valiyev"));
        Assert.Equal("state", m.T);
        Assert.True(m.Locked);
        Assert.Equal("quota", m.Reason);
        Assert.Equal(3, m.Remaining);
        Assert.Equal("Ali Valiyev", m.Student);
        Assert.Null(RoundTrip(new StateMessage(true, "no_student", 0, null)).Student);
    }

    [Fact]
    public void TextMessageRoundTrips()
    {
        var m = RoundTrip(new TextMessage("Darsga qayting!\n\"ok\""));
        Assert.Equal("message", m.T);
        Assert.Equal("Darsga qayting!\n\"ok\"", m.Text);
    }

    [Fact]
    public void CloseWindowRoundTrips()
    {
        var m = RoundTrip(new CloseWindowMessage(long.MaxValue));
        Assert.Equal("close_window", m.T);
        Assert.Equal(long.MaxValue, m.Hwnd);
    }

    [Fact]
    public void ParsesHandWrittenLogin()
    {
        var m = Assert.IsType<LoginMessage>(PipeMessage.Parse("{\"t\":\"login\",\"username\":\"u\",\"password\":\"p\"}"));
        Assert.Equal("u", m.Username);
        Assert.Equal("p", m.Password);
    }

    [Theory]
    [InlineData("{\"t\":\"hack\"}")]
    [InlineData("{\"t\":\"\"}")]
    [InlineData("{\"t\":null}")]
    [InlineData("{\"t\":5}")]
    [InlineData("{}")]
    public void UnknownOrMissingKindThrowsFormatException(string line)
        => Assert.Throws<FormatException>(() => PipeMessage.Parse(line));

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("not json")]
    [InlineData("{\"t\":\"logout\"")]
    [InlineData("[1,2]")]
    [InlineData("\"logout\"")]
    [InlineData("null")]
    [InlineData("{\"t\":\"logout\"}{\"t\":\"logout\"}")]
    public void MalformedJsonThrowsFormatException(string line)
        => Assert.Throws<FormatException>(() => PipeMessage.Parse(line));

    [Fact]
    public void NullLineThrowsFormatException()
        => Assert.Throws<FormatException>(() => PipeMessage.Parse(null!));

    [Theory]
    [InlineData("{\"t\":\"login\",\"username\":\"u\"}")]
    [InlineData("{\"t\":\"login\",\"username\":null,\"password\":\"p\"}")]
    [InlineData("{\"t\":\"login\",\"username\":\"u\",\"password\":5}")]
    [InlineData("{\"t\":\"login_result\"}")]
    [InlineData("{\"t\":\"login_result\",\"ok\":\"yes\"}")]
    [InlineData("{\"t\":\"state\",\"reason\":\"x\"}")]
    [InlineData("{\"t\":\"message\"}")]
    [InlineData("{\"t\":\"message\",\"text\":null}")]
    [InlineData("{\"t\":\"close_window\"}")]
    [InlineData("{\"t\":\"close_window\",\"hwnd\":\"12\"}")]
    [InlineData("{\"t\":\"close_window\",\"hwnd\":1.5}")]
    public void MissingOrWrongTypedRequiredFieldsThrowFormatException(string line)
        => Assert.Throws<FormatException>(() => PipeMessage.Parse(line));

    [Fact]
    public void StateWithNullsUsesSafeDefaults()
    {
        var m = Assert.IsType<StateMessage>(PipeMessage.Parse(
            "{\"t\":\"state\",\"locked\":false,\"reason\":null,\"remaining\":null,\"student\":null}"));
        Assert.False(m.Locked);
        Assert.Equal("unknown", m.Reason);
        Assert.Equal(0, m.Remaining);
        Assert.Null(m.Student);
    }

    [Fact]
    public void SnapshotWithNullOrMissingArraysIsEmpty()
    {
        var m = Assert.IsType<SnapshotMessage>(PipeMessage.Parse("{\"t\":\"snapshot\",\"windowed\":null}"));
        Assert.Empty(m.Snapshot.Windowed);
        Assert.Empty(m.Snapshot.Browsers);
        Assert.Null(m.Snapshot.Foreground);
    }

    [Fact]
    public void SnapshotSkipsInvalidEntries()
    {
        var m = Assert.IsType<SnapshotMessage>(PipeMessage.Parse(
            "{\"t\":\"snapshot\",\"windowed\":[null,5,{\"pid\":\"x\",\"exe\":\"a.exe\"},{\"pid\":3},{\"pid\":4,\"exe\":\"\"},{\"pid\":5,\"exe\":\"ok.exe\"}]," +
            "\"foreground\":7,\"browsers\":[{\"pid\":1},{\"hwnd\":9,\"pid\":2,\"host\":5},{\"hwnd\":10,\"pid\":3,\"host\":\"h.uz\"}]}"));
        Assert.Equal(new[] { new WindowedProc(5, "ok.exe") }, m.Snapshot.Windowed);
        Assert.Null(m.Snapshot.Foreground);
        Assert.Equal(new[] { new BrowserWindow(9, 2, null), new BrowserWindow(10, 3, "h.uz") }, m.Snapshot.Browsers);
    }

    private static string SnapshotLine(int windowed, int browsers)
    {
        var w = string.Join(",", Enumerable.Range(1, windowed).Select(i => $"{{\"pid\":{i},\"exe\":\"a.exe\"}}"));
        var b = string.Join(",", Enumerable.Range(1, browsers).Select(i => $"{{\"hwnd\":{i},\"pid\":{i},\"host\":null}}"));
        return $"{{\"t\":\"snapshot\",\"windowed\":[{w}],\"foreground\":null,\"browsers\":[{b}]}}";
    }

    [Fact]
    public void SnapshotAtLimitIsAccepted()
    {
        var m = Assert.IsType<SnapshotMessage>(PipeMessage.Parse(SnapshotLine(PipeMessage.MaxSnapshotEntries, PipeMessage.MaxSnapshotEntries)));
        Assert.Equal(2000, m.Snapshot.Windowed.Count);
        Assert.Equal(2000, m.Snapshot.Browsers.Count);
    }

    [Fact]
    public void OversizedSnapshotIsRejected()
    {
        Assert.Equal(2000, PipeMessage.MaxSnapshotEntries);
        Assert.Throws<FormatException>(() => PipeMessage.Parse(SnapshotLine(2001, 0)));
        Assert.Throws<FormatException>(() => PipeMessage.Parse(SnapshotLine(0, 2001)));
    }

    [Fact]
    public void SerializingOversizedSnapshotThrows()
    {
        var snap = new Snapshot(Enumerable.Range(0, 2001).Select(i => new WindowedProc(i, "a.exe")).ToList(), null, Array.Empty<BrowserWindow>());
        Assert.Throws<FormatException>(() => PipeMessage.Serialize(new SnapshotMessage(snap)));
    }

    [Fact]
    public void UnknownExtraPropertiesAreIgnored()
        => Assert.IsType<LogoutMessage>(PipeMessage.Parse("{\"t\":\"logout\",\"extra\":[1,{\"a\":2}]}"));
}
