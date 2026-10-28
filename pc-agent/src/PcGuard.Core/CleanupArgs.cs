namespace PcGuard.Core;

/// <summary>Command line of Cleanup-PcGuard.exe. <c>Error</c> is set when the arguments are invalid. There is deliberately no silent mode.</summary>
public sealed record CleanupArgs(bool ListOnly, bool PreviewOnly, bool Purge, bool NoPause, bool Help, string? Error)
{
    public static CleanupArgs Parse(string[] args)
    {
        bool listOnly = false, previewOnly = false, purge = false, noPause = false, help = false;

        static CleanupArgs Err(string e) => new(false, false, false, false, false, e);

        foreach (var arg in args)
        {
            switch (arg.ToLowerInvariant())
            {
                case "--list-only": listOnly = true; break;
                case "--preview-only": previewOnly = true; break;
                case "--purge": purge = true; break;
                case "--no-pause": noPause = true; break;
                case "--help": help = true; break;
                default: return Err($"Unknown argument: {arg}");
            }
        }

        if (listOnly && previewOnly)
            return Err("--list-only and --preview-only cannot be combined.");
        if (purge && (listOnly || previewOnly))
            return Err("--purge cannot be combined with --list-only or --preview-only.");

        return new CleanupArgs(listOnly, previewOnly, purge, noPause, help, null);
    }
}
