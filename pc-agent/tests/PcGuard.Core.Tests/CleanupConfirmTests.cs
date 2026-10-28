using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class CleanupConfirmTests
{
    [Theory]
    [InlineData("YES")]
    [InlineData("yes")]
    [InlineData("Yes")]
    [InlineData("  YES  ")]
    [InlineData("\tyes\r\n")]
    public void Yes_variants_are_accepted(string input) => Assert.True(CleanupConfirm.IsYes(input));

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("y")]
    [InlineData("Y")]
    [InlineData("yes please")]
    [InlineData("no")]
    [InlineData("YESS")]
    [InlineData("YE S")]
    public void Everything_else_is_rejected(string? input) => Assert.False(CleanupConfirm.IsYes(input));
}
