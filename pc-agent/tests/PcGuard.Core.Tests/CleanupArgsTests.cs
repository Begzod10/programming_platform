using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class CleanupArgsTests
{
    [Fact]
    public void No_arguments_means_full_flow()
    {
        var a = CleanupArgs.Parse(Array.Empty<string>());
        Assert.Null(a.Error);
        Assert.False(a.ListOnly);
        Assert.False(a.PreviewOnly);
        Assert.False(a.Purge);
        Assert.False(a.NoPause);
        Assert.False(a.Help);
    }

    [Fact]
    public void Each_switch_sets_its_flag()
    {
        Assert.True(CleanupArgs.Parse(new[] { "--list-only" }).ListOnly);
        Assert.True(CleanupArgs.Parse(new[] { "--preview-only" }).PreviewOnly);
        Assert.True(CleanupArgs.Parse(new[] { "--purge" }).Purge);
        Assert.True(CleanupArgs.Parse(new[] { "--no-pause" }).NoPause);
        Assert.True(CleanupArgs.Parse(new[] { "--help" }).Help);
    }

    [Fact]
    public void Switches_are_case_insensitive_and_combinable()
    {
        var a = CleanupArgs.Parse(new[] { "--PURGE", "--No-Pause" });
        Assert.Null(a.Error);
        Assert.True(a.Purge);
        Assert.True(a.NoPause);
    }

    [Fact]
    public void Unknown_switch_is_an_error()
    {
        var a = CleanupArgs.Parse(new[] { "--kill" });
        Assert.Equal("Unknown argument: --kill", a.Error);
    }

    [Fact]
    public void Silent_style_switches_do_not_exist()
    {
        Assert.NotNull(CleanupArgs.Parse(new[] { "--yes" }).Error);
        Assert.NotNull(CleanupArgs.Parse(new[] { "--silent" }).Error);
        Assert.NotNull(CleanupArgs.Parse(new[] { "--force" }).Error);
    }

    [Fact]
    public void List_only_and_preview_only_conflict()
    {
        var a = CleanupArgs.Parse(new[] { "--list-only", "--preview-only" });
        Assert.Equal("--list-only and --preview-only cannot be combined.", a.Error);
    }

    [Fact]
    public void Purge_with_list_only_or_preview_only_is_an_error()
    {
        Assert.Equal("--purge cannot be combined with --list-only or --preview-only.", CleanupArgs.Parse(new[] { "--list-only", "--purge" }).Error);
        Assert.Equal("--purge cannot be combined with --list-only or --preview-only.", CleanupArgs.Parse(new[] { "--preview-only", "--purge" }).Error);
    }
}
