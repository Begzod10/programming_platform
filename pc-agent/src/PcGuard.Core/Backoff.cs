namespace PcGuard.Core;

/// <summary>Reconnect delays: 1, 2, 5, 10, 30 s, then 30 s forever. <c>attempt</c> is 1-based (1 = first retry).</summary>
public static class Backoff
{
    private static readonly int[] Seconds = { 1, 2, 5, 10, 30 };

    public static TimeSpan NextDelay(int attempt)
    {
        var i = Math.Clamp(attempt, 1, Seconds.Length) - 1;
        return TimeSpan.FromSeconds(Seconds[i]);
    }
}
