using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class WindowFilterTests
{
    private static bool F(bool visible = true, bool cloaked = false, int w = 800, int h = 600,
        bool tool = false, bool app = false)
        => WindowFilter.CountsAsAppWindow(visible, cloaked, w, h, tool, app);

    [Fact] public void VisibleWindowCounts() => Assert.True(F());
    [Fact] public void InvisibleDoesNot() => Assert.False(F(visible: false));
    [Fact] public void CloakedDoesNot() => Assert.False(F(cloaked: true));
    [Fact] public void ZeroWidthDoesNot() => Assert.False(F(w: 0));
    [Fact] public void ZeroHeightDoesNot() => Assert.False(F(h: 0));
    [Fact] public void NegativeSizeDoesNot() => Assert.False(F(w: -5));
    [Fact] public void SmallPlainWindowStillCounts() => Assert.True(F(w: 1, h: 1));
    [Fact] public void ToolWindowAt100x100Counts() => Assert.True(F(tool: true, w: 100, h: 100));
    [Fact] public void ToolWindowLargeCounts() => Assert.True(F(tool: true));
    [Fact] public void ToolWindowNarrowerThan100DoesNot() => Assert.False(F(tool: true, w: 99, h: 500));
    [Fact] public void ToolWindowShorterThan100DoesNot() => Assert.False(F(tool: true, w: 500, h: 99));
    [Fact] public void ToolWindowWithAppStyleCountsEvenIfSmall() => Assert.True(F(tool: true, app: true, w: 50, h: 50));
    [Fact] public void AppStyleDoesNotOverrideInvisible() => Assert.False(F(visible: false, app: true));
    [Fact] public void AppStyleDoesNotOverrideCloaked() => Assert.False(F(cloaked: true, app: true));
}
