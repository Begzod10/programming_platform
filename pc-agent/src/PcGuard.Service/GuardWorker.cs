using System.Threading.Channels;
using PcGuard.Core;

namespace PcGuard.Service;

/// <summary>
/// The guard: owns the session (token in memory only), the rule cache, usage queue and WebSocket,
/// enforces every 2 s and talks to the shell over the pipe. Session changes (login, logout, usage
/// upload, token death) are serialised through one command channel so they never race.
///
/// The shell is only the service's eyes (snapshots); every decision is made here
/// (<see cref="EnforcementPlanner"/>). Without a fresh snapshot the planner falls back to stricter
/// name-only enforcement and the shell is relaunched.
/// </summary>
internal sealed class GuardWorker : BackgroundService
{
    private static readonly TimeSpan TickEvery = TimeSpan.FromSeconds(2);
    private static readonly TimeSpan UploadEvery = TimeSpan.FromSeconds(60);
    private const int MaxBatchesPerUpload = 20;

    private abstract record Command;
    private sealed record LoginCmd : Command;
    private sealed record LogoutCmd : Command;
    private sealed record UploadCmd : Command;
    private sealed record TokenDeadCmd(int Generation) : Command;

    private sealed class Session
    {
        public required string Token { get; init; }
        public required int Generation { get; init; }
        public required string Tag { get; init; } // per-login GUID; usage events carry it so they upload with this token only
        public required string? StudentName { get; init; }
        public required CancellationTokenSource WsCts { get; init; }
        public PcRules? LastServerRules { get; set; }
        public volatile bool WsConnected;
        public Task? WsTask;
    }

    private readonly ILogger<GuardWorker> _log;
    private readonly Uri _baseUrl;
    private readonly Func<DateTimeOffset> _clock = () => DateTimeOffset.Now;
    // Bounded so a flood of pipe commands cannot grow memory without limit; oldest dropped if full.
    private readonly Channel<Command> _commands = Channel.CreateBounded<Command>(
        new BoundedChannelOptions(256) { SingleReader = true, FullMode = BoundedChannelFullMode.DropOldest });
    private readonly object _snapLock = new();
    private readonly object _stateLock = new();
    private readonly ShellPin _shellPin = new();

    // Latest pending login (password held only until consumed). Guarded by _loginLock.
    // _loginQueued ensures at most ONE LoginCmd marker is ever in the channel, so a login flood can
    // never push a LogoutCmd / TokenDeadCmd out under the channel's DropOldest policy.
    private readonly object _loginLock = new();
    private LoginMessage? _pendingLogin;
    private int _loginQueued;

    // Tag -> token for the current (ClosedAt null) and recently closed sessions, memory only.
    private readonly object _sessionsLock = new();
    private readonly Dictionary<string, SessionToken> _sessions = new();

    // created in ExecuteAsync (after the data folder is secured)
    private RuleCache _cache = null!;
    private UsageQueue _queue = null!;
    private UsageTracker _tracker = null!;
    private BackendClient _backend = null!;
    private PipeServer _pipe = null!;
    private ProcessEnumerator _enumerator = null!;
    private ShellSupervisor _supervisor = null!;
    private ProcessKiller _killer = null!;
    private string _machineKey = "";
    private readonly string _hostname = Environment.MachineName;

    private volatile Session? _session; // written only by the command loop
    private int _generation;
    private Snapshot? _snapshot;
    private DateTimeOffset _snapshotAt = DateTimeOffset.MinValue;
    private DateTimeOffset? _lastSnapshotAt;
    private DateTimeOffset? _lastAliveAt; // liveness only; never freshens the snapshot
    private int? _snapshotPid;
    private uint? _snapshotSession;
    private uint? _lastConsole;
    private DateTimeOffset? _shellMissingSince;
    private StateMessage? _lastStateSent;
    private bool _wasFallback;

