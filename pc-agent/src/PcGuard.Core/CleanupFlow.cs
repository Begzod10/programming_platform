namespace PcGuard.Core;

/// <summary>Decisions of the Cleanup-PcGuard.exe flow. Exit code 2 of the list/preview step (read-only refusals shown as FAILED) must not block the removal.</summary>
public static class CleanupFlow
{
    public const string PreviewPartialWarning =
        "The preview reported steps that would FAIL or be SKIPPED (shown above). The real removal will report the same; you can still continue.";

    /// <summary>0 and 2 continue; 1 (error / not elevated) and anything else stop.</summary>
    public static bool ShouldContinueAfterList(int code) => code is 0 or 2;

    public static bool ShouldContinueAfterPreview(int code) => code is 0 or 2;
}
