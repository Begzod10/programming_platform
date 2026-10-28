using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class CleanupFlowTests
{
    [Theory]
    [InlineData(0, true)]
    [InlineData(2, true)]
    [InlineData(1, false)]
    [InlineData(3, false)]
    [InlineData(64, false)]
    [InlineData(-1, false)]
    [InlineData(130, false)]
    public void Continue_after_list(int code, bool expected) => Assert.Equal(expected, CleanupFlow.ShouldContinueAfterList(code));

    [Theory]
    [InlineData(0, true)]
    [InlineData(2, true)]
    [InlineData(1, false)]
    [InlineData(3, false)]
    [InlineData(64, false)]
    [InlineData(-1, false)]
    [InlineData(130, false)]
    public void Continue_after_preview(int code, bool expected) => Assert.Equal(expected, CleanupFlow.ShouldContinueAfterPreview(code));

    [Fact]
    public void Preview_warning_text_is_exact() =>
        Assert.Equal("The preview reported steps that would FAIL or be SKIPPED (shown above). The real removal will report the same; you can still continue.", CleanupFlow.PreviewPartialWarning);
}
