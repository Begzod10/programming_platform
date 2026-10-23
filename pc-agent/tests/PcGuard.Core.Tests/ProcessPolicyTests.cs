using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class ProcessPolicyTests
{
    private static PcRules Rules(bool locked, params AllowEntry[] allow) =>
        new(locked, "lesson", 10, "Student", allow, Array.Empty<string>());

    private static ProcInfo Proc(string exe, bool window = true, string? publisher = null) =>
        new(1, exe, window, publisher);

    [Fact]
    public void NotLocked_YieldsNoViolators()
    {
        var result = ProcessPolicy.FindViolators(new[] { Proc("chrome.exe") }, Rules(false));
        Assert.Empty(result);
    }

    [Fact]
    public void Locked_FlagsProcessNotInAllowlist()
    {
        var result = ProcessPolicy.FindViolators(new[] { Proc("chrome.exe") }, Rules(true, new AllowEntry("code.exe", null)));
        Assert.Single(result);
        Assert.Equal("chrome.exe", result[0].Exe);
    }

    [Fact]
    public void ExeComparisonIsCaseInsensitive()
    {
        var result = ProcessPolicy.FindViolators(new[] { Proc("Code.EXE") }, Rules(true, new AllowEntry("code.exe", null)));
        Assert.Empty(result);
    }

    [Fact]
    public void PublisherEntry_AllowsContainingPublisherCaseInsensitive()
    {
        var rules = Rules(true, new AllowEntry("app.exe", "Microsoft"));
        Assert.Empty(ProcessPolicy.FindViolators(new[] { Proc("app.exe", publisher: "Microsoft Corporation") }, rules));
        Assert.Empty(ProcessPolicy.FindViolators(new[] { Proc("app.exe", publisher: "MICROSOFT corp") }, rules));
    }

    [Fact]
    public void PublisherEntry_FlagsDifferentOrNullPublisher()
    {
        var rules = Rules(true, new AllowEntry("app.exe", "Microsoft"));
        Assert.Single(ProcessPolicy.FindViolators(new[] { Proc("app.exe", publisher: "Evil Inc") }, rules));
        Assert.Single(ProcessPolicy.FindViolators(new[] { Proc("app.exe", publisher: null) }, rules));
    }

    [Fact]
    public void ProcessWithoutVisibleWindow_IsNeverViolator()
    {
        var result = ProcessPolicy.FindViolators(new[] { Proc("chrome.exe", window: false) }, Rules(true));
        Assert.Empty(result);
    }

    [Fact]
    public void ProtectedNames_AreNeverViolators()
    {
        foreach (var name in ProcessPolicy.Protected)
        {
            Assert.Empty(ProcessPolicy.FindViolators(new[] { Proc(name) }, Rules(true)));
            Assert.Empty(ProcessPolicy.FindViolators(new[] { Proc(name.ToUpperInvariant()) }, Rules(true)));
        }
    }
}
