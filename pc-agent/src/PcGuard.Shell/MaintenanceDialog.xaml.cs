using System.Windows;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Threading;
using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>
/// Maintenance code dialog, opened by the "Administrator" link. Takes the six-digit one-time code a
/// teacher issued in the console and sends it to the service (maintenance_redeem); the service checks
/// it with the backend and answers admin_result. The duration was chosen by the teacher, not here.
///
/// The code exists only in the TextBox and in one local variable for the duration of the pipe write:
/// the box is cleared before the write is awaited and nothing keeps it in a field or property.
/// Topmost, owned by the window it was opened from (so the owner's own keep-on-top never covers it)
/// and WS_EX_TOOLWINDOW. Escape or Cancel closes it.
/// </summary>
public partial class MaintenanceDialog : Window
{
    // the service gives the backend 10 s; allow for the pipe and the command queue on top
    private static readonly TimeSpan BusyTimeout = TimeSpan.FromSeconds(15);

    private readonly DispatcherTimer _busyTimer;
    private readonly DispatcherTimer _countdown;
    private UiLang _lang;
    private bool _busy;
    private string? _errorCode;
    private int _retrySeconds;

    internal Func<PipeMessage, Task<bool>>? Sender { get; set; }

    internal MaintenanceDialog(UiLang lang)
    {
        InitializeComponent();
        _lang = lang;

        _busyTimer = new DispatcherTimer { Interval = BusyTimeout };
        _busyTimer.Tick += (_, _) => { _busyTimer.Stop(); SetBusy(false); ShowError(AdminErrors.Offline, 0); };
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

        // digits only, at most six: typed text, pasted text and anything else (Space bypasses
        // PreviewTextInput, so TextChanged filters as the last line)
        CodeBox.PreviewTextInput += (_, e) => e.Handled = MaintenanceCode.FilterInput(e.Text).Length != e.Text.Length;
        DataObject.AddPastingHandler(CodeBox, OnPaste);
        CodeBox.TextChanged += (_, _) =>
        {
            var filtered = MaintenanceCode.FilterInput(CodeBox.Text);
            if (filtered == CodeBox.Text) return;
            CodeBox.Text = filtered;
            CodeBox.CaretIndex = filtered.Length;
        };

        Apply();
    }

    internal void SetLanguage(UiLang lang)
    {
        _lang = lang;
        Apply();
    }

    /// <summary>The service's answer to the last maintenance_redeem.</summary>
    internal void ShowResult(AdminResultMessage r)
    {
        _busyTimer.Stop();
        SetBusy(false);
        if (r.Ok)
        {
            Close();
            return;
        }
        ShowError(r.Error, r.RetrySeconds);
        CodeBox.Focus();
    }

    private void OnPaste(object sender, DataObjectPastingEventArgs e)
    {
        e.CancelCommand();
        if (e.DataObject.GetData(DataFormats.UnicodeText) is not string pasted) return;
        var start = CodeBox.SelectionStart;
        var current = CodeBox.Text.Remove(start, CodeBox.SelectionLength);
        var merged = MaintenanceCode.FilterInput(current.Insert(start, pasted));
        CodeBox.Text = merged;
        CodeBox.CaretIndex = merged.Length;
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
        TitleText.Text = UiStrings.AdminTitle(_lang);
        CodeLabel.Text = UiStrings.MaintenanceCodeLabel(_lang);
        UnlockButton.Content = UiStrings.AdminUnlockButton(_lang);
        CancelButton.Content = UiStrings.AdminCancelButton(_lang);
        var hasError = _errorCode is not null;
        ErrorText.Text = hasError ? UiStrings.AdminError(_lang, _errorCode, _retrySeconds) : "";
        ErrorText.Visibility = hasError ? Visibility.Visible : Visibility.Collapsed;
        var lockedOut = _retrySeconds > 0;
        UnlockButton.IsEnabled = !_busy && !lockedOut;
        CodeBox.IsEnabled = !_busy && !lockedOut;
    }

    private async void OnUnlockClick(object sender, RoutedEventArgs e)
    {
        if (_busy || _retrySeconds > 0 || Sender is null) return;

        // read and clear in one step; the string then exists only inside the message handed to the pipe
        var code = CodeBox.Text;
        CodeBox.Clear();
        if (!MaintenanceCode.IsWellFormed(code))
        {
            ShowError(AdminErrors.InvalidCode, 0);
            CodeBox.Focus();
            return;
        }

        ClearError();
        SetBusy(true);
        _busyTimer.Stop();
        _busyTimer.Start();

        bool sent;
        try
        {
            sent = await Sender(new MaintenanceRedeemMessage(code));
        }
        catch (Exception ex)
        {
            ShellLog.Error("Maintenance code send", ex); // type and stack trace only, never the code
            sent = false;
        }

        if (!sent)
        {
            _busyTimer.Stop();
            SetBusy(false);
            ShowError(AdminErrors.Error, 0);
        }
        // on success the busy state ends with admin_result (or the 15 s timer)
    }

    private void OnCancelClick(object sender, RoutedEventArgs e) => Close();
}
