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
    private const uint SDDL_REVISION_1 = 1;

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
    /// Returns the new pid and its creation time (FILETIME ticks) so the caller can pin the exact
    /// instance. Throws Win32Exception on failure (e.g. ERROR_NO_TOKEN when nobody is signed in).
    ///
    /// Hardening:
    /// - The environment block is rebuilt with <see cref="EnvironmentFilter"/> so HKCU-set
    ///   DOTNET_/COMPlus_/CORECLR_/COR_ variables cannot load student code into the shell (I3a).
    /// - The process gets a security descriptor (owner = Administrators) that DENIES the interactive
    ///   user PROCESS_TERMINATE, PROCESS_SUSPEND_RESUME, PROCESS_VM_WRITE/VM_OPERATION and
    ///   PROCESS_CREATE_THREAD, so a standard user cannot kill, suspend or inject the shell by handle,
    ///   and cannot rewrite the DACL (owner is Administrators). NOT covered, by design: an administrator
    ///   can still stop it; same-user injection through other vectors is out of scope.
    /// </summary>
    public static (int Pid, long CreatedAt) LaunchInSession(uint sessionId, string exePath)
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
                var psd = BuildShellSecurityDescriptor(userSid); // IntPtr.Zero if it could not be built
                if (!CreateEnvironmentBlock(out var env, primary, false))
                {
                    if (psd != IntPtr.Zero) LocalFree(psd);
                    throw new Win32Exception(Marshal.GetLastWin32Error(), "CreateEnvironmentBlock");
                }
                var filtered = PinnedEnvironmentBlock(env);
                try
                {
                    var sa = new SECURITY_ATTRIBUTES { nLength = Marshal.SizeOf<SECURITY_ATTRIBUTES>(), lpSecurityDescriptor = psd, bInheritHandle = 0 };
                    var si = new STARTUPINFO { cb = Marshal.SizeOf<STARTUPINFO>(), lpDesktop = @"winsta0\default" };
                    var cmd = new StringBuilder("\"" + exePath + "\"");
                    if (!CreateProcessAsUser(primary, exePath, cmd, ref sa, IntPtr.Zero, false,
                            CREATE_UNICODE_ENVIRONMENT | CREATE_NEW_PROCESS_GROUP, filtered.AddrOfPinnedObject(),
                            Path.GetDirectoryName(exePath), ref si, out var pi))
                        throw new Win32Exception(Marshal.GetLastWin32Error(), "CreateProcessAsUser");
                    GetProcessTimes(pi.hProcess, out var created, out _, out _, out _);
                    CloseHandle(pi.hThread);
                    CloseHandle(pi.hProcess);
                    return (pi.dwProcessId, created);
                }
                finally
                {
                    filtered.Free();
                    DestroyEnvironmentBlock(env);
                    if (psd != IntPtr.Zero) LocalFree(psd);
                }
            }
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

    // Deny ACE must precede the allow ACEs. Owner/group = Administrators (BA) so a standard user cannot
    // rewrite the DACL; SYSTEM (SY) keeps full control.
    private static IntPtr BuildShellSecurityDescriptor(string? userSid)
    {
        if (userSid is null) return IntPtr.Zero;
        var sddl = $"O:BAG:BAD:(D;;0x{DeniedToUser:X};;;{userSid})(A;;0x{AllowedToUser:X};;;{userSid})(A;;GA;;;SY)(A;;GA;;;BA)";
        return ConvertStringSecurityDescriptorToSecurityDescriptor(sddl, SDDL_REVISION_1, out var psd, out _) ? psd : IntPtr.Zero;
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
