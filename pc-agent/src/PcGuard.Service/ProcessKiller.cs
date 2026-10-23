using System.Collections.Concurrent;
using System.ComponentModel;
using System.Diagnostics;

namespace PcGuard.Service;

/// <summary>
/// Terminates violators off the guard loop: CloseMainWindow() when the process has a main window
/// handle, then Kill(entireProcessTree) after 3 s if it is still running; without a window it is
/// killed at once. NOTE (session 0): the service cannot see windows of the user's desktop, so
/// MainWindowHandle is expected to be 0 for user processes and the graceful step will usually be
/// skipped (to be confirmed on the Windows VM). Exceptions for exited or access-denied processes are
/// swallowed and logged at debug.
/// </summary>
internal sealed class ProcessKiller
{
    private static readonly TimeSpan Grace = TimeSpan.FromSeconds(3);

    private readonly ILogger _log;
    private readonly ConcurrentDictionary<int, byte> _pending = new();

    public ProcessKiller(ILogger log) => _log = log;

    /// <param name="expectedImagePath">Image path seen at planning time, to avoid killing a reused pid; null skips the check.</param>
    public void Schedule(int pid, string? expectedImagePath, CancellationToken stopping)
    {
        if (pid == Environment.ProcessId || !_pending.TryAdd(pid, 0)) return;
        _ = Task.Run(async () =>
        {
            try
            {
                await TerminateAsync(pid, expectedImagePath, stopping).ConfigureAwait(false);
            }
            catch (Exception e) when (e is ArgumentException or InvalidOperationException or Win32Exception
                                          or NotSupportedException or OperationCanceledException)
            {
                _log.LogDebug("Could not terminate pid {Pid}: {Error}", pid, e.GetType().Name);
            }
            finally
            {
                _pending.TryRemove(pid, out _);
            }
        }, CancellationToken.None);
    }

    private async Task TerminateAsync(int pid, string? expectedImagePath, CancellationToken stopping)
    {
        using var p = Process.GetProcessById(pid);
        _ = p.Handle; // pin the process object to this exact process from here on
        if (expectedImagePath is not null
            && !string.Equals(Native.TryGetImagePath(pid), expectedImagePath, StringComparison.OrdinalIgnoreCase))
            return; // pid was reused

        var asked = p.MainWindowHandle != IntPtr.Zero && p.CloseMainWindow();
        if (asked)
        {
            using var cts = CancellationTokenSource.CreateLinkedTokenSource(stopping);
            cts.CancelAfter(Grace);
            try { await p.WaitForExitAsync(cts.Token).ConfigureAwait(false); }
            catch (OperationCanceledException) { /* grace over */ }
        }
        if (!p.HasExited)
        {
            p.Kill(entireProcessTree: true);
            _log.LogInformation("Terminated {Exe} (pid {Pid})", Path.GetFileName(expectedImagePath) ?? "process", pid);
        }
    }
}
