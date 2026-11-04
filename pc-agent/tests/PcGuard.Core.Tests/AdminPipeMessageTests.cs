using System.Text.Json;
using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class AdminPipeMessageTests
{
    private static T RoundTrip<T>(T msg) where T : PipeMessage
    {
        var line = PipeMessage.Serialize(msg);
        Assert.DoesNotContain('\n', line);
        Assert.DoesNotContain('\r', line);
        return Assert.IsType<T>(PipeMessage.Parse(line));
    }

    [Fact]
    public void AdminUnlockRoundTripsWithExactWireFormat()
    {
        var line = PipeMessage.Serialize(new AdminUnlockMessage(@".\admin", "pw", 60));
        Assert.Equal("{\"t\":\"admin_unlock\",\"username\":\".\\\\admin\",\"password\":\"pw\",\"minutes\":60}", line);
        var m = RoundTrip(new AdminUnlockMessage("CORP\\x", "p@ss\nword", 240));
        Assert.Equal("admin_unlock", m.T);
        Assert.Equal("CORP\\x", m.Username);
        Assert.Equal("p@ss\nword", m.Password);
        Assert.Equal(240, m.Minutes);
    }

    [Fact]
    public void AdminUnlockToStringNeverContainsPassword()
    {
        var m = new AdminUnlockMessage("admin", "s3cret-pass", 15);
        var s = m.ToString();
        Assert.DoesNotContain("s3cret-pass", s);
        Assert.Contains("admin", s);
        Assert.Contains("***", s);
        Assert.Contains("15", s);
        // also when printed as part of a collection or another record
        Assert.DoesNotContain("s3cret-pass", $"{new[] { m }.Single()}");
        Assert.DoesNotContain("s3cret-pass", new Wrapper(m).ToString());
    }

    private sealed record Wrapper(PipeMessage Inner);

    [Theory]
    [InlineData("{\"t\":\"admin_unlock\",\"username\":\"u\",\"password\":\"p\"}", 0)]
    [InlineData("{\"t\":\"admin_unlock\",\"username\":\"u\",\"password\":\"p\",\"minutes\":\"15\"}", 0)]
    [InlineData("{\"t\":\"admin_unlock\",\"username\":\"u\",\"password\":\"p\",\"minutes\":15.5}", 0)]
    [InlineData("{\"t\":\"admin_unlock\",\"username\":\"u\",\"password\":\"p\",\"minutes\":99999999999}", 0)]
    [InlineData("{\"t\":\"admin_unlock\",\"username\":\"u\",\"password\":\"p\",\"minutes\":null}", 0)]
    [InlineData("{\"t\":\"admin_unlock\",\"username\":\"u\",\"password\":\"p\",\"minutes\":-60}", -60)]
    [InlineData("{\"t\":\"admin_unlock\",\"username\":\"u\",\"password\":\"p\",\"minutes\":100000}", 100000)]
    public void AdminUnlockWithMissingOrNonIntegerMinutesParsesAsZero(string line, int expected)
    {
        // 0 (or any value outside {15, 60, 240}) is rejected by the service with invalid_duration
        var m = Assert.IsType<AdminUnlockMessage>(PipeMessage.Parse(line));
        Assert.Equal(expected, m.Minutes);
    }

    [Theory]
    [InlineData("{\"t\":\"admin_unlock\",\"password\":\"p\",\"minutes\":15}")]
    [InlineData("{\"t\":\"admin_unlock\",\"username\":\"u\",\"minutes\":15}")]
    [InlineData("{\"t\":\"admin_unlock\",\"username\":5,\"password\":\"p\",\"minutes\":15}")]
    [InlineData("{\"t\":\"admin_unlock\",\"username\":\"u\",\"password\":null,\"minutes\":15}")]
    [InlineData("{\"t\":\"admin_result\"}")]
    [InlineData("{\"t\":\"admin_result\",\"ok\":1}")]
    [InlineData("{\"t\":\"maintenance\"}")]
    [InlineData("{\"t\":\"maintenance\",\"active\":\"true\"}")]
    [InlineData("{\"t\":\"maintenance\",\"active\":true}")]
    [InlineData("{\"t\":\"maintenance\",\"active\":true,\"until_utc\":null}")]
    [InlineData("{\"t\":\"maintenance\",\"active\":true,\"until_utc\":\"tomorrow\"}")]
    [InlineData("{\"t\":\"maintenance\",\"active\":true,\"until_utc\":5}")]
    public void MissingOrWrongTypedRequiredFieldsThrow(string line)
        => Assert.Throws<FormatException>(() => PipeMessage.Parse(line));

    [Fact]
    public void AdminEndIsExactlyTheTag()
    {
        Assert.Equal("{\"t\":\"admin_end\"}", PipeMessage.Serialize(new AdminEndMessage()));
        Assert.IsType<AdminEndMessage>(PipeMessage.Parse("{\"t\":\"admin_end\",\"password\":\"ignored\"}"));
        Assert.Equal("admin_end", RoundTrip(new AdminEndMessage()).T);
    }

    [Fact]
    public void AdminResultRoundTrips()
    {
        Assert.Equal("{\"t\":\"admin_result\",\"ok\":true,\"error\":null,\"retry_seconds\":0}",
            PipeMessage.Serialize(new AdminResultMessage(true, null, 0)));
        var ok = RoundTrip(new AdminResultMessage(true, null, 0));
        Assert.True(ok.Ok);
        Assert.Null(ok.Error);
        Assert.Equal(0, ok.RetrySeconds);
        var lo = RoundTrip(new AdminResultMessage(false, "locked_out", 600));
        Assert.False(lo.Ok);
        Assert.Equal("locked_out", lo.Error);
        Assert.Equal(600, lo.RetrySeconds);
    }

    [Theory]
    [InlineData("{\"t\":\"admin_result\",\"ok\":false,\"error\":\"not_admin\"}", 0)]
    [InlineData("{\"t\":\"admin_result\",\"ok\":false,\"error\":\"locked_out\",\"retry_seconds\":-5}", 0)]
    [InlineData("{\"t\":\"admin_result\",\"ok\":false,\"error\":\"locked_out\",\"retry_seconds\":\"9\"}", 0)]
    [InlineData("{\"t\":\"admin_result\",\"ok\":false,\"error\":\"locked_out\",\"retry_seconds\":42,\"x\":1}", 42)]
    public void AdminResultRetrySecondsDefaultsSafely(string line, int expected)
        => Assert.Equal(expected, Assert.IsType<AdminResultMessage>(PipeMessage.Parse(line)).RetrySeconds);

    [Fact]
    public void MaintenanceRoundTripsInUtc()
    {
        var until = new DateTimeOffset(2026, 10, 23, 15, 15, 0, TimeSpan.FromHours(5)); // 10:15 UTC
        var line = PipeMessage.Serialize(new MaintenanceMessage(true, until));
        Assert.Equal("{\"t\":\"maintenance\",\"active\":true,\"until_utc\":\"2026-10-23T10:15:00.0000000Z\"}", line);
        var m = RoundTrip(new MaintenanceMessage(true, until));
        Assert.True(m.Active);
        Assert.Equal(until, m.UntilUtc);
        Assert.Equal(TimeSpan.Zero, m.UntilUtc!.Value.Offset);
    }

    [Fact]
    public void InactiveMaintenanceHasNullUntil()
    {
        Assert.Equal("{\"t\":\"maintenance\",\"active\":false,\"until_utc\":null}",
            PipeMessage.Serialize(new MaintenanceMessage(false, DateTimeOffset.UtcNow)));
        var m = Assert.IsType<MaintenanceMessage>(PipeMessage.Parse("{\"t\":\"maintenance\",\"active\":false,\"until_utc\":\"garbage\"}"));
        Assert.False(m.Active);
        Assert.Null(m.UntilUtc);
    }

    [Fact]
    public void MaintenanceAcceptsAnIsoTimeWithOffset()
    {
        var m = Assert.IsType<MaintenanceMessage>(PipeMessage.Parse(
            "{\"t\":\"maintenance\",\"active\":true,\"until_utc\":\"2026-10-23T15:15:00+05:00\",\"extra\":[1]}"));
        Assert.Equal(new DateTimeOffset(2026, 10, 23, 10, 15, 0, TimeSpan.Zero), m.UntilUtc);
    }

    [Fact]
    public void AdminUnlockSnakeCaseFields()
    {
        using var doc = JsonDocument.Parse(PipeMessage.Serialize(new AdminUnlockMessage("a", "b", 15)));
        var r = doc.RootElement;
        Assert.Equal("admin_unlock", r.GetProperty("t").GetString());
        Assert.Equal(15, r.GetProperty("minutes").GetInt32());
    }
}
