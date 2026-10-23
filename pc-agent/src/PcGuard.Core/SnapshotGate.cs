namespace PcGuard.Core;

/// <summary>
/// Pure gate: a shell snapshot may only be trusted when it came from the process in the CURRENT
/// active console session. After fast user switching a pinned shell can linger in a now-disconnected
/// session and keep sending snapshots; those must not be treated as fresh for the new console
/// session (the planner then falls back and the supervisor launches a shell in the new session).
/// </summary>
public static class SnapshotGate
{
    public static bool IsUsable(uint? snapshotSessionId, uint? activeConsoleSessionId)
        => snapshotSessionId is { } s && activeConsoleSessionId is { } c && s == c;
}
