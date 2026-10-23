using System.Windows.Automation;
using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>
/// Reads the omnibox text of Chrome/Edge windows through UI Automation and reduces it to a bare host.
/// PRIVACY: the raw address text lives only in a local variable of <see cref="ReadHost"/>; it is
/// never stored, logged or sent. Not thread-safe: call from one worker thread. WINDOWS ONLY.
/// </summary>
internal sealed class BrowserAddressReader
{
    // Chromium's omnibox is an Edit control of this UIA class in both Chrome and Edge, independent
    // of the UI language (the accessible Name is localised, so it is not used).
    private const string OmniboxClass = "OmniboxViewViews";
    private static readonly Condition OmniboxCondition = new AndCondition(
        new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Edit),
        new PropertyCondition(AutomationElement.ClassNameProperty, OmniboxClass));

    private readonly Dictionary<long, AutomationElement> _cache = new();

    public string? ReadHost(long hwnd)
    {
        try
        {
            var raw = ReadRaw(hwnd, allowRetry: true);
            return AddressBarParser.ExtractHost(raw);
        }
        catch (Exception e) when (e is ElementNotAvailableException or InvalidOperationException
                                      or System.ComponentModel.Win32Exception or TimeoutException
                                      or System.Runtime.InteropServices.COMException)
        {
            _cache.Remove(hwnd);
            return null; // unreadable => host unknown (the service then allows the window)
        }
    }

    public void Prune(IReadOnlySet<long> liveHwnds)
    {
        foreach (var k in _cache.Keys.Where(k => !liveHwnds.Contains(k)).ToList()) _cache.Remove(k);
    }

    private string? ReadRaw(long hwnd, bool allowRetry)
    {
        if (!_cache.TryGetValue(hwnd, out var edit))
        {
            var root = AutomationElement.FromHandle(new IntPtr(hwnd));
            edit = root.FindFirst(TreeScope.Descendants, OmniboxCondition);
            if (edit is null) return null;
            _cache[hwnd] = edit;
        }
        try
        {
            if (!edit.TryGetCurrentPattern(ValuePattern.Pattern, out var p)) return null;
            return ((ValuePattern)p).Current.Value;
        }
        catch (ElementNotAvailableException) when (allowRetry)
        {
            _cache.Remove(hwnd); // stale element (browser rebuilt its UI): search once more
            return ReadRaw(hwnd, allowRetry: false);
        }
    }
}
