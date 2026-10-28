using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class SetupArgsTests
{
    [Fact]
    public void No_arguments_means_menu()
    {
        var a = SetupArgs.Parse(Array.Empty<string>());
        Assert.Null(a.Error);
        Assert.False(a.Install);
        Assert.False(a.Uninstall);
        Assert.False(a.Purge);
        Assert.False(a.NoPause);
        Assert.False(a.Help);
        Assert.Null(a.BackendUrl);
    }

    [Fact]
    public void Install_with_url_and_no_pause()
    {
        var a = SetupArgs.Parse(new[] { "--install", "--backend-url", "https://x.uz/api/v1", "--no-pause" });
        Assert.Null(a.Error);
        Assert.True(a.Install);
        Assert.False(a.Uninstall);
        Assert.Equal("https://x.uz/api/v1", a.BackendUrl);
        Assert.True(a.NoPause);
    }

    [Fact]
    public void Flags_are_case_insensitive()
    {
        var a = SetupArgs.Parse(new[] { "--INSTALL" });
        Assert.Null(a.Error);
        Assert.True(a.Install);
    }

    [Fact]
    public void Uninstall_alone()
    {
        var a = SetupArgs.Parse(new[] { "--uninstall" });
        Assert.Null(a.Error);
        Assert.True(a.Uninstall);
        Assert.False(a.Purge);
    }

    [Fact]
    public void Purge_without_uninstall_is_an_error()
    {
        var a = SetupArgs.Parse(new[] { "--purge" });
        Assert.Equal("--purge must be used as: --uninstall --purge.", a.Error);
    }

    [Fact]
    public void Backend_url_without_install_is_an_error()
    {
        var a = SetupArgs.Parse(new[] { "--backend-url", "https://x.uz/api/v1" });
        Assert.Equal("--backend-url can only be used together with --install.", a.Error);
    }

    [Fact]
    public void Backend_url_with_uninstall_is_an_error()
    {
        var a = SetupArgs.Parse(new[] { "--uninstall", "--backend-url", "https://x.uz/api/v1" });
        Assert.Equal("--backend-url can only be used together with --install.", a.Error);
    }

    [Fact]
    public void Allow_writable_package_flag()
    {
        var a = SetupArgs.Parse(new[] { "--install", "--allow-writable-package" });
        Assert.Null(a.Error);
        Assert.True(a.AllowWritablePackage);
        Assert.False(SetupArgs.Parse(new[] { "--install" }).AllowWritablePackage);
    }

    [Fact]
    public void Uninstall_with_purge()
    {
        var a = SetupArgs.Parse(new[] { "--uninstall", "--purge" });
        Assert.Null(a.Error);
        Assert.True(a.Uninstall);
        Assert.True(a.Purge);
    }

    [Fact]
    public void Help_flag()
    {
        var a = SetupArgs.Parse(new[] { "--help" });
        Assert.Null(a.Error);
        Assert.True(a.Help);
    }

    [Fact]
    public void Unknown_flag_is_an_error()
    {
        var a = SetupArgs.Parse(new[] { "--frobnicate" });
        Assert.Equal("Unknown argument: --frobnicate", a.Error);
    }

    [Fact]
    public void Backend_url_without_value_is_an_error()
    {
        var a = SetupArgs.Parse(new[] { "--install", "--backend-url" });
        Assert.Equal("--backend-url needs a value.", a.Error);
    }

    [Fact]
    public void Backend_url_followed_by_another_flag_is_an_error()
    {
        var a = SetupArgs.Parse(new[] { "--backend-url", "--install" });
        Assert.Equal("--backend-url needs a value.", a.Error);
    }

    [Fact]
    public void Install_and_uninstall_together_is_an_error()
    {
        var a = SetupArgs.Parse(new[] { "--install", "--uninstall" });
        Assert.Equal("--install and --uninstall cannot be combined.", a.Error);
    }

    [Fact]
    public void Install_and_purge_together_is_an_error()
    {
        var a = SetupArgs.Parse(new[] { "--install", "--purge" });
        Assert.Equal("--install and --purge cannot be combined.", a.Error);
    }
}
