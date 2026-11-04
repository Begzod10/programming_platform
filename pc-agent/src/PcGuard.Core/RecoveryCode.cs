using System.Globalization;
using System.Security.Cryptography;
using System.Text;

namespace PcGuard.Core;

/// <summary>
/// The offline, install-time recovery code: set by the person who installs PC Guard, typed on the
/// lock screen to stop and disable PC Guard on that PC when nothing else works (no backend, Task
/// Manager hidden). Only a PBKDF2 hash is ever stored:
/// <c>pbkdf2-sha256$&lt;iterations&gt;$&lt;salt b64&gt;$&lt;hash b64&gt;</c> (PBKDF2-HMAC-SHA256, 16-byte random salt,
/// 32-byte hash). Nothing here logs, stores or puts the code into an exception message.
/// </summary>
public static class RecoveryCode
{
    public const int MinLength = 10;
    public const int MaxLength = 128;
    public const int MinDistinct = 3;
    /// <summary>Iterations used for new hashes (OWASP 2021 minimum for PBKDF2-HMAC-SHA256).</summary>
    public const int Iterations = 310_000;
    public const int MinIterations = 310_000;
    /// <summary>Upper bound accepted from a stored value (keeps one verification well under a few seconds).</summary>
    public const int MaxIterations = 5_000_000;
    public const int SaltBytes = 16;
    public const int HashBytes = 32;
    public const string Scheme = "pbkdf2-sha256";
    /// <summary>Longest stored value accepted (the real form is about 91 characters).</summary>
    public const int MaxStoredLength = 128;

    // Compared case-insensitively. Short on purpose: the length and distinct-character rules do the rest.
    private static readonly string[] DenyList =
    {
        "0123456789", "1234567890", "12345678910", "0987654321", "9876543210", "1111111111",
        "password12", "password123", "password1234", "passw0rd12", "parol12345", "parol123456",
        "qwertyuiop", "qwerty1234", "qwerty12345", "1q2w3e4r5t", "1qaz2wsx3edc", "asdfghjkl1", "zxcvbnm123",
        "abcdefghij", "abcd123456", "abc1234567", "admin12345", "administrator", "iloveyou12",
        "pcguard123", "pcguard1234", "recovery12", "recovery123",
    };

    /// <summary>Null when <paramref name="code"/> is acceptable as a new recovery code; otherwise the reason (never containing the code).</summary>
    public static string? Validate(string? code) => Validate((code ?? "").AsSpan());

    /// <inheritdoc cref="Validate(string?)"/>
    public static string? Validate(ReadOnlySpan<char> code)
    {
        if (code.Length == 6 && AllDigits(code))
            return "The recovery code must not be 6 digits (that is the shape of a teacher maintenance code).";
        if (code.Length < MinLength) return $"The recovery code must be at least {MinLength} characters long.";
        if (code.Length > MaxLength) return $"The recovery code must be at most {MaxLength} characters long.";
        foreach (var c in code)
            if (c is < ' ' or > '~')
                return "The recovery code may contain only printable ASCII characters (letters A-Z, digits, punctuation and spaces).";
        if (code[0] == ' ' || code[^1] == ' ') return "The recovery code must not start or end with a space.";
        if (Distinct(code) < MinDistinct) return $"The recovery code must contain at least {MinDistinct} different characters.";
        foreach (var weak in DenyList)
            if (code.Equals(weak.AsSpan(), StringComparison.OrdinalIgnoreCase))
                return "The recovery code is too common; choose another one.";
        return null;
    }

    /// <summary>Hashes a valid code with a fresh random salt. Throws ArgumentException (without the code) for an invalid one.</summary>
    public static string Hash(string code)
    {
        ArgumentNullException.ThrowIfNull(code);
        return Hash(code.AsSpan());
    }

    /// <inheritdoc cref="Hash(string)"/>
    public static string Hash(ReadOnlySpan<char> code)
    {
        Span<byte> salt = stackalloc byte[SaltBytes];
        RandomNumberGenerator.Fill(salt);
        return Hash(code, salt, Iterations);
    }

