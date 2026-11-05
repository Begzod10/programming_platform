using System.Diagnostics;
using System.Runtime.Versioning;
using System.Security.AccessControl;
using System.Security.Cryptography;
using System.Security.Principal;
using PcGuard.Core;

[assembly: SupportedOSPlatform("windows")]

namespace PcGuard.Setup;

internal static class Program
{
    private const int ExitUsage = 2;
    private const int ExitIntegrity = 3;
    private const int ExitUnsafePackage = 4;
    private const int ExitNotElevated = 1;
    private const int ExitCancelled = 130;
    private const int ExitDefaultCode = 64;

    // Real Windows folder from the OS API, never from an environment variable.
    private static readonly string WindowsDir = Environment.GetFolderPath(Environment.SpecialFolder.Windows);

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

        if (!CheckPackageAcl(packageRoot, args.AllowWritablePackage, out var packageVerified))
            return ExitUnsafePackage;
        // The default recovery code file is read only from a package folder that really passed the check.
        var defaultCodeAllowed = packageVerified && !args.AllowWritablePackage;
        var defaultCodePath = Path.Combine(packageRoot, DefaultRecoveryCode.FileName);

        var silent = args.Install && args.BackendUrl is not null;
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

        // Extra apps kept running on this PC (Allowlist:ExtraApps). Asked only in the interactive flow and
        // only when no --allow-app was given. Empty = none given: install.ps1 then keeps the extras of an
        // existing install (upgrade).
        var extraApps = args.AllowApps;
        if (!silent && extraApps.Count == 0)
        {
            while (true)
            {
                Console.Write("Extra apps to keep running on this PC (comma separated exe names, e.g. anydesk.exe; empty for none): ");
                var line = SafeReadLine();
                if (line is null) break; // no console input: none
                var (names, error) = ExtraAllowlist.ValidateForInstall(ExtraAllowlist.SplitList(line));
                if (error is null) { extraApps = names; break; }
                Console.Error.WriteLine(error);
            }
        }

        // Offline recovery code (stops and disables PC Guard on this PC from the lock screen). Typed hidden,
        // twice; only its PBKDF2 hash leaves this process, and only through a file in Setup's admin-only
        // temp folder (-RecoveryCodeHashFile). Neither the code nor the hash is ever on a command line.
        // An optional default-recovery-code.txt in the package folder can supply the code (never hardcoded,
        // never on a command line); it goes through the same hash and the same admin-only hash file.
        string? recoveryHash = null;
        var recoverySource = RecoveryCodeSource.None;
        if (args.NoRecoveryCode)
        {
            // explicitly none: nothing asked, nothing passed (an upgrade keeps a code set before)
            if (DefaultCodeEntryExists(defaultCodePath))
                Console.WriteLine($"Note: {DefaultRecoveryCode.FileName} is present but not used (--no-recovery-code).");
        }
        else if (args.DefaultRecoveryCode)
        {
            using var def = LoadDefaultCode(defaultCodePath, defaultCodeAllowed);
            if (def.Status != DefaultCodeStatus.Loaded || def.Code is null)
            {
                Console.Error.WriteLine(def.Message ?? $"--default-recovery-code: {DefaultRecoveryCode.FileName} was not found next to Setup-PcGuard.exe ({packageRoot}).");
                Console.Error.WriteLine("Installation aborted. Nothing was changed.");
                return ExitDefaultCode;
            }
            Console.WriteLine($"Using the recovery code from {DefaultRecoveryCode.FileName} (--default-recovery-code).");
            recoveryHash = RecoveryCode.Hash(def.Code.AsSpan());
            recoverySource = RecoveryCodeSource.Default;
        }
        else if (silent)
        {
            Console.WriteLine("Warning: no recovery code is set by a silent install (there is no offline way out of a stuck lock screen). Run Setup interactively to set one, or pass --no-recovery-code to silence this warning.");
            if (DefaultCodeEntryExists(defaultCodePath))
                Console.WriteLine($"Note: {DefaultRecoveryCode.FileName} is present but not used; pass --default-recovery-code to use it.");
        }
        else
        {
            using var def = LoadDefaultCode(defaultCodePath, defaultCodeAllowed);
            RecoveryPromptResult prompt;
            if (def.Status == DefaultCodeStatus.Loaded && def.Code is not null)
            {
                prompt = RecoveryCodePrompt.RunWithDefault(def.Code, ReadHidden, e => Console.Error.WriteLine(e));
            }
            else
            {
                if (def.Message is not null)
                {
                    Console.Error.WriteLine(def.Message);
                    Console.Error.WriteLine("The default recovery code file is not used; type a code instead.");
                }
                prompt = RecoveryCodePrompt.Run(ReadHidden, e => Console.Error.WriteLine(e), confirmNoCode: AskYesNoOrNull);
            }
            if (prompt.Outcome == RecoveryPromptOutcome.Aborted) return ExitUsage;
            recoveryHash = prompt.Hash;
            recoverySource = prompt.Source;
        }

