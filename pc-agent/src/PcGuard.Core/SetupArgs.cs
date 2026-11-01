namespace PcGuard.Core;

/// <summary>Command line of Setup-PcGuard.exe. <c>Error</c> is set when the arguments are invalid.</summary>
public sealed record SetupArgs(
    bool Install, bool Uninstall, bool Purge, string? BackendUrl, bool NoPause, bool Help, bool AllowWritablePackage, string? Error)
{
    public static SetupArgs Parse(string[] args)
    {
        bool install = false, uninstall = false, purge = false, noPause = false, help = false, allowWritable = false;
        string? url = null;

        SetupArgs Err(string e) => new(false, false, false, null, false, false, false, e);

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i].ToLowerInvariant())
            {
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

        return new SetupArgs(install, uninstall, purge, url, noPause, help, allowWritable, null);
    }
}