    public GuardWorker(ILogger<GuardWorker> log, IConfiguration config)
    {
        _log = log;
        var raw = config["Backend:BaseUrl"];
        if (!Uri.TryCreate(raw, UriKind.Absolute, out var u) || u.Scheme is not ("https" or "http"))
        {
            _log.LogCritical("Backend:BaseUrl is missing or invalid; the PC stays locked (sign-in impossible)");
            u = new Uri("https://invalid.invalid/api/v1");
        }
        if (u.Scheme == "http") _log.LogWarning("Backend:BaseUrl uses plain http; passwords and tokens travel unencrypted");
        if (u.Host.Contains("CHANGE-ME", StringComparison.OrdinalIgnoreCase)) _log.LogCritical("Backend:BaseUrl was not configured (CHANGE-ME)");
        _baseUrl = u;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var shellPath = Path.Combine(AppContext.BaseDirectory, "PcGuard.Shell.exe");
        var store = new SecureStore(_log);
        var secured = true;
        try { store.EnsureDirectory(); }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or InvalidOperationException)
        {
            secured = false;
            _log.LogCritical("Could not secure the data folder: {Error} {Message}. Running fail-closed: memory-only, locked.", e.GetType().Name, e.Message);
        }

        if (secured)
        {
            try { _machineKey = store.LoadOrCreateMachineKey(); }
            catch (Exception e) when (e is IOException or UnauthorizedAccessException)
            {
                _machineKey = Guid.NewGuid().ToString("D");
                _log.LogError("Could not persist the machine key ({Error}); using a temporary one", e.GetType().Name);
            }
        }
        else
        {
            // fail closed: no persisted cache (locked, Defaults allowlist) and no persisted queue;
            // nothing sensitive is written to an unprotected folder.
            _machineKey = Guid.NewGuid().ToString("D");
        }

        _cache = new RuleCache(store.RulesPath, TimeSpan.FromMinutes(10), _clock, persist: secured);
        _queue = new UsageQueue(store.UsageQueuePath, persist: secured);
        _tracker = new UsageTracker(_clock);
        _backend = new BackendClient(_baseUrl, _log);
        _pipe = new PipeServer(shellPath, _shellPin, _log);
        _enumerator = new ProcessEnumerator(shellPath, _log);
        _supervisor = new ShellSupervisor(shellPath, _shellPin, _log);
        _killer = new ProcessKiller(_log);

        // Startup purge: any queued events from before this process started have no token in memory
        // and can never be safely attributed, so drop them (never upload with the wrong token).
        foreach (var tag in _queue.Tags()) _queue.DropTag(tag);

        _pipe.MessageReceived += OnPipeMessageAsync;
        _pipe.ClientConnected += _ => PushStateAsync(force: true);

        _log.LogInformation("PC Guard started (queued usage events after startup purge: {Count})", _queue.Count);

