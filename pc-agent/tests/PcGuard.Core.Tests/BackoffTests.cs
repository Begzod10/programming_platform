using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class BackoffTests
{
    [Theory]
    [InlineData(1, 1)]
    [InlineData(2, 2)]
    [InlineData(3, 5)]
    [InlineData(4, 10)]
    [InlineData(5, 30)]
    [InlineData(6, 30)]
    [InlineData(1000, 30)]
    [InlineData(int.MaxValue, 30)]
    public void FollowsSchedule(int attempt, int seconds)
        => Assert.Equal(TimeSpan.FromSeconds(seconds), Backoff.NextDelay(attempt));

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    [InlineData(int.MinValue)]
    public void NonPositiveAttemptUsesFirstDelay(int attempt)
        => Assert.Equal(TimeSpan.FromSeconds(1), Backoff.NextDelay(attempt));
}
