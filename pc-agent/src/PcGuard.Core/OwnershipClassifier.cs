namespace PcGuard.Core;

/// <summary>
/// Pure decision for a process's ownership flags (used by the service's process enumerator).
/// - Image path unreadable (the SYSTEM service, with SeDebugPrivilege enabled, could not even open
///   the process, e.g. a protected process): service-owned, so it is never killed.
/// - Token owner readable: service-owned only if the owner is SYSTEM, LOCAL SERVICE or NETWORK SERVICE.
/// - Token owner unreadable but image readable: service-owned only if the image is a system image
///   (under %SystemRoot%, owned by TrustedInstaller/SYSTEM/Administrators). A program on a
///   user-writable path cannot make itself immune by hiding its token owner.
/// </summary>
public static class OwnershipClassifier
{
    private static readonly HashSet<string> ServiceSids = new(StringComparer.OrdinalIgnoreCase)
    {
        "S-1-5-18", "S-1-5-19", "S-1-5-20",
    };

    public static (bool IsServiceOwned, bool IsSystemImage) Classify(bool pathReadable, string? ownerSid, bool imageIsSystemImage)
    {
        if (!pathReadable) return (true, false);
        if (ownerSid is not null) return (ServiceSids.Contains(ownerSid), imageIsSystemImage);
        return (imageIsSystemImage, imageIsSystemImage);
    }
}
