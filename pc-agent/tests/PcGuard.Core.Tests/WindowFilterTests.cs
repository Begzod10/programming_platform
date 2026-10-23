using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class WindowFilterTests
{
    private static bool F(bool visible = true, bool cloaked = false, int w = 800, int h = 600,
        bool tool = false, bool app = false, bool title = true)
        => WindowFilter.CountsAsAppWindow(visible, cloaked, w, h, tool, app, title);

    [Fact] public void VisibleTitledWindowCounts() => Assert.True(F());
    [Fact] public void InvisibleDoesNot() => Assert.False(F(visible: false));
    [Fact] public void CloakedDoesNot() => Assert.False(F(cloaked: true));
    [Fact] public void ZeroWidthDoesNot() => Assert.False(F(w: 0));
    [Fact] public void ZeroHeightDoesNot() => Assert.False(F(h: 0));
    [Fact] public void NegativeSizeDoesNot() => Assert.False(F(w: -5));
    [Fact] public void ToolWindowWithoutAppStyleDoesNot() => Assert.False(F(tool: true));
    [Fact] public void ToolWindowWithAppStyleCounts() => Assert.True(F(tool: true, app: true));
    [Fact] public void AppStyleCountsWithoutTitle() => Assert.True(F(app: true, title: false));
    [Fact] public void UntitledPlainWindowDoesNot() => Assert.False(F(title: false));
    [Fact] public void AppStyleDoesNotOverrideInvisible() => Assert.False(F(visible: false, app: true));
    [Fact] public void AppStyleDoesNotOverrideCloaked() => Assert.False(F(cloaked: true, app: true));
}
