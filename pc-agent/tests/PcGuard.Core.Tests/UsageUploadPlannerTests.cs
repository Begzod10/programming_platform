using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class UsageUploadPlannerTests
{
    private static readonly DateTimeOffset Now = new(2026, 10, 24, 10, 0, 0, TimeSpan.Zero);

    [Fact]
    public void OpenSessionUploadsWithItsToken()
    {
        var d = UsageUploadPlanner.Decide(new SessionToken("tok-A", null), Now);
        Assert.Equal(UsageTagAction.Upload, d.Action);
        Assert.Equal("tok-A", d.Token);
    }

    [Fact]
    public void UnknownTagIsDropped()
    {
        // token not in memory (e.g. after a service restart): never upload with another session's token
        var d = UsageUploadPlanner.Decide(null, Now);
        Assert.Equal(UsageTagAction.Drop, d.Action);
        Assert.Null(d.Token);
    }

    [Fact]
    public void ClosedSessionWithinGraceUploadsWithItsOwnToken()
    {
        var d = UsageUploadPlanner.Decide(new SessionToken("tok-A", Now.AddHours(-23)), Now);
        Assert.Equal(UsageTagAction.Upload, d.Action);
        Assert.Equal("tok-A", d.Token);
    }

    [Fact]
    public void ClosedSessionAtExactlyGraceStillUploads()
    {
        Assert.Equal(TimeSpan.FromHours(24), UsageUploadPlanner.Grace);
        var d = UsageUploadPlanner.Decide(new SessionToken("tok-A", Now.AddHours(-24)), Now);
        Assert.Equal(UsageTagAction.Upload, d.Action);
    }

    [Fact]
    public void ClosedSessionPastGraceIsDropped()
    {
        var d = UsageUploadPlanner.Decide(new SessionToken("tok-A", Now.AddHours(-24).AddSeconds(-1)), Now);
        Assert.Equal(UsageTagAction.Drop, d.Action);
    }

    [Fact]
    public void FutureClosedAtIsDropped()
    {
        // clock moved backwards: do not trust it, drop rather than risk cross-student upload
        var d = UsageUploadPlanner.Decide(new SessionToken("tok-A", Now.AddMinutes(10)), Now);
        Assert.Equal(UsageTagAction.Drop, d.Action);
    }
}
