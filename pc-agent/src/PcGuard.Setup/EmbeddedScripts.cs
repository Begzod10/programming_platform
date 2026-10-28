using System.Reflection;
using System.Security.Cryptography;

namespace PcGuard.Setup;

/// <summary>Writes the embedded PowerShell scripts into the admin-only folder and verifies them by SHA-256.</summary>
internal static class EmbeddedScripts
{
    public const string Install = "install.ps1";
    public const string Uninstall = "uninstall.ps1";

    /// <summary>Extracts one script and returns its full path. Throws if the file on disk does not match the embedded bytes.</summary>
    public static string Extract(string name, string adminOnlyDir)
    {
        var bytes = ReadEmbedded(name);
        var expected = SHA256.HashData(bytes);

        var target = Path.Combine(adminOnlyDir, name);
        // CreateNew: never overwrite or follow an existing file.
        using (var fs = new FileStream(target, FileMode.CreateNew, FileAccess.Write, FileShare.None))
        {
            fs.Write(bytes, 0, bytes.Length);
        }

        var actual = SHA256.HashData(File.ReadAllBytes(target));
        if (!CryptographicOperations.FixedTimeEquals(expected, actual))
            throw new InvalidDataException($"Integrity check failed for {name}: the extracted file differs from the embedded script.");

        return target;
    }

    private static byte[] ReadEmbedded(string name)
    {
        using var s = Assembly.GetExecutingAssembly().GetManifestResourceStream(name)
            ?? throw new InvalidDataException($"Embedded script {name} is missing from this exe.");
        using var ms = new MemoryStream();
        s.CopyTo(ms);
        return ms.ToArray();
    }
}
