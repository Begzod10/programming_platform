using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace PcGuard.Core;

/// <summary>
/// Durable FIFO of usage events waiting for upload, each carrying a non-secret session tag so an
/// event recorded under one sign-in is only ever uploaded with that sign-in's own token (see
/// <see cref="UsageUploadPlanner"/>). Backed by a JSON-lines file rewritten atomically (temp file +
/// rename) on every change; the in-memory copy is authoritative if the disk write fails. Corrupt or
/// untagged lines are skipped on load and never throw. Holds at most <see cref="MaxEvents"/> events
/// across all tags: the oldest overall are dropped first (a tag-agnostic cap). Thread-safe.
/// With <c>persist: false</c> it keeps everything in memory only (used when the data folder could
/// not be secured — nothing sensitive is written to an unprotected location).
/// </summary>
public sealed class UsageQueue
{
    public const int MaxEvents = 20_000;
    public const int MaxBatch = 500;

    private sealed record Line(
        [property: JsonPropertyName("tag")] string? Tag,
        [property: JsonPropertyName("app_name")] string? AppName,
        [property: JsonPropertyName("started_at")] DateTimeOffset? StartedAt,
        [property: JsonPropertyName("ended_at")] DateTimeOffset? EndedAt,
        [property: JsonPropertyName("was_locked")] bool? WasLocked);

    private readonly record struct Entry(string Tag, UsageEvent Ev);

    private readonly string _path;
    private readonly bool _persist;
    private readonly object _lock = new();
    private readonly List<Entry> _items;

    public UsageQueue(string path, bool persist = true)
    {
        _path = path;
        _persist = persist;
        _items = persist ? Load(path) : new List<Entry>();
        if (_items.Count > MaxEvents) _items.RemoveRange(0, _items.Count - MaxEvents);
    }

    public int Count
    {
        get { lock (_lock) return _items.Count; }
    }

    /// <summary>Tags present in the queue, each once, ordered by their first (oldest) event.</summary>
    public IReadOnlyList<string> Tags()
    {
        lock (_lock)
        {
            var seen = new HashSet<string>();
            var order = new List<string>();
            foreach (var it in _items)
                if (seen.Add(it.Tag)) order.Add(it.Tag);
            return order;
        }
    }

    public void Enqueue(string tag, IEnumerable<UsageEvent> events)
    {
        if (string.IsNullOrWhiteSpace(tag)) throw new ArgumentException("A session tag is required", nameof(tag));
        ArgumentNullException.ThrowIfNull(events);
        var valid = events.Where(IsValid).Select(e => new Entry(tag, e)).ToList();
        if (valid.Count == 0) return;
        lock (_lock)
        {
            _items.AddRange(valid);
            if (_items.Count > MaxEvents) _items.RemoveRange(0, _items.Count - MaxEvents);
            Save();
        }
    }

    /// <summary>Oldest first, at most min(max, 500) events of <paramref name="tag"/>. Does not remove anything.</summary>
    public IReadOnlyList<UsageEvent> PeekBatch(string tag, int max)
    {
        var cap = Math.Min(max, MaxBatch);
        if (cap <= 0) return Array.Empty<UsageEvent>();
        lock (_lock)
        {
            var result = new List<UsageEvent>(Math.Min(cap, _items.Count));
            foreach (var it in _items)
            {
                if (it.Tag != tag) continue;
                result.Add(it.Ev);
                if (result.Count == cap) break;
            }
            return result;
        }
    }

    /// <summary>Drops the first <paramref name="count"/> events of <paramref name="tag"/> (no-op if count &lt;= 0).</summary>
    public void Remove(string tag, int count)
    {
        if (count <= 0) return;
        lock (_lock)
        {
            var removed = 0;
            _items.RemoveAll(it => it.Tag == tag && removed < count && ++removed > 0);
            if (removed > 0) Save();
        }
    }

    /// <summary>Drops every event of <paramref name="tag"/>.</summary>
    public void DropTag(string tag)
    {
        lock (_lock)
        {
            if (_items.RemoveAll(it => it.Tag == tag) > 0) Save();
        }
    }

    private static bool IsValid(UsageEvent? e)
        => e is not null && !string.IsNullOrWhiteSpace(e.AppName) && e.EndedAt > e.StartedAt;

    private static List<Entry> Load(string path)
    {
        var result = new List<Entry>();
        string text;
        try
        {
            if (!File.Exists(path)) return result;
            text = Encoding.UTF8.GetString(File.ReadAllBytes(path)); // invalid bytes become U+FFFD
        }
        catch
        {
            return result;
        }

        foreach (var raw in text.Split('\n'))
        {
            var line = raw.Trim();
            if (line.Length == 0) continue;
            try
            {
                var l = JsonSerializer.Deserialize<Line>(line);
                if (l is { Tag: { } tag, AppName: { } name, StartedAt: { } s, EndedAt: { } en, WasLocked: { } wl }
                    && !string.IsNullOrWhiteSpace(tag))
                {
                    var e = new UsageEvent(name, s, en, wl);
                    if (IsValid(e)) result.Add(new Entry(tag, e));
                }
            }
            catch
            {
                // corrupt line: skip
            }
        }
        return result;
    }

    private void Save()
    {
        if (!_persist) return;
        try
        {
            var dir = Path.GetDirectoryName(Path.GetFullPath(_path));
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            var sb = new StringBuilder();
            foreach (var it in _items)
                sb.Append(JsonSerializer.Serialize(new Line(it.Tag, it.Ev.AppName, it.Ev.StartedAt, it.Ev.EndedAt, it.Ev.WasLocked))).Append('\n');
            var tmp = _path + ".tmp";
            File.WriteAllText(tmp, sb.ToString(), new UTF8Encoding(false));
            File.Move(tmp, _path, overwrite: true);
        }
        catch
        {
            // best effort: the in-memory queue stays authoritative and the next change retries the write
        }
    }
}
