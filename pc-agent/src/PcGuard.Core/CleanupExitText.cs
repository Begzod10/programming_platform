namespace PcGuard.Core;

public static class CleanupExitText
{
    /// <summary>Plain-language meaning of a cleanup.ps1 exit code (0 ok, 1 error / not elevated, 2 partial failure).</summary>
    public static string Describe(int code) => code switch
    {
        0 => "finished successfully (exit code 0).",
        1 => "FAILED with exit code 1: an error occurred or the script was not run as Administrator. Nothing may have been changed; read the messages above.",
        2 => "finished with exit code 2: at least one step FAILED (partial failure). Read the FAILED lines above and follow the hints; you can run this program again.",
        _ => $"FAILED with unexpected exit code {code}. Read the messages above.",
    };
}
