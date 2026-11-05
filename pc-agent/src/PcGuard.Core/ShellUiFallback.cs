using System.Globalization;
using System.Text;

namespace PcGuard.Core;

/// <summary>What the shell could show after startup.</summary>
public enum ShellUiMode
{
    /// <summary>Sign-in window, overlay and banner were built.</summary>
    Full,
    /// <summary>Building them threw (for example Windows text input, TSF, failing inside a TextBox
    /// constructor); a minimal lock window without any text input is shown instead.</summary>
    Fallback,
    /// <summary>Not even the fallback window could be shown; the shell runs without a window.</summary>
    NoWindow,
}

/// <summary>
/// Defence in depth for the shell UI (real-PC bug, 2026-11-05: an OutOfMemoryException from
/// TF_CreateInputProcessorProfiles inside the TextBox constructor ended the shell before it ever
/// connected, so the service saw no shell at all). Whatever the UI does, the shell still starts its
/// pipe client, so the service sees it alive and keeps enforcing; a broken UI never loosens anything.
/// Covered: exceptions thrown while CONSTRUCTING or SHOWING the main windows during startup. Not
/// covered: crashes that cannot be caught (stack overflow, access violation, fail-fast inside native
/// code), failures in the App constructor before OnStartup, and failures of dialogs opened later
/// (those reach the dispatcher handler, are logged, and the shell keeps running).
/// </summary>
public static class ShellUiFallback
{
    public static ShellUiMode Mode(bool mainWindowsBuilt, bool fallbackShown)
        => mainWindowsBuilt ? ShellUiMode.Full : fallbackShown ? ShellUiMode.Fallback : ShellUiMode.NoWindow;

    /// <summary>The fallback lock window hides only while the connected service reports a signed-in
    /// student or maintenance mode (as the sign-in window does); otherwise it covers the screen.</summary>
    public static bool FallbackVisible(bool connected, bool signedIn, bool maintenance)
        => !(connected && (signedIn || maintenance));
}

/// <summary>
/// Security descriptor of the shell's token OBJECT (who may open the token handle), passed to
/// DuplicateTokenEx by the service. It does not change anything INSIDE the token (user, groups,
/// privileges, integrity level, default DACL, session stay exactly as WTSQueryUserToken returned them).
/// Why it exists: the 2026-11-05 trail logged "Administrators enabled: unknown", i.e. the shell could
/// not open its own token. Either the restricted default DACL (removed) reached the process token, or a
/// token duplicated by the SYSTEM service without a descriptor gets one derived from the SERVICE's
/// default DACL (typically SYSTEM full, Administrators read; nothing for a standard user or a
/// UAC-filtered administrator). The second is inferred, not verified on Windows; this descriptor makes
/// the outcome independent of it. It grants what an ordinary logon token grants: SYSTEM,
/// Administrators and the user. No deny entries, no OWNER RIGHTS entry.
/// </summary>
public static class ShellTokenSecurity
{
    public static string TokenObjectSddl(string userSid)
    {
        if (!IsPlainSid(userSid)) throw new ArgumentException("A plain S-1-... SID is required", nameof(userSid));
        return $"D:(A;;GA;;;SY)(A;;GA;;;BA)(A;;GA;;;{userSid})";
    }

    private static bool IsPlainSid(string? sid)
        => sid is { Length: <= 200 } && System.Text.RegularExpressions.Regex.IsMatch(sid, @"\AS-1-[0-9]+(-[0-9]+)+\z");
}

public static partial class ShellDiagnostics
{
    /// <summary>At most this many inner exceptions are written per report.</summary>
    public const int MaxInnerExceptions = 5;

    public static string UiModeLine(ShellUiMode mode) => mode switch
    {
        ShellUiMode.Full => Step("windows created"),
        ShellUiMode.Fallback => Step("main windows failed: showing the fallback lock window (no text input, nobody can sign in until the shell is restarted)"),
        _ => Step("no window could be created: running without a window; the pipe client still reports to the service"),
    };

    /// <summary>"yes"/"no" when the shell could read its own token, else "unknown" with the Win32 code.</summary>
    public static string OwnTokenText(bool? administratorsEnabled, int win32) => administratorsEnabled switch
    {
        true => "yes",
        false => "no",
        null => string.Create(CultureInfo.InvariantCulture, $"unknown (own token not readable, Win32 {win32})"),
    };

    /// <summary>
    /// Full exception report for shell.log: type, HRESULT and stack trace of the exception and of up to
    /// <see cref="MaxInnerExceptions"/> inner exceptions. PRIVACY: never the message (it can hold user
    /// input, paths or URLs).
    /// </summary>
    public static string ExceptionReport(Exception e)
    {
        var sb = new StringBuilder();
        Append(sb, e);
        var inner = e.InnerException;
        for (var i = 0; inner is not null && i < MaxInnerExceptions; i++, inner = inner.InnerException)
        {
            sb.Append(Environment.NewLine).Append("--- inner: ");
            Append(sb, inner);
        }
        return sb.ToString();
    }

    private static void Append(StringBuilder sb, Exception e)
    {
        sb.Append(e.GetType().FullName).Append(string.Create(CultureInfo.InvariantCulture, $" (HRESULT 0x{e.HResult:X8})"));
        if (!string.IsNullOrEmpty(e.StackTrace)) sb.Append(Environment.NewLine).Append(e.StackTrace);
    }
}
