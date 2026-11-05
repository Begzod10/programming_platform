using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class SingleInstancePolicyTests
{
    [Theory]
    [InlineData(true, 0, MutexOpenResult.CreatedNew)]
    [InlineData(true, 183, MutexOpenResult.AlreadyExists)] // ERROR_ALREADY_EXISTS
    [InlineData(false, 5, MutexOpenResult.AccessDenied)]   // ERROR_ACCESS_DENIED (the real-PC bug)
    [InlineData(false, 6, MutexOpenResult.Failed)]
    [InlineData(false, 0, MutexOpenResult.Failed)]
    public void ClassifiesTheCreateMutexOutcome(bool handleValid, int win32, MutexOpenResult expected)
        => Assert.Equal(expected, SingleInstancePolicy.Classify(handleValid, win32));

    [Fact]
    public void CreatedNewRunsAsThePrimaryInstance()
    {
        Assert.Equal(SingleInstanceAction.RunAsPrimary, SingleInstancePolicy.Decide(MutexOpenResult.CreatedNew, anotherShellRunning: false));
        Assert.Equal(SingleInstanceAction.RunAsPrimary, SingleInstancePolicy.Decide(MutexOpenResult.CreatedNew, anotherShellRunning: true));
    }

    [Theory]
    [InlineData(MutexOpenResult.AlreadyExists)]
    [InlineData(MutexOpenResult.AccessDenied)]
    [InlineData(MutexOpenResult.Failed)]
    public void ExistingNameWithAGenuineShellRunningExitsCleanly(MutexOpenResult r)
        => Assert.Equal(SingleInstanceAction.ExitDuplicate, SingleInstancePolicy.Decide(r, anotherShellRunning: true));

    [Theory]
    [InlineData(MutexOpenResult.AlreadyExists)]
    [InlineData(MutexOpenResult.AccessDenied)]
    [InlineData(MutexOpenResult.Failed)]
    public void SquattedOrStaleNameWithoutAnotherShellStillRuns(MutexOpenResult r)
        // a name held by something that is not a running genuine shell must never stop the lock screen
        => Assert.Equal(SingleInstanceAction.RunWithoutLock, SingleInstancePolicy.Decide(r, anotherShellRunning: false));

    [Fact]
    public void MutexSddlGrantsTheUserAndSystemFullMutexAccess()
    {
        var sddl = SingleInstancePolicy.MutexSddl("S-1-5-21-1-2-3-1001");
        Assert.Equal("D:(A;;0x1F0001;;;S-1-5-21-1-2-3-1001)(A;;0x1F0001;;;SY)", sddl);
        Assert.Throws<ArgumentException>(() => SingleInstancePolicy.MutexSddl(" "));
    }

    [Fact]
    public void TheTokenDefaultDaclCannotServeANamedMutex()
    {
        // the root cause: the restricted default DACL grants the user no MUTEX_MODIFY_STATE (0x0001,
        // the same bit as PROCESS/THREAD_TERMINATE), so a named mutex created without an explicit SD is
        // unusable for a standard user or a UAC-filtered administrator
        Assert.Equal(0u, ShellSecurity.UserAllowedRights & 0x0001u);
        Assert.Contains("(A;;0x121400;;;S-1-5-21-1-2-3-1001)", ShellSecurity.DefaultDaclSddl("S-1-5-21-1-2-3-1001"));
        Assert.Contains("0x1F0001;;;S-1-5-21-1-2-3-1001", SingleInstancePolicy.MutexSddl("S-1-5-21-1-2-3-1001"));
    }
}

public class StartupFailurePolicyTests
{
    [Fact]
    public void AnUnhandledExceptionBeforeStartupCompletedTerminates()
        => Assert.True(StartupFailurePolicy.ShouldTerminate(startupComplete: false));

    [Fact]
    public void AnUnhandledExceptionAfterStartupKeepsTheShellRunning()
        => Assert.False(StartupFailurePolicy.ShouldTerminate(startupComplete: true));

