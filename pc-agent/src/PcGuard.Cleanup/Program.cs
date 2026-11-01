using System.Diagnostics;
using System.Runtime.Versioning;
using PcGuard.Core;
using PcGuard.Setup; // linked shared sources: AdminTempDir, EmbeddedScripts, Elevation

[assembly: SupportedOSPlatform("windows")]

namespace PcGuard.Cleanup;

internal static class Program
{
    private const string ScriptName = "cleanup.ps1";
    private const string TempPrefix = "PcGuard-cleanup-"; // NOT PcGuard-setup-*: cleanup.ps1 deletes those folders, even while running from one
    private const int ExitUsage = 64; // distinct from 2 = partial failure of the script
    private const int ExitIntegrity = 3;
    private const int ExitNotElevated = 1;
    private const int ExitCancelled = 130;

    // Real Windows folder from the OS API, never from an environment variable.
    private static readonly string WindowsDir = Environment.GetFolderPath(Environment.SpecialFolder.Windows);

    private static volatile bool _cancelRequested;
    private static Process? _child;
    private static AdminTempDir? _temp;
    private static readonly object CleanupLock = new();

    private static int Main(string[] argv)
    {
        var args = CleanupArgs.Parse(argv);
        if (args.Error is not null)
        {
            Console.Error.WriteLine(args.Error);
            PrintUsage();
            return ExitUsage;
        }
        if (args.Help)
        {
            PrintUsage();
            return 0;
        }

        var exit = Run(args);
        if (!args.NoPause)
        {
            Console.WriteLine();
            Console.Write("Press Enter to close...");
            SafeReadLine();
        }
        return exit;
    }

    private static int Run(CleanupArgs args)
    {
        Console.WriteLine("PC Guard cleanup");
        Console.WriteLine("================");

        if (!OperatingSystem.IsWindows() || !Elevation.IsElevated())
        {
            Console.Error.WriteLine("This program must run as Administrator. Right-click Cleanup-PcGuard.exe and choose \"Run as administrator\".");
            return ExitNotElevated;
        }

        // Ctrl+C is only intercepted while a child runs (see OnCancel).
        Console.CancelKeyPress += OnCancel;
        AppDomain.CurrentDomain.ProcessExit += (_, _) => Cleanup();

        try
        {
            // Step 1: extract (admin-only folder, hash check). The folder lives until the end and is removed in finally.
            lock (CleanupLock) { _temp = AdminTempDir.Create(TempPrefix, "Cleanup"); }
            var scriptPath = EmbeddedScripts.Extract(ScriptName, _temp.Path);

            // Step 2: list busy scripts (closes nothing).
            Console.WriteLine();
            Console.WriteLine("Step 1 of 3: busy script processes (nothing is closed)");
            var code = RunChild(CleanupCommand.BuildList(scriptPath, WindowsDir), "List of busy scripts");
            if (!CleanupFlow.ShouldContinueAfterList(code) || args.ListOnly) return code;

            // Step 3: preview (changes nothing).
            Console.WriteLine();
            Console.WriteLine("Step 2 of 3: preview of the PC Guard removal (nothing is changed)");
            code = RunChild(CleanupCommand.BuildPreview(scriptPath, WindowsDir), "Preview");
            if (!CleanupFlow.ShouldContinueAfterPreview(code)) return code;
            if (code == 2)
            {
                Console.WriteLine();
                Console.WriteLine(CleanupFlow.PreviewPartialWarning);
            }
            if (args.PreviewOnly) return code;

            // Step 4: confirm.
            Console.WriteLine();
            Console.Write("Type YES to remove PC Guard (anything else exits): ");
            if (!CleanupConfirm.IsYes(SafeReadLine()))
            {
                Console.WriteLine();
                Console.WriteLine("Nothing was changed.");
                return 0;
            }

            // Step 5: purge question (default No).
            var purge = args.Purge;
            if (!purge)
            {
                Console.Write("Also delete PC Guard's data (machine key, rules)? [y/N] ");
                var a = SafeReadLine()?.Trim();
                purge = string.Equals(a, "y", StringComparison.OrdinalIgnoreCase) || string.Equals(a, "yes", StringComparison.OrdinalIgnoreCase);
            }
            else
            {
                Console.WriteLine("Also delete PC Guard's data (machine key, rules): yes (--purge).");
            }

            // Step 6: real removal. -Force only skips the script's own YES prompt.
            Console.WriteLine();
            Console.WriteLine("Step 3 of 3: removing PC Guard" + (purge ? " and its data" : " (data is kept)"));
            code = RunChild(CleanupCommand.BuildRemove(scriptPath, purge, WindowsDir), "Removal");
            return code;
        }
        catch (Exception e) when (e is IOException or InvalidDataException or UnauthorizedAccessException
                                      or InvalidOperationException or System.ComponentModel.Win32Exception)
        {
            Console.Error.WriteLine("Cleanup could not run the script: " + e.Message);
            return ExitIntegrity;
        }
        catch (Exception e)
        {
            Console.Error.WriteLine("Unexpected error: " + e.GetType().Name + ": " + e.Message);
            return ExitNotElevated; // exit code 1 = error
        }
        finally
        {
            Cleanup();
        }
    }

