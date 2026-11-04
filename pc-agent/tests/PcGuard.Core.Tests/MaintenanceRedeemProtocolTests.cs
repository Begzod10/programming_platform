using System.Text.Json;
using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class MaintenanceRedeemProtocolTests
{
    [Fact]
    public void BodyHasExactlyMachineKeyAndCode()
    {
        var body = BackendProtocol.MaintenanceRedeemBody("0f8c1e2a-1111-2222-3333-444455556666", "123456");
        Assert.Equal("{\"machine_key\":\"0f8c1e2a-1111-2222-3333-444455556666\",\"code\":\"123456\"}", body);
        using var doc = JsonDocument.Parse(body);
        Assert.Equal(2, doc.RootElement.EnumerateObject().Count());
    }

    [Fact]
    public void EndpointIsUnderTheBaseUrl()
        => Assert.Equal("https://h.example/api/v1/pc/maintenance/redeem",
            BackendProtocol.Endpoint(new Uri("https://h.example/api/v1"), BackendProtocol.MaintenanceRedeemPath).AbsoluteUri);

    [Theory]
    [InlineData("{\"minutes\":15}", 15)]
    [InlineData("{\"minutes\":60}", 60)]
    [InlineData("{\"minutes\":240,\"extra\":true}", 240)]
    public void OkWithAnAllowedDuration(string body, int minutes)
        => Assert.Equal(MaintenanceRedeemResult.Ok(minutes), BackendProtocol.ClassifyMaintenanceRedeem(200, body));

    [Theory]
    [InlineData("{\"minutes\":30}")]
    [InlineData("{\"minutes\":0}")]
    [InlineData("{\"minutes\":-15}")]
    [InlineData("{\"minutes\":100000}")]
    [InlineData("{\"minutes\":99999999999}")]
    [InlineData("{\"minutes\":15.5}")]
    [InlineData("{\"minutes\":15.0}")]
    [InlineData("{\"minutes\":\"15\"}")]
    [InlineData("{\"minutes\":null}")]
    [InlineData("{}")]
    [InlineData("[15]")]
    [InlineData("15")]
    [InlineData("not json")]
    [InlineData("")]
    [InlineData(null)]
    public void OkWithAnythingButAnAllowedIntegerIsAnError(string? body)
        => Assert.Equal(new MaintenanceRedeemResult(MaintenanceRedeemStatus.Error), BackendProtocol.ClassifyMaintenanceRedeem(200, body));

    [Theory]
    [InlineData(403, "{\"detail\":\"invalid_code\"}", MaintenanceRedeemStatus.InvalidCode)]
    [InlineData(403, null, MaintenanceRedeemStatus.InvalidCode)]
    [InlineData(429, null, MaintenanceRedeemStatus.RateLimited)]
    [InlineData(408, null, MaintenanceRedeemStatus.Offline)]
    [InlineData(502, null, MaintenanceRedeemStatus.Offline)]
    [InlineData(503, null, MaintenanceRedeemStatus.Offline)]
    [InlineData(504, null, MaintenanceRedeemStatus.Offline)]
    [InlineData(500, null, MaintenanceRedeemStatus.Error)]
    [InlineData(401, null, MaintenanceRedeemStatus.Error)]
    [InlineData(404, null, MaintenanceRedeemStatus.Error)]
    [InlineData(422, null, MaintenanceRedeemStatus.Error)]
    [InlineData(301, null, MaintenanceRedeemStatus.Error)]
    [InlineData(201, "{\"minutes\":15}", MaintenanceRedeemStatus.Error)]
    public void NonOkStatuses(int status, string? body, MaintenanceRedeemStatus expected)
    {
        var r = BackendProtocol.ClassifyMaintenanceRedeem(status, body);
        Assert.Equal(expected, r.Status);
        Assert.Equal(0, r.Minutes);
    }

    [Fact]
    public void ResultToStringShowsNoMoreThanStatusAndMinutes()
        => Assert.Equal("MaintenanceRedeemResult { Status = Ok, Minutes = 15 }", MaintenanceRedeemResult.Ok(15).ToString());
}
