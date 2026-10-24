using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class BrowserWindowEligibilityTests
{
    [Fact] public void UnownedNormalWindowIsEligible() => Assert.True(BrowserWindowEligibility.IsEligible(hasOwner: false, toolWindow: false, width: 1000, height: 700));
    [Fact] public void OwnedWindowIsNot() => Assert.False(BrowserWindowEligibility.IsEligible(true, false, 1000, 700));
    [Fact] public void ToolWindowIsNot() => Assert.False(BrowserWindowEligibility.IsEligible(false, true, 1000, 700));
    [Fact] public void ZeroWidthIsNot() => Assert.False(BrowserWindowEligibility.IsEligible(false, false, 0, 700));
    [Fact] public void ZeroHeightIsNot() => Assert.False(BrowserWindowEligibility.IsEligible(false, false, 1000, 0));
    [Fact] public void OwnedToolPopupIsNot() => Assert.False(BrowserWindowEligibility.IsEligible(true, true, 300, 400));
    [Fact] public void SmallUnownedWindowIsEligible() => Assert.True(BrowserWindowEligibility.IsEligible(false, false, 1, 1));
}
