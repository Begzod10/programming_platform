using PcGuard.Core;

namespace PcGuard.Core.Tests;

public sealed class UsageQueueTests : IDisposable
{
    private static readonly DateTimeOffset T0 = new(2026, 10, 23, 9, 0, 0, TimeSpan.FromHours(5));
    private readonly string _dir = Path.Combine(Path.GetTempPath(), "pcguard-uq-" + Guid.NewGuid().ToString("N"));
    private string QueuePath => Path.Combine(_dir, "usage.queue");

    public void Dispose()
    {
        try { Directory.Delete(_dir, recursive: true); } catch { /* best effort */ }
    }

    private static UsageEvent Ev(int i, bool locked = false)
        => new($"app{i}.exe", T0.AddSeconds(i * 10), T0.AddSeconds(i * 10 + 5), locked);

    [Fact]
    public void EmptyQueueWhenFileMissing()
    {
        var q = new UsageQueue(QueuePath);
        Assert.Equal(0, q.Count);
        Assert.Empty(q.PeekBatch(10));
    }

    [Fact]
    public void PersistsAcrossInstances()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(new[] { Ev(1), Ev(2, locked: true) });
        var q2 = new UsageQueue(QueuePath);
        Assert.Equal(2, q2.Count);
        Assert.Equal(new[] { Ev(1), Ev(2, locked: true) }, q2.PeekBatch(10));
    }

    [Fact]
    public void PreservesOffsetsExactly()
    {
        var e = new UsageEvent("code.exe", new DateTimeOffset(2026, 1, 2, 3, 4, 5, 678, TimeSpan.FromHours(5)),
            new DateTimeOffset(2026, 1, 2, 3, 5, 0, TimeSpan.FromHours(5)), false);
        new UsageQueue(QueuePath).Enqueue(new[] { e });
        var back = Assert.Single(new UsageQueue(QueuePath).PeekBatch(1));
        Assert.Equal(e, back);
        Assert.Equal(TimeSpan.FromHours(5), back.StartedAt.Offset);
    }

    [Fact]
    public void PeekBatchIsOldestFirstAndLimited()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(Enumerable.Range(0, 5).Select(i => Ev(i)));
        q.Enqueue(new[] { Ev(5) });
        Assert.Equal(new[] { Ev(0), Ev(1), Ev(2) }, q.PeekBatch(3));
        Assert.Equal(6, q.Count); // peek does not remove
    }

    [Fact]
    public void PeekBatchIsCappedAt500()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(Enumerable.Range(0, 700).Select(i => Ev(i)));
        Assert.Equal(500, q.PeekBatch(10_000).Count);
        Assert.Empty(q.PeekBatch(0));
        Assert.Empty(q.PeekBatch(-1));
    }

    [Fact]
    public void RemoveDropsFirstCountAndPersists()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(Enumerable.Range(0, 4).Select(i => Ev(i)));
        q.Remove(2);
        Assert.Equal(new[] { Ev(2), Ev(3) }, q.PeekBatch(10));
        Assert.Equal(new[] { Ev(2), Ev(3) }, new UsageQueue(QueuePath).PeekBatch(10));
    }

    [Fact]
    public void RemoveMoreThanCountEmptiesAndNonPositiveIsNoOp()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(new[] { Ev(1), Ev(2) });
        q.Remove(0);
        q.Remove(-3);
        Assert.Equal(2, q.Count);
        q.Remove(99);
        Assert.Equal(0, q.Count);
        Assert.Equal(0, new UsageQueue(QueuePath).Count);
    }

    [Fact]
    public void CorruptLinesAreSkipped()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(new[] { Ev(1), Ev(2) });
        var lines = File.ReadAllLines(QueuePath).ToList();
        lines.Insert(1, "{not json");
        lines.Insert(0, "{\"app_name\":\"x.exe\"}");           // missing fields
        lines.Add("[1,2,3]");
        lines.Add("{\"app_name\":\"\",\"started_at\":\"2026-10-23T09:00:00+05:00\",\"ended_at\":\"2026-10-23T09:00:05+05:00\",\"was_locked\":false}");
        lines.Add("");
        lines.Add("\0\0\0garbage");
        File.WriteAllLines(QueuePath, lines);
        var q2 = new UsageQueue(QueuePath);
        Assert.Equal(new[] { Ev(1), Ev(2) }, q2.PeekBatch(10));
    }

    [Fact]
    public void BinaryGarbageFileDoesNotThrow()
    {
        Directory.CreateDirectory(_dir);
        File.WriteAllBytes(QueuePath, new byte[] { 0xFF, 0xFE, 0x00, 0x01, 0x0A, 0xC3 });
        var q = new UsageQueue(QueuePath);
        Assert.Equal(0, q.Count);
        q.Enqueue(new[] { Ev(1) });
        Assert.Equal(1, new UsageQueue(QueuePath).Count);
    }

    [Fact]
    public void CapDropsOldest()
    {
        Assert.Equal(20_000, UsageQueue.MaxEvents);
        var q = new UsageQueue(QueuePath);
        q.Enqueue(Enumerable.Range(0, 19_999).Select(i => Ev(i)));
        q.Enqueue(new[] { Ev(100_000), Ev(100_001), Ev(100_002) });
        Assert.Equal(20_000, q.Count);
        Assert.Equal(Ev(2), q.PeekBatch(1)[0]);
        Assert.Equal(20_000, new UsageQueue(QueuePath).Count);
    }

    [Fact]
    public void LoadingAnOversizedFileKeepsNewest()
    {
        Directory.CreateDirectory(_dir);
        var q = new UsageQueue(QueuePath);
        q.Enqueue(Enumerable.Range(0, 20_000).Select(i => Ev(i)));
        File.AppendAllLines(QueuePath, File.ReadLines(QueuePath).Take(5).ToList());
        var q2 = new UsageQueue(QueuePath);
        Assert.Equal(20_000, q2.Count);
        Assert.Equal(Ev(5), q2.PeekBatch(1)[0]);
    }

    [Fact]
    public void EnqueueEmptyIsNoOp()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(Array.Empty<UsageEvent>());
        Assert.Equal(0, q.Count);
    }

    [Fact]
    public void InvalidEventsAreNotQueued()
    {
        // the server rejects a whole batch with 422 for one bad event, so never queue one
        var q = new UsageQueue(QueuePath);
        q.Enqueue(new[]
        {
            new UsageEvent("", T0, T0.AddSeconds(5), false),
            new UsageEvent("a.exe", T0, T0, false),
            new UsageEvent("b.exe", T0.AddSeconds(5), T0, false),
            Ev(1),
        });
        Assert.Equal(new[] { Ev(1) }, q.PeekBatch(10));
    }

    [Fact]
    public void NoTempFileLeftBehind()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(new[] { Ev(1) });
        q.Remove(1);
        Assert.Equal(new[] { "usage.queue" }, Directory.GetFiles(_dir).Select(Path.GetFileName));
    }

    [Fact]
    public void ConcurrentEnqueueLosesNothing()
    {
        var q = new UsageQueue(QueuePath);
        Parallel.For(0, 8, t => { for (var i = 0; i < 25; i++) q.Enqueue(new[] { Ev(t * 1000 + i) }); });
        Assert.Equal(200, q.Count);
        Assert.Equal(200, new UsageQueue(QueuePath).Count);
    }
}
