using System.ComponentModel;
using System.Diagnostics;
using PcGuard.Core;

namespace PcGuard.Service;

/// <summary>
/// Keeps the shell (PcGuard.Shell.exe, Task 12) running in the console user's session. The decision
/// is the pure <see cref="ShellLaunchPolicy"/>; this class only performs it. WINDOWS ONLY.
/// </summary>
internal sealed class ShellSupervisor
{
    private readonly string _shellPath;
    private readonly ShellPin _pin;
    private readonly ILogger _log;
    private DateTimeOffset? _lastLaunchAt;
    private readonly ShellRelaunchBackoff _backoff = new();
    private uint? _backoffSession;
    private int _loggedFailures;
    // every shell instance this service launched (pid + creation time), newest last; bounded
    private readonly object _launchedLock = new();
    private readonly List<(int Pid, long CreatedAt)> _launched = new();
    private const int MaxRemembered = 64;

    public ShellSupervisor(string shellPath, ShellPin pin, ILogger log)
    {
        _shellPath = shellPath;
        _pin = pin;
        _log = log;
    }

    /// <summary>Called from the guard loop.</summary>
    public void Supervise(DateTimeOffset now, DateTimeOffset? shellMissingSince, DateTimeOffset? lastSnapshotAt,
        DateTimeOffset? lastAliveAt, uint? consoleSession, IReadOnlyList<int> runningShellPids)
    {
        // a new console session (or nobody signed in) starts a fresh back-off episode
        if (consoleSession != _backoffSession)
        {
            _backoffSession = consoleSession;
            _backoff.Reset();
        }
        _backoff.ObserveLiveness(Latest(lastSnapshotAt, lastAliveAt));

        var action = ShellLaunchPolicy.Decide(now, shellMissingSince, _lastLaunchAt,
            consoleSession is not null, runningShellPids.Count > 0, lastSnapshotAt, lastAliveAt);
        switch (action)
        {
            case ShellAction.Launch:
                // back-off: a shell that keeps dying/hanging without ever connecting is relaunched after
                // 15, 30, 60, 120, then 300 s instead of every ~33 s forever (name-only enforcement meanwhile)
                var mayLaunch = _backoff.MayLaunch(now);
                LogBackoff(_backoff.TakeWarning());
                if (!mayLaunch) return;
                _lastLaunchAt = now; // also on failure: retry at most every 15 s
                if (!File.Exists(_shellPath))
                {
                    _log.LogError("Shell executable is missing at {Path}", _shellPath);
                    return;
                }
                try
                {
                    // launched SUSPENDED: pin the exact instance BEFORE it resumes and can connect,
                    // so the shell's first connect is never rejected by a not-yet-set pin.
                    var (pid, _) = Native.LaunchInSession(consoleSession!.Value, _shellPath,
                        (p, createdAt) =>
                        {
                            _pin.Set(p, createdAt);
                            Remember(p, createdAt);
                        }, _log);
                    _backoff.Started(now);
                    _log.LogInformation("Launched shell (pid {Pid}) in session {Session}", pid, consoleSession);
                }
                catch (Win32Exception e) when (e.NativeErrorCode == 1008)
                {
                    // ERROR_NO_TOKEN: nobody signed in on the console yet / secure desktop (logon, UAC). Normal; try later.
                    _backoff.Reset(); // the next sign-in gets its shell without a back-off delay
                    _log.LogDebug("Shell launch deferred in session {Session}: no interactive token yet", consoleSession);
                }
                catch (Win32Exception e)
                {
                    _log.LogWarning("Could not launch shell in session {Session}: {Code} {Message}", consoleSession, e.NativeErrorCode, e.Message);
                }
                break;

            case ShellAction.KillHung:
                foreach (var pid in runningShellPids)
                {
                    try
                    {
                        using var p = Process.GetProcessById(pid);
                        p.Kill(entireProcessTree: true);
                        _log.LogWarning("Killed unresponsive shell (pid {Pid})", pid);
                    }
                    catch (Exception e) when (e is ArgumentException or InvalidOperationException or Win32Exception)
                    {
                        _log.LogDebug("Could not kill shell pid {Pid}: {Error}", pid, e.GetType().Name);
                    }
                }
                LogBackoff(_backoff.KilledUnresponsive(now));
                break;
        }
    }

