using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace PcGuard.Core;

/// <summary>
/// Durable FIFO of usage events waiting for upload. Backed by a JSON-lines file that is rewritten
/// atomically (temp file + rename) on every change; the in-memory copy is authoritative if the disk
/// write fails. Corrupt lines are skipped on load and never throw. Holds at most
/// <see cref="MaxEvents"/> events: the oldest are dropped first.
/// Thread-safe. Intended use is a single uploader doing PeekBatch -> upload -> Remove(n) while no
/// other thread calls Remove; Enqueue from elsewhere is safe except that hitting the cap between a
/// peek and its Remove would shift the head (the uploader should Enqueue on its own thread).
/// </summary>
public sealed class UsageQueue
{
    public const int MaxEvents = 20_000;
    public const int MaxBatch = 500;

    private sealed record Line(
        [property: JsonPropertyName("app_name")] string? AppName,
        [property: JsonPropertyName("started_at")] DateTimeOffset? StartedAt,
        [property: JsonPropertyName("ended_at")] DateTimeOffset? EndedAt,
        [property: JsonPropertyName("was_locked")] bool? WasLocked);

    private readonly string _path;
    private readonly object _lock = new();
    private readonly List<UsageEvent> _items;

    public UsageQueue(string path)
    {
        _path = path;
        _items = Load(path);
        if (_items.Count > MaxEvents) _items.RemoveRange(0, _items.Count - MaxEvents);
    }

    public int Count
    {
        get { lock (_lock) return _items.Count; }
    }

    public void Enqueue(IEnumerable<UsageEvent> events)
    {
        ArgumentNullException.ThrowIfNull(events);
        var valid = events.Where(IsValid).ToList();
        if (valid.Count == 0) return;
        lock (_lock)
        {
            _items.AddRange(valid);
            if (_items.Count > MaxEvents) _items.RemoveRange(0, _items.Count - MaxEvents);
            Save();
        }
    }

    /// <summary>Oldest first, at most min(max, 500) events. Does not remove anything.</summary>
    public IReadOnlyList<UsageEvent> PeekBatch(int max)
    {
        lock (_lock)
        {
            var n = Math.Min(Math.Min(max, MaxBatch), _items.Count);
            return n <= 0 ? Array.Empty<UsageEvent>() : _items.GetRange(0, n).ToArray();
        }
    }

    /// <summary>Drops the first <paramref name="count"/> events (all if count exceeds Count; no-op if count &lt;= 0).</summary>
    public void Remove(int count)
    {
        if (count <= 0) return;
        lock (_lock)
        {
            _items.RemoveRange(0, Math.Min(count, _items.Count));
            Save();
        }
    }

    private static bool IsValid(UsageEvent? e)
        => e is not null && !string.IsNullOrWhiteSpace(e.AppName) && e.EndedAt > e.StartedAt;

    private static List<UsageEvent> Load(string path)
    {
        var result = new List<UsageEvent>();
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
                if (l is { AppName: { } name, StartedAt: { } s, EndedAt: { } en, WasLocked: { } wl })
                {
                    var e = new UsageEvent(name, s, en, wl);
                    if (IsValid(e)) result.Add(e);
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
        try
        {
            var dir = Path.GetDirectoryName(Path.GetFullPath(_path));
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            var sb = new StringBuilder();
            foreach (var e in _items)
                sb.Append(JsonSerializer.Serialize(new Line(e.AppName, e.StartedAt, e.EndedAt, e.WasLocked))).Append('\n');
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
