using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class PowerShellCommandTests
{
    private const string Ps = @"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe";

    [Fact]
    public void Install_command_is_exact()
    {
        var c = PowerShellCommand.BuildInstall(
            @"C:\ProgramData\PcGuard\setup-1\install.ps1", "https://x.uz/api/v1", @"C:\Pkg\PcGuard\dist", @"C:\Windows");
        Assert.Equal(Ps, c.Executable);
        Assert.Equal(
            new[]
            {
                "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", @"C:\ProgramData\PcGuard\setup-1\install.ps1",
                "-BackendBaseUrl", "https://x.uz/api/v1", "-DistDir", @"C:\Pkg\PcGuard\dist",
            },
            c.Arguments);
    }

    [Fact]
    public void Uninstall_without_purge_is_exact()
    {
        var c = PowerShellCommand.BuildUninstall(@"C:\t\uninstall.ps1", false, @"C:\Windows");
        Assert.Equal(Ps, c.Executable);
        Assert.Equal(
            new[] { "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", @"C:\t\uninstall.ps1" },
            c.Arguments);
    }

    [Fact]
    public void Uninstall_with_purge_appends_switch()
    {
        var c = PowerShellCommand.BuildUninstall(@"C:\t\uninstall.ps1", true, @"C:\Windows");
        Assert.Equal(
            new[] { "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", @"C:\t\uninstall.ps1", "-Purge" },
            c.Arguments);
    }

    [Fact]
    public void Trailing_backslash_on_system_root_is_handled()
    {
        var c = PowerShellCommand.BuildUninstall("s.ps1", false, @"C:\Windows\");
        Assert.Equal(Ps, c.Executable);
    }

    [Fact]
    public void Hostile_url_stays_one_argument()
    {
        var c = PowerShellCommand.BuildInstall("s.ps1", "https://x.uz/api/v1 -InstallDir C:\\evil", "d", @"C:\Windows");
        Assert.Equal("https://x.uz/api/v1 -InstallDir C:\\evil", c.Arguments[6]);
        Assert.Equal(9, c.Arguments.Count);
    }
}
