using System.Windows;
using System.Windows.Interop;
using System.Windows.Threading;
using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>
/// Full-screen (virtual screen of all monitors), topmost sign-in window. It can never be closed by
/// the user (Closing is always cancelled); it is only hidden after a successful sign-in.
/// The password lives in the PasswordBox and in one local variable for the duration of the pipe
/// write; the box is cleared before the write is awaited.
/// </summary>
public partial class LoginWindow : Window
{
    private static readonly TimeSpan BusyTimeout = TimeSpan.FromSeconds(20);

    private readonly DispatcherTimer _keepOnTop;
    private readonly DispatcherTimer _busyTimer;
    private UiLang _lang;
    private bool _connected;
    private bool _busy;
    private string? _errorCode;
    private bool _hasError;

    internal Func<PipeMessage, Task<bool>>? Sender { get; set; }
    internal event Action<UiLang>? LanguageChanged;

    internal LoginWindow(UiLang lang)
    {
        InitializeComponent();
        _lang = lang;

        _keepOnTop = new DispatcherTimer { Interval = TimeSpan.FromSeconds(1) };
        _keepOnTop.Tick += (_, _) => Cover();
        _busyTimer = new DispatcherTimer { Interval = BusyTimeout };
        _busyTimer.Tick += (_, _) => { _busyTimer.Stop(); SetBusy(false); ShowError("offline"); };

        Closing += (_, e) => { if (!App.Quitting) e.Cancel = true; }; // Alt+F4 / any close: ignored
        SourceInitialized += (_, _) => Cover();
        Deactivated += (_, _) => { if (IsVisible) Dispatcher.BeginInvoke(ActivateSafe, DispatcherPriority.Background); };
        IsVisibleChanged += (_, _) =>
        {
            if (IsVisible) { _keepOnTop.Start(); Cover(); ActivateSafe(); UserBox.Focus(); }
            else _keepOnTop.Stop();
        };
        Microsoft.Win32.SystemEvents.DisplaySettingsChanged += (_, _) => Dispatcher.BeginInvoke(Cover);

        ApplyLanguage();
    }

    private void ActivateSafe()
    {
        try { Activate(); } catch (InvalidOperationException) { }
    }

    /// <summary>Stretch over the whole virtual screen in physical pixels (all monitors) and stay topmost.</summary>
    private void Cover()
    {
        var hwnd = new WindowInteropHelper(this).Handle;
        if (hwnd == IntPtr.Zero) return;
        var (x, y, w, h) = Native.VirtualScreen();
        Native.SetWindowPos(hwnd, Native.HWND_TOPMOST, x, y, w, h, Native.SWP_NOACTIVATE | Native.SWP_SHOWWINDOW);
    }

    internal void ShowLogin()
    {
        if (!IsVisible) Show();
    }

    internal void HideLogin()
    {
        if (!IsVisible) return;
        _busyTimer.Stop();
        SetBusy(false);
        UserBox.Clear();
        PwBox.Clear();
        ClearError();
        Hide();
    }

    internal void SetLanguage(UiLang lang)
    {
        _lang = lang;
        ApplyLanguage();
    }

    internal void SetConnected(bool connected)
    {
        _connected = connected;
        if (!connected) SetBusy(false);
        ApplyLanguage();
    }

    internal void ShowLoginResult(LoginResultMessage r)
    {
        _busyTimer.Stop();
        SetBusy(false);
        if (r.Ok) { ClearError(); return; }
        ShowError(r.Error);
        PwBox.Focus();
    }

    private void ShowError(string? code)
    {
        _errorCode = code;
        _hasError = true;
        ApplyLanguage();
    }

    private void ClearError()
    {
        _errorCode = null;
        _hasError = false;
        ApplyLanguage();
    }

    private void SetBusy(bool busy)
    {
        _busy = busy;
        ApplyLanguage();
    }

    private void ApplyLanguage()
    {
        UserLabel.Text = UiStrings.UsernameLabel(_lang);
        PwLabel.Text = UiStrings.PasswordLabel(_lang);
        LoginButton.Content = UiStrings.LoginButton(_lang);
        NoticeText.Text = UiStrings.Notice(_lang);
        ConnectingText.Text = UiStrings.Connecting(_lang);
        ConnectingText.Visibility = _connected ? Visibility.Collapsed : Visibility.Visible;
        ErrorText.Text = _hasError ? UiStrings.LoginError(_lang, _errorCode) : "";
        ErrorText.Visibility = _hasError ? Visibility.Visible : Visibility.Collapsed;
        var enabled = _connected && !_busy;
        LoginButton.IsEnabled = enabled;
        UserBox.IsEnabled = !_busy;
        PwBox.IsEnabled = !_busy;
    }

    private void OnLangClick(object sender, RoutedEventArgs e)
    {
        _lang = _lang == UiLang.Uz ? UiLang.Ru : UiLang.Uz;
        ApplyLanguage();
        LanguageChanged?.Invoke(_lang);
    }

    private async void OnLoginClick(object sender, RoutedEventArgs e)
    {
        if (_busy || !_connected || Sender is null) return;
        var user = UserBox.Text.Trim();
        if (user.Length == 0 || PwBox.Password.Length == 0)
        {
            ShowError("bad_credentials");
            return;
        }

        ClearError();
        SetBusy(true);
        _busyTimer.Stop();
        _busyTimer.Start();

        bool sent;
        try
        {
            // The password is read and the box cleared in one step; the string exists only inside
            // the message object handed to the pipe client.
            sent = await Sender(new LoginMessage(user, TakePassword()));
        }
        catch (Exception ex)
        {
            ShellLog.Error("Login send", ex);
            sent = false;
        }

        if (!sent)
        {
            _busyTimer.Stop();
            SetBusy(false);
            ShowError("offline");
        }
        // on success the busy state ends with login_result (or the 20 s timer)
    }

    private string TakePassword()
    {
        var p = PwBox.Password;
        PwBox.Clear();
        return p;
    }
}