    // Information line for every new back-off delay, plus the one-time Warning (with the shell.log path).
    private void LogBackoff(bool warningDue)
    {
        if (warningDue)
            _log.LogWarning("{Message}", ShellDiagnostics.BackoffWarning(_backoff.ConsecutiveFailures, ShellRelaunchBackoff.Delay(_backoff.ConsecutiveFailures)));
        if (_backoff.ConsecutiveFailures > 0 && _backoff.ConsecutiveFailures != _loggedFailures)
            _log.LogInformation("{Message}", ShellDiagnostics.BackoffInfo(_backoff.ConsecutiveFailures, ShellRelaunchBackoff.Delay(_backoff.ConsecutiveFailures)));
        _loggedFailures = _backoff.ConsecutiveFailures;
    }

    private static DateTimeOffset? Latest(DateTimeOffset? a, DateTimeOffset? b)
        => a is null ? b : b is null ? a : (a > b ? a : b);

    private void Remember(int pid, long createdAt)
    {
        lock (_launchedLock)
        {
            _launched.Add((pid, createdAt));
            if (_launched.Count > MaxRemembered) _launched.RemoveAt(0);
        }
    }

    /// <summary>
    /// Recovery release: terminates every PcGuard.Shell.exe this service launched, in ALL sessions
    /// (a shell in a disconnected fast-user-switching session never gets "released"). A process is
    /// ours when it is one of the remembered pid + creation-time instances or its image is this
    /// install's PcGuard.Shell.exe (same path, or the same file on disk). Returns how many were
    /// terminated. Never throws.
    /// </summary>
    public int TerminateAll()
    {
        List<(int Pid, long CreatedAt)> launched;
        lock (_launchedLock) launched = new List<(int, long)>(_launched);

        var candidates = new HashSet<int>(launched.Select(l => l.Pid));
        try
        {
            foreach (var p in Process.GetProcessesByName(Path.GetFileNameWithoutExtension(_shellPath)))
            {
                using (p) candidates.Add(p.Id);
            }
        }
        catch (Exception e) when (e is InvalidOperationException or Win32Exception)
        {
            _log.LogWarning("Could not list shell processes ({Error})", e.GetType().Name);
        }

        var killed = 0;
        foreach (var pid in candidates)
        {
            if (pid == Environment.ProcessId) continue;
            var created = Native.TryGetProcessCreationTime(pid);
            var remembered = created is { } c && launched.Contains((pid, c));
            if (!remembered && !IsThisInstallsShell(pid)) continue;
            try
            {
                using var p = Process.GetProcessById(pid);
                // the pid may have been reused between the checks: compare the creation time again
                if (created is null || Native.TryGetProcessCreationTime(pid) != created) continue;
                p.Kill(entireProcessTree: false);
                killed++;
            }
            catch (Exception e) when (e is ArgumentException or InvalidOperationException or Win32Exception or NotSupportedException)
            {
                _log.LogDebug("Could not terminate shell pid {Pid}: {Error}", pid, e.GetType().Name);
            }
        }
        return killed;
    }

    private bool IsThisInstallsShell(int pid)
    {
        var image = Native.TryGetImagePath(pid);
        if (image is null) return false;
        try
        {
            if (string.Equals(Path.GetFullPath(image), Path.GetFullPath(_shellPath), StringComparison.OrdinalIgnoreCase)) return true;
        }
        catch (Exception e) when (e is ArgumentException or NotSupportedException or PathTooLongException)
        {
            return false;
        }
        return Native.SameFileIdentity(image, _shellPath);
    }
}