    /// <summary>Hash with a given salt and iteration count (deterministic; for tests and known vectors).</summary>
    public static string Hash(ReadOnlySpan<char> code, ReadOnlySpan<byte> salt, int iterations)
    {
        if (Validate(code) is { } error) throw new ArgumentException("Invalid recovery code: " + error);
        if (salt.Length != SaltBytes) throw new ArgumentException($"The salt must be {SaltBytes} bytes.", nameof(salt));
        if (iterations is < MinIterations or > MaxIterations)
            throw new ArgumentException($"Iterations must be {MinIterations}..{MaxIterations}.", nameof(iterations));
        Span<byte> hash = stackalloc byte[HashBytes];
        Derive(code, salt, iterations, hash);
        var result = Scheme + "$" + iterations.ToString(CultureInfo.InvariantCulture) + "$"
                     + Convert.ToBase64String(salt) + "$" + Convert.ToBase64String(hash);
        CryptographicOperations.ZeroMemory(hash);
        return result;
    }

    /// <summary>True when <paramref name="stored"/> has exactly the stored form (canonical base64, iterations in range).</summary>
    public static bool IsWellFormedStored(string? stored)
    {
        Span<byte> salt = stackalloc byte[SaltBytes];
        Span<byte> hash = stackalloc byte[HashBytes];
        return TryParse(stored, salt, hash, out _);
    }

    /// <summary>
    /// True only if <paramref name="code"/> hashes to <paramref name="stored"/>. The final comparison is
    /// constant-time. False (never an exception) for a null/oversized code or a malformed stored value.
    /// </summary>
    public static bool Verify(string? code, string? stored)
    {
        try
        {
            if (code is null || code.Length == 0 || code.Length > MaxLength) return false;
            Span<byte> salt = stackalloc byte[SaltBytes];
            Span<byte> expected = stackalloc byte[HashBytes];
            Span<byte> actual = stackalloc byte[HashBytes];
            if (!TryParse(stored, salt, expected, out var iterations)) return false;
            Derive(code.AsSpan(), salt, iterations, actual);
            var same = CryptographicOperations.FixedTimeEquals(actual, expected);
            CryptographicOperations.ZeroMemory(actual);
            return same;
        }
        catch (Exception)
        {
            return false;
        }
    }

    private static void Derive(ReadOnlySpan<char> code, ReadOnlySpan<byte> salt, int iterations, Span<byte> destination)
    {
        var bytes = new byte[Encoding.UTF8.GetMaxByteCount(code.Length)];
        try
        {
            var n = Encoding.UTF8.GetBytes(code, bytes);
            Rfc2898DeriveBytes.Pbkdf2(bytes.AsSpan(0, n), salt, destination, iterations, HashAlgorithmName.SHA256);
        }
        finally
        {
            CryptographicOperations.ZeroMemory(bytes);
        }
    }

    private static bool TryParse(string? stored, Span<byte> salt, Span<byte> hash, out int iterations)
    {
        iterations = 0;
        if (stored is null || stored.Length > MaxStoredLength) return false;
        var parts = stored.Split('$');
        if (parts.Length != 4 || !string.Equals(parts[0], Scheme, StringComparison.Ordinal)) return false;

        var it = parts[1];
        if (it.Length is 0 or > 7 || it[0] == '0') return false;
        foreach (var c in it)
            if (c is < '0' or > '9') return false;
        iterations = int.Parse(it, NumberStyles.None, CultureInfo.InvariantCulture);
        if (iterations is < MinIterations or > MaxIterations) return false;

        return DecodeExact(parts[2], salt) && DecodeExact(parts[3], hash);
    }

    // Exactly destination.Length bytes, and the text must be the canonical encoding of them.
    private static bool DecodeExact(string text, Span<byte> destination)
    {
        if (text.Length != (destination.Length + 2) / 3 * 4) return false;
        foreach (var c in text)
            if (!(c is >= 'A' and <= 'Z' or >= 'a' and <= 'z' or >= '0' and <= '9' or '+' or '/' or '=')) return false;
        Span<byte> buffer = stackalloc byte[destination.Length + 3];
        if (!Convert.TryFromBase64String(text, buffer, out var written) || written != destination.Length) return false;
        if (!string.Equals(Convert.ToBase64String(buffer[..written]), text, StringComparison.Ordinal)) return false;
        buffer[..written].CopyTo(destination);
        return true;
    }

