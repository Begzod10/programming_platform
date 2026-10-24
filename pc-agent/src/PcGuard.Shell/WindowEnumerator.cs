using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>One visible application window. Title text is never read (only whether it is non-empty).</summary>
internal readonly record struct AppWindow(long Hwnd, int Pid, string Exe, bool BrowserEligible);

/// <summary>Enumerates visible top-level application windows via EnumWindows. WINDOWS ONLY.</summary>
internal static class WindowEnumerator
{
    public const string UnknownExe = "?";

    public static List<AppWindow> Enumerate()
    {
        var result = new List<AppWindow>();
        var exeCache = new Dictionary<uint, string>();
        var self = (uint)Environment.ProcessId;

        Native.EnumWindows((hwnd, _) =>
        {
            try
            {
                if (!Native.IsWindowVisible(hwnd)) return true;
                if (Native.GetWindowThreadProcessId(hwnd, out var pid) == 0 || pid == 0 || pid == self) return true;
                if (!Native.GetWindowRect(hwnd, out var r)) return true;
                var ex = Native.GetExStyle(hwnd);
                var counts = WindowFilter.CountsAsAppWindow(
                    visible: true,
                    cloaked: Native.IsCloaked(hwnd),
                    width: r.Right - r.Left,
                    height: r.Bottom - r.Top,
                    toolWindow: (ex & Native.WS_EX_TOOLWINDOW) != 0,
                    appWindowStyle: (ex & Native.WS_EX_APPWINDOW) != 0);
                if (!counts) return true;

                // UWP: the frame belongs to ApplicationFrameHost; the real app owns a CoreWindow child.
                IReadOnlyList<int> pids = new[] { (int)pid };
                if (Native.ClassName(hwnd) == "ApplicationFrameWindow")
                    pids = UwpPidPicker.Pick((int)pid, CoreWindowPids(hwnd));

                var eligible = BrowserWindowEligibility.IsEligible(
                    hasOwner: Native.GetWindow(hwnd, Native.GW_OWNER) != IntPtr.Zero,
                    toolWindow: (ex & Native.WS_EX_TOOLWINDOW) != 0,
                    width: r.Right - r.Left, height: r.Bottom - r.Top);

                foreach (var p in pids)
                {
                    if (p == (int)self) continue;
                    if (!exeCache.TryGetValue((uint)p, out var exe))
                    {
                        // Unknown (protected/elevated) images are still reported: the service needs the pid
                        // to treat the process as windowed; it ignores the name for that purpose.
                        exe = Native.TryGetExeName((uint)p) ?? UnknownExe;
                        exeCache[(uint)p] = exe;
                    }
                    result.Add(new AppWindow(hwnd.ToInt64(), p, exe, eligible));
                }
            }
            catch (Exception e)
            {
                ShellLog.Error("EnumWindows callback", e);
            }
            return true;
        }, IntPtr.Zero);

        return result;
    }

    private static List<int> CoreWindowPids(IntPtr frame)
    {
        var pids = new List<int>();
        Native.EnumChildWindows(frame, (child, _) =>
        {
            if (Native.ClassName(child) == "Windows.UI.Core.CoreWindow"
                && Native.GetWindowThreadProcessId(child, out var cp) != 0 && cp != 0)
                pids.Add((int)cp);
            return true;
        }, IntPtr.Zero);
        return pids;
    }

    /// <summary>Lower-case exe name of the foreground window's process, or null (also for the shell itself).</summary>
    public static string? ForegroundExe()
    {
        var fg = Native.GetForegroundWindow();
        if (fg == IntPtr.Zero) return null;
        if (Native.GetWindowThreadProcessId(fg, out var pid) == 0 || pid == 0 || pid == (uint)Environment.ProcessId) return null;
        return Native.TryGetExeName(pid)?.ToLowerInvariant();
    }

    /// <summary>
    /// Re-check for close_window: the handle must still be a visible TOP-LEVEL window owned by a
    /// browser process. Anything else is refused.
    /// </summary>
    public static bool IsVisibleBrowserTopLevel(long hwndValue)
    {
        var hwnd = new IntPtr(hwndValue);
        if (!Native.IsWindow(hwnd) || !Native.IsWindowVisible(hwnd)) return false;
        if (Native.GetAncestor(hwnd, Native.GA_ROOT) != hwnd) return false;
        if (!BrowserWindowEligibility.IsEligible(
                hasOwner: Native.GetWindow(hwnd, Native.GW_OWNER) != IntPtr.Zero,
                toolWindow: (Native.GetExStyle(hwnd) & Native.WS_EX_TOOLWINDOW) != 0,
                width: 1, height: 1)) // size already checked when the window was reported
            return false;
        if (Native.GetWindowThreadProcessId(hwnd, out var pid) == 0 || pid == 0 || pid == (uint)Environment.ProcessId) return false;
        return BrowserHostRule.IsBrowser(Native.TryGetExeName(pid));
    }

    public static void Close(long hwndValue)
    {
        if (!IsVisibleBrowserTopLevel(hwndValue)) return;
        Native.PostMessageW(new IntPtr(hwndValue), Native.WM_CLOSE, IntPtr.Zero, IntPtr.Zero);
    }
}
