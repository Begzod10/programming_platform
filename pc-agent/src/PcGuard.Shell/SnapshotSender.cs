using PcGuard.Core;

namespace PcGuard.Shell;

/// <summary>
/// Every 2 s (and right after connecting) builds a window snapshot and sends it to the service.
/// Runs entirely on thread-pool threads. PRIVACY: titles and URLs never leave this process except as
/// the bare browser host in the local pipe message.
/// </summary>
internal sealed class SnapshotSender : IDisposable
{
    private static readonly TimeSpan Interval = TimeSpan.FromSeconds(2);
    private static readonly TimeSpan BrowserReadBudget = TimeSpan.FromMilliseconds(1500);
    private const int MaxBrowsers = 200;

    private readonly PipeClient _pipe;
    private readonly CancellationTokenSource _cts = new();
    private readonly BrowserAddressReader _reader = new();
    private int _busy;

    public SnapshotSender(PipeClient pipe)
    {
        _pipe = pipe;
        _pipe.ConnectionChanged += OnConnectionChanged;
    }

    public void Start() => _ = Task.Run(() => LoopAsync(_cts.Token));

    private void OnConnectionChanged(bool connected)
    {
        if (connected) _ = Task.Run(SendOnceAsync);
    }

    private async Task LoopAsync(CancellationToken ct)
    {
        using var timer = new PeriodicTimer(Interval);
        try
        {
            while (await timer.WaitForNextTickAsync(ct).ConfigureAwait(false))
                await SendOnceAsync().ConfigureAwait(false);
        }
        catch (OperationCanceledException) { }
    }

    private async Task SendOnceAsync()
    {
        if (!_pipe.IsConnected) return;
        if (Interlocked.Exchange(ref _busy, 1) == 1) return; // previous snapshot still in progress
        try
        {
            var snapshot = await BuildAsync().ConfigureAwait(false);
            await _pipe.SendAsync(new SnapshotMessage(snapshot)).ConfigureAwait(false);
        }
        catch (Exception e)
        {
            ShellLog.Error("SnapshotSender", e);
        }
        finally
        {
            Volatile.Write(ref _busy, 0);
        }
    }

    private async Task<Snapshot> BuildAsync()
    {
        var windows = WindowEnumerator.Enumerate();

        var windowed = windows
            .GroupBy(w => w.Pid)
            .Select(g => new WindowedProc(g.Key, g.First().Exe))
            .Take(PipeMessage.MaxSnapshotEntries)
            .ToList();

        var browserWindows = windows.Where(w => BrowserHostRule.IsBrowser(w.Exe)).Take(MaxBrowsers).ToList();
        var hosts = await ReadHostsAsync(browserWindows).ConfigureAwait(false);
        var browsers = browserWindows
            .Select(w => new BrowserWindow(w.Hwnd, w.Pid, hosts.GetValueOrDefault(w.Hwnd)))
            .ToList();

        return new Snapshot(windowed, WindowEnumerator.ForegroundExe(), browsers);
    }

    // UI Automation can block on a hung browser: read on a worker with a time budget; whatever is not
    // done in time is reported as unknown (null host). A still-running read must finish before the
    // next one starts, because the reader is single-threaded.
    private Task<Dictionary<long, string?>>? _pendingRead;

    private async Task<Dictionary<long, string?>> ReadHostsAsync(List<AppWindow> browserWindows)
    {
        var none = new Dictionary<long, string?>();
        if (browserWindows.Count == 0) return none;
        if (_pendingRead is { IsCompleted: false }) return none;

        var live = browserWindows.Select(w => w.Hwnd).ToHashSet();
        var result = new Dictionary<long, string?>();
        var work = Task.Run(() =>
        {
            _reader.Prune(live);
            foreach (var w in browserWindows)
            {
                var host = _reader.ReadHost(w.Hwnd);
                lock (result) result[w.Hwnd] = host;
            }
            return result;
        });
        _pendingRead = work;
        try
        {
            await work.WaitAsync(BrowserReadBudget).ConfigureAwait(false);
        }
        catch (TimeoutException)
        {
            lock (result) return new Dictionary<long, string?>(result); // partial: the rest is null
        }
        catch (Exception e)
        {
            ShellLog.Error("BrowserAddressReader", e);
            return none;
        }
        lock (result) return new Dictionary<long, string?>(result);
    }

    public void Dispose()
    {
        _pipe.ConnectionChanged -= OnConnectionChanged;
        _cts.Cancel();
    }
}
