using System.Diagnostics;
using System.Runtime.Versioning;
using PcGuard.Core;

[assembly: SupportedOSPlatform("windows")]

namespace PcGuard.Setup;

internal static class Program
{
    private const int ExitUsage = 2;
    private const int ExitIntegrity = 3;
    private const int ExitNotElevated = 1;
    private const int ExitCancelled = 130;

    private static volatile bool _cancelRequested;
    private static Process? _child;
    private static AdminTempDir? _temp;
    private static readonly object CleanupLock = new();

    private static int Main(string[] argv)
    {
        var args = SetupArgs.Parse(argv);
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

        var silent = args.NoPause && (args.Install || args.Uninstall);
        var exit = Run(args);
        if (!silent)
        {
            Console.WriteLine();
            Console.Write("Press Enter to close...");
            SafeReadLine();
        }
        return exit;
    }

    private static int Run(SetupArgs args)
    {
        Console.WriteLine("PC Guard setup");
        Console.WriteLine("==============");

        if (!OperatingSystem.IsWindows() || !Elevation.IsElevated())
        {
            Console.Error.WriteLine("This program must run as Administrator. Right-click Setup-PcGuard.exe and choose \"Run as administrator\".");
            return ExitNotElevated;
        }

        // Ctrl+C / Ctrl+Break: first press asks the child to stop (it gets the same signal) and we clean up afterwards;
        // a second press kills the child. Cleanup in the finally blocks always runs.
        Console.CancelKeyPress += OnCancel;
        AppDomain.CurrentDomain.ProcessExit += (_, _) => Cleanup();

        var packageRoot = Path.GetDirectoryName(Environment.ProcessPath) ?? "";

        bool install, purge = false;
        if (args.Install) install = true;
        else if (args.Uninstall) { install = false; purge = args.Purge; }
        else
        {
            var choice = Menu();
            if (choice == 3) return 0;
            install = choice == 1;
        }

        return install ? DoInstall(args, packageRoot) : DoUninstall(args, purge);
    }

    private static int Menu()
    {
        while (true)
        {
            Console.WriteLine();
            Console.WriteLine("  [1] Install or upgrade PC Guard");
            Console.WriteLine("  [2] Uninstall PC Guard");
            Console.WriteLine("  [3] Quit");
            Console.Write("Choose 1, 2 or 3: ");
            var line = SafeReadLine();
            if (line is null) return 3; // no console input: quit
            switch (line.Trim())
            {
                case "1": return 1;
                case "2": return 2;
                case "3": return 3;
            }
        }
    }

    private static int DoInstall(SetupArgs args, string packageRoot)
    {
        var missing = PackageLocator.Check(File.Exists, packageRoot);
        if (missing.Count > 0)
        {
            Console.Error.WriteLine($"The PC Guard files were not found next to Setup-PcGuard.exe ({packageRoot}).");
            Console.Error.WriteLine("Missing: " + string.Join(", ", missing));
            Console.Error.WriteLine("Keep the whole PcGuard folder together (Setup-PcGuard.exe, dist\\, scripts\\) and run it from there.");
            return ExitUsage;
        }

        var silent = args.BackendUrl is not null;
        var urlInput = args.BackendUrl;
        BackendUrlResult result;
        while (true)
        {
            if (urlInput is null)
            {
                Console.Write("Backend URL (for example https://host/api/v1): ");
                urlInput = SafeReadLine();
                if (urlInput is null)
                {
                    Console.Error.WriteLine("No backend URL given.");
                    return ExitUsage;
                }
            }
            result = BackendUrlValidator.Validate(urlInput);
            if (result.Ok) break;
            Console.Error.WriteLine("Invalid backend URL: " + result.Error);
            if (silent) return ExitUsage;
            urlInput = null;
        }
        if (result.Warning is not null) Console.WriteLine("Warning: " + result.Warning);

        var distDir = Path.Combine(packageRoot, "dist");
        Console.WriteLine();
        Console.WriteLine("About to install or upgrade PC Guard:");
        Console.WriteLine("  Backend URL : " + result.Normalized);
        Console.WriteLine("  Files from  : " + distDir);
        Console.WriteLine("  Installs to : Program Files\\PcGuard (service \"PcGuard\", LocalSystem, starts automatically)");
        if (!silent && !Confirm("Type YES to continue: "))
        {
            Console.WriteLine("Cancelled. Nothing was changed.");
            return 0;
        }

        return RunScript(EmbeddedScripts.Install, script =>
            PowerShellCommand.BuildInstall(script, result.Normalized!, distDir, Environment.GetEnvironmentVariable("SystemRoot") ?? @"C:\Windows"));
    }

