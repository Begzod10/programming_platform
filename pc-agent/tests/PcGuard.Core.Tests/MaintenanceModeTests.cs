using PcGuard.Core;

namespace PcGuard.Core.Tests;

/// <summary>Monotonic time the test moves by hand (like Environment.TickCount64, never tied to the wall clock).</summary>
internal sealed class FakeMonotonic
{
    public TimeSpan Now { get; set; } = TimeSpan.FromHours(3);
    public void Advance(TimeSpan by) => Now += by;
    public Func<TimeSpan> Source => () => Now;
}

public class MaintenanceModeTests
{
    // wall clock: only for the displayed end time (Until) and the audit log
    private static readonly DateTimeOffset T0 = new(2026, 10, 23, 10, 0, 0, TimeSpan.Zero);

    private static (MaintenanceMode Mode, FakeMonotonic Mono) New()
    {
        var mono = new FakeMonotonic();
        return (new MaintenanceMode(mono.Source), mono);
    }

    [Fact]
    public void AllowedDurationsAreExactly15_60_240()
        => Assert.Equal(new[] { 15, 60, 240 }, MaintenanceMode.AllowedMinutes.ToArray());

    [Theory]
    [InlineData(15)]
    [InlineData(60)]
    [InlineData(240)]
    public void ActivateWithAllowedDurationSetsUntil(int minutes)
    {
        var (m, _) = New();
        Assert.True(m.Activate(T0, minutes));
        Assert.True(m.IsActive());
        Assert.Equal(T0.AddMinutes(minutes), m.Until);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-15)]
    [InlineData(1)]
    [InlineData(14)]
    [InlineData(16)]
    [InlineData(30)]
    [InlineData(241)]
    [InlineData(int.MaxValue)]
    [InlineData(int.MinValue)]
    public void ActivateRejectsAnyOtherDuration(int minutes)
    {
        var (m, _) = New();
        Assert.False(m.Activate(T0, minutes));
        Assert.False(m.IsActive());
        Assert.Null(m.Until);
    }

    [Fact]
    public void InvalidDurationDoesNotChangeAnActiveMode()
    {
        var (m, mono) = New();
        m.Activate(T0, 15);
        mono.Advance(TimeSpan.FromMinutes(1));
        Assert.False(m.Activate(T0.AddMinutes(1), 9999));
        Assert.Equal(T0.AddMinutes(15), m.Until);
        Assert.True(m.IsActive());
    }

    [Fact]
    public void InactiveByDefault()
    {
        var (m, _) = New();
        Assert.False(m.IsActive());
        Assert.Null(m.Until);
    }

    [Fact]
    public void ActiveUntilJustBeforeExpiryThenInactive()
    {
        var (m, mono) = New();
        m.Activate(T0, 15);
        mono.Advance(TimeSpan.FromMinutes(15) - TimeSpan.FromTicks(1));
        Assert.True(m.IsActive());
        mono.Advance(TimeSpan.FromTicks(1));
        Assert.False(m.IsActive());
        mono.Advance(TimeSpan.FromHours(5));
        Assert.False(m.IsActive());
    }

    [Fact]
    public void TheWallClockPassedToActivateNeverDecidesTheDeadline()
    {
        // wall clock set far back or far ahead at activation: the window still lasts exactly 15 monotonic minutes
        var (m, mono) = New();
        m.Activate(T0.AddDays(-400), 15);
        mono.Advance(TimeSpan.FromMinutes(14));
        Assert.True(m.IsActive());
        mono.Advance(TimeSpan.FromMinutes(1));
        Assert.False(m.IsActive());

        var (m2, mono2) = New();
        m2.Activate(T0.AddYears(5), 15);
        mono2.Advance(TimeSpan.FromMinutes(15));
        Assert.False(m2.IsActive());
    }

    [Fact]
    public void MonotonicTimeBeforeTheStartMakesItInactive()
    {
        // the old "clock set back" intent, expressed with the monotonic source: a reading before the
        // start (which a real monotonic clock never produces) is never treated as inside the window
        var (m, mono) = New();
        m.Activate(T0, 240);
        mono.Advance(TimeSpan.FromTicks(-1));
        Assert.False(m.IsActive());
        mono.Advance(TimeSpan.FromDays(-1));
        Assert.False(m.IsActive());
    }

    [Fact]
    public void EndReturnsWhetherItWasActivatedAndClears()
    {
        var (m, _) = New();
        Assert.False(m.End());
        m.Activate(T0, 60);
        Assert.True(m.End());
        Assert.False(m.IsActive());
        Assert.Null(m.Until);
        Assert.False(m.End());
    }

    [Fact]
    public void TryExpireEndsOnceAtExpiry()
    {
        var (m, mono) = New();
        Assert.False(m.TryExpire());
        m.Activate(T0, 15);
        mono.Advance(TimeSpan.FromMinutes(14));
        Assert.False(m.TryExpire());
        Assert.True(m.IsActive());
        mono.Advance(TimeSpan.FromMinutes(1));
        Assert.True(m.TryExpire());
        Assert.Null(m.Until);
        mono.Advance(TimeSpan.FromMinutes(1));
        Assert.False(m.TryExpire());
    }

    [Fact]
    public void TryExpireOnMonotonicTimeBeforeTheStartEndsForGood()
    {
        var (m, mono) = New();
        m.Activate(T0, 240);
        mono.Advance(TimeSpan.FromMinutes(-1));
        Assert.True(m.TryExpire());
        // time coming forward again does not revive it
        mono.Advance(TimeSpan.FromMinutes(2));
        Assert.False(m.IsActive());
        Assert.Null(m.Until);
    }

    [Fact]
    public void ReactivateReplacesTheWindowFromNow()
    {
        var (m, mono) = New();
        m.Activate(T0, 240);
        mono.Advance(TimeSpan.FromMinutes(10));
        Assert.True(m.Activate(T0.AddMinutes(10), 15));
        Assert.Equal(T0.AddMinutes(25), m.Until);
        mono.Advance(TimeSpan.FromMinutes(14));
        Assert.True(m.IsActive());
        mono.Advance(TimeSpan.FromMinutes(1));
        Assert.False(m.IsActive()); // the old 240-minute window is gone
    }

    [Fact]
    public void DefaultSourceIsTheSystemMonotonicClock()
    {
        var m = new MaintenanceMode();
        Assert.True(m.Activate(DateTimeOffset.Now, 15));
        Assert.True(m.IsActive());
        var a = MonotonicClock.Now();
        var b = MonotonicClock.Now();
        Assert.True(b >= a);
        Assert.True(a > TimeSpan.Zero);
    }
}
