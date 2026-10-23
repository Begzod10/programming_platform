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
        UpdateWindows();
    }

    private void OnConnection(bool connected)
    {
        _connected = connected;
        if (!connected) _state = null; // a restarted service starts signed out; wait for its state
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
            case CloseWindowMessage c:
                _ = Task.Run(() => WindowEnumerator.Close(c.Hwnd));
                break;
        }
    }

    private void UpdateWindows(bool forceHideLogin = false)
    {
        var signedIn = _connected && _state?.Student is not null;
        if (signedIn || forceHideLogin) _login?.HideLogin();
        else _login?.ShowLogin();

        if (signedIn && _state!.Locked) _overlay?.ShowFor(_state.Student!, _state.Remaining);
        else _overlay?.HideOverlay();
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
