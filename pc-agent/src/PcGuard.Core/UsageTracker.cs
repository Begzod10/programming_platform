namespace PcGuard.Core;

public sealed record UsageEvent(string AppName, DateTimeOffset StartedAt, DateTimeOffset EndedAt, bool WasLocked);

/// <summary>
/// Collapses periodic foreground-app observations into usage events.
/// Records only app name, start/end and lock flag (no titles, URLs or paths).
/// Thread-safe: Observe runs on the guard loop, Drain on the uploader.
/// </summary>
public sealed class UsageTracker
{
    // Server rejects events longer than 12 h; stay safely below.
    private static readonly TimeSpan MaxChunk = TimeSpan.FromHours(12) - TimeSpan.FromMinutes(1);
    private static readonly TimeSpan MinDuration = TimeSpan.FromSeconds(1);

    // Observe runs about every 2 s; a longer silence means sleep/suspend or a stalled loop.
    private static readonly TimeSpan MaxObserveGap = TimeSpan.FromSeconds(30);

    private readonly Func<DateTimeOffset> _clock;
    private readonly object _lock = new();
    private readonly List<UsageEvent> _closed = new();
    private string? _exe;
    private bool _locked;
    private DateTimeOffset _start;
    private DateTimeOffset _lastSeen;

    public UsageTracker(Func<DateTimeOffset> clock) => _clock = clock;

    public void Observe(string? exe, bool locked)
    {
        lock (_lock)
        {
            var now = _clock();
            var name = string.IsNullOrWhiteSpace(exe) ? null : exe.ToLowerInvariant();
            if (_exe is not null)
            {
                if (now < _start) _exe = null; // clock went backwards: discard open interval
                else if (now - _lastSeen > MaxObserveGap) CloseOpen(_lastSeen); // slept/stalled: do not count the gap
                else if (name != _exe || locked != _locked) CloseOpen(now);
                else EmitFullChunks(now);
            }
            _lastSeen = now;
            if (name is not null && _exe is null)
            {
                _exe = name;
                _locked = locked;
                _start = now;
            }
        }
    }

    public IReadOnlyList<UsageEvent> Drain()
    {
        lock (_lock)
        {
            var now = _clock();
            if (_exe is not null)
            {
                if (now < _start) _exe = null;
                else if (now - _lastSeen > MaxObserveGap) CloseOpen(_lastSeen); // stale: nothing stays open
                else
                {
                    EmitFullChunks(now);
                    if (now - _start >= MinDuration)
                    {
                        _closed.Add(new UsageEvent(_exe, _start, now, _locked));
                        _start = now; // keep tracking the same app from now on
                        _lastSeen = now;
                    }
                    // else: slice < 1 s stays in the open interval so it is not lost
                }
            }
            var result = _closed.ToArray();
            _closed.Clear();
            return result;
        }
    }

    // Emits whole max-size chunks while the open interval exceeds the cap, reopening after each.
    private void EmitFullChunks(DateTimeOffset now)
    {
        while (now - _start > MaxChunk)
        {
            _closed.Add(new UsageEvent(_exe!, _start, _start + MaxChunk, _locked));
            _start += MaxChunk;
        }
    }

    private void CloseOpen(DateTimeOffset end)
    {
        EmitFullChunks(end);
        if (end - _start >= MinDuration)
            _closed.Add(new UsageEvent(_exe!, _start, end, _locked));
        _exe = null;
    }
}
