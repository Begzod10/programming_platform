using System.ComponentModel;
using System.IO.Pipes;
using System.Runtime.InteropServices;
using System.Security;
using System.Security.Principal;
using System.Text;
using Microsoft.Win32.SafeHandles;
using PcGuard.Core;

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
    private const uint TOKEN_IMPERSONATE = 0x0004;
    private const uint MAXIMUM_ALLOWED = 0x02000000;
    private const int SecurityImpersonation = 2;
    private const int TokenPrimary = 1;
    private const uint CREATE_UNICODE_ENVIRONMENT = 0x00000400;
    private const uint CREATE_NEW_PROCESS_GROUP = 0x00000200;
    private const uint CREATE_SUSPENDED = 0x00000004;
    private const uint SDDL_REVISION_1 = 1;

    [StructLayout(LayoutKind.Sequential)]
    private struct SECURITY_ATTRIBUTES
    {
        public int nLength;
        public IntPtr lpSecurityDescriptor;
        public int bInheritHandle;
    }

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
    private static extern bool DuplicateTokenEx(SafeAccessTokenHandle existing, uint desiredAccess, ref SECURITY_ATTRIBUTES tokenAttributes,
        int impersonationLevel, int tokenType, out SafeAccessTokenHandle newToken);

    [DllImport("userenv.dll", SetLastError = true)]
    private static extern bool CreateEnvironmentBlock(out IntPtr environment, SafeAccessTokenHandle token, bool inherit);

    [DllImport("userenv.dll", SetLastError = true)]
    private static extern bool DestroyEnvironmentBlock(IntPtr environment);

    [DllImport("advapi32.dll", EntryPoint = "CreateProcessAsUserW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool CreateProcessAsUser(SafeAccessTokenHandle token, string? applicationName, StringBuilder commandLine,
        IntPtr processAttributes, IntPtr threadAttributes, bool inheritHandles, uint creationFlags, IntPtr environment,
        string? currentDirectory, ref STARTUPINFO startupInfo, out PROCESS_INFORMATION processInformation);

    [DllImport("advapi32.dll", EntryPoint = "ConvertStringSecurityDescriptorToSecurityDescriptorW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool ConvertStringSecurityDescriptorToSecurityDescriptor(string sddl, uint revision, out IntPtr securityDescriptor, out uint size);

    [StructLayout(LayoutKind.Sequential)]
    private struct LUID
    {
        public uint LowPart;
        public int HighPart;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct TOKEN_PRIVILEGES
    {
        public int PrivilegeCount; // always 1 here
        public LUID Luid;
        public uint Attributes;
    }

    private const uint TOKEN_ADJUST_PRIVILEGES = 0x0020;
    private const uint SE_PRIVILEGE_ENABLED = 0x00000002;
    private const int ERROR_NOT_ALL_ASSIGNED = 1300;

    [DllImport("advapi32.dll", EntryPoint = "LookupPrivilegeValueW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool LookupPrivilegeValue(string? systemName, string name, out LUID luid);

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern bool AdjustTokenPrivileges(SafeAccessTokenHandle token, bool disableAll, ref TOKEN_PRIVILEGES newState,
        int bufferLength, IntPtr previousState, IntPtr returnLength);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern uint ResumeThread(IntPtr thread);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool TerminateProcess(IntPtr process, uint exitCode);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetProcessTimes(IntPtr process, out long creation, out long exit, out long kernel, out long user);

    [StructLayout(LayoutKind.Sequential)]
    private struct BY_HANDLE_FILE_INFORMATION
    {
        public uint FileAttributes;
        public long CreationTime, LastAccessTime, LastWriteTime;
        public uint VolumeSerialNumber, FileSizeHigh, FileSizeLow, NumberOfLinks, FileIndexHigh, FileIndexLow;
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetFileInformationByHandle(SafeFileHandle file, out BY_HANDLE_FILE_INFORMATION info);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr LocalFree(IntPtr mem);

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

    /// <summary>
    /// Enables SeDebugPrivilege on the service's own token so the SYSTEM service can open (query the
    /// image of, and terminate) user processes even when their own DACL denies access. Called once at
    /// startup, before the first enforcement tick. Logged at Information on success, at Error with the
    /// Win32 code on failure (enforcement continues; such processes may then be unreadable).
    /// </summary>
    public static void EnableSeDebugPrivilege(ILogger log)
    {
        using var self = System.Diagnostics.Process.GetCurrentProcess();
        if (!OpenProcessToken(self.SafeHandle, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, out var token))
        {
            log.LogError("Could not open the service token to enable SeDebugPrivilege (Win32 {Code})", Marshal.GetLastWin32Error());
            return;
        }
        using (token)
        {
            if (!LookupPrivilegeValue(null, "SeDebugPrivilege", out var luid))
            {
                log.LogError("LookupPrivilegeValue(SeDebugPrivilege) failed (Win32 {Code})", Marshal.GetLastWin32Error());
                return;
            }
            var tp = new TOKEN_PRIVILEGES { PrivilegeCount = 1, Luid = luid, Attributes = SE_PRIVILEGE_ENABLED };
            var ok = AdjustTokenPrivileges(token, false, ref tp, Marshal.SizeOf<TOKEN_PRIVILEGES>(), IntPtr.Zero, IntPtr.Zero);
            var err = Marshal.GetLastWin32Error(); // AdjustTokenPrivileges can "succeed" with ERROR_NOT_ALL_ASSIGNED
            if (!ok || err == ERROR_NOT_ALL_ASSIGNED)
                log.LogError("Enabling SeDebugPrivilege failed (Win32 {Code})", ok ? ERROR_NOT_ALL_ASSIGNED : err);
            else
                log.LogInformation("SeDebugPrivilege enabled");
        }
    }

    // ---- service configuration (recovery code release) ----

    private const uint SC_MANAGER_CONNECT = 0x0001;
    private const uint SERVICE_CHANGE_CONFIG = 0x0002;
    private const uint SERVICE_NO_CHANGE = 0xFFFFFFFF;
    private const uint SERVICE_DISABLED = 0x00000004;

    [DllImport("advapi32.dll", EntryPoint = "OpenSCManagerW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern IntPtr OpenSCManager(string? machineName, string? databaseName, uint desiredAccess);

    [DllImport("advapi32.dll", EntryPoint = "OpenServiceW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern IntPtr OpenService(IntPtr scManager, string serviceName, uint desiredAccess);

    [DllImport("advapi32.dll", EntryPoint = "ChangeServiceConfigW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool ChangeServiceConfig(IntPtr service, uint serviceType, uint startType, uint errorControl,
        string? binaryPathName, string? loadOrderGroup, IntPtr tagId, string? dependencies,
        string? serviceStartName, string? password, string? displayName);

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern bool CloseServiceHandle(IntPtr handle);

    /// <summary>
    /// Sets the start type of the service <paramref name="serviceName"/> to Disabled (nothing else is
    /// changed: SERVICE_NO_CHANGE for type and error control, null strings keep the rest). Used by the
    /// recovery code release so that neither the SCM recovery actions nor a reboot start it again.
    /// Returns 0 on success, otherwise the Win32 error code. Never throws.
    /// </summary>
    public static int DisableService(string serviceName)
    {
        var scm = OpenSCManager(null, null, SC_MANAGER_CONNECT);
        if (scm == IntPtr.Zero) return Marshal.GetLastWin32Error();
        try
        {
            var svc = OpenService(scm, serviceName, SERVICE_CHANGE_CONFIG);
            if (svc == IntPtr.Zero) return Marshal.GetLastWin32Error();
            try
            {
                return ChangeServiceConfig(svc, SERVICE_NO_CHANGE, SERVICE_DISABLED, SERVICE_NO_CHANGE,
                    null, null, IntPtr.Zero, null, null, null, null)
                    ? 0
                    : Marshal.GetLastWin32Error();
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

    /// <summary>True when both paths resolve to the same on-disk file (volume serial + file index),
    /// which is immune to 8.3 short paths and symlinks. False if either file cannot be opened.</summary>
    public static bool SameFileIdentity(string a, string b)
    {
        try
        {
            using var ha = File.OpenHandle(a, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
            using var hb = File.OpenHandle(b, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
            if (!GetFileInformationByHandle(ha, out var ia) || !GetFileInformationByHandle(hb, out var ib)) return false;
            return ia.VolumeSerialNumber == ib.VolumeSerialNumber
                   && ia.FileIndexHigh == ib.FileIndexHigh && ia.FileIndexLow == ib.FileIndexLow;
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or ArgumentException or NotSupportedException)
        {
            return false;
        }
    }

    /// <summary>Process creation time as a FILETIME (100 ns ticks). Used with the pid to pin an exact
    /// process instance and defeat PID reuse. Null when it cannot be read.</summary>
    public static long? TryGetProcessCreationTime(int pid)
    {
        using var h = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, false, (uint)pid);
        if (h.IsInvalid) return null;
        return GetProcessTimes(h.DangerousGetHandle(), out var creation, out _, out _, out _) ? creation : null;
    }

    /// <summary>
    /// Starts <paramref name="exePath"/> as the user signed in to <paramref name="sessionId"/>, on that
    /// user's interactive desktop (winsta0\default). Requires SYSTEM (SE_TCB_NAME for WTSQueryUserToken).
    /// The process is created SUSPENDED; <paramref name="beforeResume"/> is invoked with the new pid and
    /// its creation time (FILETIME ticks) so the caller can pin the exact instance BEFORE it runs and
    /// can connect (closes the first-connect race), then the primary thread is resumed. Throws
    /// Win32Exception on a launch failure (e.g. ERROR_NO_TOKEN when nobody is signed in).
    ///
    /// The shell runs with the console user's ORDINARY token (2026-11-05, real-PC bug): nothing inside
    /// the token is changed (no default DACL, privilege, integrity, group or session change, no
    /// restricted token), and the process and thread get default security (no deny ACEs, no owner
    /// change). The earlier restricted token default DACL made every object the shell created (its
    /// named mutex, the objects of Windows text input) unusable for a UAC administrator or a standard
    /// user, so the lock screen never appeared. Ending the shell is therefore possible for the student;
    /// it gains nothing: this service relaunches it, and while no shell reports, the stricter
    /// name-only fallback closes every non-allowlisted app.
    /// What stays: the environment block is rebuilt with <see cref="EnvironmentFilter"/> so HKCU-set
    /// DOTNET_/COMPlus_/CORECLR_/COR_ variables cannot load student code into the shell (I3a), and the
    /// suspended start + pin (the pipe accepts only this exact instance).
    /// The token is duplicated only to give the token OBJECT an explicit security descriptor
    /// (<see cref="ShellTokenSecurity.TokenObjectSddl"/>: SYSTEM, Administrators, the user) so the
    /// shell can open its own token like any normal process; if the SID cannot be read the duplicate
    /// gets the default descriptor and the launch goes on.
    /// </summary>
    public static (int Pid, long CreatedAt) LaunchInSession(uint sessionId, string exePath, Action<int, long> beforeResume, ILogger log)
    {
        if (!WTSQueryUserToken(sessionId, out var userToken)) throw new Win32Exception(Marshal.GetLastWin32Error(), "WTSQueryUserToken");
        using (userToken)
        {
            var primary = DuplicateForShell(userToken, log);
            using (primary)
            {
                if (!CreateEnvironmentBlock(out var env, primary, false))
                    throw new Win32Exception(Marshal.GetLastWin32Error(), "CreateEnvironmentBlock");
                var filtered = PinnedEnvironmentBlock(env);
                var launched = false;
                PROCESS_INFORMATION pi = default;
                try
                {
                    var si = new STARTUPINFO { cb = Marshal.SizeOf<STARTUPINFO>(), lpDesktop = @"winsta0\default" };
                    var cmd = new StringBuilder("\"" + exePath + "\"");
                    if (!CreateProcessAsUser(primary, exePath, cmd, IntPtr.Zero, IntPtr.Zero, false,
                            CREATE_UNICODE_ENVIRONMENT | CREATE_NEW_PROCESS_GROUP | CREATE_SUSPENDED, filtered.AddrOfPinnedObject(),
                            Path.GetDirectoryName(exePath), ref si, out pi))
                        throw new Win32Exception(Marshal.GetLastWin32Error(), "CreateProcessAsUser");
                    launched = true;
                    if (!GetProcessTimes(pi.hProcess, out var created, out _, out _, out _))
                    {
                        var err = Marshal.GetLastWin32Error();
                        log.LogError("Could not read the shell's creation time (Win32 {Code}); terminating the suspended instance", err);
                        TerminateProcess(pi.hProcess, 1); // never pin createdAt = 0
                        throw new Win32Exception(err, "GetProcessTimes");
                    }
                    try
                    {
                        beforeResume(pi.dwProcessId, created); // set the pin before the shell can connect
                    }
                    catch
                    {
                        // pinning failed: do NOT resume an unpinned shell (the pipe would reject it anyway)
                        log.LogError("Pinning the shell threw; terminating the suspended instance");
                        TerminateProcess(pi.hProcess, 1);
                        throw;
                    }
                    if (ResumeThread(pi.hThread) == 0xFFFFFFFF)
                    {
                        var err = Marshal.GetLastWin32Error();
                        log.LogError("Could not resume the shell (Win32 {Code}); terminating the suspended instance", err);
                        TerminateProcess(pi.hProcess, 1);
                        throw new Win32Exception(err, "ResumeThread");
                    }
                    return (pi.dwProcessId, created);
                }
                finally
                {
                    if (launched)
                    {
                        if (pi.hThread != IntPtr.Zero) CloseHandle(pi.hThread);
                        if (pi.hProcess != IntPtr.Zero) CloseHandle(pi.hProcess);
                    }
                    filtered.Free();
                    DestroyEnvironmentBlock(env);
                }
            }
        }
    }

    // Primary-token duplicate of the user's token with an explicit token-OBJECT security descriptor
    // (see LaunchInSession). The token's contents are not modified. Access: what CreateProcessAsUser
    // (QUERY, DUPLICATE, ASSIGN_PRIMARY) and CreateEnvironmentBlock (QUERY, DUPLICATE, IMPERSONATE) need.
    private static SafeAccessTokenHandle DuplicateForShell(SafeAccessTokenHandle userToken, ILogger log)
    {
        const uint access = TOKEN_QUERY | TOKEN_DUPLICATE | TOKEN_ASSIGN_PRIMARY | TOKEN_IMPERSONATE | MAXIMUM_ALLOWED;
        var sd = IntPtr.Zero;
        var userSid = UserSidOf(userToken);
        if (userSid is null)
            log.LogWarning("Could not read the interactive user SID; the shell token object gets the default security descriptor");
        else if (!ConvertStringSecurityDescriptorToSecurityDescriptor(ShellTokenSecurity.TokenObjectSddl(userSid), SDDL_REVISION_1, out sd, out _))
        {
            log.LogWarning("Shell token object SDDL conversion failed (Win32 {Code}); using the default security descriptor", Marshal.GetLastWin32Error());
            sd = IntPtr.Zero;
        }
        try
        {
            var sa = new SECURITY_ATTRIBUTES { nLength = Marshal.SizeOf<SECURITY_ATTRIBUTES>(), lpSecurityDescriptor = sd, bInheritHandle = 0 };
            if (!DuplicateTokenEx(userToken, access, ref sa, SecurityImpersonation, TokenPrimary, out var primary))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "DuplicateTokenEx");
            return primary;
        }
        finally
        {
            if (sd != IntPtr.Zero) LocalFree(sd);
        }
    }

    private static string? UserSidOf(SafeAccessTokenHandle token)
    {
        try
        {
            using var id = new WindowsIdentity(token.DangerousGetHandle());
            return id.User?.Value;
        }
        catch (Exception e) when (e is ArgumentException or SecurityException or UnauthorizedAccessException)
        {
            return null;
        }
    }

    // Read the user's environment block, strip runtime-hijacking variables, and pin a fresh Unicode,
    // double-null-terminated block for CreateProcessAsUser. The caller frees the returned handle.
    private static GCHandle PinnedEnvironmentBlock(IntPtr block)
    {
        var entries = new List<string>();
        var ptr = block;
        while (ptr != IntPtr.Zero)
        {
            var s = Marshal.PtrToStringUni(ptr);
            if (string.IsNullOrEmpty(s)) break;
            entries.Add(s);
            ptr += (s.Length + 1) * 2;
        }
        var kept = EnvironmentFilter.Strip(entries);
        var sb = new StringBuilder();
        foreach (var e in kept) sb.Append(e).Append('\0');
        sb.Append('\0');
        return GCHandle.Alloc(Encoding.Unicode.GetBytes(sb.ToString()), GCHandleType.Pinned);
    }
}
