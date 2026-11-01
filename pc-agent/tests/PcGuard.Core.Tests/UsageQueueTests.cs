using PcGuard.Core;

namespace PcGuard.Core.Tests;

public sealed class UsageQueueTests : IDisposable
{
    private const string S1 = "sess-one";
    private const string S2 = "sess-two";
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
        Assert.Empty(q.Tags());
        Assert.Empty(q.PeekBatch(S1, 10));
    }

    [Fact]
    public void PersistsEventsAndTagAcrossInstances()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(S1, new[] { Ev(1), Ev(2, locked: true) });
        var q2 = new UsageQueue(QueuePath);
        Assert.Equal(2, q2.Count);
        Assert.Equal(new[] { S1 }, q2.Tags());
        Assert.Equal(new[] { Ev(1), Ev(2, locked: true) }, q2.PeekBatch(S1, 10));
    }

    [Fact]
    public void PreservesOffsetsExactly()
    {
        var e = new UsageEvent("code.exe", new DateTimeOffset(2026, 1, 2, 3, 4, 5, 678, TimeSpan.FromHours(5)),
            new DateTimeOffset(2026, 1, 2, 3, 5, 0, TimeSpan.FromHours(5)), false);
        new UsageQueue(QueuePath).Enqueue(S1, new[] { e });
        var back = Assert.Single(new UsageQueue(QueuePath).PeekBatch(S1, 1));
        Assert.Equal(e, back);
        Assert.Equal(TimeSpan.FromHours(5), back.StartedAt.Offset);
    }

    [Fact]
    public void TagsAreDistinctInFirstSeenOrder()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(S2, new[] { Ev(0) });
        q.Enqueue(S1, new[] { Ev(1) });
        q.Enqueue(S2, new[] { Ev(2) });
        Assert.Equal(new[] { S2, S1 }, q.Tags());
    }

    [Fact]
    public void PeekBatchReturnsOnlyThatTagOldestFirst()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(S1, new[] { Ev(0), Ev(1) });
        q.Enqueue(S2, new[] { Ev(2) });
        q.Enqueue(S1, new[] { Ev(3) });
        Assert.Equal(new[] { Ev(0), Ev(1), Ev(3) }, q.PeekBatch(S1, 10));
        Assert.Equal(new[] { Ev(2) }, q.PeekBatch(S2, 10));
        Assert.Empty(q.PeekBatch("nope", 10));
    }

    [Fact]
    public void PeekBatchIsCappedAt500()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(S1, Enumerable.Range(0, 700).Select(i => Ev(i)));
        Assert.Equal(500, q.PeekBatch(S1, 10_000).Count);
        Assert.Empty(q.PeekBatch(S1, 0));
        Assert.Empty(q.PeekBatch(S1, -1));
    }

    [Fact]
    public void RemoveDropsFirstCountOfTagAndPersists()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(S1, new[] { Ev(0), Ev(1) });
        q.Enqueue(S2, new[] { Ev(2), Ev(3) });
        q.Enqueue(S1, new[] { Ev(4) });
        q.Remove(S1, 2);
        Assert.Equal(new[] { Ev(4) }, q.PeekBatch(S1, 10));
        Assert.Equal(new[] { Ev(2), Ev(3) }, q.PeekBatch(S2, 10)); // other tag untouched
        var reloaded = new UsageQueue(QueuePath);
        Assert.Equal(new[] { Ev(4) }, reloaded.PeekBatch(S1, 10));
        Assert.Equal(new[] { Ev(2), Ev(3) }, reloaded.PeekBatch(S2, 10));
    }

    [Fact]
    public void RemoveMoreThanCountEmptiesTagAndNonPositiveIsNoOp()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(S1, new[] { Ev(1), Ev(2) });
        q.Remove(S1, 0);
        q.Remove(S1, -3);
        Assert.Equal(2, q.Count);
        q.Remove(S1, 99);
        Assert.Equal(0, q.Count);
        Assert.Equal(0, new UsageQueue(QueuePath).Count);
    }

    [Fact]
    public void DropTagRemovesAllOfOneTagOnly()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(S1, new[] { Ev(0), Ev(1) });
        q.Enqueue(S2, new[] { Ev(2) });
        q.DropTag(S1);
        Assert.Equal(new[] { S2 }, q.Tags());
        Assert.Equal(new[] { Ev(2) }, q.PeekBatch(S2, 10));
        Assert.Equal(new[] { S2 }, new UsageQueue(QueuePath).Tags());
    }

    [Fact]
    public void CorruptLinesAreSkipped()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(S1, new[] { Ev(1), Ev(2) });
        var lines = File.ReadAllLines(QueuePath).ToList();
        lines.Insert(1, "{not json");
        lines.Insert(0, "{\"tag\":\"x\",\"app_name\":\"x.exe\"}");           // missing timestamps
        lines.Add("[1,2,3]");
        lines.Add("{\"app_name\":\"notag.exe\",\"started_at\":\"2026-10-23T09:00:00+05:00\",\"ended_at\":\"2026-10-23T09:00:05+05:00\",\"was_locked\":false}"); // no tag
        lines.Add("");
        lines.Add("\0\0\0garbage");
        File.WriteAllLines(QueuePath, lines);
        var q2 = new UsageQueue(QueuePath);
        Assert.Equal(new[] { Ev(1), Ev(2) }, q2.PeekBatch(S1, 10));
        Assert.Equal(new[] { S1 }, q2.Tags());
    }

    [Fact]
    public void BinaryGarbageFileDoesNotThrow()
    {
        Directory.CreateDirectory(_dir);
        File.WriteAllBytes(QueuePath, new byte[] { 0xFF, 0xFE, 0x00, 0x01, 0x0A, 0xC3 });
        var q = new UsageQueue(QueuePath);
        Assert.Equal(0, q.Count);
        q.Enqueue(S1, new[] { Ev(1) });
        Assert.Equal(1, new UsageQueue(QueuePath).Count);
    }

    [Fact]
    public void CapDropsOldestRegardlessOfTag()
    {
        Assert.Equal(20_000, UsageQueue.MaxEvents);
        var q = new UsageQueue(QueuePath);
        q.Enqueue(S1, Enumerable.Range(0, 19_999).Select(i => Ev(i)));
        q.Enqueue(S2, new[] { Ev(100_000), Ev(100_001), Ev(100_002) });
        Assert.Equal(20_000, q.Count);
        Assert.Equal(Ev(2), q.PeekBatch(S1, 1)[0]); // the two oldest S1 events were dropped
        Assert.Equal(3, q.PeekBatch(S2, 10).Count);
        Assert.Equal(20_000, new UsageQueue(QueuePath).Count);
    }

    [Fact]
    public void EnqueueEmptyIsNoOp()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(S1, Array.Empty<UsageEvent>());
        Assert.Equal(0, q.Count);
        Assert.Empty(q.Tags());
    }

    [Fact]
    public void InvalidEventsAreNotQueued()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(S1, new[]
        {
            new UsageEvent("", T0, T0.AddSeconds(5), false),
            new UsageEvent("a.exe", T0, T0, false),
            new UsageEvent("b.exe", T0.AddSeconds(5), T0, false),
            Ev(1),
        });
        Assert.Equal(new[] { Ev(1) }, q.PeekBatch(S1, 10));
    }

    [Fact]
    public void BlankTagIsRejected()
    {
        var q = new UsageQueue(QueuePath);
        Assert.Throws<ArgumentException>(() => q.Enqueue("", new[] { Ev(1) }));
        Assert.Throws<ArgumentException>(() => q.Enqueue("   ", new[] { Ev(1) }));
    }

    [Fact]
    public void NoTempFileLeftBehind()
    {
        var q = new UsageQueue(QueuePath);
        q.Enqueue(S1, new[] { Ev(1) });
        q.Remove(S1, 1);
        Assert.Equal(new[] { "usage.queue" }, Directory.GetFiles(_dir).Select(Path.GetFileName));
    }

    [Fact]
    public void ConcurrentEnqueueLosesNothing()
    {
        var q = new UsageQueue(QueuePath);
        Parallel.For(0, 8, t => { for (var i = 0; i < 25; i++) q.Enqueue(S1, new[] { Ev(t * 1000 + i) }); });
        Assert.Equal(200, q.Count);
        Assert.Equal(200, new UsageQueue(QueuePath).Count);
    }

    [Fact]
    public void PersistDisabledKeepsNothingOnDisk()
    {
        var q = new UsageQueue(QueuePath, persist: false);
        q.Enqueue(S1, new[] { Ev(1), Ev(2) });
        Assert.Equal(2, q.Count);              // in memory
        Assert.False(File.Exists(QueuePath));  // nothing written
        Assert.Equal(0, new UsageQueue(QueuePath).Count);
    }
}
