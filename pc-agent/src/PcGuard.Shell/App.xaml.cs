using System.Windows;
using System.Windows.Threading;
using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>
/// Entry point. Launched only by the guard service (no autostart). Single instance, never exits on
/// user action, logs unhandled exceptions to %LocalAppData%\PcGuard\shell.log and keeps running once
/// started. A failure BEFORE startup completed (or a startup that hangs past the watchdog) ends the
/// process with a non-zero exit code after logging, so no windowless shell is left behind; a second
/// instance of the same install in the same session exits with code 0. shell.log carries a one-line
/// startup trail (single-instance result, windows created, pipe connect attempts with Win32 codes).
/// It exits only (a) on the service's "released" message after an accepted recovery code, and only
/// when the pipe server was verified to be the PcGuard service process, or (b) when the connection is
/// gone and the SCM reports PcGuard stopped AND disabled (a missed "released"; the service also
/// terminates every shell it launched 1.5 s after sending it).
/// </summary>
public partial class App : Application
{
    private const string MutexName = @"Local\PcGuard.Shell.SingleInstance";
    private const int MaxQueuedMessages = 20;

    private Microsoft.Win32.SafeHandles.SafeWaitHandle? _instance; // single-instance name, held open for the process lifetime
    private bool _startupComplete; // Volatile: read by the dispatcher handler and the watchdog thread
    private Timer? _startupWatchdog;
    private PipeClient? _pipe;
    private SnapshotSender? _sender;
    private LoginWindow? _login;
    private LockOverlay? _overlay;
    private MaintenanceBanner? _banner;
    private MaintenanceDialog? _dialog;
    private RecoveryDialog? _recoveryDialog;
    // request ids of recovery_release (separate from the maintenance ones)
    private readonly MaintenanceRequestTracker _recoveryRequests = new();
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
            // before startup completed: never mask the failure (a windowless shell is a zombie the
            // service kills and relaunches forever); after it: log and keep the lock screen up
            if (StartupFailurePolicy.ShouldTerminate(Volatile.Read(ref _startupComplete)))
                ExitAfterStartupFailure(args.Exception);
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

        // startup watchdog: a startup that hangs (never throws) must not leave a windowless process either
        _startupWatchdog = new Timer(_ =>
        {
            if (Volatile.Read(ref _startupComplete)) return;
            ShellLog.Info(ShellDiagnostics.WatchdogLine(StartupFailurePolicy.WatchdogTimeout, StartupFailurePolicy.WatchdogExitCode));
            Environment.Exit(StartupFailurePolicy.WatchdogExitCode);
        }, null, StartupFailurePolicy.WatchdogTimeout, Timeout.InfiniteTimeSpan);

