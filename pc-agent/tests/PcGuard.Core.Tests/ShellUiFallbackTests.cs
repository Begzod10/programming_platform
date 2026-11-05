using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class ShellUiFallbackTests
{
    [Theory]
    [InlineData(true, false, ShellUiMode.Full)]
    [InlineData(true, true, ShellUiMode.Full)]
    [InlineData(false, true, ShellUiMode.Fallback)]
    [InlineData(false, false, ShellUiMode.NoWindow)]
    public void ModeFollowsWhatCouldBeBuilt(bool mainWindows, bool fallbackShown, ShellUiMode expected)
        => Assert.Equal(expected, ShellUiFallback.Mode(mainWindows, fallbackShown));

    [Theory]
    // the fallback lock window hides only when the SERVICE says a student is signed in or maintenance is on
    [InlineData(false, false, false, true)]
    [InlineData(false, true, true, true)] // no service connection: whatever was last known, stay locked
    [InlineData(true, false, false, true)]
    [InlineData(true, true, false, false)]
    [InlineData(true, false, true, false)]
    public void FallbackWindowStaysUpUnlessTheServiceSaysOtherwise(bool connected, bool signedIn, bool maintenance, bool visible)
        => Assert.Equal(visible, ShellUiFallback.FallbackVisible(connected, signedIn, maintenance));

    [Fact]
    public void ModeLinesKeepTheOldWindowsCreatedStepAndNameTheDegradedModes()
    {
        Assert.Equal("Startup: windows created", ShellDiagnostics.UiModeLine(ShellUiMode.Full));
        Assert.StartsWith("Startup: main windows failed: showing the fallback lock window", ShellDiagnostics.UiModeLine(ShellUiMode.Fallback));
        Assert.StartsWith("Startup: no window could be created", ShellDiagnostics.UiModeLine(ShellUiMode.NoWindow));
        Assert.Contains("pipe client", ShellDiagnostics.UiModeLine(ShellUiMode.NoWindow));
    }

    [Fact]
    public void FallbackTextIsBilingualAndAsksForAnAdult()
    {
        var t = UiStrings.FallbackLock();
        Assert.Contains("bloklangan", t);
        Assert.Contains("заблокирован", t);
        Assert.Contains("administrator", t);
        Assert.Contains("администратор", t);
    }
}

public class ExceptionReportTests
{
    private static Exception Thrown(Func<Exception> make)
    {
        try { throw make(); }
        catch (Exception e) { return e; }
    }

    [Fact]
    public void ReportHasTypeHresultAndStackButNeverTheMessage()
    {
        var e = Thrown(() => new OutOfMemoryException("secret-message-text"));
        var r = ShellDiagnostics.ExceptionReport(e);
        Assert.StartsWith("System.OutOfMemoryException (HRESULT 0x8007000E)", r);
        Assert.Contains(nameof(Thrown), r); // stack trace present
        Assert.DoesNotContain("secret-message-text", r);
    }

    [Fact]
    public void InnerExceptionsAreIncludedByTypeAndHresult()
    {
        var inner = Thrown(() => new System.Runtime.InteropServices.COMException("inner-secret", unchecked((int)0x80040154)));
        var outer = Thrown(() => new InvalidOperationException("outer-secret", inner));
        var r = ShellDiagnostics.ExceptionReport(outer);
        Assert.StartsWith("System.InvalidOperationException (HRESULT 0x80131509)", r);
        Assert.Contains("--- inner: System.Runtime.InteropServices.COMException (HRESULT 0x80040154)", r);
        Assert.DoesNotContain("secret", r);
    }

    [Fact]
    public void InnerChainIsBounded()
    {
        Exception e = new InvalidOperationException("x");
        for (var i = 0; i < 20; i++) e = new InvalidOperationException("x", e);
        var r = ShellDiagnostics.ExceptionReport(e);
        var count = r.Split("--- inner:").Length - 1;
        Assert.Equal(ShellDiagnostics.MaxInnerExceptions, count);
    }

    [Fact]
    public void NoStackTraceIsFine()
        => Assert.Equal("System.TimeoutException (HRESULT 0x80131505)", ShellDiagnostics.ExceptionReport(new TimeoutException("m")));
}

public class OwnTokenTextTests
{
    [Fact]
    public void ReadableTokenSaysYesOrNo()
    {
        Assert.Equal("yes", ShellDiagnostics.OwnTokenText(true, 0));
        Assert.Equal("no", ShellDiagnostics.OwnTokenText(false, 0));
    }

    [Fact]
    public void UnreadableTokenNamesTheWin32Code()
        // the 2026-11-05 trail only said "unknown": the shell could not open its own token
        => Assert.Equal("unknown (own token not readable, Win32 5)", ShellDiagnostics.OwnTokenText(null, 5));
}

public class ShellTokenSecurityTests
{
    [Fact]
    public void TokenObjectGrantsSystemAdminsAndTheUserOnly()
        => Assert.Equal("D:(A;;GA;;;SY)(A;;GA;;;BA)(A;;GA;;;S-1-5-21-1-2-3-1001)",
            ShellTokenSecurity.TokenObjectSddl("S-1-5-21-1-2-3-1001"));

    [Fact]
    public void TokenObjectSddlHasNoDenyAndNoOwnerRightsEntries()
    {
        // the removed protection used deny ACEs and an empty OWNER RIGHTS ACE; none of that may come back
        var sddl = ShellTokenSecurity.TokenObjectSddl("S-1-5-21-1-2-3-1001");
        Assert.DoesNotContain("(D;", sddl);
        Assert.DoesNotContain(";OW)", sddl);
        Assert.DoesNotContain("S-1-3-4", sddl);
    }

    [Theory]
    [InlineData("")]
    [InlineData("  ")]
    [InlineData("S-1-5-21-1)(A;;GA;;;WD")] // SDDL injection
    [InlineData("WD")]
    [InlineData("S-1-5-x")]
    public void AnythingButAPlainSidIsRejected(string sid)
        => Assert.Throws<ArgumentException>(() => ShellTokenSecurity.TokenObjectSddl(sid));
}
