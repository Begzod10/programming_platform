using System.Security.Cryptography;

namespace PcGuard.Core;

/// <summary>What Setup found about <see cref="DefaultRecoveryCode.FileName"/> (from the file system, without opening it).</summary>
/// <param name="IsDirectory">A folder has that name.</param>
/// <param name="IsReparsePoint">The entry is a symbolic link, junction or other reparse point.</param>
/// <param name="Length">Size in bytes.</param>
public sealed record DefaultCodeFile(bool IsDirectory, bool IsReparsePoint, long Length);

public enum DefaultCodeStatus { Absent, Ignored, Invalid, Loaded }

/// <summary>
/// Result of reading the default recovery code file. <see cref="Code"/> is set only when
/// <see cref="Status"/> is Loaded; it is a char[] that <see cref="Dispose"/> zeroes. <see cref="Message"/>
/// never contains the code.
/// </summary>
public sealed class DefaultCodeLoad : IDisposable
{
    internal DefaultCodeLoad(DefaultCodeStatus status, string? message, char[]? code = null)
    {
        Status = status;
        Message = message;
        Code = code;
    }

    public DefaultCodeStatus Status { get; }
    public string? Message { get; }
    public char[]? Code { get; private set; }

    public void Dispose()
    {
        if (Code is not null) Array.Clear(Code);
        Code = null;
    }
}

/// <summary>
/// The optional <c>default-recovery-code.txt</c> next to Setup-PcGuard.exe: one known recovery code an
/// administrator can use for several installs without typing it. It is never hardcoded, never on a
/// command line, and never part of a built package. Strict reading rules: only when the package folder
/// passed the admin-only check (never with --allow-writable-package); a regular file (no link) of at
/// most <see cref="MaxFileBytes"/> bytes that standard users can neither read nor change; plain
/// printable ASCII on one line; exactly one trailing CR LF, LF or CR is removed, nothing else is
/// trimmed; then the normal <see cref="RecoveryCode.Validate(ReadOnlySpan{char})"/> rules apply.
/// Every byte and char buffer is zeroed; messages never contain the code.
/// </summary>
public static class DefaultRecoveryCode
{
    public const string FileName = "default-recovery-code.txt";

    /// <summary>The longest code (128) plus CR LF.</summary>
    public const int MaxFileBytes = RecoveryCode.MaxLength + 2;

    public const string FoundMessage = "A default recovery code file was found (" + FileName + ").";

    private const AceRights ReadOrChange =
        AceRights.ReadData | AceRights.GenericRead | AceRights.GenericAll | AceRights.GenericWrite
        | AceRights.WriteData | AceRights.AppendData | AceRights.Delete | AceRights.ChangePermissions | AceRights.TakeOwnership;

    /// <summary>Allow entries on the file that let Users, Authenticated Users, Everyone or INTERACTIVE read or change it.</summary>
    public static IReadOnlyList<UnsafeGrant> FindExposure(IEnumerable<AceInfo> aces) =>
        PackageAclPolicy.FindLowPrivilegeGrants(aces, ReadOrChange);

    /// <summary>
    /// Reads the file through the given callbacks. <paramref name="file"/> null = there is no such entry.
    /// <paramref name="readAces"/> returns the file's ACEs; <paramref name="read"/> returns at most the
    /// given number of bytes from the file (the buffer is zeroed here afterwards). I/O errors from the
    /// callbacks are returned as Invalid, never thrown.
    /// </summary>
    /// <param name="packageAclPassed">True only when the package folder passed the admin-only check AND
    /// Setup runs without --allow-writable-package.</param>
    public static DefaultCodeLoad Load(bool packageAclPassed, DefaultCodeFile? file,
        Func<IReadOnlyList<AceInfo>> readAces, Func<int, byte[]> read)
    {
        if (file is null) return new DefaultCodeLoad(DefaultCodeStatus.Absent, null);
        if (!packageAclPassed)
            return new DefaultCodeLoad(DefaultCodeStatus.Ignored,
                $"{FileName} was found but is ignored: the package folder did not pass the admin-only permission check (--allow-writable-package). It was not read.");
        if (file.IsReparsePoint)
            return Invalid($"{FileName} is a link or junction; it is ignored (not read).");
        if (file.IsDirectory)
            return Invalid($"{FileName} is not a regular file; it is ignored.");
        if (file.Length > MaxFileBytes)
            return Invalid(TooLarge());

        byte[]? bytes = null;
        try
        {
            if (FindExposure(readAces()) is { Count: > 0 } grants)
                return Invalid($"{FileName} can be read or changed by standard users ({grants[0].Group}); it is ignored (not read). "
                               + "Keep it only in an admin-only folder (see the README).");
            bytes = read(MaxFileBytes + 1);
            return Decode(bytes);
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or InvalidOperationException
                                      or NotSupportedException or System.Security.SecurityException)
        {
            return Invalid($"{FileName} could not be read ({e.GetType().Name}); it is ignored.");
        }
        finally
        {
            if (bytes is not null) CryptographicOperations.ZeroMemory(bytes);
        }
    }

    /// <summary>Decodes the file content (the caller zeroes <paramref name="bytes"/>).</summary>
    public static DefaultCodeLoad Decode(ReadOnlySpan<byte> bytes)
    {
        if (bytes.Length > MaxFileBytes) return Invalid(TooLarge());
        if (bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF)
            return Invalid($"{FileName} starts with a byte order mark (BOM); save it as plain ASCII text (ANSI) without one. It is ignored.");

        var n = bytes.Length;
        if (n >= 2 && bytes[n - 2] == '\r' && bytes[n - 1] == '\n') n -= 2;
        else if (n >= 1 && (bytes[n - 1] == '\n' || bytes[n - 1] == '\r')) n -= 1;
        var body = bytes[..n];

        if (body.Length == 0) return Invalid($"{FileName} is empty; it is ignored.");
        foreach (var b in body)
        {
            if (b is < 0x20 or > 0x7E)
                return Invalid($"{FileName} must hold only the code, on one line, in printable ASCII (letters A-Z, digits, punctuation, inner spaces); it is ignored.");
        }

        var code = new char[body.Length];
        for (var i = 0; i < body.Length; i++) code[i] = (char)body[i];
        if (RecoveryCode.Validate(code) is { } reason)
        {
            Array.Clear(code);
            return Invalid($"{FileName}: {reason}");
        }
        return new DefaultCodeLoad(DefaultCodeStatus.Loaded, FoundMessage, code);
    }

    private static string TooLarge() => $"{FileName} is larger than {MaxFileBytes} bytes; it is ignored (not read).";

    private static DefaultCodeLoad Invalid(string message) => new(DefaultCodeStatus.Invalid, message);
}