        try
        {
            StartUp();
        }
        catch (Exception ex)
        {
            ShellLog.Error("Startup", ex);
            ExitAfterStartupFailure(ex);
        }
    }

    private static void ExitAfterStartupFailure(Exception ex)
    {
        ShellLog.Info(ShellDiagnostics.StartupFailedLine(ex.GetType().FullName ?? "Exception", StartupFailurePolicy.StartupFailedExitCode));
        Environment.Exit(StartupFailurePolicy.StartupFailedExitCode);
    }

    private void StartUp()
    {
        int session;
        using (var me = System.Diagnostics.Process.GetCurrentProcess()) session = me.SessionId;
        ShellLog.Info(ShellDiagnostics.Step(string.Create(System.Globalization.CultureInfo.InvariantCulture,
            $"pid {Environment.ProcessId}, session {session}, Administrators enabled: {Native.AdministratorsEnabled()}")));

        var (result, win32, handle) = Native.CreateSingleInstanceMutex(MutexName);
        var another = result != MutexOpenResult.CreatedNew && Native.AnotherShellInstanceRunning();
        var action = SingleInstancePolicy.Decide(result, another);
        ShellLog.Info(ShellDiagnostics.SingleInstanceLine(result, win32, action));
        if (action == SingleInstanceAction.ExitDuplicate)
        {
            // another genuine shell of this install runs in this session: leave quietly (no window was
            // created, nothing to clean up; the handle closes with the process)
            handle?.Dispose();
            Quitting = true;
            Environment.Exit(StartupFailurePolicy.DuplicateExitCode);
            return;
        }
        _instance = handle; // RunWithoutLock: null or an opened (squatted/stale) name; never stops the lock screen

        _login = new LoginWindow(_lang) { Sender = m => _pipe?.SendAsync(m) ?? Task.FromResult(false) };
        _login.LanguageChanged += OnLanguageChanged;
        _overlay = new LockOverlay(_lang) { SignOutRequested = () => _ = _pipe?.SendAsync(new LogoutMessage()) };
        _login.AdminRequested += () => OpenMaintenanceDialog(_login);
        _overlay.AdminRequested = () => OpenMaintenanceDialog(_overlay);
        _login.RecoveryRequested += () => OpenRecoveryDialog(_login);
        _overlay.RecoveryRequested = () => OpenRecoveryDialog(_overlay);
        _banner = new MaintenanceBanner(_lang) { EndRequested = () => _ = _pipe?.SendAsync(new AdminEndMessage()) };
        _login.SetConnected(false);
        _login.Show();
        ShellLog.Info(ShellDiagnostics.Step("windows created"));

        _pipe = new PipeClient(VerifyServer, ServiceStoppedAndDisabled);
        _pipe.ConnectionChanged += c => Dispatcher.BeginInvoke(() => OnConnection(c));
        _pipe.MessageReceived += (m, trust) => Dispatcher.BeginInvoke(() => OnMessage(m, trust));
        _pipe.GaveUp += () => Dispatcher.BeginInvoke(() => Release("The PcGuard service is stopped and disabled: exiting"));
        _sender = new SnapshotSender(_pipe);
        _pipe.Start();
        _sender.Start();
        ShellLog.Info(ShellDiagnostics.Step("pipe client and snapshot sender started"));

        Volatile.Write(ref _startupComplete, true);
        _startupWatchdog?.Dispose();
        _startupWatchdog = null;
        ShellLog.Info("Shell started");
    }

    private void OnLanguageChanged(UiLang lang)
    {
        _lang = lang;
        _overlay?.SetLanguage(lang);
        _login?.SetLanguage(lang);
        _banner?.SetLanguage(lang);
        _dialog?.SetLanguage(lang);
        _recoveryDialog?.SetLanguage(lang);
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
            _recoveryRequests.Cancel();
        }
        _login?.SetConnected(connected);
        UpdateWindows();
    }

    private static PipeServerTrust VerifyServer(Microsoft.Win32.SafeHandles.SafePipeHandle pipe)
        => ShellServiceCheck.ClassifyServer(Native.TryGetPipeServerProcessId(pipe), Native.TryProbeService(ShellServiceCheck.ServiceName));

    private static bool ServiceStoppedAndDisabled()
        => ShellServiceCheck.ShouldExit(Native.TryProbeService(ShellServiceCheck.ServiceName));

    private void OnMessage(PipeMessage message, PipeServerTrust trust)
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
            case RecoveryResultMessage r:
                if (_recoveryRequests.Accept(r.Id)) _recoveryDialog?.ShowResult(r);
                break;
            case ReleasedMessage:
                // the only message that makes the shell exit: never from a server not proven to be the service
                if (ShellServiceCheck.HonourReleased(trust)) Release("Released with the recovery code: exiting");
                else ShellLog.Info("Ignored 'released' from a pipe server that could not be verified");
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
        if (_recoveryDialog is { } rd && (!_connected || rd.Owner is not { IsVisible: true }))
            rd.Close();
    }

    /// <summary>The service accepted the recovery code and is stopping for good: close everything and exit.</summary>
    private void Release(string reason)
    {
        if (Quitting) return;
        ShellLog.Info(reason);
        Quitting = true; // lets the sign-in window and the banner close
        _dialog?.Close();
        _recoveryDialog?.Close();
        Shutdown();
    }

    /// <summary>Activates an open maintenance or recovery dialog; true when there was one (only one at a time).</summary>
    private bool ActivateOpenDialog()
    {
        Window? open = (Window?)_dialog ?? _recoveryDialog;
        if (open is null) return false;
        try { open.Activate(); } catch (InvalidOperationException) { }
        return true;
    }

    private void OpenRecoveryDialog(Window owner)
    {
        if (!_connected || !owner.IsVisible || ActivateOpenDialog()) return;

        var dialog = new RecoveryDialog(_lang)
        {
            Owner = owner, // owned: always above the topmost owner, even when it re-asserts its z-order
            Sender = m => _pipe?.SendAsync(m) ?? Task.FromResult(false),
            Requests = _recoveryRequests,
        };
        _recoveryDialog = dialog;
        if (_login is not null) _login.DialogOpen = true;
        dialog.Closed += (_, _) =>
        {
            if (ReferenceEquals(_recoveryDialog, dialog)) _recoveryDialog = null;
            if (_login is null || Quitting) return;
            _login.DialogOpen = false;
            if (_login.IsVisible) _login.ActivateSafe();
        };
        dialog.Show();
    }

    private void OpenMaintenanceDialog(Window owner)
    {
        if (!_connected || _maintenanceUntil is not null || !owner.IsVisible) return;
        if (ActivateOpenDialog()) return;

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
        _startupWatchdog?.Dispose();
        _instance?.Dispose();
        base.OnExit(e);
    }
}
