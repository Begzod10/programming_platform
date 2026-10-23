namespace PcGuard.Core;

/// <summary>
/// A session's upload credential, held in memory only. <see cref="ClosedAt"/> is null while the
/// session is open (the current sign-in) and set to the sign-out / token-death time afterwards.
/// The backend accepts a closed session's token for 24 h so buffered usage can still be uploaded.
/// </summary>
public sealed record SessionToken(string Token, DateTimeOffset? ClosedAt);

public enum UsageTagAction { Upload, Drop }

public sealed record UsageTagDecision(UsageTagAction Action, string? Token);

/// <summary>
/// Pure decision: a batch of usage events tagged with a session must be uploaded with THAT session's
/// own token, never another's. Fixes cross-student attribution: the backend files usage under the
/// token's own session.
/// </summary>
public static class UsageUploadPlanner
{
    public static readonly TimeSpan Grace = TimeSpan.FromHours(24);

    private static readonly UsageTagDecision Dropped = new(UsageTagAction.Drop, null);

    /// <param name="session">The tag's token info, or null when it is not in memory (e.g. after a
    /// service restart) — in that case the events are dropped rather than risk a wrong-student upload.</param>
    public static UsageTagDecision Decide(SessionToken? session, DateTimeOffset now)
    {
        if (session is null) return Dropped;
        if (session.ClosedAt is not { } closed) return new UsageTagDecision(UsageTagAction.Upload, session.Token);
        var age = now - closed;
        return age >= TimeSpan.Zero && age <= Grace
            ? new UsageTagDecision(UsageTagAction.Upload, session.Token)
            : Dropped;
    }
}
