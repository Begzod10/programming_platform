using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class PackageLocatorTests
{
    private static string P(string root, string name) => Path.Combine(root, "dist", name);

    [Fact]
    public void Complete_package_has_nothing_missing()
    {
        var root = Path.Combine("x", "PcGuard");
        var existing = new HashSet<string>
        {
            P(root, "PcGuard.Service.exe"), P(root, "PcGuard.Shell.exe"), P(root, "appsettings.json"),
        };
        Assert.Empty(PackageLocator.Check(existing.Contains, root));
    }

    [Fact]
    public void Everything_missing_lists_all_three_in_order()
    {
        var missing = PackageLocator.Check(_ => false, Path.Combine("x", "PcGuard"));
        Assert.Equal(
            new[] { @"dist\PcGuard.Service.exe", @"dist\PcGuard.Shell.exe", @"dist\appsettings.json" },
            missing);
    }

    [Fact]
    public void Only_the_missing_file_is_reported()
    {
        var root = Path.Combine("x", "PcGuard");
        var existing = new HashSet<string> { P(root, "PcGuard.Service.exe"), P(root, "appsettings.json") };
        Assert.Equal(new[] { @"dist\PcGuard.Shell.exe" }, PackageLocator.Check(existing.Contains, root));
    }
}