    private static int DoUninstall(SetupArgs args, bool purge)
    {
        var scripted = args.Uninstall;
        if (!scripted)
        {
            purge = AskYesNo("Also delete the PC Guard data (machine key, rules, usage queue) in ProgramData? [y/N]: ");
            Console.WriteLine();
            Console.WriteLine("About to uninstall PC Guard (service and install folder)" + (purge ? " and PURGE its data." : "; data is kept."));
            if (!Confirm("Type YES to continue: "))
            {
                Console.WriteLine("Cancelled. Nothing was changed.");
                return 0;
            }
        }

        var p = purge;
        return RunScript(EmbeddedScripts.Uninstall, script =>
            PowerShellCommand.BuildUninstall(script, p, Environment.GetEnvironmentVariable("SystemRoot") ?? @"C:\Windows"));
    }

    /// <summary>Extracts the embedded script into an admin-only folder, runs it, always deletes the folder.</summary>
    private static int RunScript(string scriptName, Func<string, PowerShellCommand> build)
    {
        try
        {
            lock (CleanupLock) { _temp = AdminTempDir.Create(); }
            var scriptPath = EmbeddedScripts.Extract(scriptName, _temp.Path);
            var cmd = build(scriptPath);

            if (!File.Exists(cmd.Executable))
            {
                Console.Error.WriteLine("Windows PowerShell was not found at " + cmd.Executable);
                return ExitIntegrity;
            }

            var psi = new ProcessStartInfo(cmd.Executable)
            {
                UseShellExecute = false,          // child inherits this console: output streams live
                WorkingDirectory = _temp.Path,    // never the (possibly user-writable) current directory
            };
            foreach (var a in cmd.Arguments) psi.ArgumentList.Add(a); // array, never a concatenated string

            Console.WriteLine();
            Console.WriteLine("Running " + scriptName + " ...");
            Console.WriteLine();

            int code;
            using (var proc = Process.Start(psi) ?? throw new InvalidOperationException("Could not start PowerShell."))
            {
                _child = proc;
                proc.WaitForExit();
                code = proc.ExitCode;
                _child = null;
            }

            Console.WriteLine();
            if (_cancelRequested) Console.WriteLine("Cancelled with Ctrl+C. The operation may be incomplete; run it again or check the service.");
            Console.WriteLine(code == 0
                ? $"{scriptName} finished successfully (exit code 0)."
                : $"{scriptName} FAILED with exit code {code}. Read the messages above.");
            return code != 0 ? code : (_cancelRequested ? ExitCancelled : 0);
        }
        catch (Exception e) when (e is IOException or InvalidDataException or UnauthorizedAccessException
                                      or InvalidOperationException or System.ComponentModel.Win32Exception)
        {
            Console.Error.WriteLine("Setup could not run the script: " + e.Message);
            return ExitIntegrity;
        }
        finally
        {
            Cleanup();
        }
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
        e.Cancel = true; // keep running so that the finally blocks and cleanup execute
        if (!_cancelRequested)
        {
            _cancelRequested = true;
            Console.WriteLine();
            Console.WriteLine("Ctrl+C received: waiting for the running script to stop. Press Ctrl+C again to force it.");
            return;
        }
        try { _child?.Kill(entireProcessTree: true); } catch (Exception) { /* already gone */ }
    }

    private static bool Confirm(string prompt)
    {
        Console.Write(prompt);
        return string.Equals(SafeReadLine()?.Trim(), "YES", StringComparison.Ordinal);
    }

    private static bool AskYesNo(string prompt)
    {
        Console.Write(prompt);
        var a = SafeReadLine()?.Trim();
        return string.Equals(a, "y", StringComparison.OrdinalIgnoreCase) || string.Equals(a, "yes", StringComparison.OrdinalIgnoreCase);
    }

    private static string? SafeReadLine()
    {
        try { return Console.ReadLine(); }
        catch (IOException) { return null; }
    }

    private static void PrintUsage()
    {
        Console.WriteLine("Usage: Setup-PcGuard.exe [--install --backend-url <https://host/api/v1>] [--uninstall [--purge]] [--no-pause] [--help]");
        Console.WriteLine("  (no arguments)   interactive menu");
        Console.WriteLine("  --install        install or upgrade; with --backend-url it runs without questions");
        Console.WriteLine("  --uninstall      uninstall without questions (add --purge to also delete ProgramData\\PcGuard)");
        Console.WriteLine("  --no-pause       with --install/--uninstall: do not wait for Enter at the end");
    }
}
