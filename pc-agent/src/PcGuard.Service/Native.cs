using System.ComponentModel;
using System.IO.Pipes;
using System.Runtime.InteropServices;
using System.Security;
using System.Security.Principal;
using System.Text;
using Microsoft.Win32.SafeHandles;

namespace PcGuard.Service;

/// <summary>
/// All P/Invoke declarations of the guard service. WINDOWS ONLY: compile-checked on macOS, verified on
/// the Windows VM (Task 13). Keep logic out of this file.
/// </summary>
internal static class Native
{
    public const uint NoConsoleSession = 0xFFFFFFFF;

    private const uint PROCESS_QUERY_LIMITED_INFORMATION = 0x1000;
    private const uint TOKEN_QUERY = 0x0008;
    private const uint TOKEN_DUPLICATE = 0x0002;
    private const uint TOKEN_ASSIGN_PRIMARY = 0x0001;
    private const uint TOKEN_ADJUST_DEFAULT = 0x0080;
    private const uint TOKEN_ADJUST_SESSIONID = 0x0100;
    private const uint MAXIMUM_ALLOWED = 0x02000000;
    private const int SecurityImpersonation = 2;
    private const int TokenPrimary = 1;
    private const uint CREATE_UNICODE_ENVIRONMENT = 0x00000400;
    private const uint CREATE_NEW_PROCESS_GROUP = 0x00000200;

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct STARTUPINFO
    {
        public int cb;
        public string? lpReserved;
        public string? lpDesktop;
        public string? lpTitle;
        public int dwX, dwY, dwXSize, dwYSize, dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags;
        public short wShowWindow, cbReserved2;
        public IntPtr lpReserved2, hStdInput, hStdOutput, hStdError;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct PROCESS_INFORMATION
    {
        public IntPtr hProcess, hThread;
        public int dwProcessId, dwThreadId;
    }

    [DllImport("kernel32.dll")]
    private static extern uint WTSGetActiveConsoleSessionId();

    [DllImport("wtsapi32.dll", SetLastError = true)]
    private static extern bool WTSQueryUserToken(uint sessionId, out SafeAccessTokenHandle token);

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern bool DuplicateTokenEx(SafeAccessTokenHandle existing, uint desiredAccess, IntPtr tokenAttributes,
        int impersonationLevel, int tokenType, out SafeAccessTokenHandle newToken);

    [DllImport("userenv.dll", SetLastError = true)]
    private static extern bool CreateEnvironmentBlock(out IntPtr environment, SafeAccessTokenHandle token, bool inherit);

    [DllImport("userenv.dll", SetLastError = true)]
    private static extern bool DestroyEnvironmentBlock(IntPtr environment);

    [DllImport("advapi32.dll", EntryPoint = "CreateProcessAsUserW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool CreateProcessAsUser(SafeAccessTokenHandle token, string? applicationName, StringBuilder commandLine,
        IntPtr processAttributes, IntPtr threadAttributes, bool inheritHandles, uint creationFlags, IntPtr environment,
        string? currentDirectory, ref STARTUPINFO startupInfo, out PROCESS_INFORMATION processInformation);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool CloseHandle(IntPtr handle);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetNamedPipeClientProcessId(SafePipeHandle pipe, out uint clientProcessId);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern SafeProcessHandle OpenProcess(uint desiredAccess, bool inheritHandle, uint processId);

    [DllImport("kernel32.dll", EntryPoint = "QueryFullProcessImageNameW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool QueryFullProcessImageName(SafeProcessHandle process, uint flags, StringBuilder exeName, ref uint size);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool ProcessIdToSessionId(uint processId, out uint sessionId);

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern bool OpenProcessToken(SafeProcessHandle process, uint desiredAccess, out SafeAccessTokenHandle token);

    /// <summary>The session attached to the physical console, or null when none (e.g. at boot / during switch).</summary>
    public static uint? ActiveConsoleSessionId()
    {
        var id = WTSGetActiveConsoleSessionId();
        return id == NoConsoleSession ? null : id;
    }

    public static uint? SessionIdOf(int pid)
        => ProcessIdToSessionId((uint)pid, out var s) ? s : null;

    /// <summary>Win32 path of the process image (\\?\ not used), or null when it cannot be queried.</summary>
    public static string? TryGetImagePath(int pid)
    {
        using var h = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, false, (uint)pid);
        if (h.IsInvalid) return null;
        var sb = new StringBuilder(1024);
        var size = (uint)sb.Capacity;
        return QueryFullProcessImageName(h, 0, sb, ref size) ? sb.ToString(0, (int)size) : null;
    }

    /// <summary>SID of the user that owns the process token, or null if it cannot be read.</summary>
    public static SecurityIdentifier? TryGetProcessOwner(int pid)
    {
        using var h = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, false, (uint)pid);
        if (h.IsInvalid) return null;
        if (!OpenProcessToken(h, TOKEN_QUERY, out var token)) return null;
        using (token)
        {
            try
            {
                using var id = new WindowsIdentity(token.DangerousGetHandle());
                return id.User;
            }
            catch (Exception e) when (e is ArgumentException or SecurityException or UnauthorizedAccessException)
            {
                return null;
            }
        }
    }

    public static int? TryGetPipeClientProcessId(SafePipeHandle pipe)
        => GetNamedPipeClientProcessId(pipe, out var pid) ? (int)pid : null;

    /// <summary>
    /// Starts <paramref name="exePath"/> as the user signed in to <paramref name="sessionId"/>, on that
    /// user's interactive desktop (winsta0\default). Requires SYSTEM (SE_TCB_NAME for WTSQueryUserToken).
    /// Returns the new pid. Throws Win32Exception on failure (e.g. ERROR_NO_TOKEN when nobody is signed in).
    /// </summary>
    public static int LaunchInSession(uint sessionId, string exePath)
    {
        if (!WTSQueryUserToken(sessionId, out var userToken)) throw new Win32Exception(Marshal.GetLastWin32Error(), "WTSQueryUserToken");
        using (userToken)
        {
            if (!DuplicateTokenEx(userToken,
                    TOKEN_QUERY | TOKEN_DUPLICATE | TOKEN_ASSIGN_PRIMARY | TOKEN_ADJUST_DEFAULT | TOKEN_ADJUST_SESSIONID | MAXIMUM_ALLOWED,
                    IntPtr.Zero, SecurityImpersonation, TokenPrimary, out var primary))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "DuplicateTokenEx");
            using (primary)
            {
                if (!CreateEnvironmentBlock(out var env, primary, false))
                    throw new Win32Exception(Marshal.GetLastWin32Error(), "CreateEnvironmentBlock");
                try
                {
                    var si = new STARTUPINFO { cb = Marshal.SizeOf<STARTUPINFO>(), lpDesktop = @"winsta0\default" };
                    var cmd = new StringBuilder("\"" + exePath + "\"");
                    if (!CreateProcessAsUser(primary, exePath, cmd, IntPtr.Zero, IntPtr.Zero, false,
                            CREATE_UNICODE_ENVIRONMENT | CREATE_NEW_PROCESS_GROUP, env,
                            Path.GetDirectoryName(exePath), ref si, out var pi))
                        throw new Win32Exception(Marshal.GetLastWin32Error(), "CreateProcessAsUser");
                    CloseHandle(pi.hThread);
                    CloseHandle(pi.hProcess);
                    return pi.dwProcessId;
                }
                finally
                {
                    DestroyEnvironmentBlock(env);
                }
            }
        }
    }
}
