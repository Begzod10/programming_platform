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
        var action = ShellLaunchPolicy.Decide(now, shellMissingSince, _lastLaunchAt,
            consoleSession is not null, runningShellPids.Count > 0, lastSnapshotAt, lastAliveAt);
        switch (action)
        {
            case ShellAction.Launch:
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
                        (p, createdAt) => _pin.Set(p, createdAt), _log);
                    _log.LogInformation("Launched shell (pid {Pid}) in session {Session}", pid, consoleSession);
                }
                catch (Win32Exception e) when (e.NativeErrorCode == 1008)
                {
                    // ERROR_NO_TOKEN: nobody signed in on the console yet / secure desktop (logon, UAC). Normal; try later.
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
                break;
        }
    }
}
