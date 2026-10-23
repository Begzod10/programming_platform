using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class UsageTrackerTests
{
    private static readonly DateTimeOffset T0 = new(2026, 10, 23, 9, 0, 0, TimeSpan.Zero);

    private sealed class Clock
    {
        public DateTimeOffset Now = T0;
        public void Advance(TimeSpan d) => Now += d;
    }

    private static (UsageTracker t, Clock c) Make()
    {
        var c = new Clock();
        return (new UsageTracker(() => c.Now), c);
    }

    [Fact]
    public void RepeatedObservationsOfOneAppMergeIntoOneEvent()
    {
        var (t, c) = Make();
        t.Observe("code.exe", false);
        c.Advance(TimeSpan.FromSeconds(2)); t.Observe("code.exe", false);
        c.Advance(TimeSpan.FromSeconds(2)); t.Observe("code.exe", false);
        c.Advance(TimeSpan.FromSeconds(2));
        var events = t.Drain();
        var e = Assert.Single(events);
        Assert.Equal("code.exe", e.AppName);
        Assert.Equal(T0, e.StartedAt);
        Assert.Equal(T0.AddSeconds(6), e.EndedAt);
        Assert.False(e.WasLocked);
    }

    [Fact]
    public void AppNameIsLowerCased()
    {
        var (t, c) = Make();
        t.Observe("Chrome.EXE", false);
        c.Advance(TimeSpan.FromSeconds(5));
        Assert.Equal("chrome.exe", Assert.Single(t.Drain()).AppName);
    }

    [Fact]
    public void AppChangeSplitsEvents()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(4)); t.Observe("b.exe", false);
        c.Advance(TimeSpan.FromSeconds(4));
        var ev = t.Drain();
        Assert.Equal(2, ev.Count);
        Assert.Equal("a.exe", ev[0].AppName);
        Assert.Equal(T0.AddSeconds(4), ev[0].EndedAt);
        Assert.Equal("b.exe", ev[1].AppName);
        Assert.Equal(T0.AddSeconds(4), ev[1].StartedAt);
        Assert.Equal(T0.AddSeconds(8), ev[1].EndedAt);
    }

    [Fact]
    public void LockFlagChangeSplitsEvents()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(4)); t.Observe("a.exe", true);
        c.Advance(TimeSpan.FromSeconds(4));
        var ev = t.Drain();
        Assert.Equal(2, ev.Count);
        Assert.False(ev[0].WasLocked);
        Assert.True(ev[1].WasLocked);
    }

    [Fact]
    public void NullExeEndsInterval()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(3)); t.Observe(null, false);
        c.Advance(TimeSpan.FromSeconds(10));
        var e = Assert.Single(t.Drain());
        Assert.Equal(T0.AddSeconds(3), e.EndedAt);
    }

    [Fact]
    public void ShorterThanOneSecondIsDropped()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromMilliseconds(999));
        Assert.Empty(t.Drain());
    }

    [Fact]
    public void ExactlyOneSecondIsKept()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(1));
        Assert.Single(t.Drain());
    }

    [Fact]
    public void DrainTwiceReturnsEventsOnlyOnce()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(5));
        Assert.Single(t.Drain());
        Assert.Empty(t.Drain());
    }

    [Fact]
    public void ContinuingAppAfterDrainKeepsTracking()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(5));
        t.Drain();
        c.Advance(TimeSpan.FromSeconds(5)); t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(5));
        var e = Assert.Single(t.Drain());
        Assert.Equal(T0.AddSeconds(5), e.StartedAt);
        Assert.Equal(T0.AddSeconds(15), e.EndedAt);
    }

    [Fact]
    public void LongIntervalIsSplitBelowTwelveHours()
    {
        var (t, c) = Make();
        for (var i = 0; i <= 30 * 120; i++) { t.Observe("a.exe", false); c.Advance(TimeSpan.FromSeconds(30)); }
        c.Advance(-TimeSpan.FromSeconds(30));
        var ev = t.Drain();
        Assert.True(ev.Count >= 3);
        var max = TimeSpan.FromHours(12) - TimeSpan.FromMinutes(1);
        foreach (var e in ev)
        {
            Assert.True(e.EndedAt > e.StartedAt);
            Assert.True(e.EndedAt - e.StartedAt <= max);
        }
        Assert.Equal(T0, ev[0].StartedAt);
        for (var i = 1; i < ev.Count; i++) Assert.Equal(ev[i - 1].EndedAt, ev[i].StartedAt);
        Assert.Equal(T0.AddHours(30), ev[^1].EndedAt);
    }

    [Fact]
    public void LongIntervalIsSplitDuringObserveToo()
    {
        var (t, c) = Make();
        for (var i = 0; i < 13 * 120; i++) { t.Observe("a.exe", false); c.Advance(TimeSpan.FromSeconds(30)); }
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(5));
        var ev = t.Drain();
        Assert.Equal(2, ev.Count);
        Assert.All(ev, e => Assert.True(e.EndedAt - e.StartedAt < TimeSpan.FromHours(12)));
    }

    [Fact]
    public void ClockMovingBackwardsDiscardsOpenInterval()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(10));
        c.Now = T0.AddSeconds(-60);
        Assert.Empty(t.Drain());
    }

    [Fact]
    public void ClockBackwardsOnObserveRestartsInterval()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Now = T0.AddSeconds(-60); t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(5));
        var e = Assert.Single(t.Drain());
        Assert.Equal(T0.AddSeconds(-60), e.StartedAt);
        Assert.Equal(T0.AddSeconds(-55), e.EndedAt);
    }

    [Fact]
    public void SameAppAfterLongGapEndsAtLastObservationAndStartsFresh()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(10)); t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromDays(2)); t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(10));
        var ev = t.Drain();
        Assert.Equal(2, ev.Count);
        Assert.Equal(T0.AddSeconds(10), ev[0].EndedAt);
        Assert.Equal(T0.AddDays(2).AddSeconds(10), ev[1].StartedAt);
        Assert.Equal(T0.AddDays(2).AddSeconds(20), ev[1].EndedAt);
    }

    [Fact]
    public void DifferentAppAfterLongGapDoesNotChargeTheGap()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(10)); t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromDays(2)); t.Observe("b.exe", false);
        c.Advance(TimeSpan.FromSeconds(5));
        var ev = t.Drain();
        Assert.Equal("a.exe", ev[0].AppName);
        Assert.Equal(T0.AddSeconds(10), ev[0].EndedAt);
        Assert.Equal("b.exe", ev[1].AppName);
        Assert.Equal(T0.AddDays(2).AddSeconds(10), ev[1].StartedAt);
    }

    [Fact]
    public void GapOfExactly30sIsContinuous()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(30)); t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(30));
        var e = Assert.Single(t.Drain());
        Assert.Equal(T0.AddSeconds(60), e.EndedAt);
    }

    [Fact]
    public void GapOf31sIsAGap()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(31)); t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(5));
        var ev = t.Drain();
        // first interval had zero length up to its last observation (dropped); second is 5 s
        var e = Assert.Single(ev);
        Assert.Equal(T0.AddSeconds(31), e.StartedAt);
    }

    [Fact]
    public void DrainAfterLongSilenceEndsAtLastObservationAndLeavesNothingOpen()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(10)); t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromHours(5));
        var e = Assert.Single(t.Drain());
        Assert.Equal(T0.AddSeconds(10), e.EndedAt);
        c.Advance(TimeSpan.FromHours(1));
        Assert.Empty(t.Drain());
    }

    [Fact]
    public void SubSecondDrainSliceIsNotLost()
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromMilliseconds(600));
        Assert.Empty(t.Drain());
        c.Advance(TimeSpan.FromMilliseconds(600));
        var e = Assert.Single(t.Drain());
        Assert.Equal(T0, e.StartedAt);
        Assert.Equal(T0.AddMilliseconds(1200), e.EndedAt);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    public void EmptyExeIsTreatedLikeNull(string exe)
    {
        var (t, c) = Make();
        t.Observe("a.exe", false);
        c.Advance(TimeSpan.FromSeconds(3)); t.Observe(exe, false);
        c.Advance(TimeSpan.FromSeconds(10));
        var e = Assert.Single(t.Drain());
        Assert.Equal(T0.AddSeconds(3), e.EndedAt);
    }

    [Fact]
    public async Task ConcurrentObserveAndDrainDoNotThrow()
    {
        long ticks = T0.UtcTicks;
        var t = new UsageTracker(() => new DateTimeOffset(Interlocked.Read(ref ticks), TimeSpan.Zero));
        var stop = false;
        var obs = Task.Run(() =>
        {
            var i = 0;
            while (!Volatile.Read(ref stop))
            {
                Interlocked.Add(ref ticks, TimeSpan.FromSeconds(2).Ticks);
                t.Observe(i++ % 2 == 0 ? "a.exe" : "b.exe", false);
            }
        });
        for (var i = 0; i < 200; i++) t.Drain();
        Volatile.Write(ref stop, true);
        await obs;
    }
}
