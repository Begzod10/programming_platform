using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class EnvironmentFilterTests
{
    [Theory]
    [InlineData("DOTNET_STARTUP_HOOKS=c:\\evil.dll")]
    [InlineData("dotnet_startup_hooks=x")]
    [InlineData("DoTnEt_gcServer=1")]
    [InlineData("CORECLR_ENABLE_PROFILING=1")]
    [InlineData("CORECLR_PROFILER_PATH=c:\\p.dll")]
    [InlineData("coreclr_profiler={...}")]
    [InlineData("COMPlus_ReadyToRun=0")]
    [InlineData("complus_gcserver=1")]
    [InlineData("COR_ENABLE_PROFILING=1")]
    [InlineData("COR_PROFILER=x")]
    public void BlockedPrefixesAreStripped(string entry)
        => Assert.True(EnvironmentFilter.IsBlocked(entry));

    [Theory]
    [InlineData("PATH=c:\\windows")]
    [InlineData("DOTNET=1")]            // no underscore -> not the DOTNET_ prefix
    [InlineData("DOTNETROOT=c:\\")]      // not DOTNET_
    [InlineData("COMPUTERNAME=LAB01")]   // not COMPLUS_
    [InlineData("CORP_SERVER=x")]        // not COR_
    [InlineData("USERNAME=ali")]
    [InlineData("=C:=C:\\cur")]          // drive-current-dir var, empty name
    [InlineData("MALFORMED_NO_EQUALS")]
    public void OtherEntriesAreKept(string entry)
        => Assert.False(EnvironmentFilter.IsBlocked(entry));

    [Fact]
    public void StripRemovesOnlyBlockedEntriesPreservingOrder()
    {
        var input = new[]
        {
            "PATH=c:\\windows",
            "DOTNET_STARTUP_HOOKS=evil",
            "USERNAME=ali",
            "COMPlus_ReadyToRun=0",
            "CORECLR_PROFILER_PATH=p",
            "TEMP=c:\\temp",
        };
        Assert.Equal(new[] { "PATH=c:\\windows", "USERNAME=ali", "TEMP=c:\\temp" }, EnvironmentFilter.Strip(input));
    }

    [Fact]
    public void StripHandlesEmptyInput() => Assert.Empty(EnvironmentFilter.Strip(Array.Empty<string>()));
}
