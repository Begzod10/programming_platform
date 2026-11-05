using System.Globalization;

namespace PcGuard.Core;

/// <summary>Outcome of creating the shell's named single-instance mutex.</summary>
public enum MutexOpenResult { CreatedNew, AlreadyExists, AccessDenied, Failed }

/// <summary>What the shell does after the single-instance check.</summary>
public enum SingleInstanceAction
{
    /// <summary>This process created the name: it is the instance.</summary>
    RunAsPrimary,
    /// <summary>Another genuine shell of this install runs in this session: exit cleanly (code 0).</summary>
    ExitDuplicate,
    /// <summary>The name exists (or could not be created) but no other genuine shell runs: the name is
    /// squatted or stale. Run anyway: a name must never be able to suppress the lock screen.</summary>
    RunWithoutLock,
}

/// <summary>
/// Single-instance rules of the shell. The mutex <c>Local\PcGuard.Shell.SingleInstance</c> is created
/// with DEFAULT security: since 2026-11-05 the service launches the shell with the console user's
/// ordinary token, whose default DACL grants the user full control of the objects it creates, so a
/// default-security named mutex works for the built-in Administrator, a UAC administrator (split token)
/// and a standard user alike. (Background, real-PC bug: the service used to give the shell token a
/// restricted default DACL; every named object the shell or Windows text input (TSF) created then got
/// ACCESS_DENIED. That customization was removed, see <see cref="ShellTokenSecurity"/>.) ACCESS_DENIED
/// or any other failure is still treated as "the name exists": the shell exits only when another
/// genuine shell runs, otherwise it runs without the lock (a squatted name never stops the lock screen).
/// </summary>
public static class SingleInstancePolicy
{
    public const int ErrorAccessDenied = 5;
    public const int ErrorAlreadyExists = 183;

    /// <summary>Classifies CreateMutexEx: whether it returned a handle and GetLastError.</summary>
    public static MutexOpenResult Classify(bool handleValid, int win32Error)
    {
        if (handleValid) return win32Error == ErrorAlreadyExists ? MutexOpenResult.AlreadyExists : MutexOpenResult.CreatedNew;
        return win32Error == ErrorAccessDenied ? MutexOpenResult.AccessDenied : MutexOpenResult.Failed;
    }

    /// <param name="anotherShellRunning">Another process with this install's shell image runs in this
    /// session (only consulted when the name was not created new).</param>
    public static SingleInstanceAction Decide(MutexOpenResult result, bool anotherShellRunning)
    {
        if (result == MutexOpenResult.CreatedNew) return SingleInstanceAction.RunAsPrimary;
        return anotherShellRunning ? SingleInstanceAction.ExitDuplicate : SingleInstanceAction.RunWithoutLock;
    }
}

/// <summary>
/// Startup failure rules of the shell: an exception before the shell is fully initialised (windows
/// shown, pipe client started) must END the process with a non-zero code, never leave a windowless
/// process the service later kills as unresponsive (ShutdownMode is OnExplicitShutdown, so a shell
/// without windows never exits by itself). After startup, unhandled UI exceptions are logged and the
/// shell keeps running (a shell that exits on a glitch would unlock the PC until it is relaunched).
/// </summary>
public static class StartupFailurePolicy
{
    public const int DuplicateExitCode = 0;
    public const int StartupFailedExitCode = 3;
    public const int WatchdogExitCode = 4;

    /// <summary>Startup must complete within this time (shorter than the service's hung timeout, so
    /// the shell ends itself with a logged reason before the service has to kill it).</summary>
    public static readonly TimeSpan WatchdogTimeout = TimeSpan.FromSeconds(20);

    public static bool ShouldTerminate(bool startupComplete) => !startupComplete;
}

/// <summary>
/// Service-side back-off for relaunching a shell that keeps failing to connect (killed as unresponsive,
/// or exited without ever sending a snapshot/alive frame). Delays after N consecutive failures:
/// 15, 30, 60, 120 s, then 300 s. The delay counts from the failure. A connection resets it. Enforcement
/// is not affected (the guard stays in name-only fallback while no shell reports). Pure; one instance
/// per service, used from the guard loop only.
/// </summary>
public sealed class ShellRelaunchBackoff
{
    private static readonly int[] StepSeconds = { 15, 30, 60, 120, 300 };
    public static readonly TimeSpan MaxDelay = TimeSpan.FromSeconds(300);
    public const int WarnAfter = 2;