        var distDir = Path.Combine(packageRoot, "dist");
        Console.WriteLine();
        Console.WriteLine("About to install or upgrade PC Guard:");
        Console.WriteLine("  Backend URL : " + result.Normalized);
        Console.WriteLine("  Files from  : " + distDir);
        Console.WriteLine("  Installs to : Program Files\\PcGuard (service \"PcGuard\", LocalSystem, starts automatically)");
        Console.WriteLine("  Extra apps  : " + (extraApps.Count > 0
            ? string.Join(", ", extraApps) + " (kept running on this PC even while it is locked)"
            : "none given (an upgrade keeps the extra apps configured before)"));
        Console.WriteLine("  Recovery code: " + RecoveryCodePrompt.SummaryText(recoveryHash is null ? RecoveryCodeSource.None : recoverySource));
        if (recoveryHash is null)
        {
            Console.WriteLine("                 (an upgrade keeps an unused recovery code set before; a used one, or one of a");
            Console.WriteLine("                 PC Guard that was released or disabled, is never kept)");
        }
        if (!silent && !Confirm("Type YES to continue: "))
        {
            Console.WriteLine("Cancelled. Nothing was changed.");
            return 0;
        }

        return RunScript(EmbeddedScripts.Install, (tempDir, script) =>
        {
            string? hashFile = null;
            if (recoveryHash is not null)
            {
                hashFile = Path.Combine(tempDir, RecoveryCode.TransferFileName);
                WriteAdminOnlyFile(hashFile, RecoveryCode.ToTransferBytes(recoveryHash));
            }
            return PowerShellCommand.BuildInstall(script, result.Normalized!, distDir, WindowsDir, extraApps, hashFile);
        });
    }

    /// <summary>True when something (file, folder or link) named default-recovery-code.txt is in the package folder. Never reads it.</summary>
    private static bool DefaultCodeEntryExists(string path)
    {
        try
        {
            File.GetAttributes(path);
            return true;
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException)
        {
            return false;
        }
    }

    /// <summary>
    /// Windows side of <see cref="DefaultRecoveryCode.Load"/>: link/folder/size from the entry itself (a link
    /// is never opened), the file's own ACL, then at most MaxFileBytes + 1 bytes through an unbuffered
    /// stream (no FileStream buffer keeps a copy). The bytes are zeroed in Core.
    /// </summary>
    private static DefaultCodeLoad LoadDefaultCode(string path, bool allowed)
    {
        DefaultCodeFile? entry;
        try
        {
            var attrs = File.GetAttributes(path); // does not follow a link
            var isDir = (attrs & FileAttributes.Directory) != 0;
            var isLink = (attrs & FileAttributes.ReparsePoint) != 0;
            entry = new DefaultCodeFile(isDir, isLink, isDir || isLink ? 0 : new FileInfo(path).Length);
        }
        catch (Exception e) when (e is FileNotFoundException or DirectoryNotFoundException)
        {
            entry = null;
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException)
        {
            entry = new DefaultCodeFile(false, false, 0); // exists but cannot be inspected: Load reports the read error
        }

        return DefaultRecoveryCode.Load(allowed, entry, () => PackageAcl.ReadFile(path), max =>
        {
            using var fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read, bufferSize: 0, FileOptions.None);
            if (fs.Length > DefaultRecoveryCode.MaxFileBytes) return new byte[max]; // grew since the check: report as too large
            var buf = new byte[max];
            var total = 0;
            int n;
            while (total < max && (n = fs.Read(buf, total, max - total)) > 0) total += n;
            if (total == max) return buf;
            var exact = buf.AsSpan(0, total).ToArray();
            CryptographicOperations.ZeroMemory(buf);
            return exact;
        });
    }

    /// <summary>Refuses a package folder that standard users can modify (they could swap files that end up in a SYSTEM service).</summary>
    /// <param name="verified">True only when the permissions were read and found safe (not when --allow-writable-package let an unsafe or unreadable folder pass).</param>
    private static bool CheckPackageAcl(string packageRoot, bool allowWritable, out bool verified)
    {
        verified = false;
        Console.WriteLine("Package folder: " + packageRoot);
        Console.WriteLine("Install refuses a package folder that standard users can modify (see the README: copy it to C:\\PcGuardSetup and lock it with icacls).");

        PackageVerdict verdict;
        try
        {
            verdict = PackageAclPolicy.Evaluate(PackageAcl.Read(packageRoot));
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or InvalidOperationException)
        {
            Console.Error.WriteLine("Cannot read the permissions of the package folder: " + e.Message);
            if (!allowWritable) return false;
            Console.Error.WriteLine("WARNING: continuing because --allow-writable-package was given.");
            return true;
        }

        if (verdict.IsSafe)
        {
            verified = true;
            return true;
        }

        foreach (var line in PackageAclPolicy.DescribeGrants(verdict.Grants))
            Console.Error.WriteLine("  " + line);
        foreach (var p in verdict.ReparsePaths.Take(5))
            Console.Error.WriteLine("  Link or junction inside the package (could point anywhere): " + p);
        if (verdict.ReparsePaths.Count > 5)
            Console.Error.WriteLine($"  and {verdict.ReparsePaths.Count - 5} more.");
        if (verdict.TooLarge)
            Console.Error.WriteLine($"  The dist folder has more than {PackageAclPolicy.MaxEntries} files and folders; it is too large to check and is treated as unsafe.");

        if (!allowWritable)
        {
            Console.Error.WriteLine("Refusing to install: a standard user could replace files before they are installed as a SYSTEM service.");
            foreach (var line in PackageAclPolicy.RemedyLines)
                Console.Error.WriteLine("  " + line);
            return false;
        }
        Console.Error.WriteLine("WARNING: --allow-writable-package given. Continuing although the package folder is not safe!");
        return true;
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
        return RunScript(EmbeddedScripts.Uninstall, (_, script) =>
            PowerShellCommand.BuildUninstall(script, p, WindowsDir));
    }

    /// <summary>
    /// Writes a new file (it must not exist) that only SYSTEM and Administrators can access: owner
    /// Administrators, protected DACL with SYSTEM and Administrators full control, set when the file is
    /// created. Used for the recovery code hash handed to install.ps1.
    /// </summary>
    private static void WriteAdminOnlyFile(string path, byte[] content)
    {
        var sec = new FileSecurity();
        var admins = new SecurityIdentifier(WellKnownSidType.BuiltinAdministratorsSid, null);
        sec.SetOwner(admins);
        sec.SetAccessRuleProtection(isProtected: true, preserveInheritance: false);
        sec.AddAccessRule(new FileSystemAccessRule(new SecurityIdentifier(WellKnownSidType.LocalSystemSid, null), FileSystemRights.FullControl, AccessControlType.Allow));
        sec.AddAccessRule(new FileSystemAccessRule(admins, FileSystemRights.FullControl, AccessControlType.Allow));
        try
        {
            using var fs = new FileInfo(path).Create(FileMode.CreateNew, FileSystemRights.Write | FileSystemRights.ReadData,
                FileShare.None, 4096, FileOptions.WriteThrough, sec);
            fs.Write(content);
        }
        finally
        {
            CryptographicOperations.ZeroMemory(content);
        }
    }

    /// <summary>Overwrites a small file with zeros and deletes it (best effort; the temp folder is deleted afterwards anyway).</summary>
    private static void WipeFile(string path)
    {
        try
        {
            var fi = new FileInfo(path);
            if (!fi.Exists) return;
            if ((fi.Attributes & FileAttributes.ReparsePoint) == 0 && fi.Length <= 4096)
            {
                using var fs = new FileStream(path, FileMode.Open, FileAccess.Write, FileShare.None);
                fs.Write(new byte[fs.Length]);
                fs.Flush(flushToDisk: true);
            }
            fi.Delete();
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException)
        {
            // the folder delete in Cleanup removes it
        }
    }

    /// <summary>Extracts the embedded script into an admin-only folder, runs it, always deletes the folder.</summary>
    /// <param name="build">Gets the admin-only temp folder and the extracted script path.</param>
    private static int RunScript(string scriptName, Func<string, string, PowerShellCommand> build)
    {
        try
        {
            lock (CleanupLock) { _temp = AdminTempDir.Create(); }
            var scriptPath = EmbeddedScripts.Extract(scriptName, _temp.Path);
            var cmd = build(_temp.Path, scriptPath);

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
            _cancelRequested = false;
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
            var cancelled = _cancelRequested;
            _cancelRequested = false;
            return code != 0 ? code : (cancelled ? ExitCancelled : 0);
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
            WipeFile(Path.Combine(t.Path, RecoveryCode.TransferFileName)); // install.ps1 normally wiped it already
            if (t.TryDelete()) _temp = null;
            else Console.Error.WriteLine($"Warning: could not delete the temporary folder {t.Path}. Delete it manually.");
        }
    }

    private static void OnCancel(object? sender, ConsoleCancelEventArgs e)
    {
        var child = _child;
        if (child is null) return; // no script running: let Ctrl+C end the program normally (ProcessExit cleans up)
        e.Cancel = true; // keep running so that the finally blocks and cleanup execute
        if (!_cancelRequested)
        {
            _cancelRequested = true;
            Console.WriteLine();
            Console.WriteLine("Ctrl+C received: waiting for the running script to stop. Press Ctrl+C again to force it.");
            return;
        }
        try { child.Kill(entireProcessTree: true); } catch (Exception) { /* already gone */ }
    }

    private static bool Confirm(string prompt)
    {
        Console.Write(prompt);
        return string.Equals(SafeReadLine()?.Trim(), "YES", StringComparison.Ordinal);
    }

    /// <summary>True for y/yes, false for anything else, null when there is no console input.</summary>
    private static bool? AskYesNoOrNull(string prompt)
    {
        Console.Write(prompt);
        var a = SafeReadLine();
        if (a is null) return null;
        a = a.Trim();
        return string.Equals(a, "y", StringComparison.OrdinalIgnoreCase) || string.Equals(a, "yes", StringComparison.OrdinalIgnoreCase);
    }

    private static bool AskYesNo(string prompt)
    {
        Console.Write(prompt);
        var a = SafeReadLine()?.Trim();
        return string.Equals(a, "y", StringComparison.OrdinalIgnoreCase) || string.Equals(a, "yes", StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>
    /// Reads one line without echo (Console.ReadKey with intercept), Backspace supported. Returns the
    /// characters as an exact-length char[] (the caller zeroes it) or null when there is no console.
    /// At most MaxLength + 1 characters are kept, so a longer entry is reported as too long.
    /// </summary>
    private static char[]? ReadHidden(string prompt)
    {
        Console.Write(prompt);
        using var editor = new HiddenLineEditor(RecoveryCode.MaxLength + 1);
        try
        {
            while (true)
            {
                var k = Console.ReadKey(intercept: true); // intercept: the key is never echoed
                if (editor.Process(k.Key, k.KeyChar)) break;
            }
        }
        catch (Exception e) when (e is InvalidOperationException or IOException)
        {
            // no interactive console (input redirected)
            Console.WriteLine();
            return null;
        }
        Console.WriteLine();
        return editor.TakeCopy();
    }

    private static string? SafeReadLine()
    {
        try { return Console.ReadLine(); }
        catch (IOException) { return null; }
    }

    private static void PrintUsage()
    {
        Console.WriteLine("Usage: Setup-PcGuard.exe [--install --backend-url <https://host/api/v1> [--allow-app <name.exe>]... [--no-recovery-code | --default-recovery-code]] [--uninstall [--purge]] [--allow-writable-package] [--no-pause] [--help]");
        Console.WriteLine("  (no arguments)   interactive menu");
        Console.WriteLine("  --install        install or upgrade; with --backend-url it runs without questions");
        Console.WriteLine("  --allow-app <name.exe>   with --install: keep this app running on this PC even while it is locked");
        Console.WriteLine("                   (repeatable, at most 16; bare exe name such as anydesk.exe, letters, digits, . - _ only).");
        Console.WriteLine("                   Without it an upgrade keeps the extra apps configured before. Use only on test/admin PCs:");
        Console.WriteLine("                   remote-control software kept running lets anyone at the PC use it while the PC is locked.");
        Console.WriteLine("  --no-recovery-code   with --install: do not set an offline recovery code and do not ask for one.");
        Console.WriteLine("                   The interactive install asks for the recovery code (typed hidden, twice); it is NEVER");
        Console.WriteLine("                   accepted on the command line, and its hash never either (it goes to install.ps1 in an");
        Console.WriteLine("                   admin-only file). At least 12 characters, 6 different ones, no common words, years,");
        Console.WriteLine("                   keyboard runs or repeats. A silent install sets none and prints a warning.");
        Console.WriteLine("                   The code works ONCE. Without a new code an upgrade keeps an unused code set before,");
        Console.WriteLine("                   but never one that was used (or of a PC Guard that was released or disabled).");
        Console.WriteLine("  --default-recovery-code   with --install: use the code in default-recovery-code.txt next to");
        Console.WriteLine("                   Setup-PcGuard.exe without asking (exit code 64 if it is missing or invalid). The file is");
        Console.WriteLine("                   read only from a package folder that passed the admin-only check (never with");
        Console.WriteLine("                   --allow-writable-package), at most 130 bytes, the code alone on one line. The");
        Console.WriteLine("                   interactive install offers it too (Enter = use it, - = none). The code sits in plain");
        Console.WriteLine("                   text: delete the file after installing. Cannot be combined with --no-recovery-code.");
        Console.WriteLine("  --uninstall      uninstall without questions (add --purge to also delete ProgramData\\PcGuard)");
        Console.WriteLine("  --allow-writable-package   install even if standard users can modify the package folder, or it holds links or too many files (NOT recommended)");
        Console.WriteLine("  --no-pause       with --install/--uninstall: do not wait for Enter at the end");
    }
}