    [Fact]
    public void ExitCodesAreDistinctAndOnlyTheDuplicateIsZero()
    {
        Assert.Equal(0, StartupFailurePolicy.DuplicateExitCode);
        Assert.NotEqual(0, StartupFailurePolicy.StartupFailedExitCode);
        Assert.NotEqual(0, StartupFailurePolicy.WatchdogExitCode);
        Assert.NotEqual(StartupFailurePolicy.StartupFailedExitCode, StartupFailurePolicy.WatchdogExitCode);
    }

    [Fact]
    public void WatchdogFiresBeforeTheServiceDeclaresTheShellHung()
    {
        Assert.True(StartupFailurePolicy.WatchdogTimeout > TimeSpan.FromSeconds(5));
        Assert.True(StartupFailurePolicy.WatchdogTimeout < ShellLaunchPolicy.HungAfter);
    }
}

public class ShellRelaunchBackoffTests
{
    private static readonly DateTimeOffset T0 = new(2026, 11, 5, 10, 0, 0, TimeSpan.Zero);

    [Theory]
    [InlineData(1, 15)]
    [InlineData(2, 30)]
    [InlineData(3, 60)]
    [InlineData(4, 120)]
    [InlineData(5, 300)]
    [InlineData(6, 300)]
    [InlineData(100, 300)]
    public void DelayDoublesFrom15SecondsUpTo5Minutes(int failures, int seconds)
        => Assert.Equal(TimeSpan.FromSeconds(seconds), ShellRelaunchBackoff.Delay(failures));

    [Fact]
    public void NoFailureNoDelay()
    {
        var b = new ShellRelaunchBackoff();
        Assert.Equal(TimeSpan.Zero, ShellRelaunchBackoff.Delay(0));
        Assert.True(b.MayLaunch(T0));
        Assert.Equal(0, b.ConsecutiveFailures);
    }

    [Fact]
    public void KilledUnresponsiveShellDelaysTheNextLaunch()
    {
        var b = new ShellRelaunchBackoff();
        b.Started(T0);
        b.ObserveLiveness(null);
        var kill = T0.AddSeconds(32);
        b.KilledUnresponsive(kill);
        Assert.Equal(1, b.ConsecutiveFailures);
        Assert.False(b.MayLaunch(kill.AddSeconds(14)));
        Assert.True(b.MayLaunch(kill.AddSeconds(15)));
    }

    [Fact]
    public void RepeatedFailuresBackOffAndWarnExactlyOnce()
    {
        var b = new ShellRelaunchBackoff();
        var now = T0;
        var warnings = 0;
        var expected = new[] { 15, 30, 60, 120, 300, 300, 300 };
        foreach (var seconds in expected)
        {
            b.Started(now);
            now = now.AddSeconds(32);
            if (b.KilledUnresponsive(now)) warnings++;
            Assert.False(b.MayLaunch(now.AddSeconds(seconds - 1)));
            Assert.True(b.MayLaunch(now.AddSeconds(seconds)));
            now = now.AddSeconds(seconds);
        }
        Assert.Equal(1, warnings);
        Assert.Equal(expected.Length, b.ConsecutiveFailures);
    }

    [Fact]
    public void TheWarningComesAtTheSecondConsecutiveFailure()
    {
        var b = new ShellRelaunchBackoff();
        b.Started(T0);
        Assert.False(b.KilledUnresponsive(T0.AddSeconds(32)));
        b.Started(T0.AddSeconds(50));
        Assert.True(b.KilledUnresponsive(T0.AddSeconds(82)));
    }

    [Fact]
    public void AShellThatExitedWithoutConnectingCountsOnceAsAFailure()
    {
        var b = new ShellRelaunchBackoff();
        b.Started(T0);
        // the process is gone (crashed, or exited after a startup failure); the next launch decision sees it
        Assert.False(b.MayLaunch(T0.AddSeconds(20)));
        Assert.Equal(1, b.ConsecutiveFailures);
        Assert.False(b.MayLaunch(T0.AddSeconds(21))); // not counted twice
        Assert.Equal(1, b.ConsecutiveFailures);
        Assert.True(b.MayLaunch(T0.AddSeconds(35)));
    }

