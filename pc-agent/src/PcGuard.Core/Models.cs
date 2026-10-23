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
