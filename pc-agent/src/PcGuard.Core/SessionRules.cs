namespace PcGuard.Core;

public static class SessionRules
{
    /// <summary>
    /// Effective rules when no student is signed in: locked with reason "no_student", but the cached
    /// allowlist (or the defaults) and browser hosts still apply so the sign-in screen and tools work.
    /// </summary>
    public static PcRules SignedOut(PcRules cached) => cached with
    {
        Locked = true,
        Reason = "no_student",
        Remaining = 0,
        StudentName = null,
        Allowlist = cached.Allowlist.Count > 0 ? cached.Allowlist : Defaults.Allowlist,
    };

    public static StateMessage ToStateMessage(PcRules r) => new(r.Locked, r.Reason, r.Remaining, r.StudentName);
}

public enum ShellAction { None, Launch, KillHung }

public static class ShellLaunchPolicy
{
    public static readonly TimeSpan MissingGrace = TimeSpan.FromSeconds(6);
    public static readonly TimeSpan MinLaunchInterval = TimeSpan.FromSeconds(15);
    public static readonly TimeSpan HungAfter = TimeSpan.FromSeconds(30);

    /// <param name="shellMissingSince">When the last fresh snapshot went missing; null = shell is reporting.</param>
    /// <param name="lastLaunchAt">Last time the service launched the shell, if ever.</param>
    /// <param name="hasConsoleSession">A user is signed in on the physical console.</param>
    /// <param name="shellProcessRunning">The installed shell exe is running in that session.</param>
    /// <param name="lastSnapshotAt">Last snapshot received from a verified shell, if ever.</param>
    /// <param name="lastAliveAt">Last "alive" frame (shell is up but deliberately not sending snapshots), if ever.
    /// Counts as liveness for the hung decision only; it never makes a snapshot fresh.</param>
    public static ShellAction Decide(DateTimeOffset now, DateTimeOffset? shellMissingSince, DateTimeOffset? lastLaunchAt,
        bool hasConsoleSession, bool shellProcessRunning, DateTimeOffset? lastSnapshotAt,
        DateTimeOffset? lastAliveAt = null)
    {
        if (!hasConsoleSession || shellMissingSince is not { } since) return ShellAction.None;
        if (now - since < MissingGrace) return ShellAction.None;

        if (shellProcessRunning)
        {
            // give a running shell time to (re)connect; one that stays silent is hung
            var liveness = Max(ClampFuture(lastSnapshotAt, now), ClampFuture(lastAliveAt, now));
            var reference = Max(since, Max(liveness, ClampFuture(lastLaunchAt, now)));
            return now - reference >= HungAfter ? ShellAction.KillHung : ShellAction.None;
        }

        if (ClampFuture(lastLaunchAt, now) is { } l && now - l < MinLaunchInterval) return ShellAction.None;
        return ShellAction.Launch;
    }

    // a launch time in the future (clock moved back) must not block launching for that long
    private static DateTimeOffset? ClampFuture(DateTimeOffset? t, DateTimeOffset now) => t is { } v && v > now ? null : t;

    private static DateTimeOffset Max(DateTimeOffset a, DateTimeOffset? b) => b is { } v && v > a ? v : a;
    private static DateTimeOffset? Max(DateTimeOffset? a, DateTimeOffset? b) => a is null ? b : b is null ? a : (a > b ? a : b);
}
