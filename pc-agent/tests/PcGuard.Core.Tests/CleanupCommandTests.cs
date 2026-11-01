using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class CleanupCommandTests
{
    private const string Ps = @"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe";
    private const string Script = @"C:\ProgramData\PcGuard-cleanup-abc\cleanup.ps1";

    [Fact]
    public void List_only_is_exact()
    {
        var c = CleanupCommand.BuildList(Script, @"C:\Windows");
        Assert.Equal(Ps, c.Executable);
        Assert.Equal(new[] { "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", Script, "-FindBusyScripts" }, c.Arguments);
    }

    [Fact]
    public void Preview_is_exact()
    {
        var c = CleanupCommand.BuildPreview(Script, @"C:\Windows");
        Assert.Equal(Ps, c.Executable);
        Assert.Equal(new[] { "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", Script, "-RemovePcGuard", "-WhatIf" }, c.Arguments);
    }

    [Fact]
    public void Remove_without_purge_is_exact()
    {
        var c = CleanupCommand.BuildRemove(Script, false, @"C:\Windows");
        Assert.Equal(new[] { "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", Script, "-RemovePcGuard", "-Force" }, c.Arguments);
    }

    [Fact]
    public void Remove_with_purge_is_exact()
    {
        var c = CleanupCommand.BuildRemove(Script, true, @"C:\Windows");
        Assert.Equal(new[] { "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", Script, "-RemovePcGuard", "-Force", "-Purge" }, c.Arguments);
    }

    [Fact]
    public void Dangerous_switches_never_appear()
    {
        var all = new[]
        {
            CleanupCommand.BuildList(Script, @"C:\Windows"),
            CleanupCommand.BuildPreview(Script, @"C:\Windows"),
            CleanupCommand.BuildRemove(Script, false, @"C:\Windows"),
            CleanupCommand.BuildRemove(Script, true, @"C:\Windows"),
        };
        foreach (var c in all)
        {
            Assert.DoesNotContain("-Kill", c.Arguments);
            Assert.DoesNotContain("-IgnoreAcl", c.Arguments);
            Assert.DoesNotContain("-InstallDir", c.Arguments);
        }
    }

    [Fact]
    public void Preview_and_list_never_carry_force_or_purge()
    {
        foreach (var c in new[] { CleanupCommand.BuildList(Script, @"C:\Windows"), CleanupCommand.BuildPreview(Script, @"C:\Windows") })
        {
            Assert.DoesNotContain("-Force", c.Arguments);
            Assert.DoesNotContain("-Purge", c.Arguments);
        }
    }

    [Fact]
    public void Windows_dir_with_trailing_backslash_is_normalised()
    {
        Assert.Equal(Ps, CleanupCommand.BuildList(Script, @"C:\Windows\").Executable);
    }
}
