using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class ExtraAllowlistTests
{
    private static readonly DateTimeOffset Now = new(2026, 11, 4, 10, 0, 0, TimeSpan.Zero);

    // ---------------- name rule ----------------

    [Theory]
    [InlineData("anydesk.exe")]
    [InlineData("AnyDesk.EXE")]
    [InlineData("a.exe")]                      // 5 chars: minimum
    [InlineData("my-tool_v2.1.exe")]
    [InlineData("TeamViewer_Service.exe")]
    public void Valid_names(string name) => Assert.True(ExtraAllowlist.IsValidName(name));

    [Theory]
    [InlineData("")]
    [InlineData(".exe")]                       // 4 chars
    [InlineData("anydesk")]                    // no .exe
    [InlineData("anydesk.com")]
    [InlineData("anydesk.exe.txt")]
    [InlineData("any desk.exe")]               // space
    [InlineData(" anydesk.exe")]
    [InlineData("anydesk.exe ")]
    [InlineData(@"C:\Tools\anydesk.exe")]      // path
    [InlineData("tools/anydesk.exe")]
    [InlineData(@"..\anydesk.exe")]
    [InlineData("*.exe")]                      // wildcard
    [InlineData("any?esk.exe")]
    [InlineData("anydesk.exe,cmd.exe")]
    [InlineData("anydesk.exe;x")]
    [InlineData("\"anydesk.exe\"")]
    [InlineData("anydésk.exe")]                // non-ASCII letter
    [InlineData("anydesk\t.exe")]
    public void Invalid_names(string name) => Assert.False(ExtraAllowlist.IsValidName(name));

    [Fact]
    public void Null_is_invalid() => Assert.False(ExtraAllowlist.IsValidName(null));

    [Fact]
    public void Length_limit_is_64()
    {
        var n64 = new string('a', 60) + ".exe";
        var n65 = new string('a', 61) + ".exe";
        Assert.Equal(64, n64.Length);
        Assert.True(ExtraAllowlist.IsValidName(n64));
        Assert.False(ExtraAllowlist.IsValidName(n65));
    }

    // ---------------- Parse ----------------

    [Fact]
    public void Parse_splits_valid_and_rejected_and_lowercases()
    {
        var (valid, rejected) = ExtraAllowlist.Parse(new[] { "AnyDesk.exe", "bad name.exe", "rustdesk.exe", @"C:\x.exe" });
        Assert.Equal(new[] { "anydesk.exe", "rustdesk.exe" }, valid);
        Assert.Equal(new[] { "bad name.exe", @"C:\x.exe" }, rejected);
    }

    [Fact]
    public void Parse_empty_input_gives_empty_lists()
    {
        var (valid, rejected) = ExtraAllowlist.Parse(Array.Empty<string>());
        Assert.Empty(valid);
        Assert.Empty(rejected);
    }

    [Fact]
    public void Parse_null_sequence_gives_empty_lists()
    {
        var (valid, rejected) = ExtraAllowlist.Parse(null);
        Assert.Empty(valid);
        Assert.Empty(rejected);
    }

    [Fact]
    public void Parse_drops_case_insensitive_duplicates_silently()
    {
        var (valid, rejected) = ExtraAllowlist.Parse(new[] { "anydesk.exe", "ANYDESK.EXE", "AnyDesk.exe" });
        Assert.Equal(new[] { "anydesk.exe" }, valid);
        Assert.Empty(rejected);
    }

    [Fact]
    public void Parse_null_and_empty_entries_are_rejected()
    {
        var (valid, rejected) = ExtraAllowlist.Parse(new string?[] { null, "", "a.exe" });
        Assert.Equal(new[] { "a.exe" }, valid);
        Assert.Equal(2, rejected.Count);
    }

    [Fact]
    public void Parse_keeps_at_most_16_and_rejects_the_rest()
    {
        var names = Enumerable.Range(1, 17).Select(i => $"app{i}.exe").ToList();
        var (valid, rejected) = ExtraAllowlist.Parse(names);
        Assert.Equal(16, valid.Count);
        Assert.Equal(names.Take(16), valid);
        Assert.Equal(new[] { "app17.exe" }, rejected);
    }

    [Fact]
    public void Parse_invalid_entries_do_not_use_up_the_16_slots()
    {
        var names = new[] { "bad name.exe" }.Concat(Enumerable.Range(1, 16).Select(i => $"app{i}.exe")).ToList();
        var (valid, rejected) = ExtraAllowlist.Parse(names);
        Assert.Equal(16, valid.Count);
        Assert.Equal(new[] { "bad name.exe" }, rejected);
    }

    [Fact]
    public void Max_entries_is_16() => Assert.Equal(16, ExtraAllowlist.MaxEntries);

    // ---------------- Merge ----------------

    [Fact]
    public void Merge_appends_extras_without_publisher()
    {
        var rules = new[] { new AllowEntry("code.exe", null) };
        var merged = ExtraAllowlist.Merge(rules, new[] { "anydesk.exe" });
        Assert.Equal(new[] { new AllowEntry("code.exe", null), new AllowEntry("anydesk.exe", null) }, merged);
    }

    [Fact]
    public void Merge_with_no_extras_returns_the_same_list()
    {
        var rules = new[] { new AllowEntry("code.exe", null) };
        Assert.Same(rules, ExtraAllowlist.Merge(rules, Array.Empty<string>()));
    }

    [Fact]
    public void Merge_is_deduplicated_case_insensitively_against_existing_entries()
    {
        var rules = new[] { new AllowEntry("AnyDesk.exe", null), new AllowEntry("code.exe", null) };
        var merged = ExtraAllowlist.Merge(rules, new[] { "anydesk.exe", "ANYDESK.EXE" });
        Assert.Equal(rules, merged);
    }

    [Fact]
    public void Merge_deduplicates_within_extras()
    {
        var merged = ExtraAllowlist.Merge(Array.Empty<AllowEntry>(), new[] { "a.exe", "A.EXE" });
        Assert.Equal(new[] { new AllowEntry("a.exe", null) }, merged);
    }

    [Fact]
    public void Merge_adds_a_publisher_free_entry_next_to_a_publisher_bound_one()
    {
        // the extra app must stay alive whatever its file metadata says
        var rules = new[] { new AllowEntry("anydesk.exe", "AnyDesk Software") };
        var merged = ExtraAllowlist.Merge(rules, new[] { "anydesk.exe" });
        Assert.Equal(new[] { new AllowEntry("anydesk.exe", "AnyDesk Software"), new AllowEntry("anydesk.exe", null) }, merged);
    }

    [Fact]
    public void Merge_does_not_modify_the_defaults()
    {
        var before = Defaults.Allowlist.ToList();
        var merged = ExtraAllowlist.Merge(Defaults.Allowlist, new[] { "anydesk.exe" });
        Assert.Equal(before, Defaults.Allowlist);
        Assert.Equal(before.Count + 1, merged.Count);
        Assert.DoesNotContain(Defaults.Allowlist, e => e.Exe == "anydesk.exe");
    }

    // ---------------- Apply: every state ----------------

    private static readonly string[] Extras = { "anydesk.exe" };

    private static bool Allows(PcRules r, string exe) => r.Allowlist.Any(e => e.Exe == exe && e.Publisher is null);

    [Fact]
    public void Apply_keeps_every_other_field()
    {
        var r = new PcRules(true, "quota_pending", 3, "Ali", new[] { new AllowEntry("code.exe", null) }, new[] { "example.uz" });
        var a = ExtraAllowlist.Apply(r, Extras);
        Assert.Equal(r with { Allowlist = a.Allowlist }, a);
        Assert.True(Allows(a, "anydesk.exe"));
        Assert.True(Allows(a, "code.exe"));
    }

    [Fact]
    public void Apply_without_extras_returns_the_same_rules()
    {
        var r = new PcRules(true, "x", 0, null, Defaults.Allowlist, Array.Empty<string>());
        Assert.Same(r, ExtraAllowlist.Apply(r, Array.Empty<string>()));
    }

    [Fact]
    public void Signed_out_with_defaults_includes_extras()
    {
        var cache = new RuleCache(Path.Combine(Path.GetTempPath(), "never-" + Guid.NewGuid().ToString("N")), TimeSpan.FromMinutes(10), () => Now, persist: false);
        var r = ExtraAllowlist.Apply(SessionRules.SignedOut(cache.Current()), Extras);
        Assert.True(r.Locked);
        Assert.Equal("no_student", r.Reason);
        Assert.True(Allows(r, "anydesk.exe"));
        Assert.All(Defaults.Allowlist, d => Assert.Contains(d, r.Allowlist));
    }

    [Fact]
    public void Fail_closed_cache_includes_extras()
    {
        // persist:false = data folder could not be secured: locked with the default allowlist
        var cache = new RuleCache("unused", TimeSpan.FromMinutes(10), () => Now, persist: false);
        var r = ExtraAllowlist.Apply(cache.Current(), Extras);
        Assert.True(r.Locked);
        Assert.Equal("offline_timeout", r.Reason);
        Assert.True(Allows(r, "anydesk.exe"));
    }

    [Fact]
    public void Signed_in_student_rules_include_extras_and_nothing_else_changes()
    {
        var now = Now;
        var cache = new RuleCache("unused", TimeSpan.FromMinutes(10), () => now, persist: false);
        cache.Apply(new PcRules(true, "quota_pending", 2, "Ali", new[] { new AllowEntry("code.exe", null) }, new[] { "example.uz" }));
        var r = ExtraAllowlist.Apply(cache.Current(), Extras);
        Assert.Equal(new[] { "code.exe", "anydesk.exe" }, r.Allowlist.Select(e => e.Exe));
        Assert.Equal(new[] { "example.uz" }, r.BrowserHosts);
    }

    [Fact]
    public void Offline_cache_includes_extras()
    {
        var now = Now;
        var cache = new RuleCache("unused", TimeSpan.FromMinutes(10), () => now, persist: false);
        cache.Apply(new PcRules(false, "ok", 0, "Ali", new[] { new AllowEntry("code.exe", null) }, Array.Empty<string>()));
        now = now.AddMinutes(11); // cache too old: offline_timeout, locked, cached allowlist
        var r = ExtraAllowlist.Apply(cache.Current(), Extras);
        Assert.True(r.Locked);
        Assert.Equal("offline_timeout", r.Reason);
        Assert.Equal(new[] { "code.exe", "anydesk.exe" }, r.Allowlist.Select(e => e.Exe));
    }

    [Fact]
    public void Extras_are_not_stored_in_the_rule_cache()
    {
        var now = Now;
        var cache = new RuleCache("unused", TimeSpan.FromMinutes(10), () => now, persist: false);
        cache.Apply(new PcRules(true, "quota_pending", 2, "Ali", new[] { new AllowEntry("code.exe", null) }, Array.Empty<string>()));
        _ = ExtraAllowlist.Apply(cache.Current(), Extras);
        Assert.DoesNotContain(cache.Current().Allowlist, e => e.Exe == "anydesk.exe");
    }

    [Fact]
    public void Maintenance_on_top_still_unlocks()
    {
        var r = SessionRules.WithMaintenance(ExtraAllowlist.Apply(SessionRules.SignedOut(
            new PcRules(true, "x", 0, null, Defaults.Allowlist, Array.Empty<string>())), Extras), true);
        Assert.False(r.Locked);
        Assert.True(Allows(r, "anydesk.exe"));
    }

    // ---------------- enforcement with extras ----------------

    private static readonly RunningProcess[] Procs =
    {
        new(201, "AnyDesk.exe", null, false, false),
        new(202, "notepad.exe", null, false, true),
        new(203, "game.exe", null, false, false),
    };

    private static Snapshot WindowedAll() =>
        new(Procs.Select(p => new WindowedProc(p.Pid, p.Exe)).ToList(), null, Array.Empty<BrowserWindow>());

    [Fact]
    public void Locked_fresh_extra_app_survives_others_are_killed()
    {
        var rules = ExtraAllowlist.Apply(SessionRules.SignedOut(
            new PcRules(true, "x", 0, null, Defaults.Allowlist, Array.Empty<string>())), Extras);
        var plan = EnforcementPlanner.Plan(rules, WindowedAll(), Now, Now, Procs);
        Assert.Equal(new[] { 202, 203 }, plan.KillPids);
    }

    [Fact]
    public void Locked_fallback_extra_app_survives()
    {
        var rules = ExtraAllowlist.Apply(new PcRules(true, "offline_timeout", 0, null, Defaults.Allowlist, new[] { "example.uz" }), Extras);
        var plan = EnforcementPlanner.Plan(rules, null, DateTimeOffset.MinValue, Now, Procs);
        Assert.True(plan.UsedFallback);
        Assert.Equal(new[] { 203 }, plan.KillPids); // notepad: system image, spared in fallback
    }

    [Fact]
    public void Without_extras_the_app_is_killed()
    {
        var rules = new PcRules(true, "x", 0, null, Defaults.Allowlist, Array.Empty<string>());
        var plan = EnforcementPlanner.Plan(rules, WindowedAll(), Now, Now, Procs);
        Assert.Contains(201, plan.KillPids);
    }

    // ---------------- install-time validation (Setup) ----------------

    [Fact]
    public void ValidateForInstall_accepts_and_normalises()
    {
        var (names, error) = ExtraAllowlist.ValidateForInstall(new[] { "AnyDesk.exe", "anydesk.exe", "rustdesk.exe" });
        Assert.Null(error);
        Assert.Equal(new[] { "anydesk.exe", "rustdesk.exe" }, names);
    }

    [Fact]
    public void ValidateForInstall_refuses_an_invalid_name()
    {
        var (names, error) = ExtraAllowlist.ValidateForInstall(new[] { "anydesk.exe", @"C:\x\evil.exe" });
        Assert.Empty(names);
        Assert.NotNull(error);
        Assert.Contains(@"C:\x\evil.exe", error);
    }

    [Fact]
    public void ValidateForInstall_refuses_17()
    {
        var (names, error) = ExtraAllowlist.ValidateForInstall(Enumerable.Range(1, 17).Select(i => $"app{i}.exe"));
        Assert.Empty(names);
        Assert.NotNull(error);
        Assert.Contains("16", error);
    }

    [Fact]
    public void ValidateForInstall_16_distinct_are_fine()
    {
        var (names, error) = ExtraAllowlist.ValidateForInstall(Enumerable.Range(1, 16).Select(i => $"app{i}.exe"));
        Assert.Null(error);
        Assert.Equal(16, names.Count);
    }

    [Fact]
    public void SplitList_splits_on_commas_and_trims()
    {
        Assert.Equal(new[] { "anydesk.exe", "rustdesk.exe" }, ExtraAllowlist.SplitList(" anydesk.exe , rustdesk.exe ,, "));
        Assert.Empty(ExtraAllowlist.SplitList(""));
        Assert.Empty(ExtraAllowlist.SplitList("   "));
        Assert.Empty(ExtraAllowlist.SplitList(null));
    }
}
