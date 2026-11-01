namespace PcGuard.Core;

/// <summary>
/// The three fixed PowerShell invocations of Cleanup-PcGuard.exe, as argument LISTS. They never contain
/// -Kill, -IgnoreAcl or -InstallDir.
/// </summary>
public static class CleanupCommand
{
    private static PowerShellCommand Build(string scriptPath, string systemRoot, params string[] extra)
    {
        var a = new List<string> { "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", scriptPath };
        a.AddRange(extra);
        return new PowerShellCommand(PowerShellCommand.PowerShellExe(systemRoot), a);
    }

    /// <summary>List busy script processes; closes nothing.</summary>
    public static PowerShellCommand BuildList(string scriptPath, string systemRoot = @"C:\Windows") =>
        Build(scriptPath, systemRoot, "-FindBusyScripts");

    /// <summary>Show what the removal would do; changes nothing.</summary>
    public static PowerShellCommand BuildPreview(string scriptPath, string systemRoot = @"C:\Windows") =>
        Build(scriptPath, systemRoot, "-RemovePcGuard", "-WhatIf");

    /// <summary>The real removal. -Force only skips the script's own YES prompt (the exe has already asked).</summary>
    public static PowerShellCommand BuildRemove(string scriptPath, bool purge, string systemRoot = @"C:\Windows") =>
        purge
            ? Build(scriptPath, systemRoot, "-RemovePcGuard", "-Force", "-Purge")
            : Build(scriptPath, systemRoot, "-RemovePcGuard", "-Force");
}
