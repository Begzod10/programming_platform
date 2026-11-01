using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class UwpPidPickerTests
{
    [Fact]
    public void CoreWindowPidsDifferingFromFrameAreReported()
        => Assert.Equal(new[] { 50 }, UwpPidPicker.Pick(10, new[] { 50 }));

    [Fact]
    public void FramePidFilteredAndDeduplicated()
        => Assert.Equal(new[] { 50, 60 }, UwpPidPicker.Pick(10, new[] { 10, 60, 50, 60 }));

    [Fact]
    public void FallsBackToFramePidWhenNoCoreWindow()
        => Assert.Equal(new[] { 10 }, UwpPidPicker.Pick(10, Array.Empty<int>()));

    [Fact]
    public void FallsBackToFramePidWhenOnlyFrameOwnedChildren()
        => Assert.Equal(new[] { 10 }, UwpPidPicker.Pick(10, new[] { 10, 10 }));
}