    /// <summary>Runs one PowerShell command with the console shared; returns its exit code (Ctrl+C aware).</summary>
    private static int RunChild(PowerShellCommand cmd, string label)
    {
        if (_temp is null) throw new InvalidOperationException("No working folder.");
        if (!File.Exists(cmd.Executable))
        {
            Console.Error.WriteLine("Windows PowerShell was not found at " + cmd.Executable);
            return ExitIntegrity;
        }

        var psi = new ProcessStartInfo(cmd.Executable)
        {
            UseShellExecute = false,         // child inherits this console: output streams live
            WorkingDirectory = _temp.Path,   // never the (possibly user-writable) current directory
        };
        foreach (var a in cmd.Arguments) psi.ArgumentList.Add(a); // array, never a concatenated string

        Console.WriteLine();
        int code;
        _cancelRequested = false;
        using (var proc = Process.Start(psi) ?? throw new InvalidOperationException("Could not start PowerShell."))
        {
            _child = proc;
            proc.WaitForExit();
            code = proc.ExitCode;
            _child = null;
        }

        Console.WriteLine();
        var cancelled = _cancelRequested;
        _cancelRequested = false;
        if (cancelled) Console.WriteLine("Cancelled with Ctrl+C. This step may be incomplete; run this program again to check.");
        Console.WriteLine($"{label} {CleanupExitText.Describe(code)}");
        return code != 0 ? code : (cancelled ? ExitCancelled : 0);
    }

    private static void Cleanup()
    {
        lock (CleanupLock)
        {
            var t = _temp;
            if (t is null) return;
            if (t.TryDelete()) _temp = null;
            else Console.Error.WriteLine($"Warning: could not delete the temporary folder {t.Path}. Delete it manually.");
        }
    }

    private static void OnCancel(object? sender, ConsoleCancelEventArgs e)
    {
        var child = _child;
        if (child is null) return; // no child running: Ctrl+C ends the program normally (ProcessExit cleans up)
        e.Cancel = true;           // keep running so that the finally block and cleanup execute
        if (!_cancelRequested)
        {
            _cancelRequested = true;
            Console.WriteLine();
            Console.WriteLine("Ctrl+C received: waiting for the running step to stop. Press Ctrl+C again to force it.");
            return;
        }
        try { child.Kill(entireProcessTree: true); } catch (Exception) { /* already gone */ }
    }

    private static string? SafeReadLine()
    {
        try { return Console.ReadLine(); }
        catch (IOException) { return null; }
    }

    private static void PrintUsage()
    {
        Console.WriteLine("Usage: Cleanup-PcGuard.exe [--list-only | --preview-only] [--purge] [--no-pause] [--help]");
        Console.WriteLine("  (no arguments)   list busy scripts, preview the removal, ask YES, ask about data, remove PC Guard");
        Console.WriteLine("  --list-only      only list busy script processes (closes nothing), then exit");
        Console.WriteLine("  --preview-only   list, then preview what the removal would do (changes nothing), then exit");
        Console.WriteLine("  --purge          answer yes to \"delete PC Guard's data\" (you are still asked to type YES)");
        Console.WriteLine("  --no-pause       do not wait for Enter at the end");
        Console.WriteLine("  There is no silent mode: removal always asks you to type YES.");
        Console.WriteLine("  Busy scripts are never closed; PC Guard's own service and shell are ended as part of the removal.");
        Console.WriteLine("  The preview does not include the data purge (it removes only %ProgramData%\\PcGuard, after the same checks).");
        Console.WriteLine("  Exit codes: 0 ok, 1 error or not Administrator, 2 partial failure, 3 integrity/startup problem, 64 bad command line, 130 cancelled.");
    }
}