    private static bool AllDigits(ReadOnlySpan<char> s)
    {
        foreach (var c in s)
            if (c is < '0' or > '9') return false;
        return true;
    }

    private static int Distinct(ReadOnlySpan<char> s)
    {
        Span<bool> seen = stackalloc bool[128];
        var n = 0;
        foreach (var c in s)
        {
            if (c >= 128 || seen[c]) continue;
            seen[c] = true;
            n++;
        }
        return n;
    }
}

/// <summary>Error code of <see cref="RecoveryResultMessage"/> besides invalid_code, locked_out and error (<see cref="AdminErrors"/>).</summary>
public static class RecoveryErrors
{
    /// <summary>No recovery code was set at install (no recovery.hash on this PC).</summary>
    public const string NotConfigured = "not_configured";
}

/// <summary>
/// Decision logic around one recovery_release in the service: not configured first (never counted),
/// then the local limiter (1 s spacing, 5 failures -> 10 minutes, shared rules with maintenance
/// codes but its own instance), then the PBKDF2 verification happens in the caller, then
/// <see cref="Complete"/>. Only a wrong code counts. Not thread-safe: the service serialises calls.
/// </summary>
public sealed class RecoveryGate
{
    private readonly AdminAttemptLimiter _limiter;

    public RecoveryGate(AdminAttemptLimiter limiter) => _limiter = limiter;

    public int ConsecutiveFailures => _limiter.ConsecutiveFailures;

    /// <summary>Null: verify the code now. Otherwise answer with this and do NOT verify.</summary>
    public RecoveryResultMessage? Precheck(DateTimeOffset now, bool configured)
    {
        if (!configured) return new RecoveryResultMessage(false, RecoveryErrors.NotConfigured, 0);
        var d = _limiter.Check(now);
        return d.Kind == AdminAttemptKind.Allowed ? null : new RecoveryResultMessage(false, AdminErrors.LockedOut, d.RetrySeconds);
    }

    public RecoveryResultMessage Complete(DateTimeOffset now, bool verified)
    {
        if (verified)
        {
            _limiter.RecordSuccess();
            return new RecoveryResultMessage(true, null, 0);
        }
        _limiter.RecordFailure(now);
        var d = _limiter.Check(now);
        return d.Kind == AdminAttemptKind.LockedOut
            ? new RecoveryResultMessage(false, AdminErrors.LockedOut, d.RetrySeconds)
            : new RecoveryResultMessage(false, AdminErrors.InvalidCode, 0);
    }
}

/// <summary>Event-log texts of the recovery code. None takes the code (or its hash).</summary>
public static class RecoveryAudit
{
    public static string Accepted() => "Recovery code accepted: PC Guard stopped and disabled on this PC";

    public static string Rejected(int consecutiveFailures)
        => $"Recovery code rejected ({consecutiveFailures.ToString(CultureInfo.InvariantCulture)} of {AdminAttemptLimiter.MaxFailures} consecutive failures)";

    public static string LockedOut()
        => $"Recovery code attempts locked out for {(int)AdminAttemptLimiter.Lockout.TotalMinutes} minutes after {AdminAttemptLimiter.MaxFailures} consecutive failures";

    public static string RefusedLockedOut(int retrySeconds)
        => $"Recovery code attempt refused: locked out for another {retrySeconds.ToString(CultureInfo.InvariantCulture)} s";

    public static string NotConfigured() => "Recovery code attempt refused: no recovery code is configured on this PC";

    public static string DisableFailed(int win32Error)
        => $"Recovery release: could not set the PcGuard service start type to Disabled (error {win32Error.ToString(CultureInfo.InvariantCulture)}); PC Guard will start again after a reboot";
}
