using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class MaintenanceModeTests
{
    private static readonly DateTimeOffset T0 = new(2026, 10, 23, 10, 0, 0, TimeSpan.Zero);

    [Fact]
    public void AllowedDurationsAreExactly15_60_240()
        => Assert.Equal(new[] { 15, 60, 240 }, MaintenanceMode.AllowedMinutes.ToArray());

    [Theory]
    [InlineData(15)]
    [InlineData(60)]
    [InlineData(240)]
    public void ActivateWithAllowedDurationSetsUntil(int minutes)
    {
        var m = new MaintenanceMode();
        Assert.True(m.Activate(T0, minutes));
        Assert.True(m.IsActive(T0));
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
        var m = new MaintenanceMode();
        Assert.False(m.Activate(T0, minutes));
        Assert.False(m.IsActive(T0));
        Assert.Null(m.Until);
    }

    [Fact]
    public void InvalidDurationDoesNotChangeAnActiveMode()
    {
        var m = new MaintenanceMode();
        m.Activate(T0, 15);
        Assert.False(m.Activate(T0.AddMinutes(1), 9999));
        Assert.Equal(T0.AddMinutes(15), m.Until);
    }

    [Fact]
    public void InactiveByDefault()
    {
        var m = new MaintenanceMode();
        Assert.False(m.IsActive(T0));
        Assert.Null(m.Until);
    }

    [Fact]
    public void ActiveUntilJustBeforeExpiryThenInactive()
    {
        var m = new MaintenanceMode();
        m.Activate(T0, 15);
        Assert.True(m.IsActive(T0.AddMinutes(15).AddTicks(-1)));
        Assert.False(m.IsActive(T0.AddMinutes(15)));
        Assert.False(m.IsActive(T0.AddHours(5)));
    }

    [Fact]
    public void ClockSetBackMakesItInactive()
    {
        var m = new MaintenanceMode();
        m.Activate(T0, 240);
        Assert.False(m.IsActive(T0.AddTicks(-1)));
        Assert.False(m.IsActive(T0.AddDays(-1)));
    }

    [Fact]
    public void EndReturnsWhetherItWasActivatedAndClears()
    {
        var m = new MaintenanceMode();
        Assert.False(m.End());
        m.Activate(T0, 60);
        Assert.True(m.End());
        Assert.False(m.IsActive(T0));
        Assert.Null(m.Until);
        Assert.False(m.End());
    }

    [Fact]
    public void TryExpireEndsOnceAtExpiry()
    {
        var m = new MaintenanceMode();
        Assert.False(m.TryExpire(T0));
        m.Activate(T0, 15);
        Assert.False(m.TryExpire(T0.AddMinutes(14)));
        Assert.True(m.IsActive(T0.AddMinutes(14)));
        Assert.True(m.TryExpire(T0.AddMinutes(15)));
        Assert.Null(m.Until);
        Assert.False(m.TryExpire(T0.AddMinutes(16)));
    }

    [Fact]
    public void TryExpireOnClockSetBackEndsForGood()
    {
        var m = new MaintenanceMode();
        m.Activate(T0, 240);
        Assert.True(m.TryExpire(T0.AddMinutes(-1)));
        // the clock coming back does not revive it
        Assert.False(m.IsActive(T0.AddMinutes(1)));
        Assert.Null(m.Until);
    }

    [Fact]
    public void ReactivateReplacesTheWindowFromNow()
    {
        var m = new MaintenanceMode();
        m.Activate(T0, 240);
        Assert.True(m.Activate(T0.AddMinutes(10), 15));
        Assert.Equal(T0.AddMinutes(25), m.Until);
        Assert.False(m.IsActive(T0.AddMinutes(5))); // before the new start
    }
}