    private enum Outcome { None, Pending, Connected, Failed }

    private DateTimeOffset? _start;
    private Outcome _outcome = Outcome.None;
    private DateTimeOffset? _notBefore;
    private bool _warned;
    private bool _warningPending;

    public int ConsecutiveFailures { get; private set; }

    /// <summary>Delay after <paramref name="failures"/> consecutive failures (0 = none).</summary>
    public static TimeSpan Delay(int failures)
        => failures <= 0 ? TimeSpan.Zero : TimeSpan.FromSeconds(StepSeconds[Math.Min(failures, StepSeconds.Length) - 1]);

    /// <summary>A shell process was created (launched and resumed) at <paramref name="now"/>.</summary>
    public void Started(DateTimeOffset now)
    {
        _start = now;
        _outcome = Outcome.Pending;
    }

    /// <summary>Latest snapshot/alive time from a verified shell; one at/after the start means it connected.</summary>
    public void ObserveLiveness(DateTimeOffset? liveness)
    {
        if (_outcome != Outcome.Pending || _start is not { } s || liveness is not { } l || l < s) return;
        _outcome = Outcome.Connected;
        ConsecutiveFailures = 0;
        _notBefore = null;
        _warned = false;
        _warningPending = false;
    }

    /// <summary>The service killed the shell as unresponsive. True when the one-time warning is due now.</summary>
    public bool KilledUnresponsive(DateTimeOffset now)
    {
        if (_outcome == Outcome.Failed) return false;
        RecordFailure(now);
        return TakeWarning();
    }

    /// <summary>
    /// Asked when a launch is about to happen (the shell process is not running). A start still pending
    /// means the shell exited without connecting: counted once as a failure. False while backing off.
    /// </summary>
    public bool MayLaunch(DateTimeOffset now)
    {
        if (_outcome == Outcome.Pending) RecordFailure(now);
        if (_notBefore is not { } nb) return true;
        if (now >= nb) return true;
        return nb - now > MaxDelay; // the clock moved back: never block for longer than the maximum
    }

    /// <summary>True once per back-off episode, when the failure count reaches <see cref="WarnAfter"/>.</summary>
    public bool TakeWarning()
    {
        var w = _warningPending;
        _warningPending = false;
        return w;
    }

    /// <summary>Console session changed or nobody is signed in: start over.</summary>
    public void Reset()
    {
        _start = null;
        _outcome = Outcome.None;
        _notBefore = null;
        _warned = false;
        _warningPending = false;
        ConsecutiveFailures = 0;
    }

    private void RecordFailure(DateTimeOffset now)
    {
        _outcome = Outcome.Failed;
        ConsecutiveFailures++;
        _notBefore = now + Delay(ConsecutiveFailures);
        if (ConsecutiveFailures >= WarnAfter && !_warned)
        {
            _warned = true;
            _warningPending = true;
        }
    }
}

/// <summary>Why the pipe server rejects a client on the pin (pid + creation time) check.</summary>
public enum PinCheck { Match, NoPin, PidMismatch, CreationTimeUnreadable, CreationTimeMismatch }

public static class PinCheckRules
{
    public static PinCheck Classify(bool pinSet, int pinnedPid, long pinnedCreatedAt, int pid, long? createdAt)
    {
        if (!pinSet) return PinCheck.NoPin;
        if (pid != pinnedPid) return PinCheck.PidMismatch;
        if (createdAt is not { } c) return PinCheck.CreationTimeUnreadable;
        return c == pinnedCreatedAt ? PinCheck.Match : PinCheck.CreationTimeMismatch;
    }
}

/// <summary>
/// Fixed one-line diagnostics of the shell startup trail (shell.log) and of the service's pipe
/// rejections and relaunch back-off (event log). PRIVACY: only pids, session ids, enum names, exception
/// TYPE names and Win32 codes; never user names, passwords, URLs, window titles or exception messages.
/// </summary>
public static partial class ShellDiagnostics
{
    public const string ShellLogHint = @"%LocalAppData%\PcGuard\shell.log of the signed-in user (C:\Users\<name>\AppData\Local\PcGuard\shell.log)";

