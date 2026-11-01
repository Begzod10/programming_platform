namespace PcGuard.Core;

/// <summary>
/// A UWP app's visible top-level window is an ApplicationFrameWindow owned by ApplicationFrameHost;
/// the real app owns a child Windows.UI.Core.CoreWindow. Picks the pids to report as windowed.
/// </summary>
public static class UwpPidPicker
{
    public static IReadOnlyList<int> Pick(int framePid, IEnumerable<int> coreWindowPids)
    {
        var real = coreWindowPids.Where(p => p != framePid).Distinct().OrderBy(p => p).ToList();
        return real.Count > 0 ? real : new[] { framePid };
    }
}
