using System.Windows;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Threading;
using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>
/// Recovery code dialog, opened by the "Tiklash kodi" / "Код восстановления" link. Takes the offline
/// recovery code that was set when PC Guard was installed and sends it to the service
/// (recovery_release with a fresh request id); the service verifies it locally against the stored
/// hash and answers recovery_result with the same id. On success the service also sends "released"
/// and App exits the shell; this dialog only closes.
///
/// The code exists only in the PasswordBox and in one local variable for the duration of the pipe
/// write: the box is cleared before the write is awaited and nothing keeps it in a field or property.
/// PasswordBox has no undo and refuses copy/cut. Same window handling as <see cref="MaintenanceDialog"/>:
/// topmost, owned by the window it was opened from (so the owner's keep-on-top never covers it),
/// WS_EX_TOOLWINDOW. Escape or Cancel closes it.
/// </summary>
public partial class RecoveryDialog : Window
{
    // PBKDF2 takes well under a second; allow for the pipe and a busy service on top
    private static readonly TimeSpan BusyTimeout = TimeSpan.FromSeconds(15);

    private readonly DispatcherTimer _busyTimer;
    private readonly DispatcherTimer _countdown;
    private UiLang _lang;
    private bool _busy;
    private string? _errorCode;
    private int _retrySeconds;

    internal Func<PipeMessage, Task<bool>>? Sender { get; set; }

    /// <summary>Request ids of recovery_release, shared by every recovery dialog of this shell.</summary>
    internal MaintenanceRequestTracker Requests { get; set; } = new();

    internal RecoveryDialog(UiLang lang)
    {
        InitializeComponent();
        _lang = lang;

        _busyTimer = new DispatcherTimer { Interval = BusyTimeout };
        _busyTimer.Tick += (_, _) =>
        {
            _busyTimer.Stop();
            Requests.Cancel(); // a later answer to this attempt is ignored
            SetBusy(false);
            ShowError(AdminErrors.Error, 0);
        };
        _countdown = new DispatcherTimer { Interval = TimeSpan.FromSeconds(1) };
        _countdown.Tick += (_, _) => CountdownTick();

        SourceInitialized += (_, _) =>
        {
            var h = new WindowInteropHelper(this).Handle;
            Native.SetExStyle(h, Native.GetExStyle(h) | Native.WS_EX_TOOLWINDOW);
        };
        Loaded += (_, _) =>
        {
            try { Activate(); } catch (InvalidOperationException) { }
            CodeBox.Focus();
        };
        Closed += (_, _) =>
        {
            Requests.Cancel(); // nothing is waiting for an answer any more
            _busyTimer.Stop();
            _countdown.Stop();
            CodeBox.Clear();
        };
        PreviewKeyDown += (_, e) =>
        {
            if (e.Key == Key.Escape)
            {
                e.Handled = true;
                Close();
            }
        };

        Apply();
    }

    internal void SetLanguage(UiLang lang)
    {
        _lang = lang;
        Apply();
    }

    /// <summary>The service's answer to the pending recovery_release (App checks the request id).</summary>
    internal void ShowResult(RecoveryResultMessage r)
    {
        _busyTimer.Stop();
        SetBusy(false);
        if (r.Ok)
        {
            Close(); // the service follows with "released": App closes everything and exits
            return;
        }
        ShowError(r.Error, r.RetrySeconds);
        CodeBox.Focus();
    }

    private void ShowError(string? code, int retrySeconds)
    {
        _errorCode = code ?? AdminErrors.Error;
        _retrySeconds = code == AdminErrors.LockedOut ? Math.Max(1, retrySeconds) : 0;
        if (_retrySeconds > 0) _countdown.Start();
        else _countdown.Stop();
        Apply();
    }

    private void ClearError()
    {
        _errorCode = null;
        _retrySeconds = 0;
        _countdown.Stop();
        Apply();
    }

    private void CountdownTick()
    {
        if (--_retrySeconds > 0)
        {
            Apply();
            return;
        }
        ClearError();
    }

    private void SetBusy(bool busy)
    {
        _busy = busy;
        Apply();
    }

    private void Apply()
    {
        TitleText.Text = UiStrings.RecoveryTitle(_lang);
        HintText.Text = UiStrings.RecoveryHint(_lang);
        CodeLabel.Text = UiStrings.RecoveryCodeLabel(_lang);
        UnlockButton.Content = UiStrings.AdminUnlockButton(_lang);
        CancelButton.Content = UiStrings.AdminCancelButton(_lang);
        var hasError = _errorCode is not null;
        ErrorText.Text = hasError ? UiStrings.RecoveryError(_lang, _errorCode, _retrySeconds) : "";
        ErrorText.Visibility = hasError ? Visibility.Visible : Visibility.Collapsed;
        var lockedOut = _retrySeconds > 0;
        UnlockButton.IsEnabled = !_busy && !lockedOut;
        CodeBox.IsEnabled = !_busy && !lockedOut;
    }

    private async void OnUnlockClick(object sender, RoutedEventArgs e)
    {
        if (_busy || _retrySeconds > 0 || Sender is null) return;

        // read and clear in one step; the string then exists only inside the message handed to the pipe
        var code = CodeBox.Password;
        CodeBox.Clear();
        if (code.Length == 0)
        {
            ShowError(AdminErrors.InvalidCode, 0); // nothing sent, nothing counted
            CodeBox.Focus();
            return;
        }
        if (!RecoveryCode.IsPrintableAscii(code))
        {
            // typed on a non-English layout (or with other characters a code never has): it can never
            // match, so it is not sent and costs no attempt
            ShowError(RecoveryErrors.WrongLayout, 0);
            CodeBox.Focus();
            return;
        }

        ClearError();
        SetBusy(true);
        _busyTimer.Stop();
        _busyTimer.Start();

        var id = Requests.Begin();
        bool sent;
        try
        {
            sent = await Sender(new RecoveryReleaseMessage(id, code));
        }
        catch (Exception ex)
        {
            ShellLog.Error("Recovery code send", ex); // type and stack trace only, never the code
            sent = false;
        }

        if (!sent)
        {
            if (Requests.Pending == id) Requests.Cancel();
            _busyTimer.Stop();
            SetBusy(false);
            ShowError(AdminErrors.Error, 0);
        }
        // on success the busy state ends with recovery_result (or the 15 s timer)
    }

    private void OnCancelClick(object sender, RoutedEventArgs e) => Close();
}
