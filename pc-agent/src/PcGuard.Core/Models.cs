namespace PcGuard.Core;

public record AllowEntry(string Exe, string? Publisher);

public record PcRules(
    bool Locked,
    string Reason,
    int Remaining,
    string? StudentName,
    IReadOnlyList<AllowEntry> Allowlist,
    IReadOnlyList<string> BrowserHosts);

public record ProcInfo(int Pid, string Exe, bool HasVisibleWindow, string? Publisher);

/// <summary>A process with a visible top-level window in the student's session, as reported by the shell.</summary>
public record WindowedProc(int Pid, string Exe);

/// <summary>A top-level browser window reported by the shell. Host is the bare host read from the address bar (never stored or sent).</summary>
public record BrowserWindow(long Hwnd, int Pid, string? Host, bool Readable = true);

/// <summary>What the shell sees in the student's session. Only a report: the service decides.</summary>
public record Snapshot(IReadOnlyList<WindowedProc> Windowed, string? Foreground, IReadOnlyList<BrowserWindow> Browsers);

/// <summary>A process in the active console session as enumerated by the service itself.</summary>
public record RunningProcess(int Pid, string Exe, string? Publisher, bool IsSystemOwned);
