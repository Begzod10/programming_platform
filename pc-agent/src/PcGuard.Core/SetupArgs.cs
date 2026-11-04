namespace PcGuard.Core;

/// <summary>Command line of Setup-PcGuard.exe. <c>Error</c> is set when the arguments are invalid.</summary>
public sealed record SetupArgs(
    bool Install, bool Uninstall, bool Purge, string? BackendUrl, bool NoPause, bool Help, bool AllowWritablePackage, string? Error)
{
    /// <summary>Extra apps kept running on this PC (<c>--allow-app</c>, repeatable), validated and normalised (see <see cref="ExtraAllowlist"/>).</summary>
    public IReadOnlyList<string> AllowApps { get; init; } = Array.Empty<string>();

    /// <summary><c>--no-recovery-code</c>: install without an offline recovery code and without asking for one.
    /// The code itself is NEVER accepted on the command line (only typed hidden in the interactive install).</summary>
    public bool NoRecoveryCode { get; init; }

    public static SetupArgs Parse(string[] args)
    {
        bool install = false, uninstall = false, purge = false, noPause = false, help = false, allowWritable = false, noRecovery = false;
        string? url = null;
        var apps = new List<string>();

        SetupArgs Err(string e) => new(false, false, false, null, false, false, false, e);

        for (var i = 0; i < args.Length; i++)
        {
            // never echo such an argument: it may carry the secret itself (--recovery-code=...)
            if (args[i].StartsWith("--recovery-code", StringComparison.OrdinalIgnoreCase))
                return Err("The recovery code is never accepted on the command line; run Setup-PcGuard.exe interactively to set it (it is typed hidden).");
            switch (args[i].ToLowerInvariant())
            {
                case "--no-recovery-code": noRecovery = true; break;
                case "--install": install = true; break;
                case "--uninstall": uninstall = true; break;
                case "--purge": purge = true; break;
                case "--allow-writable-package": allowWritable = true; break;
                case "--no-pause": noPause = true; break;
                case "--help": help = true; break;
                case "--backend-url":
                    if (i + 1 >= args.Length || args[i + 1].StartsWith("--", StringComparison.Ordinal))
                        return Err("--backend-url needs a value.");
                    url = args[++i];
                    break;
                case "--allow-app":
                    if (i + 1 >= args.Length || args[i + 1].StartsWith("--", StringComparison.Ordinal))
                        return Err("--allow-app needs a value.");
                    apps.Add(args[++i]);
                    break;
                default:
                    return Err($"Unknown argument: {args[i]}");
            }
        }

        if (install && purge)
            return Err("--install and --purge cannot be combined.");
        if (install && uninstall)
            return Err("--install and --uninstall cannot be combined.");
        if (purge && !uninstall)
            return Err("--purge must be used as: --uninstall --purge.");
        if (url is not null && !install)
            return Err("--backend-url can only be used together with --install.");

        if (apps.Count > 0 && !install)
            return Err("--allow-app can only be used together with --install.");
        if (noRecovery && !install)
            return Err("--no-recovery-code can only be used together with --install.");

        var (allowApps, appError) = ExtraAllowlist.ValidateForInstall(apps);
        if (appError is not null)
            return Err(appError);

        return new SetupArgs(install, uninstall, purge, url, noPause, help, allowWritable, null) { AllowApps = allowApps, NoRecoveryCode = noRecovery };
    }
}
