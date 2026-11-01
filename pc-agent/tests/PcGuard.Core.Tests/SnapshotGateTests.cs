using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class SnapshotGateTests
{
    [Fact]
    public void UsableWhenSnapshotSessionEqualsConsole()
        => Assert.True(SnapshotGate.IsUsable(2u, 2u));

    [Fact]
    public void NotUsableWhenSessionsDiffer()
        => Assert.False(SnapshotGate.IsUsable(2u, 3u)); // fast user switch: old session's snapshot is stale

    [Fact]
    public void NotUsableWhenSnapshotSessionUnknown()
        => Assert.False(SnapshotGate.IsUsable(null, 2u));

    [Fact]
    public void NotUsableWhenNoConsoleSession()
        => Assert.False(SnapshotGate.IsUsable(2u, null)); // logon screen / switch in progress
}
