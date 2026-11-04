using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class MaintenanceRequestTrackerTests
{
    [Fact]
    public void NothingIsAcceptedWithoutAPendingRequest()
    {
        var t = new MaintenanceRequestTracker();
        Assert.Null(t.Pending);
        Assert.False(t.Accept(0));
        Assert.False(t.Accept(1));
    }

    [Fact]
    public void BeginHandsOutFreshPositiveIds()
    {
        var t = new MaintenanceRequestTracker();
        var a = t.Begin();
        var b = t.Begin();
        Assert.True(a > 0);
        Assert.True(b > a);
        Assert.Equal(b, t.Pending);
    }

    [Fact]
    public void OnlyTheCurrentIdIsAcceptedAndOnlyOnce()
    {
        var t = new MaintenanceRequestTracker();
        var first = t.Begin();
        var second = t.Begin();
        Assert.False(t.Accept(first)); // a superseded request's answer is ignored
        Assert.Equal(second, t.Pending);
        Assert.True(t.Accept(second));
        Assert.Null(t.Pending);
        Assert.False(t.Accept(second)); // a duplicate answer is ignored
    }

    [Fact]
    public void CancelDropsThePendingRequestSoALateAnswerIsIgnored()
    {
        // dialog timed out or was closed: the answer that arrives later must not be shown in a new dialog
        var t = new MaintenanceRequestTracker();
        var id = t.Begin();
        t.Cancel();
        Assert.Null(t.Pending);
        Assert.False(t.Accept(id));
        var next = t.Begin();
        Assert.NotEqual(id, next);
        Assert.False(t.Accept(id));
        Assert.True(t.Accept(next));
    }
}

public class MaintenanceRedeemSlotTests
{
    [Fact]
    public void EmptySlotTakesNothing()
        => Assert.Null(new MaintenanceRedeemSlot().Take());

    [Fact]
    public void OfferIntoAnEmptySlotSupersedesNothing()
    {
        var s = new MaintenanceRedeemSlot();
        Assert.Null(s.Offer(new MaintenanceRedeemMessage(1, "123456")));
        var taken = s.Take();
        Assert.Equal(1, taken!.Id);
        Assert.Null(s.Take());
    }

    [Fact]
    public void ANewerCodeReplacesTheOlderAndReturnsItForItsErrorReply()
    {
        var s = new MaintenanceRedeemSlot();
        s.Offer(new MaintenanceRedeemMessage(1, "111111"));
        var superseded = s.Offer(new MaintenanceRedeemMessage(2, "222222"));
        Assert.Equal(1, superseded!.Id);
        var taken = s.Take();
        Assert.Equal(2, taken!.Id);
        Assert.Equal("222222", taken.Code);
    }

    [Fact]
    public void TheSupersededReplyIsAGenericErrorForThatId()
    {
        var reply = MaintenanceRedeemSlot.SupersededReply(7);
        Assert.Equal(new AdminResultMessage(false, AdminErrors.Error, 0) { Id = 7 }, reply);
        Assert.Equal("{\"t\":\"admin_result\",\"id\":7,\"ok\":false,\"error\":\"error\",\"retry_seconds\":0}",
            PipeMessage.Serialize(reply));
    }
}

public class MaintenanceRedeemTransportTests
{
    [Theory]
    [InlineData("https://lab.example.uz/api/v1")]
    [InlineData("HTTPS://lab.example.uz/api/v1")]
    [InlineData("https://127.0.0.1:8443/api/v1")]
    public void HttpsIsAllowed(string url)
        => Assert.True(BackendProtocol.AllowsMaintenanceRedeem(new Uri(url)));

    [Theory]
    [InlineData("http://lab.example.uz/api/v1")]
    [InlineData("http://localhost:8000/api/v1")] // no loopback exception for the one path the server authorises
    [InlineData("http://127.0.0.1/api/v1")]
    [InlineData("ftp://lab.example.uz/api/v1")]
    public void AnythingElseIsRefused(string url)
        => Assert.False(BackendProtocol.AllowsMaintenanceRedeem(new Uri(url)));

    [Fact]
    public void NullIsRefused() => Assert.False(BackendProtocol.AllowsMaintenanceRedeem(null));

    [Fact]
    public void RefusalAuditTextNamesTheReasonAndNeverACode()
        => Assert.Equal("Maintenance code not sent: the backend URL is not https (plain http could be forged on the LAN)",
            MaintenanceAudit.RefusedInsecureTransport());
}
