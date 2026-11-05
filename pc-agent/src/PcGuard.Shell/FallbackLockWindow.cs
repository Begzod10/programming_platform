using System.Windows;
using System.Windows.Controls;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Threading;
using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>
/// Minimal full-screen, topmost lock window used only when the normal windows could not be built
/// (<see cref="ShellUiFallback"/>). Built in code, without XAML, and only from non-text-input elements
/// (a Border and a TextBlock: no TextBox, PasswordBox, Button or Hyperlink), so it does not need
/// Windows text input (TSF), which is what failed on the real PC. It cannot be closed by the user; it
/// shows a fixed bilingual notice; nobody can sign in through it. Enforcement does not depend on it:
/// the service keeps enforcing from the snapshots the pipe client sends.
/// </summary>
internal sealed class FallbackLockWindow : Window
{
    private readonly DispatcherTimer _keepOnTop;

    internal FallbackLockWindow()
    {
        WindowStyle = WindowStyle.None;
        ResizeMode = ResizeMode.NoResize;
        ShowInTaskbar = false;
        Topmost = true;
        WindowStartupLocation = WindowStartupLocation.Manual;
        Title = "PcGuard";
        Background = new SolidColorBrush(Color.FromRgb(0x10, 0x18, 0x20));
        Focusable = false;
        Content = new Border
        {
            Child = new TextBlock
            {
                Text = UiStrings.FallbackLock(),
                Foreground = Brushes.White,
                FontSize = 22,
                TextWrapping = TextWrapping.Wrap,
                TextAlignment = TextAlignment.Center,
                MaxWidth = 900,
                Margin = new Thickness(24),
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
            },
        };

        _keepOnTop = new DispatcherTimer { Interval = TimeSpan.FromSeconds(1) };
        _keepOnTop.Tick += (_, _) => Cover();
        Closing += (_, e) => { if (!App.Quitting) e.Cancel = true; };
        SourceInitialized += (_, _) =>
        {
            var h = new WindowInteropHelper(this).Handle;
            Native.SetExStyle(h, Native.GetExStyle(h) | Native.WS_EX_TOOLWINDOW); // all virtual desktops
            Cover();
        };
        IsVisibleChanged += (_, _) =>
        {
            if (IsVisible) { _keepOnTop.Start(); Cover(); }
            else _keepOnTop.Stop();
        };
    }

    internal void SetVisible(bool visible)
    {
        if (visible && !IsVisible) Show();
        else if (!visible && IsVisible) Hide();
    }

    /// <summary>Stretch over the whole virtual screen (all monitors) and stay topmost.</summary>
    private void Cover()
    {
        if (!IsVisible) return;
        var hwnd = new WindowInteropHelper(this).Handle;
        if (hwnd == IntPtr.Zero) return;
        var (x, y, w, h) = Native.VirtualScreen();
        Native.SetWindowPos(hwnd, Native.HWND_TOPMOST, x, y, w, h, Native.SWP_NOACTIVATE);
    }
}
