using System.Windows;
using System.Windows.Threading;
using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>
/// Entry point. Launched only by the guard service (no autostart). Single instance, never exits on
/// user action, logs unhandled exceptions to %LocalAppData%\PcGuard\shell.log and keeps running.
/// </summary>
public partial class App : Application
{
    private const string MutexName = @"Local\PcGuard.Shell.SingleInstance";
    private const int MaxQueuedMessages = 20;

    private Mutex? _mutex;
    private PipeClient? _pipe;
    private SnapshotSender? _sender;
    private LoginWindow? _login;
    private LockOverlay? _overlay;
    private MaintenanceBanner? _banner;
    private MaintenanceDialog? _dialog;
    // request ids of maintenance_redeem: outlives each dialog, so a late answer never lands in a new one
    private readonly MaintenanceRequestTracker _redeemRequests = new();
    private DateTimeOffset? _maintenanceUntil; // set while the service reports maintenance mode active
    private readonly Queue<string> _messages = new();
    private bool _popupOpen;
    private UiLang _lang = UiLang.Uz;
    private bool _connected;
    private StateMessage? _state;

    public static bool Quitting { get; private set; }

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        DispatcherUnhandledException += (_, args) =>
        {
            ShellLog.Error("Dispatcher", args.Exception);
            args.Handled = true;
        };
        AppDomain.CurrentDomain.UnhandledException += (_, args) =>
        {
            if (args.ExceptionObject is Exception ex) ShellLog.Error("AppDomain", ex);
        };
        TaskScheduler.UnobservedTaskException += (_, args) =>
        {
            ShellLog.Error("Task", args.Exception);
            args.SetObserved();
        };

        _mutex = new Mutex(initiallyOwned: true, MutexName, out var createdNew);
        if (!createdNew)
        {
            _mutex.Dispose();
            _mutex = null;
            Quitting = true;
            Shutdown();
            return;
        }

        _login = new LoginWindow(_lang) { Sender = m => _pipe?.SendAsync(m) ?? Task.FromResult(false) };
        _login.LanguageChanged += OnLanguageChanged;
        _overlay = new LockOverlay(_lang) { SignOutRequested = () => _ = _pipe?.SendAsync(new LogoutMessage()) };
        _login.AdminRequested += () => OpenMaintenanceDialog(_login);
        _overlay.AdminRequested = () => OpenMaintenanceDialog(_overlay);
        _banner = new MaintenanceBanner(_lang) { EndRequested = () => _ = _pipe?.SendAsync(new AdminEndMessage()) };
        _login.SetConnected(false);
        _login.Show();

        _pipe = new PipeClient();
        _pipe.ConnectionChanged += c => Dispatcher.BeginInvoke(() => OnConnection(c));
        _pipe.MessageReceived += m => Dispatcher.BeginInvoke(() => OnMessage(m));
        _sender = new SnapshotSender(_pipe);
        _pipe.Start();
        _sender.Start();
        ShellLog.Info("Shell started");
    }

    private void OnLanguageChanged(UiLang lang)
    {
        _lang = lang;
        _overlay?.SetLanguage(lang);
        _login?.SetLanguage(lang);
        _banner?.SetLanguage(lang);
        _dialog?.SetLanguage(lang);
        UpdateWindows();
    }

    private void OnConnection(bool connected)
    {
        _connected = connected;
        if (!connected)
        {
            _state = null; // a restarted service starts signed out; wait for its state
            _maintenanceUntil = null; // and maintenance is memory-only there: a restart re-locks
            _redeemRequests.Cancel(); // no answer comes from a dead service connection
        }
        _login?.SetConnected(connected);
        UpdateWindows();
    }

    private void OnMessage(PipeMessage message)
    {
        switch (message)
        {
            case LoginResultMessage r:
                _login?.ShowLoginResult(r);
                if (r.Ok) UpdateWindows(forceHideLogin: true);
                break;
            case StateMessage s:
                _state = s;
                UpdateWindows();
                break;
            case TextMessage t:
                EnqueueMessage(t.Text);
                break;
            case AdminResultMessage r:
                // only the answer to the request this shell is waiting for (superseded, timed-out or
                // cancelled requests are ignored)
                if (_redeemRequests.Accept(r.Id)) _dialog?.ShowResult(r);
                break;
            case MaintenanceMessage m:
                _maintenanceUntil = m.Active ? m.UntilUtc : null;
                UpdateWindows();
                break;
            case CloseWindowMessage c:
                _ = Task.Run(() => WindowEnumerator.Close(c.Hwnd));
                break;
        }
    }

    private void UpdateWindows(bool forceHideLogin = false)
    {
        var signedIn = _connected && _state?.Student is not null;
        var maintenance = _connected && _maintenanceUntil is not null;
        // maintenance mode: no sign-in lock at all (a signed-in student keeps the name banner)
        if (signedIn || maintenance || forceHideLogin) _login?.HideLogin();
        else _login?.ShowLogin();

        // visible whenever a student is signed in (so an unlocked student can still sign out)
        if (signedIn) _overlay?.ShowFor(_state!.Student!, _state.Remaining, _state.Locked);
        else _overlay?.HideOverlay();

        if (maintenance) _banner?.ShowUntil(_maintenanceUntil!.Value);
        else _banner?.HideBanner();

        // the dialog is pointless once maintenance is on, without a service, or when its window went away
        if (_dialog is { } d && (maintenance || !_connected || d.Owner is not { IsVisible: true }))
            d.Close();
    }

    private void OpenMaintenanceDialog(Window owner)
    {
        if (!_connected || _maintenanceUntil is not null || !owner.IsVisible) return;
        if (_dialog is { } open)
        {
            try { open.Activate(); } catch (InvalidOperationException) { }
            return;
        }

        var dialog = new MaintenanceDialog(_lang)
        {
            Owner = owner, // owned: always above the topmost owner, even when it re-asserts its z-order
            Sender = m => _pipe?.SendAsync(m) ?? Task.FromResult(false),
            Requests = _redeemRequests,
        };
        _dialog = dialog;
        if (_login is not null) _login.DialogOpen = true;
        dialog.Closed += (_, _) =>
        {
            if (ReferenceEquals(_dialog, dialog)) _dialog = null;
            if (_login is null) return;
            _login.DialogOpen = false;
            if (_login.IsVisible) _login.ActivateSafe();
        };
        dialog.Show();
    }

    private void EnqueueMessage(string text)
    {
        if (string.IsNullOrWhiteSpace(text)) return;
        if (_messages.Count >= MaxQueuedMessages) _messages.Dequeue();
        _messages.Enqueue(text.Length > 500 ? text[..500] : text);
        ShowNextMessage();
    }

    private void ShowNextMessage()
    {
        if (_popupOpen || _messages.Count == 0) return;
        _popupOpen = true;
        var popup = new MessagePopup(_messages.Dequeue());
        popup.Closed += (_, _) =>
        {
            _popupOpen = false;
            ShowNextMessage();
        };
        popup.Show();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        _sender?.Dispose();
        _pipe?.Dispose();
        if (_mutex is not null)
        {
            try { _mutex.ReleaseMutex(); } catch (ApplicationException) { }
            _mutex.Dispose();
        }
        base.OnExit(e);
    }
}
