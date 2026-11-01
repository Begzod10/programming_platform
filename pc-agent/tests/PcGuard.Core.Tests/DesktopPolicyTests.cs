using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class DesktopPolicyTests
{
    [Theory]
    [InlineData("Default", true)]
    [InlineData("default", true)]
    [InlineData("DEFAULT", true)]
    [InlineData(null, true)]
    [InlineData("Winlogon", false)]
    [InlineData("Screen-saver", false)]
    [InlineData("Sbox_Desktop1", false)]
    [InlineData("", false)]
    public void SnapshotAllowedOnlyOnDefaultOrUnknownDesktop(string? name, bool expected)
        => Assert.Equal(expected, DesktopPolicy.ShouldSendSnapshot(name));
}
