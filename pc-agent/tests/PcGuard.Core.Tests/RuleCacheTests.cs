using PcGuard.Core;
using Xunit;

namespace PcGuard.Core.Tests;

public class RuleCacheTests : IDisposable
{
    private readonly string _dir = Path.Combine(Path.GetTempPath(), "pcguard-" + Guid.NewGuid().ToString("N"));
    private DateTimeOffset _now = new(2026, 10, 23, 10, 0, 0, TimeSpan.Zero);
    private readonly TimeSpan _maxAge = TimeSpan.FromMinutes(10);

    public RuleCacheTests() => Directory.CreateDirectory(_dir);
    public void Dispose() { try { Directory.Delete(_dir, true); } catch { } }

    private string P => Path.Combine(_dir, "rules.json");
    private RuleCache Make() => new(P, _maxAge, () => _now);

    private static PcRules Rules(bool locked, params string[] exes) => new(
        locked, locked ? "quota_pending" : "ok", 2, "Ali",
        exes.Select(e => new AllowEntry(e, null)).ToList(), new[] { "example.uz" });

    [Fact]
    public void NoFile_ReturnsLockedDefault()
    {
        var c = Make().Current();
        Assert.True(c.Locked);
        Assert.Equal("offline_timeout", c.Reason);
        Assert.Equal(Defaults.Allowlist, c.Allowlist);
    }

    [Fact]
    public void DefaultsAreEightExes()
    {
        Assert.Equal(new[] { "code.exe", "windowsterminal.exe", "cmd.exe", "powershell.exe", "python.exe", "node.exe", "chrome.exe", "msedge.exe" },
            Defaults.Allowlist.Select(a => a.Exe).ToArray());
        Assert.All(Defaults.Allowlist, a => Assert.Null(a.Publisher));
    }

    [Fact]
    public void Apply_ThenCurrent_ReturnsRulesWithinMaxAge()
    {
        var c = Make();
        var r = Rules(false, "a.exe");
        Assert.True(c.Apply(r));
        _now += TimeSpan.FromMinutes(10);
        var cur = c.Current();
        Assert.False(cur.Locked);
        Assert.Equal("a.exe", cur.Allowlist.Single().Exe);
        Assert.Equal("Ali", cur.StudentName);
        Assert.Equal(new[] { "example.uz" }, cur.BrowserHosts);
    }

    [Fact]
    public void Expired_ReturnsLockedWithLastAllowlist()
    {
        var c = Make();
        c.Apply(Rules(false, "a.exe"));
        _now += TimeSpan.FromMinutes(10) + TimeSpan.FromSeconds(1);
        var cur = c.Current();
        Assert.True(cur.Locked);
        Assert.Equal("offline_timeout", cur.Reason);
        Assert.Equal(0, cur.Remaining);
        Assert.Null(cur.StudentName);
        Assert.Equal("a.exe", cur.Allowlist.Single().Exe);
        Assert.Equal(new[] { "example.uz" }, cur.BrowserHosts);
    }

    [Fact]
    public void EmptyAllowlist_ReturnsFalse_KeepsPreviousAllowlist_TakesNewLocked()
    {
        var c = Make();
        c.Apply(Rules(true, "a.exe"));
        var ok = c.Apply(Rules(false));
        Assert.False(ok);
        var cur = c.Current();
        Assert.False(cur.Locked);
        Assert.Equal("a.exe", cur.Allowlist.Single().Exe);
    }

    [Fact]
    public void EmptyAllowlist_WithNoPrevious_UsesDefaults()
    {
        var c = Make();
        Assert.False(c.Apply(Rules(false)));
        Assert.Equal(Defaults.Allowlist, c.Current().Allowlist);
    }

    [Fact]
    public void CorruptFile_YieldsLockedDefault()
    {
        File.WriteAllText(P, "{ not json");
        var c = Make().Current();
        Assert.True(c.Locked);
        Assert.Equal("offline_timeout", c.Reason);
        Assert.Equal(Defaults.Allowlist, c.Allowlist);
    }

    [Fact]
    public void SurvivesRestart()
    {
        Make().Apply(Rules(false, "a.exe"));
        _now += TimeSpan.FromMinutes(5);
        var cur = Make().Current();
        Assert.False(cur.Locked);
        Assert.Equal("a.exe", cur.Allowlist.Single().Exe);
    }
}
