namespace PcGuard.Core;

/// <summary>A process to start: the executable and its arguments as a LIST (never one concatenated string).</summary>
public sealed record PowerShellCommand(string Executable, IReadOnlyList<string> Arguments)
{
    internal static string PowerShellExe(string systemRoot) =>
        systemRoot.TrimEnd('\\') + @"\System32\WindowsPowerShell\v1.0\powershell.exe";

    private static List<string> Prefix(string scriptPath) =>
        new() { "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", scriptPath };

    /// <param name="extraApps">Extra allowed apps; passed as ONE comma-joined argument to
    /// <c>-ExtraAllowedApps</c> (under <c>powershell -File</c> an array parameter receives a single
    /// string, which install.ps1 splits on commas). Omitted when empty, so an upgrade keeps the extras
    /// already configured. Every name must pass <see cref="ExtraAllowlist.IsValidName"/>.</param>
    /// <param name="recoveryCodeHashFile">Full path of the file holding the stored form of the recovery code
    /// (<see cref="RecoveryCode.ToTransferBytes"/>), written by Setup into its admin-only temp folder;
    /// passed as <c>-RecoveryCodeHashFile</c>. The hash itself is NEVER put on the command line: Windows
    /// PowerShell writes its command line to the "Windows PowerShell" event log (events 400/600), which
    /// standard users can read. Omitted when null, so an upgrade keeps an existing, unused code. Must
    /// be a local absolute path (<c>X:\...</c>, at most 260 characters) without '$', '"' or control
    /// characters, so neither a hash nor a code can ever be passed here by mistake.</param>
    public static PowerShellCommand BuildInstall(
        string scriptPath, string backendUrl, string distDir, string systemRoot = @"C:\Windows",
        IReadOnlyList<string>? extraApps = null, string? recoveryCodeHashFile = null)
    {
        var a = Prefix(scriptPath);
        a.AddRange(new[] { "-BackendBaseUrl", backendUrl, "-DistDir", distDir });
        if (extraApps is { Count: > 0 })
        {
            if (extraApps.Any(x => !ExtraAllowlist.IsValidName(x)))
                throw new ArgumentException("Every extra app must be " + ExtraAllowlist.Rule + ".", nameof(extraApps));
            a.Add("-ExtraAllowedApps");
            a.Add(string.Join(",", extraApps));
        }
        if (recoveryCodeHashFile is not null)
        {
            // the message never contains the value: it could be a hash or a plain code passed by mistake
            if (!IsLocalAbsolutePath(recoveryCodeHashFile))
                throw new ArgumentException("The recovery code hash file must be a local absolute path.", nameof(recoveryCodeHashFile));
            a.Add("-RecoveryCodeHashFile");
            a.Add(recoveryCodeHashFile);
        }
        return new PowerShellCommand(PowerShellExe(systemRoot), a);
    }

    private static bool IsLocalAbsolutePath(string p)
    {
        if (p.Length is < 4 or > 260) return false;
        if (!(p[0] is >= 'A' and <= 'Z' or >= 'a' and <= 'z') || p[1] != ':' || p[2] != '\\') return false;
        foreach (var c in p)
            if (c < ' ' || c is '$' or '"' or '\u007f') return false;
        return !RecoveryCode.IsWellFormedStored(p);
    }

    public static PowerShellCommand BuildUninstall(
        string scriptPath, bool purge, string systemRoot = @"C:\Windows")
    {
        var a = Prefix(scriptPath);
        if (purge) a.Add("-Purge");
        return new PowerShellCommand(PowerShellExe(systemRoot), a);
    }
}
