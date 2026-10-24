namespace PcGuard.Core;

/// <summary>Pure rule deciding whether a top-level window makes its process count as "windowed".</summary>
public static class WindowFilter
{
    public const int MinToolWindowSize = 100;

    /// <summary>
    /// Visible, non-cloaked, non-empty windows count (err toward inclusion; titles are not consulted).
    /// WS_EX_APPWINDOW always counts. A WS_EX_TOOLWINDOW without it counts only when at least
    /// 100x100 (tiny tool windows are tooltips and helpers).
    /// </summary>
    public static bool CountsAsAppWindow(bool visible, bool cloaked, int width, int height,
        bool toolWindow, bool appWindowStyle)
    {
        if (!visible || cloaked) return false;
        if (width <= 0 || height <= 0) return false;
        if (appWindowStyle) return true;
        if (toolWindow) return width >= MinToolWindowSize && height >= MinToolWindowSize;
        return true;
    }
}