        var pipeTask = _pipe.RunAsync(stoppingToken);
        var commandTask = CommandLoopAsync(stoppingToken);
        var uploadTask = UploadTimerAsync(stoppingToken);
        try
        {
            using var timer = new PeriodicTimer(TickEvery);
            do
            {
                try { Tick(stoppingToken); }
                catch (Exception e) when (e is not OperationCanceledException)
                {
                    _log.LogError(e, "Enforcement tick failed");
                }
            } while (await timer.WaitForNextTickAsync(stoppingToken).ConfigureAwait(false));
        }
        catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested) { }
        finally
        {
            _session?.WsCts.Cancel();
            await Task.WhenAll(Quiet(pipeTask), Quiet(commandTask), Quiet(uploadTask)).ConfigureAwait(false);
            // capture what was tracked under the current session's tag; never delete the rule cache
            // (the PC must stay locked after a stop). On the next start these are purged anyway.
            _tracker.Observe(null, true);
            if (_session is { } cur) _queue.Enqueue(cur.Tag, _tracker.Drain());
            _backend.Dispose();
            _log.LogInformation("PC Guard stopped");
        }
    }

    private static async Task Quiet(Task t)
    {
        try { await t.ConfigureAwait(false); }
        catch (OperationCanceledException) { }
    }

    // ---------------- enforcement ----------------

    private void Tick(CancellationToken stopping)
    {
        var now = _clock();
        var rules = Effective();
        var console = Native.ActiveConsoleSessionId();

        // Console session changed (fast user switch / sign-in): the old shell and its snapshots belong
        // to a different session. Drop them and the pin; the supervisor relaunches in the new session.
        if (console != _lastConsole)
        {
            _lastConsole = console;
            _shellPin.Clear();
            lock (_snapLock) { _snapshot = null; _snapshotAt = DateTimeOffset.MinValue; _snapshotSession = null; }
        }

        var procs = console is { } c
            ? _enumerator.Enumerate(c)
            : new SessionProcesses(Array.Empty<RunningProcess>(), Array.Empty<int>(), new Dictionary<int, string>());

        Snapshot? snap;
        DateTimeOffset at;
        int? snapPid;
        uint? snapSession;
        lock (_snapLock) { snap = _snapshot; at = _snapshotAt; snapPid = _snapshotPid; snapSession = _snapshotSession; }
        // Only a snapshot from the current console session is usable (SnapshotGate); otherwise the
        // planner runs in fallback (name-only, stricter) as if the shell were missing.
        if (!SnapshotGate.IsUsable(snapSession, console)) snap = null;

        var exempt = new List<int> { Environment.ProcessId };
        if (snapPid is { } sp && _pipe.ActiveClientPid == sp) exempt.Add(sp);

        var plan = EnforcementPlanner.Plan(rules, snap, at, now, procs.Processes, exempt);

        foreach (var hwnd in plan.CloseWindows) _ = _pipe.SendAsync(new CloseWindowMessage(hwnd));
        foreach (var pid in plan.KillPids) _killer.Schedule(pid, procs.ImagePaths.GetValueOrDefault(pid), stopping);

        if (plan.UsedFallback != _wasFallback)
        {
            _wasFallback = plan.UsedFallback;
            if (plan.UsedFallback) _log.LogWarning("No fresh snapshot from the shell: name-only enforcement");
            else _log.LogInformation("Shell snapshots resumed: window-aware enforcement");
        }

        var foreground = plan.ShellMissing ? null : snap?.Foreground;
        _tracker.Observe(_session is null ? null : foreground, rules.Locked);

        if (plan.ShellMissing) _shellMissingSince ??= now;
        else _shellMissingSince = null;
        DateTimeOffset? lastSnap;
        lock (_snapLock) lastSnap = _lastSnapshotAt;
        DateTimeOffset? lastAlive;
        lock (_snapLock) lastAlive = _lastAliveAt;
        _supervisor.Supervise(now, _shellMissingSince, lastSnap, lastAlive, console, procs.ShellPids);

        _ = PushStateAsync(force: false);
    }

    private PcRules Effective()
    {
        var s = _session;
        var cached = _cache.Current();
        if (s is null) return SessionRules.SignedOut(cached);
        return cached.StudentName is null ? cached with { StudentName = s.StudentName } : cached;
    }

    private string? FreshForeground()
    {
        var console = Native.ActiveConsoleSessionId();
        lock (_snapLock)
        {
            if (!SnapshotGate.IsUsable(_snapshotSession, console)) return null;
            var age = _clock() - _snapshotAt;
            return _snapshot is not null && age >= TimeSpan.Zero && age <= EnforcementPlanner.SnapshotMaxAge ? _snapshot.Foreground : null;
        }
    }

    private async Task PushStateAsync(bool force)
    {
        var msg = SessionRules.ToStateMessage(Effective());
        lock (_stateLock)
        {
            if (!force && msg == _lastStateSent) return;
            _lastStateSent = msg;
        }
        if (!await _pipe.SendAsync(msg).ConfigureAwait(false))
        {
            lock (_stateLock) { if (_lastStateSent == msg) _lastStateSent = null; } // resend when a shell is back
        }
    }

    // ---------------- pipe ----------------

    private Task OnPipeMessageAsync(PipeMessage message, int clientPid)
    {
        switch (message)
        {
            case SnapshotMessage s:
                if (_pipe.ActiveClientPid != clientPid) break;
                var fg = s.Snapshot.Foreground?.Trim().ToLowerInvariant();
                if (fg is { Length: > 255 }) fg = fg[..255]; // server limit for app_name; an invalid event would 422 a whole batch
                var clientSession = Native.SessionIdOf(clientPid);
                lock (_snapLock)
                {
                    _snapshot = s.Snapshot with { Foreground = string.IsNullOrEmpty(fg) ? null : fg };
                    _snapshotAt = _clock();
                    _lastSnapshotAt = _snapshotAt;
                    _snapshotPid = clientPid;
                    _snapshotSession = clientSession;
                }
                break;
            case AliveMessage:
                // shell is up but on a non-Default desktop (no snapshot): counts against "hung" only
                if (_pipe.ActiveClientPid != clientPid) break;
                lock (_snapLock) _lastAliveAt = _clock();
                break;
            case LoginMessage l:
                // Keep only the latest login (one password in memory) and enqueue at most one marker,
                // so a login flood cannot evict a LogoutCmd / TokenDeadCmd under DropOldest.
                lock (_loginLock) _pendingLogin = l;
                if (Interlocked.Exchange(ref _loginQueued, 1) == 0) _commands.Writer.TryWrite(new LoginCmd());
                break;
            case LogoutMessage:
                _commands.Writer.TryWrite(new LogoutCmd());
                break;
            default:
                _log.LogDebug("Ignoring pipe message of kind {Kind}", message.T);
                break;
        }
        return Task.CompletedTask;
    }

    // ---------------- session commands ----------------

    private async Task UploadTimerAsync(CancellationToken ct)
    {
        using var timer = new PeriodicTimer(UploadEvery);
        while (await timer.WaitForNextTickAsync(ct).ConfigureAwait(false))
            _commands.Writer.TryWrite(new UploadCmd());
    }

    private async Task CommandLoopAsync(CancellationToken ct)
    {
        await foreach (var cmd in _commands.Reader.ReadAllAsync(ct).ConfigureAwait(false))
        {
            try
            {
                switch (cmd)
                {
                    case LoginCmd:
                        Interlocked.Exchange(ref _loginQueued, 0); // reset first: a login arriving now re-queues a marker
                        LoginMessage? login;
                        lock (_loginLock) { login = _pendingLogin; _pendingLogin = null; }
                        if (login is not null) await LoginAsync(login, ct).ConfigureAwait(false);
                        break;
                    case LogoutCmd: await SignOutAsync(callLogout: true, ct).ConfigureAwait(false); break;
                    case UploadCmd: await UploadTickAsync(ct).ConfigureAwait(false); break;
                    case TokenDeadCmd d when _session is { } s && s.Generation == d.Generation:
                        await TokenDiedAsync(s).ConfigureAwait(false);
                        break;
                }
            }
            catch (OperationCanceledException) when (ct.IsCancellationRequested)
            {
                throw;
            }
            catch (Exception e)
            {
                _log.LogError("Session command {Command} failed: {Error}", cmd.GetType().Name, e.GetType().Name);
            }
        }
    }

    private async Task LoginAsync(LoginMessage m, CancellationToken ct)
    {
        // Track whether a definitive result was produced (regardless of whether the pipe write
        // succeeded), so the finally only sends "offline" on an unexpected failure — never after a
        // successful sign-in to a shell that momentarily dropped and reconnected.
        var produced = false;
        try
        {
            if (_session is not null) await SignOutAsync(callLogout: true, ct).ConfigureAwait(false);

            var username = m.Username.Trim();
            if (username.Length == 0 || m.Password.Length == 0)
            {
                produced = true;
                await _pipe.SendAsync(new LoginResultMessage(false, "bad_credentials")).ConfigureAwait(false);
                return;
            }

            var r = await _backend.LoginAsync(username, m.Password, _hostname, _machineKey, ct).ConfigureAwait(false);
            if (!r.Ok || r.Token is null || r.State is null)
            {
                _log.LogInformation("Sign-in failed: {Error}", r.Error);
                produced = true;
                await _pipe.SendAsync(new LoginResultMessage(false, r.Error ?? "offline")).ConfigureAwait(false);
                await Task.Delay(TimeSpan.FromSeconds(1), ct).ConfigureAwait(false); // slow down guessing through the shell
                return;
            }

            _tracker.Observe(null, true); // nothing tracked before sign-in belongs to this student
            _tracker.Drain();
            _cache.Apply(r.State);
            StartSession(r.Token, r.State, ct);
            _log.LogInformation("Student signed in");
            produced = true;
            await _pipe.SendAsync(new LoginResultMessage(true, null)).ConfigureAwait(false);
            await PushStateAsync(force: true).ConfigureAwait(false);
        }
        finally
        {
            // the shell must always get a result, even on an unexpected failure (its UI would hang otherwise)
            if (!produced && !ct.IsCancellationRequested)
                await _pipe.SendAsync(new LoginResultMessage(false, "offline")).ConfigureAwait(false);
        }
    }

    private void StartSession(string token, PcRules state, CancellationToken ct)
    {
        var tag = Guid.NewGuid().ToString("N");
        lock (_sessionsLock) _sessions[tag] = new SessionToken(token, null); // open session: ClosedAt null
        var s = new Session
        {
            Token = token,
            Generation = ++_generation,
            Tag = tag,
            StudentName = state.StudentName,
            WsCts = CancellationTokenSource.CreateLinkedTokenSource(ct),
            LastServerRules = state,
        };
        var handlers = new WsHandlers
        {
            ForegroundApp = FreshForeground,
            OnState = rules =>
            {
                if (_session != s) return;
                s.LastServerRules = rules;
                _cache.Apply(rules);
                _ = PushStateAsync(force: false);
            },
            OnPong = () =>
            {
                // the server re-checks the session on every heartbeat and only sends state when it
                // changed, so a pong confirms the last rules: refresh the cache's freshness
                if (_session == s && s.LastServerRules is { } last) _cache.Apply(last);
            },
            OnMessage = text =>
            {
                if (_session == s) _ = _pipe.SendAsync(new TextMessage(text));
            },
            OnConnectedChanged = up => s.WsConnected = up,
        };
        _session = s;
        s.WsTask = Task.Run(async () =>
        {
            var end = await _backend.RunWebSocketAsync(token, handlers, s.WsCts.Token).ConfigureAwait(false);
            if (end == WsEnd.TokenDead) _commands.Writer.TryWrite(new TokenDeadCmd(s.Generation));
        }, CancellationToken.None);
    }

    private async Task SignOutAsync(bool callLogout, CancellationToken ct)
    {
        var s = _session;
        if (s is null)
        {
            await PushStateAsync(force: true).ConfigureAwait(false);
            return;
        }
        _tracker.Observe(null, true);
        _queue.Enqueue(s.Tag, _tracker.Drain());
        await UploadAllAsync(s, ct).ConfigureAwait(false); // before the logout call (session must still be open)
        if (callLogout) await _backend.LogoutAsync(s.Token, ct).ConfigureAwait(false);
        await EndSessionAsync(s).ConfigureAwait(false);
        _log.LogInformation("Student signed out");
    }

    private async Task TokenDiedAsync(Session s)
    {
        _log.LogWarning("Session token is no longer valid; signing out");
        _tracker.Observe(null, true);
        _queue.Enqueue(s.Tag, _tracker.Drain()); // uploaded with THIS session's token later, or dropped if it 401s
        await EndSessionAsync(s).ConfigureAwait(false);
    }

    private async Task EndSessionAsync(Session s)
    {
        _session = null;
        // keep the token in memory, marked closed, so this session's leftover usage can still be
        // uploaded (backend accepts a closed session's token for 24 h). Never re-tag events.
        lock (_sessionsLock)
        {
            if (_sessions.TryGetValue(s.Tag, out var st) && st.ClosedAt is null)
                _sessions[s.Tag] = st with { ClosedAt = _clock() };
            PruneSessions();
        }
        s.WsCts.Cancel();
        if (s.WsTask is { } t) await Task.WhenAny(t, Task.Delay(TimeSpan.FromSeconds(3))).ConfigureAwait(false);
        s.WsCts.Dispose();
        await PushStateAsync(force: true).ConfigureAwait(false);
    }

    private async Task UploadTickAsync(CancellationToken ct)
    {
        var s = _session;
        if (s is not null) _queue.Enqueue(s.Tag, _tracker.Drain());

        if (await UploadAllAsync(s, ct).ConfigureAwait(false))
        {
            if (s is not null) await TokenDiedAsync(s).ConfigureAwait(false);
            return;
        }

        if (s is not null && !s.WsConnected)
        {
            // WebSocket down: poll the state so the cache does not expire while HTTP still works
            var (status, state) = await _backend.GetStateAsync(s.Token, ct).ConfigureAwait(false);
            if (status is 401 or 403)
            {
                await TokenDiedAsync(s).ConfigureAwait(false);
                return;
            }
            if (state is not null && _session == s)
            {
                s.LastServerRules = state;
                _cache.Apply(state);
                await PushStateAsync(force: false).ConfigureAwait(false);
            }
        }
    }

    /// <summary>
    /// Uploads every queued tag with that tag's own token (<see cref="UsageUploadPlanner"/>); a tag
    /// whose token is unknown or past the 24 h grace is dropped. Returns true when the CURRENT
    /// session's token was rejected (so the caller signs it out). A closed session's 401/403 just
    /// drops that tag.
    /// </summary>
    private async Task<bool> UploadAllAsync(Session? current, CancellationToken ct)
    {
        var currentTokenDead = false;
        foreach (var tag in _queue.Tags())
        {
            SessionToken? token;
            lock (_sessionsLock) _sessions.TryGetValue(tag, out token);
            var decision = UsageUploadPlanner.Decide(token, _clock());
            if (decision.Action == UsageTagAction.Drop || decision.Token is null)
            {
                if (_queue.PeekBatch(tag, 1).Count > 0)
                    _log.LogWarning("Dropping {Count} usage events for a session whose token is unavailable", _queue.PeekBatch(tag, UsageQueue.MaxBatch).Count);
                _queue.DropTag(tag);
                continue;
            }

            for (var i = 0; i < MaxBatchesPerUpload; i++)
            {
                var batch = _queue.PeekBatch(tag, BackendProtocol.MaxUsageBatch);
                if (batch.Count == 0) break;
                var outcome = await _backend.UploadUsageAsync(decision.Token, batch, ct).ConfigureAwait(false);
                if (outcome == UsageOutcome.Ok)
                {
                    _queue.Remove(tag, batch.Count);
                }
                else if (outcome == UsageOutcome.DropBatch)
                {
                    _log.LogWarning("Server rejected a usage batch of {Count} events; dropping it", batch.Count);
                    _queue.Remove(tag, batch.Count);
                }
                else if (outcome == UsageOutcome.TokenDead)
                {
                    _queue.DropTag(tag); // 401/403: drop this session's events entirely
                    if (current is not null && tag == current.Tag) currentTokenDead = true;
                    break;
                }
                else // Retry: keep and try again on the next tick
                {
                    break;
                }
            }
        }
        return currentTokenDead;
    }

    // Drop closed sessions whose grace has expired so the dictionary cannot grow without bound.
    private void PruneSessions()
    {
        var now = _clock();
        var stale = _sessions
            .Where(kv => kv.Value.ClosedAt is { } c && (now - c > UsageUploadPlanner.Grace || now < c))
            .Select(kv => kv.Key).ToList();
        foreach (var tag in stale) _sessions.Remove(tag);
    }
}
