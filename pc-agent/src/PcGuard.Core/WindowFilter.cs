namespace PcGuard.Core;

/// <summary>Pure rule deciding whether a top-level window makes its process count as "windowed".</summary>
public static class WindowFilter
{
    /// <summary>
    /// Visible, non-cloaked, non-empty windows only. WS_EX_APPWINDOW always counts; a tool window
    /// without it (no taskbar presence) never does; otherwise a non-empty title is required.
    /// Only the title LENGTH is ever consulted by callers, never its text.
    /// </summary>
    public static bool CountsAsAppWindow(bool visible, bool cloaked, int width, int height,
        bool toolWindow, bool appWindowStyle, bool hasTitle)
    {
        if (!visible || cloaked) return false;
        if (width <= 0 || height <= 0) return false;
        if (appWindowStyle) return true;
        if (toolWindow) return false;
        return hasTitle;
    }
}
