using System.Windows;
using System.Windows.Interop;
using System.Windows.Threading;

namespace PcGuard.Shell;

/// <summary>Teacher message, shown for 10 s without taking focus (WS_EX_NOACTIVATE), bottom right.</summary>
public partial class MessagePopup : Window
{
    private static readonly TimeSpan Lifetime = TimeSpan.FromSeconds(10);
    private readonly DispatcherTimer _timer;

    internal MessagePopup(string text)
    {
        InitializeComponent();
        BodyText.Text = text;
        SourceInitialized += (_, _) =>
        {
            var hwnd = new WindowInteropHelper(this).Handle;
            Native.SetExStyle(hwnd, Native.GetExStyle(hwnd) | Native.WS_EX_NOACTIVATE | Native.WS_EX_TOOLWINDOW);
        };
        SizeChanged += (_, _) =>
        {
            var area = SystemParameters.WorkArea;
            Left = area.Right - ActualWidth - 16;
            Top = area.Bottom - ActualHeight - 16;
        };
        _timer = new DispatcherTimer { Interval = Lifetime };
        _timer.Tick += (_, _) => { _timer.Stop(); Close(); };
        Loaded += (_, _) => _timer.Start();
    }
}