    [Fact]
    public void KilledAfterExitDetectionIsNotCountedTwice()
    {
        var b = new ShellRelaunchBackoff();
        b.Started(T0);
        b.KilledUnresponsive(T0.AddSeconds(32));
        b.KilledUnresponsive(T0.AddSeconds(33));
        Assert.False(b.MayLaunch(T0.AddSeconds(34)));
        Assert.Equal(1, b.ConsecutiveFailures);
    }

    [Fact]
    public void ConnectingResetsTheBackoffAndTheWarning()
    {
        var b = new ShellRelaunchBackoff();
        b.Started(T0);
        b.KilledUnresponsive(T0.AddSeconds(32));
        b.Started(T0.AddSeconds(50));
        Assert.True(b.KilledUnresponsive(T0.AddSeconds(82)));

        var start = T0.AddSeconds(200);
        b.Started(start);
        b.ObserveLiveness(start.AddSeconds(3)); // snapshot or alive frame after this start: it connected
        Assert.Equal(0, b.ConsecutiveFailures);
        Assert.True(b.MayLaunch(start.AddSeconds(4)));

        // a later episode warns again
        b.Started(start.AddSeconds(100));
        Assert.False(b.KilledUnresponsive(start.AddSeconds(132)));
        b.Started(start.AddSeconds(200));
        Assert.True(b.KilledUnresponsive(start.AddSeconds(232)));
    }

    [Fact]
    public void LivenessFromBeforeTheStartDoesNotCountAsConnected()
    {
        var b = new ShellRelaunchBackoff();
        b.Started(T0);
        b.ObserveLiveness(T0.AddSeconds(-5)); // the previous shell's last snapshot
        b.KilledUnresponsive(T0.AddSeconds(32));
        Assert.Equal(1, b.ConsecutiveFailures);
    }

    [Fact]
    public void AConnectedShellThatLaterHangsCountsAsOneFailure()
    {
        var b = new ShellRelaunchBackoff();
        b.Started(T0);
        b.ObserveLiveness(T0.AddSeconds(2));
        Assert.False(b.KilledUnresponsive(T0.AddSeconds(300)));
        Assert.Equal(1, b.ConsecutiveFailures);
        Assert.False(b.MayLaunch(T0.AddSeconds(310)));
        Assert.True(b.MayLaunch(T0.AddSeconds(315)));
    }

    [Fact]
    public void ResetClearsEverything()
    {
        var b = new ShellRelaunchBackoff();
        b.Started(T0);
        b.KilledUnresponsive(T0.AddSeconds(32));
        b.Reset(); // console session changed / nobody signed in
        Assert.Equal(0, b.ConsecutiveFailures);
        Assert.True(b.MayLaunch(T0.AddSeconds(33)));
    }

    [Fact]
    public void AClockMovedBackDoesNotBlockLaunchingForLong()
    {
        var b = new ShellRelaunchBackoff();
        for (var i = 0; i < 5; i++) { b.Started(T0); b.KilledUnresponsive(T0); }
        Assert.False(b.MayLaunch(T0.AddSeconds(10)));
        Assert.True(b.MayLaunch(T0.AddHours(-2))); // the not-before is more than the maximum delay away
    }
}

public class PinCheckTests
{
    [Fact]
    public void ClassifiesEveryRejectReason()
    {
        Assert.Equal(PinCheck.Match, PinCheckRules.Classify(true, 10, 500, 10, 500));
        Assert.Equal(PinCheck.NoPin, PinCheckRules.Classify(false, 0, 0, 10, 500));
        Assert.Equal(PinCheck.PidMismatch, PinCheckRules.Classify(true, 11, 500, 10, 500));
        Assert.Equal(PinCheck.CreationTimeUnreadable, PinCheckRules.Classify(true, 10, 500, 10, null));
        Assert.Equal(PinCheck.CreationTimeMismatch, PinCheckRules.Classify(true, 10, 500, 10, 501));
    }
}

