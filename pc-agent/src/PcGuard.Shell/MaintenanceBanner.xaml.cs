using System.Windows;
using System.Windows.Interop;
using System.Windows.Threading;
using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>
/// Small always-on-top banner (top right) while maintenance mode is active: "Texnik rejim HH:mm
/// gacha" / "Режим обслуживания до HH:mm" (local time) with an End button that sends admin_end.
/// Cannot be closed by the user; hidden when maintenance ends.
/// </summary>
public partial class MaintenanceBanner : Window
{
    private readonly DispatcherTimer _keepOnTop;
    private UiLang _lang;
    private DateTimeOffset _untilUtc;

    internal Action? EndRequested { get; set; }

    internal MaintenanceBanner(UiLang lang)
    {
        InitializeComponent();
        _lang = lang;
        _keepOnTop = new DispatcherTimer { Interval = TimeSpan.FromSeconds(2) };
        _keepOnTop.Tick += (_, _) => Reassert();
        SourceInitialized += (_, _) =>
        {
            var h = new WindowInteropHelper(this).Handle;
            Native.SetExStyle(h, Native.GetExStyle(h) | Native.WS_EX_TOOLWINDOW); // all virtual desktops
        };
        Closing += (_, e) => { if (!App.Quitting) e.Cancel = true; };
        SizeChanged += (_, _) => Reposition();
        IsVisibleChanged += (_, _) => { if (IsVisible) _keepOnTop.Start(); else _keepOnTop.Stop(); };
        Apply();
    }

    internal void ShowUntil(DateTimeOffset untilUtc)
    {
        _untilUtc = untilUtc;
        Apply();
        if (!IsVisible) Show();
        Reposition();
    }

    internal void HideBanner()
    {
        if (IsVisible) Hide();
    }

    internal void SetLanguage(UiLang lang)
    {
        _lang = lang;
        Apply();
    }

    private void Apply()
    {
        BannerText.Text = UiStrings.MaintenanceBanner(_lang, UiStrings.ClockTime(_untilUtc.ToLocalTime()));
        EndButton.Content = UiStrings.MaintenanceEndButton(_lang);
    }

    private void Reposition()
    {
        var area = SystemParameters.WorkArea;
        Left = area.Right - ActualWidth - 16;
        Top = area.Top + 16;
    }

    private void Reassert()
    {
        var hwnd = new WindowInteropHelper(this).Handle;
        if (hwnd == IntPtr.Zero) return;
        Native.SetWindowPos(hwnd, Native.HWND_TOPMOST, 0, 0, 0, 0,
            Native.SWP_NOMOVE | Native.SWP_NOSIZE | Native.SWP_NOACTIVATE);
    }

    private void OnEnd(object sender, RoutedEventArgs e) => EndRequested?.Invoke();
}
