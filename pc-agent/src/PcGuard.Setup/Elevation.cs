using System.Security.Principal;

namespace PcGuard.Setup;

internal static class Elevation
{
    /// <summary>True when the process token is a member of the Administrators group with the group enabled (elevated).</summary>
    public static bool IsElevated()
    {
        using var identity = WindowsIdentity.GetCurrent();
        return new WindowsPrincipal(identity).IsInRole(WindowsBuiltInRole.Administrator);
    }
}
