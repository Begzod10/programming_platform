namespace PcGuard.Core;

/// <summary>
/// Which windows may appear in a snapshot's <c>browsers</c> list and be closed by close_window:
/// only real top-level browser windows. Chromium's popups (omnibox dropdown, menus, permission
/// bubbles) are owned and/or tool windows and must never be reported or closed.
/// </summary>
public static class BrowserWindowEligibility
{
    public static bool IsEligible(bool hasOwner, bool toolWindow, int width, int height)
        => !hasOwner && !toolWindow && width > 0 && height > 0;
}
