using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class MaintenancePipeMessageTests
{
    private static T RoundTrip<T>(T msg) where T : PipeMessage
    {
        var line = PipeMessage.Serialize(msg);
        Assert.DoesNotContain('\n', line);
        Assert.DoesNotContain('\r', line);
        return Assert.IsType<T>(PipeMessage.Parse(line));
    }

    [Fact]
    public void RedeemRoundTripsWithExactWireFormat()
    {
        Assert.Equal("{\"t\":\"maintenance_redeem\",\"code\":\"123456\"}",
            PipeMessage.Serialize(new MaintenanceRedeemMessage("123456")));
        var m = RoundTrip(new MaintenanceRedeemMessage("004200"));
        Assert.Equal("maintenance_redeem", m.T);
        Assert.Equal("004200", m.Code);
    }

    [Fact]
    public void RedeemKeepsAnyStringForTheServiceToValidate()
    {
        // the pipe does not validate the shape: the service rejects it with invalid_code (MaintenanceCode)
        var m = Assert.IsType<MaintenanceRedeemMessage>(PipeMessage.Parse("{\"t\":\"maintenance_redeem\",\"code\":\"12a\"}"));
        Assert.Equal("12a", m.Code);
    }

    [Fact]
    public void RedeemToStringNeverContainsTheCode()
    {
        var m = new MaintenanceRedeemMessage("987654");
        Assert.DoesNotContain("987654", m.ToString());
        Assert.Contains("***", m.ToString());
        Assert.DoesNotContain("987654", $"{new[] { m }.Single()}");
        Assert.DoesNotContain("987654", new Wrapper(m).ToString());
    }

    private sealed record Wrapper(PipeMessage Inner);

    [Fact]
    public void ThePasswordBasedAdminUnlockKindIsGone()
        => Assert.Throws<FormatException>(() => PipeMessage.Parse(
            "{\"t\":\"admin_unlock\",\"username\":\"u\",\"password\":\"p\",\"minutes\":15}"));

    [Theory]
    [InlineData("{\"t\":\"maintenance_redeem\"}")]
    [InlineData("{\"t\":\"maintenance_redeem\",\"code\":123456}")]
    [InlineData("{\"t\":\"maintenance_redeem\",\"code\":null}")]
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
        Assert.IsType<AdminEndMessage>(PipeMessage.Parse("{\"t\":\"admin_end\",\"code\":\"ignored\"}"));
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
        var lo = RoundTrip(new AdminResultMessage(false, AdminErrors.LockedOut, 600));
        Assert.False(lo.Ok);
        Assert.Equal("locked_out", lo.Error);
        Assert.Equal(600, lo.RetrySeconds);
        Assert.Equal("rate_limited", RoundTrip(new AdminResultMessage(false, AdminErrors.RateLimited, 0)).Error);
    }

    [Theory]
    [InlineData("{\"t\":\"admin_result\",\"ok\":false,\"error\":\"invalid_code\"}", 0)]
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
}
