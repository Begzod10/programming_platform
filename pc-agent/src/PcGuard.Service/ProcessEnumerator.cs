using System.Diagnostics;
using System.Security.AccessControl;
using System.Security.Principal;
using PcGuard.Core;

namespace PcGuard.Service;

/// <param name="Processes">Processes of the session, with identity derived by the service.</param>
/// <param name="ShellPids">Pids whose image is exactly the installed shell exe.</param>
/// <param name="ImagePaths">Image path per pid (where it could be queried), used to detect pid reuse before killing.</param>
internal sealed record SessionProcesses(IReadOnlyList<RunningProcess> Processes, IReadOnlyList<int> ShellPids, IReadOnlyDictionary<int, string> ImagePaths);

/// <summary>
/// Enumerates processes of one session (the active console session). WINDOWS ONLY.
///
/// Identity rules:
/// - Exe = lower-cased file name of the process image (QueryFullProcessImageName), falling back to
///   ProcessName + ".exe" when the image cannot be queried.
/// - Publisher = FileVersionInfo.CompanyName of the image. LIMITATION: this is NOT an Authenticode
///   signature check; CompanyName is a plain resource string anyone can set in their own binary, so
///   publisher-restricted allowlist entries only stop casual renaming, not a determined student.
///   (Documented for the README task.)
/// - IsServiceOwned = the process TOKEN user (OpenProcessToken with PROCESS_QUERY_LIMITED_INFORMATION,
///   TokenUser via WindowsIdentity) is SYSTEM (S-1-5-18), LOCAL SERVICE (S-1-5-19) or NETWORK SERVICE
///   (S-1-5-20); OR the token owner / image path could not be determined (conservative: undetermined
///   =&gt; never killed). Exempt in BOTH fresh and fallback enforcement.
/// - IsSystemImage = the image lies under %SystemRoot% AND the image file is owned by TrustedInstaller,
///   SYSTEM or Administrators (inbox apps such as notepad.exe, mspaint.exe). Exempt ONLY in fallback:
///   in fresh mode a student's Notepad runs under the student's token and is a violator. The file-owner
///   check exists because standard users can write to a few folders under %SystemRoot%
///   (e.g. C:\Windows\Temp, C:\Windows\Tasks); a binary dropped there is owned by the student.
/// - Anti-spoofing: a process whose name is in ProcessPolicy.Protected but which is neither
///   service-owned, nor a system image, nor the installed shell is reported with Exe = "unverified:" +
///   name, so a game renamed to explorer.exe or pcguard.shell.exe is not protected.
/// </summary>
internal sealed class ProcessEnumerator
{
    private static readonly SecurityIdentifier LocalSystem = new(WellKnownSidType.LocalSystemSid, null);
    private static readonly SecurityIdentifier LocalService = new(WellKnownSidType.LocalServiceSid, null);
    private static readonly SecurityIdentifier NetworkService = new(WellKnownSidType.NetworkServiceSid, null);
    private static readonly SecurityIdentifier Admins = new(WellKnownSidType.BuiltinAdministratorsSid, null);
    private static readonly SecurityIdentifier TrustedInstaller = new("S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464");

    private sealed record ImageInfo(DateTime LastWriteUtc, long Length, string? Publisher, bool TrustedOwner);

    private readonly string _systemRoot;
    private readonly string _shellPath;
    private readonly ILogger _log;
    private readonly Dictionary<string, ImageInfo> _images = new(StringComparer.OrdinalIgnoreCase);

    public ProcessEnumerator(string installedShellPath, ILogger log)
    {
        _shellPath = Path.GetFullPath(installedShellPath);
        _systemRoot = Path.TrimEndingDirectorySeparator(Path.GetFullPath(Environment.GetFolderPath(Environment.SpecialFolder.Windows)))
                      + Path.DirectorySeparatorChar;
        _log = log;
    }

    /// <summary>Called from the guard loop only (not thread-safe: the image cache is unsynchronised).</summary>
    public SessionProcesses Enumerate(uint sessionId)
    {
        if (_images.Count > 4096) _images.Clear(); // bound memory

        var result = new List<RunningProcess>();
        var shells = new List<int>();
        var paths = new Dictionary<int, string>();
        foreach (var p in Process.GetProcesses())
        {
            using (p)
            {
                try
                {
                    if (p.Id is 0 or 4 || (uint)p.SessionId != sessionId) continue;
                    var path = Native.TryGetImagePath(p.Id);
                    var info = path is null ? null : Image(path);
                    var exe = (path is null ? p.ProcessName + ".exe" : Path.GetFileName(path)).ToLowerInvariant();
                    var isShell = path is not null && string.Equals(Path.GetFullPath(path), _shellPath, StringComparison.OrdinalIgnoreCase);

                    // Fail safe on undetermined identity: an unreadable token owner or image path means
                    // we cannot judge the process, so it counts as service-owned (never a kill
                    // candidate) and is NOT relabeled "unverified:".
                    var owner = Native.TryGetProcessOwner(p.Id);
                    var serviceOwned = path is null || owner is null || IsServiceAccount(owner);
                    var systemImage = path is not null && info is { TrustedOwner: true }
                                      && Path.GetFullPath(path).StartsWith(_systemRoot, StringComparison.OrdinalIgnoreCase);

                    if (ProcessPolicy.Protected.Contains(exe) && !serviceOwned && !systemImage && !isShell)
                        exe = "unverified:" + exe;
                    if (isShell) shells.Add(p.Id);
                    if (path is not null) paths[p.Id] = path;

                    result.Add(new RunningProcess(p.Id, exe, info?.Publisher, serviceOwned, systemImage));
                }
                catch (Exception e) when (e is InvalidOperationException or System.ComponentModel.Win32Exception or ArgumentException)
                {
                    // exited while we looked at it, or not accessible: skip
                    _log.LogDebug("Skipping a process during enumeration: {Error}", e.GetType().Name);
                }
            }
        }
        return new SessionProcesses(result, shells, paths);
    }

    private static bool IsServiceAccount(SecurityIdentifier? sid)
        => sid is not null && (sid.Equals(LocalSystem) || sid.Equals(LocalService) || sid.Equals(NetworkService));

    private ImageInfo? Image(string path)
    {
        try
        {
            var fi = new FileInfo(path);
            if (!fi.Exists) return null;
            if (_images.TryGetValue(path, out var cached) && cached.LastWriteUtc == fi.LastWriteTimeUtc && cached.Length == fi.Length)
                return cached;

            string? publisher = null;
            try { publisher = FileVersionInfo.GetVersionInfo(path).CompanyName; }
            catch (FileNotFoundException) { }

            var trusted = false;
            try
            {
                var owner = fi.GetAccessControl(AccessControlSections.Owner).GetOwner(typeof(SecurityIdentifier)) as SecurityIdentifier;
                trusted = owner is not null && (owner.Equals(TrustedInstaller) || owner.Equals(LocalSystem) || owner.Equals(Admins));
            }
            catch (Exception e) when (e is UnauthorizedAccessException or IOException or InvalidOperationException) { }

            var info = new ImageInfo(fi.LastWriteTimeUtc, fi.Length, string.IsNullOrWhiteSpace(publisher) ? null : publisher.Trim(), trusted);
            _images[path] = info;
            return info;
        }
        catch (Exception e) when (e is UnauthorizedAccessException or IOException or ArgumentException or NotSupportedException)
        {
            return null;
        }
    }
}
