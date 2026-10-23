using System.Windows;
using System.Windows.Threading;
using System.Windows.Interop;
using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>Small always-on-top banner (top centre) while the student is signed in and locked.</summary>
public partial class LockOverlay : Window
{
    private readonly DispatcherTimer _keepOnTop;
    private UiLang _lang;
    private string _student = "";
    private int _remaining;

    internal Action? SignOutRequested { get; set; }

    internal LockOverlay(UiLang lang)
    {
        InitializeComponent();
        _lang = lang;
        _keepOnTop = new DispatcherTimer { Interval = TimeSpan.FromSeconds(2) };
        _keepOnTop.Tick += (_, _) => Reassert();
        Closing += (_, e) => { if (!App.Quitting) e.Cancel = true; };
        SizeChanged += (_, _) => Reposition();
        IsVisibleChanged += (_, _) => { if (IsVisible) _keepOnTop.Start(); else _keepOnTop.Stop(); };
        Apply();
    }

    internal void ShowFor(string student, int remaining)
    {
        _student = student;
        _remaining = remaining;
        Apply();
        if (!IsVisible) Show();
        Reposition();
    }

    internal void HideOverlay()
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
        NameText.Text = _student;
        RemainingText.Text = UiStrings.Banner(_lang, _remaining);
        SignOutButton.Content = UiStrings.SignOut(_lang);
    }

    private void Reposition()
    {
        var area = SystemParameters.WorkArea;
        Left = area.Left + (area.Width - ActualWidth) / 2;
        Top = area.Top;
    }

    private void Reassert()
    {
        var hwnd = new WindowInteropHelper(this).Handle;
        if (hwnd == IntPtr.Zero) return;
        Native.SetWindowPos(hwnd, Native.HWND_TOPMOST, 0, 0, 0, 0,
            Native.SWP_NOMOVE | Native.SWP_NOSIZE | Native.SWP_NOACTIVATE);
    }

    private void OnSignOut(object sender, RoutedEventArgs e) => SignOutRequested?.Invoke();
}
