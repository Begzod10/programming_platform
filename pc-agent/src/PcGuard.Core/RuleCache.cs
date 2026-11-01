using System.Text.Json;

namespace PcGuard.Core;

public static class Defaults
{
    public static readonly IReadOnlyList<AllowEntry> Allowlist = Array.AsReadOnly(new[]
    {
        "code.exe", "windowsterminal.exe", "cmd.exe", "powershell.exe",
        "python.exe", "node.exe", "chrome.exe", "msedge.exe",
    }.Select(e => new AllowEntry(e, null)).ToArray());
}

public class RuleCache
{
    private sealed record Stored(PcRules Rules, DateTimeOffset AppliedAt);

    private readonly string _path;
    private readonly TimeSpan _maxAge;
    private readonly Func<DateTimeOffset> _clock;
    private readonly bool _persist;
    private readonly object _lock = new();
    private Stored? _stored;

    /// <param name="persist">When false, nothing is read from or written to disk (used when the data
    /// folder could not be secured): the cache starts empty, so Current() fails closed to locked with
    /// the default allowlist.</param>
    public RuleCache(string path, TimeSpan maxAge, Func<DateTimeOffset> clock, bool persist = true)
    {
        _path = path;
        _maxAge = maxAge;
        _clock = clock;
        _persist = persist;
        _stored = persist ? Load() : null;
    }

    /// <summary>Stores incoming rules. Returns false (and keeps the previous allowlist) when the incoming allowlist is empty.</summary>
    public bool Apply(PcRules incoming)
    {
        lock (_lock)
        {
            var valid = incoming.Allowlist.Count > 0;
            var rules = valid
                ? incoming
                : incoming with { Allowlist = _stored?.Rules.Allowlist is { Count: > 0 } prev ? prev : Defaults.Allowlist };
            _stored = new Stored(rules, _clock());
            Save(_stored);
            return valid;
        }
    }

    public PcRules Current()
    {
        lock (_lock)
        {
            if (_stored is { } s)
            {
                var age = _clock() - s.AppliedAt;
                // negative age (clock moved backwards / future timestamp) counts as expired
                if (age >= TimeSpan.Zero && age <= _maxAge)
                    return s.Rules;
            }
            return new PcRules(
                true, "offline_timeout", 0, null,
                _stored?.Rules.Allowlist is { Count: > 0 } a ? a : Defaults.Allowlist,
                _stored?.Rules.BrowserHosts ?? Array.Empty<string>());
        }
    }

    private Stored? Load()
    {
        try
        {
            if (!File.Exists(_path)) return null;
            var s = JsonSerializer.Deserialize<Stored>(File.ReadAllText(_path));
            if (s?.Rules is null) return null;
            var allow = (s.Rules.Allowlist ?? Array.Empty<AllowEntry>())
                .Where(a => a is not null && !string.IsNullOrWhiteSpace(a.Exe)).ToList();
            var hosts = (s.Rules.BrowserHosts ?? Array.Empty<string>())
                .Where(h => !string.IsNullOrWhiteSpace(h)).ToList();
            return new Stored(s.Rules with
            {
                Reason = s.Rules.Reason ?? "unknown",
                Allowlist = allow,
                BrowserHosts = hosts,
            }, s.AppliedAt);
        }
        catch
        {
            return null;
        }
    }

    private void Save(Stored s)
    {
        if (!_persist) return;
        try
        {
            var dir = Path.GetDirectoryName(Path.GetFullPath(_path));
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            var tmp = _path + ".tmp";
            File.WriteAllText(tmp, JsonSerializer.Serialize(s));
            File.Move(tmp, _path, overwrite: true);
        }
        catch
        {
            // persistence is best-effort; in-memory state remains authoritative
        }
    }
}
