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
    /// <param name="recoveryCodeHash">The stored form of the recovery code (never the code itself), passed as
    /// <c>-RecoveryCodeHash</c>; omitted when null, so an upgrade keeps an existing one. Must pass
    /// <see cref="RecoveryCode.IsWellFormedStored"/>.</param>
    public static PowerShellCommand BuildInstall(
        string scriptPath, string backendUrl, string distDir, string systemRoot = @"C:\Windows",
        IReadOnlyList<string>? extraApps = null, string? recoveryCodeHash = null)
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
        if (recoveryCodeHash is not null)
        {
            // the message never contains the value: it could be a plain code passed by mistake
            if (!RecoveryCode.IsWellFormedStored(recoveryCodeHash))
                throw new ArgumentException("The recovery code hash is not in the stored form.", nameof(recoveryCodeHash));
            a.Add("-RecoveryCodeHash");
            a.Add(recoveryCodeHash);
        }
        return new PowerShellCommand(PowerShellExe(systemRoot), a);
    }

    public static PowerShellCommand BuildUninstall(
        string scriptPath, bool purge, string systemRoot = @"C:\Windows")
    {
        var a = Prefix(scriptPath);
        if (purge) a.Add("-Purge");
        return new PowerShellCommand(PowerShellExe(systemRoot), a);
    }
}
