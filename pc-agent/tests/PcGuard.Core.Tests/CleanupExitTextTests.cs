using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class CleanupExitTextTests
{
    [Fact]
    public void Zero_is_ok() => Assert.Equal("finished successfully (exit code 0).", CleanupExitText.Describe(0));

    [Fact]
    public void One_is_error_or_not_elevated() =>
        Assert.Equal("FAILED with exit code 1: an error occurred or the script was not run as Administrator. Nothing may have been changed; read the messages above.", CleanupExitText.Describe(1));

    [Fact]
    public void Two_is_partial_failure() =>
        Assert.Equal("finished with exit code 2: at least one step FAILED (partial failure). Read the FAILED lines above and follow the hints; you can run this program again.", CleanupExitText.Describe(2));

    [Theory]
    [InlineData(3)]
    [InlineData(-1)]
    [InlineData(130)]
    public void Other_codes_are_reported_as_unexpected(int code) =>
        Assert.Equal($"FAILED with unexpected exit code {code}. Read the messages above.", CleanupExitText.Describe(code));
}
