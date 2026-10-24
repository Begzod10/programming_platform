using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class OwnershipClassifierTests
{
    private const string UserSid = "S-1-5-21-111-222-333-1001";

    [Theory]
    [InlineData("S-1-5-18")]
    [InlineData("S-1-5-19")]
    [InlineData("S-1-5-20")]
    public void ReadableServiceAccountOwner(string sid)
    {
        Assert.Equal((true, false), OwnershipClassifier.Classify(true, sid, false));
        Assert.Equal((true, true), OwnershipClassifier.Classify(true, sid, true));
    }

    [Fact]
    public void ReadableUserOwner()
    {
        Assert.Equal((false, false), OwnershipClassifier.Classify(true, UserSid, false));
        Assert.Equal((false, true), OwnershipClassifier.Classify(true, UserSid, true));
    }

    [Fact]
    public void UnreadableOwnerWithSystemImageIsServiceOwned()
        => Assert.Equal((true, true), OwnershipClassifier.Classify(true, null, true));

    [Fact]
    public void UnreadableOwnerWithOtherImageIsUserOwned()
        => Assert.Equal((false, false), OwnershipClassifier.Classify(true, null, false));

    [Fact]
    public void UnreadablePathIsServiceOwned()
    {
        Assert.Equal((true, false), OwnershipClassifier.Classify(false, null, false));
        Assert.Equal((true, false), OwnershipClassifier.Classify(false, UserSid, true));
    }
}
