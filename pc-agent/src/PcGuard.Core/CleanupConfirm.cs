namespace PcGuard.Core;

public static class CleanupConfirm
{
    /// <summary>True only for the word YES (any case) after trimming. Null, empty, "Y" or "yes please" are all No.</summary>
    public static bool IsYes(string? input) =>
        input is not null && string.Equals(input.Trim(), "YES", StringComparison.OrdinalIgnoreCase);
}