    /// <summary>Win32 error code inside a FACILITY_WIN32 HRESULT (0x8007xxxx); other values unchanged.</summary>
    public static int Win32FromHResult(int hresult)
        => (hresult & unchecked((int)0xFFFF0000)) == unchecked((int)0x80070000) ? hresult & 0xFFFF : hresult;

    /// <summary>Connect failures are logged for the first 10 attempts, then every 30th.</summary>
    public static bool ShouldLogConnectAttempt(int attempt) => attempt <= 10 || attempt % 30 == 0;

    public static string Step(string step) => "Startup: " + step;

    public static string SingleInstanceLine(MutexOpenResult result, int win32, SingleInstanceAction action)
        => string.Create(CultureInfo.InvariantCulture, $"Startup: single-instance mutex {result} (Win32 {win32}): {action}");

    public static string StartupFailedLine(string exceptionType, int exitCode)
        => string.Create(CultureInfo.InvariantCulture, $"Startup failed ({exceptionType}): exiting with code {exitCode}");

    public static string WatchdogLine(TimeSpan timeout, int exitCode)
        => string.Create(CultureInfo.InvariantCulture, $"Startup did not complete within {(int)timeout.TotalSeconds} s: exiting with code {exitCode}");

    public static string ConnectFailedLine(int attempt, string exceptionType, int win32)
        => string.Create(CultureInfo.InvariantCulture, $"Pipe: connect attempt {attempt} failed: {exceptionType} (Win32 {win32})");

    public static string ConnectedLine(int attempt, string serverTrust)
        => string.Create(CultureInfo.InvariantCulture, $"Pipe: connected on attempt {attempt} (server {serverTrust})");

    public static string ClosedByServiceLine(TimeSpan after, int attempt)
        => string.Create(CultureInfo.InvariantCulture,
            $"Pipe: the service closed the connection after {after.TotalSeconds:0.0} s (attempt {attempt}): it probably rejected this shell, see the PC Guard event log");

    public static string PinRejectLine(PinCheck check, int pid, int pinnedPid) => check switch
    {
        PinCheck.NoPin => string.Create(CultureInfo.InvariantCulture, $"Rejected pipe client pid {pid}: no shell launched by this service yet (no pin)"),
        PinCheck.PidMismatch => string.Create(CultureInfo.InvariantCulture, $"Rejected pipe client pid {pid}: not the shell instance this service launched (pinned pid {pinnedPid})"),
        PinCheck.CreationTimeUnreadable => string.Create(CultureInfo.InvariantCulture, $"Rejected pipe client pid {pid}: its process creation time could not be read"),
        PinCheck.CreationTimeMismatch => string.Create(CultureInfo.InvariantCulture, $"Rejected pipe client pid {pid}: creation time differs from the pinned instance (pid reuse)"),
        _ => string.Create(CultureInfo.InvariantCulture, $"Pipe client pid {pid} matches the pin"),
    };

    public static string SessionRejectLine(int pid, uint? clientSession, uint? consoleSession)
        => string.Create(CultureInfo.InvariantCulture,
            $"Rejected pipe client pid {pid}: in session {(clientSession is { } c ? c.ToString(CultureInfo.InvariantCulture) : "unknown")}, the active console session is {(consoleSession is { } k ? k.ToString(CultureInfo.InvariantCulture) : "none")}");

    public static string BackoffWarning(int failures, TimeSpan nextDelay)
        => string.Create(CultureInfo.InvariantCulture,
            $"The shell started {failures} times in a row without connecting to the service (killed as unresponsive or exited); relaunching with back-off, next attempt in {(int)nextDelay.TotalSeconds} s (at most every {(int)ShellRelaunchBackoff.MaxDelay.TotalMinutes} min). Enforcement stays name-only meanwhile. Look at {ShellLogHint} for the startup trail.");

    public static string BackoffInfo(int failures, TimeSpan delay)
        => string.Create(CultureInfo.InvariantCulture, $"Shell relaunch delayed {(int)delay.TotalSeconds} s after {failures} failed start(s)");
}
