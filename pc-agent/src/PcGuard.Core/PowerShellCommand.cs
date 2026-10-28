namespace PcGuard.Core;

/// <summary>A process to start: the executable and its arguments as a LIST (never one concatenated string).</summary>
public sealed record PowerShellCommand(string Executable, IReadOnlyList<string> Arguments)
{
    private static string PowerShellExe(string systemRoot) =>
        systemRoot.TrimEnd('\\') + @"\System32\WindowsPowerShell\v1.0\powershell.exe";

    private static List<string> Prefix(string scriptPath) =>
        new() { "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", scriptPath };

    public static PowerShellCommand BuildInstall(
        string scriptPath, string backendUrl, string distDir, string systemRoot = @"C:\Windows")
    {
        var a = Prefix(scriptPath);
        a.AddRange(new[] { "-BackendBaseUrl", backendUrl, "-DistDir", distDir });
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
