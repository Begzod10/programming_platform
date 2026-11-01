namespace PcGuard.Core;

/// <summary>Whether the shell may report windows for the current input desktop.</summary>
public static class DesktopPolicy
{
    /// <param name="inputDesktopName">Name of the input desktop, or null when it could not be opened
    /// (secure desktop / UAC / lock screen: keep the current behaviour).</param>
    public static bool ShouldSendSnapshot(string? inputDesktopName)
        => inputDesktopName is null || string.Equals(inputDesktopName, "Default", StringComparison.OrdinalIgnoreCase);
}
