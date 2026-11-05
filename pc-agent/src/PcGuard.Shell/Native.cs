using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32.SafeHandles;
using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>All Win32 P/Invoke of the shell in one place. WINDOWS ONLY.</summary>
internal static class Native
{
    public delegate bool EnumWindowsProc(IntPtr hwnd, IntPtr lParam);

    public const int GWL_EXSTYLE = -20;
    public const int WS_EX_TOOLWINDOW = 0x00000080;
    public const int WS_EX_APPWINDOW = 0x00040000;
    public const int WS_EX_NOACTIVATE = 0x08000000;
    public const uint WM_CLOSE = 0x0010;
    public const int DWMWA_CLOAKED = 14;
    public const uint GA_ROOT = 2;
    public const uint GW_OWNER = 4;
    public const uint PROCESS_QUERY_LIMITED_INFORMATION = 0x1000;

    public const int SM_XVIRTUALSCREEN = 76;
    public const int SM_YVIRTUALSCREEN = 77;
    public const int SM_CXVIRTUALSCREEN = 78;
    public const int SM_CYVIRTUALSCREEN = 79;

    public static readonly IntPtr HWND_TOPMOST = new(-1);
    public const uint SWP_NOSIZE = 0x0001;
    public const uint SWP_NOMOVE = 0x0002;
    public const uint SWP_NOACTIVATE = 0x0010;
    public const uint SWP_SHOWWINDOW = 0x0040;

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }

    [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr parent, EnumWindowsProc proc, IntPtr lParam);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetClassNameW(IntPtr hwnd, StringBuilder buf, int max);

    private const uint DESKTOP_SWITCHDESKTOP = 0x0100;
    private const int UOI_NAME = 2;
    [DllImport("user32.dll", SetLastError = true)] private static extern IntPtr OpenInputDesktop(uint flags, bool inherit, uint access);
    [DllImport("user32.dll")] private static extern bool CloseDesktop(IntPtr desktop);
    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool GetUserObjectInformationW(IntPtr obj, int index, StringBuilder buf, int length, out int needed);

    /// <summary>Name of the current input desktop ("Default", "Winlogon", ...) or null when it cannot be opened.</summary>
    public static string? TryGetInputDesktopName()
    {
        var h = OpenInputDesktop(0, false, DESKTOP_SWITCHDESKTOP);
        if (h == IntPtr.Zero) return null;
        try
        {
            var sb = new StringBuilder(256);
            return GetUserObjectInformationW(h, UOI_NAME, sb, sb.Capacity * 2, out _) ? sb.ToString() : null;
        }
        finally
        {
            CloseDesktop(h);
        }
    }

    public static string ClassName(IntPtr hwnd)
    {
        var sb = new StringBuilder(256);
        var n = GetClassNameW(hwnd, sb, sb.Capacity);
        return n > 0 ? sb.ToString(0, n) : "";
    }

    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc proc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
    [DllImport("user32.dll")] public static extern int GetWindowTextLengthW(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern IntPtr GetWindow(IntPtr hwnd, uint cmd);
    [DllImport("user32.dll")] public static extern IntPtr GetAncestor(IntPtr hwnd, uint flags);
    [DllImport("user32.dll")] public static extern int GetSystemMetrics(int index);
    [DllImport("user32.dll", SetLastError = true)] public static extern bool PostMessageW(IntPtr hwnd, uint msg, IntPtr wParam, IntPtr lParam);
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetWindowPos(IntPtr hwnd, IntPtr after, int x, int y, int cx, int cy, uint flags);

    [DllImport("user32.dll", EntryPoint = "GetWindowLongPtrW")] private static extern IntPtr GetWindowLongPtr64(IntPtr hwnd, int index);
    [DllImport("user32.dll", EntryPoint = "SetWindowLongPtrW")] private static extern IntPtr SetWindowLongPtr64(IntPtr hwnd, int index, IntPtr value);

    public static long GetExStyle(IntPtr hwnd) => GetWindowLongPtr64(hwnd, GWL_EXSTYLE).ToInt64();
    public static void SetExStyle(IntPtr hwnd, long style) => SetWindowLongPtr64(hwnd, GWL_EXSTYLE, new IntPtr(style));

    [DllImport("dwmapi.dll")] private static extern int DwmGetWindowAttribute(IntPtr hwnd, int attr, out int value, int size);

    public static bool IsCloaked(IntPtr hwnd)
        => DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, out var v, sizeof(int)) == 0 && v != 0;

    [DllImport("kernel32.dll", SetLastError = true)] private static extern IntPtr OpenProcess(uint access, bool inherit, uint pid);
    [DllImport("kernel32.dll", SetLastError = true)] private static extern bool CloseHandle(IntPtr h);
    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool QueryFullProcessImageNameW(IntPtr h, uint flags, StringBuilder buf, ref int size);

    /// <summary>File name of the process image (e.g. "chrome.exe"), or null when it cannot be opened.</summary>
    public static string? TryGetExeName(uint pid)
    {
        var h = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, false, pid);
        if (h == IntPtr.Zero) return null;
        try
        {
            var sb = new StringBuilder(1024);
            var size = sb.Capacity;
            if (!QueryFullProcessImageNameW(h, 0, sb, ref size)) return null;
            var name = Path.GetFileName(sb.ToString(0, size));
            return string.IsNullOrEmpty(name) ? null : name;
        }
        finally
        {
            CloseHandle(h);
        }
    }

    // ---- who serves the pipe, and what the SCM says about PcGuard (read-only; standard users have this) ----

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetNamedPipeServerProcessId(SafePipeHandle pipe, out uint serverProcessId);

    /// <summary>Process id of the server end of a connected pipe, or null when it cannot be read.</summary>
    public static int? TryGetPipeServerProcessId(SafePipeHandle pipe)
        => !pipe.IsInvalid && GetNamedPipeServerProcessId(pipe, out var pid) ? (int)pid : null;

    private const uint SC_MANAGER_CONNECT = 0x0001;
    private const uint SERVICE_QUERY_CONFIG = 0x0001;
    private const uint SERVICE_QUERY_STATUS = 0x0004;
    private const int SC_STATUS_PROCESS_INFO = 0;

    [StructLayout(LayoutKind.Sequential)]
    private struct SERVICE_STATUS_PROCESS
    {
        public uint dwServiceType, dwCurrentState, dwControlsAccepted, dwWin32ExitCode, dwServiceSpecificExitCode,
            dwCheckPoint, dwWaitHint, dwProcessId, dwServiceFlags;
    }

    [DllImport("advapi32.dll", EntryPoint = "OpenSCManagerW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern IntPtr OpenSCManager(string? machineName, string? databaseName, uint desiredAccess);

    [DllImport("advapi32.dll", EntryPoint = "OpenServiceW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern IntPtr OpenService(IntPtr scManager, string serviceName, uint desiredAccess);

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern bool QueryServiceStatusEx(IntPtr service, int infoLevel, out SERVICE_STATUS_PROCESS buffer, int bufferSize, out int bytesNeeded);

    [DllImport("advapi32.dll", EntryPoint = "QueryServiceConfigW", SetLastError = true)]
    private static extern bool QueryServiceConfig(IntPtr service, IntPtr buffer, int bufferSize, out int bytesNeeded);

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern bool CloseServiceHandle(IntPtr handle);

    /// <summary>
    /// State, start type and process id of a service (QueryServiceStatusEx + QueryServiceConfigW with
    /// SERVICE_QUERY_STATUS | SERVICE_QUERY_CONFIG only), or null when any call fails. Never throws.
    /// </summary>
    public static ServiceProbe? TryProbeService(string serviceName)
    {
        var scm = OpenSCManager(null, null, SC_MANAGER_CONNECT);
        if (scm == IntPtr.Zero) return null;
        try
        {
            var svc = OpenService(scm, serviceName, SERVICE_QUERY_CONFIG | SERVICE_QUERY_STATUS);
            if (svc == IntPtr.Zero) return null;
            try
            {
                if (!QueryServiceStatusEx(svc, SC_STATUS_PROCESS_INFO, out var status, Marshal.SizeOf<SERVICE_STATUS_PROCESS>(), out _))
                    return null;
                QueryServiceConfig(svc, IntPtr.Zero, 0, out var needed); // fails with ERROR_INSUFFICIENT_BUFFER, sets needed
                if (needed < 8 || needed > 64 * 1024) return null;
                var buffer = Marshal.AllocHGlobal(needed);
                try
                {
                    if (!QueryServiceConfig(svc, buffer, needed, out _)) return null;
                    var startType = (uint)Marshal.ReadInt32(buffer, 4); // QUERY_SERVICE_CONFIGW: dwServiceType, dwStartType, ...
                    return new ServiceProbe(status.dwCurrentState, startType, (int)status.dwProcessId);
                }
                finally
                {
                    Marshal.FreeHGlobal(buffer);
                }
            }
            finally
            {
                CloseServiceHandle(svc);
            }
        }
        finally
        {
            CloseServiceHandle(scm);
        }
    }

    public static (int X, int Y, int W, int H) VirtualScreen() => (
        GetSystemMetrics(SM_XVIRTUALSCREEN), GetSystemMetrics(SM_YVIRTUALSCREEN),
        GetSystemMetrics(SM_CXVIRTUALSCREEN), GetSystemMetrics(SM_CYVIRTUALSCREEN));

    // ---- single instance (named mutex, default security) ----

    private const uint MUTEX_MODIFY_STATE = 0x0001;
    private const uint SYNCHRONIZE = 0x00100000;

    [DllImport("kernel32.dll", EntryPoint = "CreateMutexExW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern SafeWaitHandle CreateMutexEx(IntPtr attributes, string name, uint flags, uint desiredAccess);

    /// <summary>
    /// Creates (or opens) the named single-instance mutex with DEFAULT security. The service launches
    /// the shell with the user's ordinary token, whose default DACL grants the user full control of
    /// its own objects, so this works for every account type (see <see cref="SingleInstancePolicy"/>).
    /// No explicit descriptor is built on purpose: that needed the user SID from the shell's own token,
    /// which is exactly what failed on the real PC (2026-11-05). The mutex is not owned: holding the
    /// handle keeps the name alive for the process lifetime. Returns the classified outcome, the Win32
    /// code, and the handle (null unless valid; the caller keeps it open). Never throws.
    /// </summary>
    public static (MutexOpenResult Result, int Win32, SafeWaitHandle? Handle) CreateSingleInstanceMutex(string name)
    {
        try
        {
            var h = CreateMutexEx(IntPtr.Zero, name, 0, MUTEX_MODIFY_STATE | SYNCHRONIZE);
            var err = Marshal.GetLastWin32Error(); // also set on success (ERROR_ALREADY_EXISTS)
            var valid = !h.IsInvalid;
            if (!valid) h.Dispose();
            return (SingleInstancePolicy.Classify(valid, err), err, valid ? h : null);
        }
        catch (Exception e) when (e is ArgumentException or ExternalException or EntryPointNotFoundException or DllNotFoundException)
        {
            return (MutexOpenResult.Failed, 0, null);
        }
    }

    /// <summary>
    /// True when ANOTHER process running this install's shell image (same full path as this process)
    /// runs in this session. Processes whose image cannot be read do not count (a student process named
    /// PcGuard.Shell.exe must not make the genuine shell exit). Never throws (false on any error).
    /// </summary>
    public static bool AnotherShellInstanceRunning()
    {
        try
        {
            var self = Environment.ProcessId;
            var myPath = Environment.ProcessPath;
            if (string.IsNullOrEmpty(myPath)) return false;
            myPath = Path.GetFullPath(myPath);
            int mySession;
            using (var me = System.Diagnostics.Process.GetCurrentProcess()) mySession = me.SessionId;
            foreach (var p in System.Diagnostics.Process.GetProcessesByName(Path.GetFileNameWithoutExtension(myPath)))
            {
                using (p)
                {
                    try
                    {
                        if (p.Id == self || p.SessionId != mySession) continue;
                        var image = TryGetImagePath((uint)p.Id);
                        if (image is not null && string.Equals(Path.GetFullPath(image), myPath, StringComparison.OrdinalIgnoreCase))
                            return true;
                    }
                    catch (Exception e) when (e is InvalidOperationException or System.ComponentModel.Win32Exception or ArgumentException or NotSupportedException or PathTooLongException)
                    {
                        // exited meanwhile / unreadable: does not count
                    }
                }
            }
            return false;
        }
        catch (Exception e) when (e is InvalidOperationException or System.ComponentModel.Win32Exception or ArgumentException or NotSupportedException or PathTooLongException or PlatformNotSupportedException)
        {
            return false;
        }
    }

    /// <summary>Full image path of a process, or null when it cannot be opened.</summary>
    private static string? TryGetImagePath(uint pid)
    {
        var h = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, false, pid);
        if (h == IntPtr.Zero) return null;
        try
        {
            var sb = new StringBuilder(1024);
            var size = sb.Capacity;
            return QueryFullProcessImageNameW(h, 0, sb, ref size) ? sb.ToString(0, size) : null;
        }
        finally
        {
            CloseHandle(h);
        }
    }

    private const uint TOKEN_QUERY = 0x0008;

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern bool OpenProcessToken(IntPtr process, uint desiredAccess, out IntPtr token);

    [DllImport("kernel32.dll")] private static extern IntPtr GetCurrentProcess();

    /// <summary>"yes"/"no": whether this process token has the Administrators group ENABLED (false for a
    /// standard user and for a UAC-filtered administrator); "unknown (own token not readable, Win32 N)"
    /// when the shell cannot open its own token. Diagnostics only (startup trail), never throws.</summary>
    public static string AdministratorsEnabled()
    {
        try
        {
            if (!OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, out var token))
                return ShellDiagnostics.OwnTokenText(null, Marshal.GetLastWin32Error());
            CloseHandle(token);
            using var id = System.Security.Principal.WindowsIdentity.GetCurrent();
            var enabled = new System.Security.Principal.WindowsPrincipal(id).IsInRole(System.Security.Principal.WindowsBuiltInRole.Administrator);
            return ShellDiagnostics.OwnTokenText(enabled, 0);
        }
        catch (Exception e) when (e is System.Security.SecurityException or UnauthorizedAccessException or InvalidOperationException
                                       or ExternalException or EntryPointNotFoundException)
        {
            return ShellDiagnostics.OwnTokenText(null, e.HResult);
        }
    }
}
