using System.IO;
using System.Text;

namespace PcGuard.Shell;

/// <summary>
/// Minimal local log at %LocalAppData%\PcGuard\shell.log. PRIVACY: callers pass only constant text
/// and exception TYPES/stack traces; never passwords, URLs, window titles or exception messages.
/// </summary>
internal static class ShellLog
{
    private const long MaxBytes = 512 * 1024;
    private static readonly object Gate = new();
    private static readonly string Path_ = System.IO.Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PcGuard", "shell.log");

    public static void Info(string message) => Write("INFO", message);

    public static void Error(string where, Exception e)
        => Write("ERROR", $"{where}: {e.GetType().FullName}{Environment.NewLine}{e.StackTrace}");

    private static void Write(string level, string text)
    {
        try
        {
            lock (Gate)
            {
                Directory.CreateDirectory(System.IO.Path.GetDirectoryName(Path_)!);
                var fi = new FileInfo(Path_);
                if (fi.Exists && fi.Length > MaxBytes) fi.Delete(); // crude rotation
                File.AppendAllText(Path_, $"{DateTimeOffset.Now:O} {level} {text}{Environment.NewLine}", Encoding.UTF8);
            }
        }
        catch (Exception)
        {
            // logging must never take the shell down
        }
    }
}
