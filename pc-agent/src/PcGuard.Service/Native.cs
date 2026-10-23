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
    private const uint TOKEN_ADJUST_DEFAULT = 0x0080;
    private const uint TOKEN_ADJUST_SESSIONID = 0x0100;
    private const uint MAXIMUM_ALLOWED = 0x02000000;
    private const int SecurityImpersonation = 2;
    private const int TokenPrimary = 1;
    private const uint CREATE_UNICODE_ENVIRONMENT = 0x00000400;
    private const uint CREATE_NEW_PROCESS_GROUP = 0x00000200;
    private const uint CREATE_SUSPENDED = 0x00000004;
    private const uint SDDL_REVISION_1 = 1;
    private const int TokenDefaultDacl = 6; // TOKEN_INFORMATION_CLASS.TokenDefaultDacl

    // Process access rights denied to the interactive user on the shell process (see BuildShellSddl).
    private const uint PROCESS_TERMINATE = 0x0001;
    private const uint PROCESS_CREATE_THREAD = 0x0002;
    private const uint PROCESS_VM_OPERATION = 0x0008;
    private const uint PROCESS_VM_WRITE = 0x0020;
    private const uint PROCESS_SUSPEND_RESUME = 0x0800;
    private const uint DeniedToUser = PROCESS_TERMINATE | PROCESS_CREATE_THREAD | PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_SUSPEND_RESUME; // 0x082B
    // Benign rights the user keeps so normal OS interaction still works.
    private const uint AllowedToUser = 0x1000 /*QUERY_LIMITED_INFO*/ | 0x0400 /*QUERY_INFO*/ | 0x00100000 /*SYNCHRONIZE*/ | 0x00020000 /*READ_CONTROL*/;

    [StructLayout(LayoutKind.Sequential)]
    private struct SECURITY_ATTRIBUTES
    {
        public int nLength;
        public IntPtr lpSecurityDescriptor;
        public int bInheritHandle;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct TOKEN_DEFAULT_DACL
    {
        public IntPtr DefaultDacl; // PACL into a security-descriptor buffer
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
    private static extern bool DuplicateTokenEx(SafeAccessTokenHandle existing, uint desiredAccess, IntPtr tokenAttributes,
        int impersonationLevel, int tokenType, out SafeAccessTokenHandle newToken);

    [DllImport("userenv.dll", SetLastError = true)]
    private static extern bool CreateEnvironmentBlock(out IntPtr environment, SafeAccessTokenHandle token, bool inherit);

    [DllImport("userenv.dll", SetLastError = true)]
    private static extern bool DestroyEnvironmentBlock(IntPtr environment);

    [DllImport("advapi32.dll", EntryPoint = "CreateProcessAsUserW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool CreateProcessAsUser(SafeAccessTokenHandle token, string? applicationName, StringBuilder commandLine,
        ref SECURITY_ATTRIBUTES processAttributes, IntPtr threadAttributes, bool inheritHandles, uint creationFlags, IntPtr environment,
        string? currentDirectory, ref STARTUPINFO startupInfo, out PROCESS_INFORMATION processInformation);

    [DllImport("advapi32.dll", EntryPoint = "ConvertStringSecurityDescriptorToSecurityDescriptorW", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool ConvertStringSecurityDescriptorToSecurityDescriptor(string sddl, uint revision, out IntPtr securityDescriptor, out uint size);

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern bool GetSecurityDescriptorDacl(IntPtr securityDescriptor, out bool daclPresent, out IntPtr dacl, out bool daclDefaulted);

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern bool SetTokenInformation(SafeAccessTokenHandle token, int tokenInformationClass, ref TOKEN_DEFAULT_DACL info, int length);

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
    /// Hardening (each step is best-effort: a failure is logged at ERROR and the shell still launches,
    /// because an unprotected shell beats a PC with no sign-in screen):
    /// - The environment block is rebuilt with <see cref="EnvironmentFilter"/> so HKCU-set
    ///   DOTNET_/COMPlus_/CORECLR_/COR_ variables cannot load student code into the shell (I3a).
    /// - The PROCESS gets a security descriptor denying the interactive user terminate/suspend/inject
    ///   (see <see cref="BuildShellSecurityDescriptor"/>).
    /// - The duplicated primary token's DEFAULT DACL is restricted (see <see cref="ApplyRestrictedDefaultDacl"/>)
    ///   so THREADS and other kernel objects the shell later creates are not grantable to the user for
    ///   terminate/suspend either — closing the OpenThread(THREAD_TERMINATE|THREAD_SUSPEND_RESUME) hole.
    /// </summary>
    public static (int Pid, long CreatedAt) LaunchInSession(uint sessionId, string exePath, Action<int, long> beforeResume, ILogger log)
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
                var userSid = UserSidOf(primary);
                if (userSid is null)
                    log.LogError("Shell protection skipped: could not read the interactive user SID; launching the shell unprotected");
                ApplyRestrictedDefaultDacl(primary, userSid, log); // never touches the user's original token
                var psd = BuildShellSecurityDescriptor(userSid, log); // IntPtr.Zero if it could not be built
                if (!CreateEnvironmentBlock(out var env, primary, false))
                {
                    if (psd != IntPtr.Zero) LocalFree(psd);
                    throw new Win32Exception(Marshal.GetLastWin32Error(), "CreateEnvironmentBlock");
                }
                var filtered = PinnedEnvironmentBlock(env);
                var launched = false;
                PROCESS_INFORMATION pi = default;
                try
                {
                    var sa = new SECURITY_ATTRIBUTES { nLength = Marshal.SizeOf<SECURITY_ATTRIBUTES>(), lpSecurityDescriptor = psd, bInheritHandle = 0 };
                    var si = new STARTUPINFO { cb = Marshal.SizeOf<STARTUPINFO>(), lpDesktop = @"winsta0\default" };
                    var cmd = new StringBuilder("\"" + exePath + "\"");
                    if (!CreateProcessAsUser(primary, exePath, cmd, ref sa, IntPtr.Zero, false,
                            CREATE_UNICODE_ENVIRONMENT | CREATE_NEW_PROCESS_GROUP | CREATE_SUSPENDED, filtered.AddrOfPinnedObject(),
                            Path.GetDirectoryName(exePath), ref si, out pi))
                        throw new Win32Exception(Marshal.GetLastWin32Error(), "CreateProcessAsUser");
                    launched = true;
                    GetProcessTimes(pi.hProcess, out var created, out _, out _, out _);
                    try { beforeResume(pi.dwProcessId, created); } // set the pin before the shell can connect
                    finally
                    {
                        if (ResumeThread(pi.hThread) == 0xFFFFFFFF)
                        {
                            log.LogError("Could not resume the shell (Win32 {Code}); terminating the suspended instance", Marshal.GetLastWin32Error());
                            TerminateProcess(pi.hProcess, 1);
                            throw new Win32Exception(Marshal.GetLastWin32Error(), "ResumeThread");
                        }
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
                    if (psd != IntPtr.Zero) LocalFree(psd);
                }
            }
        }
    }

    // Restrict the DUPLICATED primary token's default DACL so objects the shell creates (threads,
    // events, mutexes) grant the interactive user only the same read rights as the process SD, not
    // terminate/suspend. SYSTEM and Administrators keep full control. The shell keeps full access to
    // its own objects through the handles it receives at creation, so its own operation is unaffected.
    // Best-effort: any failure is logged at ERROR and the launch proceeds unprotected.
    private static void ApplyRestrictedDefaultDacl(SafeAccessTokenHandle primary, string? userSid, ILogger log)
    {
        if (userSid is null) return;
        var sddl = $"D:(A;;GA;;;SY)(A;;GA;;;BA)(A;;0x{AllowedToUser:X};;;{userSid})";
        if (!ConvertStringSecurityDescriptorToSecurityDescriptor(sddl, SDDL_REVISION_1, out var sd, out _))
        {
            log.LogError("Shell thread protection skipped: SDDL conversion failed (Win32 {Code})", Marshal.GetLastWin32Error());
            return;
        }
        try
        {
            if (!GetSecurityDescriptorDacl(sd, out _, out var dacl, out _))
            {
                log.LogError("Shell thread protection skipped: GetSecurityDescriptorDacl failed (Win32 {Code})", Marshal.GetLastWin32Error());
                return;
            }
            var info = new TOKEN_DEFAULT_DACL { DefaultDacl = dacl };
            if (!SetTokenInformation(primary, TokenDefaultDacl, ref info, Marshal.SizeOf<TOKEN_DEFAULT_DACL>()))
                log.LogError("Shell thread protection skipped: SetTokenInformation(TokenDefaultDacl) failed (Win32 {Code})", Marshal.GetLastWin32Error());
        }
        finally
        {
            LocalFree(sd); // the ACL is copied into the token by SetTokenInformation, so this is safe
        }
    }

    private static string? UserSidOf(SafeAccessTokenHandle primary)
    {
        try
        {
            using var id = new WindowsIdentity(primary.DangerousGetHandle());
            return id.User?.Value;
        }
        catch (Exception e) when (e is ArgumentException or SecurityException or UnauthorizedAccessException)
        {
            return null;
        }
    }

    // Process security descriptor. Covered: a standard user is DENIED PROCESS_TERMINATE,
    // PROCESS_SUSPEND_RESUME, PROCESS_VM_WRITE, PROCESS_VM_OPERATION and PROCESS_CREATE_THREAD on the
    // shell process (deny ACE first), and owner = Administrators so the user cannot rewrite the DACL.
    // Kept for the user: query/synchronize/read_control. NOT covered: SYSTEM and elevated admins keep
    // full control (can still stop it); this guards the process object only — thread objects are
    // handled by ApplyRestrictedDefaultDacl. Best-effort: on failure returns Zero (no process SD) and
    // logs at ERROR; the shell still launches.
    private static IntPtr BuildShellSecurityDescriptor(string? userSid, ILogger log)
    {
        if (userSid is null) return IntPtr.Zero;
        var sddl = $"O:BAG:BAD:(D;;0x{DeniedToUser:X};;;{userSid})(A;;0x{AllowedToUser:X};;;{userSid})(A;;GA;;;SY)(A;;GA;;;BA)";
        if (ConvertStringSecurityDescriptorToSecurityDescriptor(sddl, SDDL_REVISION_1, out var psd, out _)) return psd;
        log.LogError("Shell process protection skipped: SDDL conversion failed (Win32 {Code}); launching unprotected", Marshal.GetLastWin32Error());
        return IntPtr.Zero;
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