public class ShellDiagnosticsTests
{
    [Theory]
    [InlineData(unchecked((int)0x80070005), 5)]
    [InlineData(unchecked((int)0x800700E7), 231)] // ERROR_PIPE_BUSY
    [InlineData(2, 2)]
    [InlineData(unchecked((int)0x80131500), unchecked((int)0x80131500))] // not a Win32 HRESULT: kept
    public void Win32CodeFromHResult(int hr, int expected)
        => Assert.Equal(expected, ShellDiagnostics.Win32FromHResult(hr));

    [Theory]
    [InlineData(1, true)]
    [InlineData(10, true)]
    [InlineData(11, false)]
    [InlineData(29, false)]
    [InlineData(30, true)]
    [InlineData(60, true)]
    public void ConnectAttemptsAreLoggedFirstTenThenEveryThirtieth(int attempt, bool logged)
        => Assert.Equal(logged, ShellDiagnostics.ShouldLogConnectAttempt(attempt));

    [Fact]
    public void LineFormats()
    {
        Assert.Equal("Startup: single-instance mutex AccessDenied (Win32 5): RunWithoutLock",
            ShellDiagnostics.SingleInstanceLine(MutexOpenResult.AccessDenied, 5, SingleInstanceAction.RunWithoutLock));
        Assert.Equal("Startup: windows created", ShellDiagnostics.Step("windows created"));
        Assert.Equal("Pipe: connect attempt 3 failed: System.TimeoutException (Win32 0)",
            ShellDiagnostics.ConnectFailedLine(3, "System.TimeoutException", 0));
        Assert.Equal("Pipe: connected on attempt 2 (server Verified)", ShellDiagnostics.ConnectedLine(2, "Verified"));
        Assert.Equal("Pipe: the service closed the connection after 0.4 s (attempt 2): it probably rejected this shell, see the PC Guard event log",
            ShellDiagnostics.ClosedByServiceLine(TimeSpan.FromMilliseconds(400), 2));
        Assert.Equal("Startup failed (System.UnauthorizedAccessException): exiting with code 3",
            ShellDiagnostics.StartupFailedLine("System.UnauthorizedAccessException", 3));
        Assert.Equal("Startup did not complete within 20 s: exiting with code 4",
            ShellDiagnostics.WatchdogLine(TimeSpan.FromSeconds(20), 4));
        Assert.Equal("Shell relaunch delayed 60 s after 3 failed start(s)", ShellDiagnostics.BackoffInfo(3, TimeSpan.FromSeconds(60)));
    }

    [Fact]
    public void RejectLinesNameTheReasonWithoutSecrets()
    {
        Assert.Equal("Rejected pipe client pid 42: no shell launched by this service yet (no pin)",
            ShellDiagnostics.PinRejectLine(PinCheck.NoPin, 42, 0));
        Assert.Equal("Rejected pipe client pid 42: not the shell instance this service launched (pinned pid 41)",
            ShellDiagnostics.PinRejectLine(PinCheck.PidMismatch, 42, 41));
        Assert.Equal("Rejected pipe client pid 42: its process creation time could not be read",
            ShellDiagnostics.PinRejectLine(PinCheck.CreationTimeUnreadable, 42, 42));
        Assert.Equal("Rejected pipe client pid 42: creation time differs from the pinned instance (pid reuse)",
            ShellDiagnostics.PinRejectLine(PinCheck.CreationTimeMismatch, 42, 42));
        Assert.Equal("Rejected pipe client pid 42: in session 3, the active console session is 2",
            ShellDiagnostics.SessionRejectLine(42, 3, 2));
        Assert.Equal("Rejected pipe client pid 42: in session unknown, the active console session is none",
            ShellDiagnostics.SessionRejectLine(42, null, null));
    }

    [Fact]
    public void BackoffWarningNamesTheShellLogAndTheDelay()
    {
        var line = ShellDiagnostics.BackoffWarning(2, TimeSpan.FromSeconds(30));
        Assert.Contains("2 times in a row", line);
        Assert.Contains("30 s", line);
        Assert.Contains(@"%LocalAppData%\PcGuard\shell.log", line);
        Assert.Contains("name-only", line);
    }
}
