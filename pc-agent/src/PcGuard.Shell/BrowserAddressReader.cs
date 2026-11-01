using System.Windows.Automation;
using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>Result of reading one browser window. Readable=false means: definitively no omnibox.</summary>
internal readonly record struct HostRead(string? Host, bool Readable);

/// <summary>
/// Reads the omnibox text of Chrome/Edge windows through UI Automation and reduces it to a bare host.
/// PRIVACY: the raw address text lives only in a local variable; only the parsed bare host is kept
/// (in a small per-window cache) and nothing is logged. Reading is single-threaded (one worker);
/// <see cref="LastKnown"/> may be called from another thread. WINDOWS ONLY.
/// </summary>
internal sealed class BrowserAddressReader
{
    // Chromium's omnibox is an Edit control of this UIA class in both Chrome and Edge, independent
    // of the UI language (the accessible Name is localised, so it is not used).
    private const string OmniboxClass = "OmniboxViewViews";
    private const int MaxCache = 400;
    // Chrome enables its accessibility tree lazily on the first UIA query, so a first miss is not
    // proof; a window is called unreadable only after this many consecutive misses.
    private const int MissesBeforeUnreadable = 2;

    private static readonly Condition OmniboxCondition = new AndCondition(
        new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Edit),
        new PropertyCondition(AutomationElement.ClassNameProperty, OmniboxClass));

    private readonly Dictionary<long, AutomationElement> _elements = new();
    private readonly Dictionary<long, int> _misses = new();
    private readonly Dictionary<long, string?> _lastHost = new();
    private readonly object _gate = new();

    /// <summary>Last committed host for the window (host null if none yet); always readable=true.</summary>
    public HostRead LastKnown(long hwnd)
    {
        lock (_gate) return new HostRead(_lastHost.GetValueOrDefault(hwnd), true);
    }

    public HostRead Read(long hwnd)
    {
        try
        {
            var edit = FindOmnibox(hwnd);
            if (edit is null)
            {
                int misses;
                lock (_gate) { _misses[hwnd] = misses = _misses.GetValueOrDefault(hwnd) + 1; }
                // never unreadable if an omnibox was ever seen for this window
                bool everSeen;
                lock (_gate) everSeen = _lastHost.ContainsKey(hwnd);
                return misses >= MissesBeforeUnreadable && !everSeen
                    ? new HostRead(null, false)
                    : LastKnown(hwnd);
            }
            lock (_gate) { _misses[hwnd] = 0; _lastHost.TryAdd(hwnd, null); } // omnibox seen

            // While the student is typing, the box holds the draft, not the page: keep the last committed host.
            if (edit.Current.HasKeyboardFocus) return LastKnown(hwnd);

            if (!edit.TryGetCurrentPattern(ValuePattern.Pattern, out var p)) return LastKnown(hwnd);
            var host = AddressBarParser.ExtractHost(((ValuePattern)p).Current.Value);
            lock (_gate)
            {
                if (_lastHost.Count < MaxCache || _lastHost.ContainsKey(hwnd)) _lastHost[hwnd] = host;
            }
            return new HostRead(host, true);
        }
        catch (Exception e) when (e is ElementNotAvailableException or InvalidOperationException
                                      or System.ComponentModel.Win32Exception or TimeoutException
                                      or System.Runtime.InteropServices.COMException)
        {
            _elements.Remove(hwnd);
            return LastKnown(hwnd); // a failed read is not "no address bar"
        }
    }

    public void Prune(IReadOnlySet<long> liveHwnds)
    {
        foreach (var k in _elements.Keys.Where(k => !liveHwnds.Contains(k)).ToList()) _elements.Remove(k);
        lock (_gate)
        {
            foreach (var k in _lastHost.Keys.Where(k => !liveHwnds.Contains(k)).ToList()) _lastHost.Remove(k);
            foreach (var k in _misses.Keys.Where(k => !liveHwnds.Contains(k)).ToList()) _misses.Remove(k);
        }
    }

    private AutomationElement? FindOmnibox(long hwnd)
    {
        if (_elements.TryGetValue(hwnd, out var cached))
        {
            try
            {
                _ = cached.Current.ProcessId; // throws ElementNotAvailableException when stale
                return cached;
            }
            catch (ElementNotAvailableException)
            {
                _elements.Remove(hwnd);
            }
        }
        var root = AutomationElement.FromHandle(new IntPtr(hwnd));
        var edit = root.FindFirst(TreeScope.Descendants, OmniboxCondition);
        if (edit is not null) _elements[hwnd] = edit;
        return edit;
    }
}
