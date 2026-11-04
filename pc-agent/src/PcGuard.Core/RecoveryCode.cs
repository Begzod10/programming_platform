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
    public const int MinLength = 12;
    public const int MaxLength = 128;
    public const int MinDistinct = 6;
    /// <summary>Characters that must remain after the guessable parts (common words, years, keyboard and
    /// alphabet runs, repeated characters and repeated blocks) are taken out.</summary>
    public const int MinUnguessable = 8;
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
    /// <summary>Largest recovery.hash (or transfer file) accepted: the stored form plus a little whitespace.</summary>
    public const int MaxStoredFileBytes = MaxStoredLength + 8;
    /// <summary>
    /// Name of the file Setup writes the hash into, inside its admin-only temp folder, for install.ps1
    /// (-RecoveryCodeHashFile). The hash is never put on a command line: Windows PowerShell logs its
    /// command line (event 400/600 "HostApplication") to a log that standard users can read.
    /// </summary>
    public const string TransferFileName = "recovery-hash.in";

    // Guessable parts, matched case-insensitively ANYWHERE in the code and taken out before counting
    // what is left (see Validate). Words a school PC's installer is likely to reach for (uz/ru/en).
    private static readonly string[] CommonWords =
    {
        "maktab", "kompyuter", "komputer", "kompiuter", "computer", "admin", "parol", "password", "passw0rd",
        "p@ssw0rd", "qwerty", "school", "shkola", "sinf", "klass", "ustoz", "teacher", "uchitel", "student",
        "talaba", "oquvchi", "o'quvchi", "uchenik", "pcguard", "guard", "recovery", "tiklash", "letmein",
        "welcome", "iloveyou", "secret", "sekret", "windows", "microsoft", "uzbekistan", "ozbekiston",
        "o'zbekiston", "toshkent", "tashkent", "samarqand", "informatika", "dastur", "salom", "privet", "login",
    };

    // Keyboard rows (US layout, plain and shifted, plus the usual column walks); any 4+ character
    // stretch of one of them, forwards or backwards, is guessable.
    private static readonly string[] KeyboardRuns =
    {
        "`1234567890-=", "~!@#$%^&*()_+", "qwertyuiop[]\\", "asdfghjkl;'", "zxcvbnm,./",
        "1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,9ol.0p;/", "1q2w3e4r5t6y7u8i9o0p", "qazwsxedcrfvtgbyhnujmikolp",
    };

    private const int MinRun = 4;
    private const int MinRepeatedBlock = 3;

    /// <summary>Null when <paramref name="code"/> is acceptable as a new recovery code; otherwise the reason (never containing the code).</summary>
    public static string? Validate(string? code) => Validate((code ?? "").AsSpan());

    /// <inheritdoc cref="Validate(string?)"/>
    public static string? Validate(ReadOnlySpan<char> code)
    {
        if (code.Length == 6 && AllDigits(code))
            return "The recovery code must not be 6 digits (that is the shape of a teacher maintenance code).";
        if (code.Length < MinLength) return $"The recovery code must be at least {MinLength} characters long.";
        if (code.Length > MaxLength) return $"The recovery code must be at most {MaxLength} characters long.";
        if (!IsPrintableAscii(code))
            return "The recovery code may contain only printable ASCII characters (letters A-Z, digits, punctuation and spaces).";
        if (code[0] == ' ' || code[^1] == ' ') return "The recovery code must not start or end with a space.";
        if (Distinct(code) < MinDistinct) return $"The recovery code must contain at least {MinDistinct} different characters.";
        if (Unguessable(code) < MinUnguessable)
            return "The recovery code is too easy to guess (it is mostly common words, years, keyboard or alphabet runs, or repeated parts); "
                   + $"choose another one with at least {MinUnguessable} characters that are not such parts.";
        return null;
    }

    /// <summary>
    /// True when every character is printable ASCII (0x20-0x7E), the only characters a valid code can
    /// contain. The shell's dialog uses it to refuse, without sending or counting, text typed on a
    /// non-English keyboard layout.
    /// </summary>
    public static bool IsPrintableAscii(ReadOnlySpan<char> text)
    {
        foreach (var c in text)
            if (c is < ' ' or > '~')
                return false;
        return true;
    }

    /// <summary>The bytes Setup writes into <see cref="TransferFileName"/>: exactly the ASCII stored form, no BOM, no newline.</summary>
    public static byte[] ToTransferBytes(string stored)
    {
        // the message never contains the value: it could be a plain code passed by mistake
        if (!IsWellFormedStored(stored)) throw new ArgumentException("The recovery code hash is not in the stored form.", nameof(stored));
        return Encoding.ASCII.GetBytes(stored);
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

    // Number of characters that are NOT part of a guessable piece. Works on a lower-cased copy that is
    // zeroed afterwards.
    private static int Unguessable(ReadOnlySpan<char> code)
    {
        var n = code.Length;
        var lower = new char[n];
        var weak = new bool[n];
        try
        {
            for (var i = 0; i < n; i++) lower[i] = char.ToLowerInvariant(code[i]);
            var text = lower.AsSpan();

            foreach (var word in CommonWords) MarkAll(text, word.AsSpan(), weak);
            MarkYears(text, weak);
            foreach (var row in KeyboardRuns) MarkKeyboardRun(text, row, weak);
            MarkSequences(text, weak);
            MarkRepeatedChars(text, weak);
            MarkRepeatedBlocks(text, weak);

            var left = 0;
            foreach (var w in weak) if (!w) left++;
            return left;
        }
        finally
        {
            Array.Clear(lower);
        }
    }

    private static void MarkAll(ReadOnlySpan<char> text, ReadOnlySpan<char> part, bool[] weak)
    {
        if (part.Length == 0 || part.Length > text.Length) return;
        for (var i = 0; i + part.Length <= text.Length; i++)
            if (text.Slice(i, part.Length).SequenceEqual(part))
                Array.Fill(weak, true, i, part.Length);
    }

    // 19xx and 20xx (school years, birth years).
    private static void MarkYears(ReadOnlySpan<char> text, bool[] weak)
    {
        for (var i = 0; i + 4 <= text.Length; i++)
        {
            if (!(IsDigit(text[i]) && IsDigit(text[i + 1]) && IsDigit(text[i + 2]) && IsDigit(text[i + 3]))) continue;
            if ((text[i] == '1' && text[i + 1] == '9') || (text[i] == '2' && text[i + 1] == '0'))
                Array.Fill(weak, true, i, 4);
        }
    }

    // Every stretch of MinRun or more characters that appears in a keyboard row, forwards or backwards.
    private static void MarkKeyboardRun(ReadOnlySpan<char> text, string row, bool[] weak)
    {
        var reversed = new string(row.Reverse().ToArray());
        foreach (var r in new[] { row, reversed })
        {
            for (var i = 0; i < text.Length; i++)
            {
                var best = 0;
                for (var len = MinRun; i + len <= text.Length; len++)
                {
                    if (r.AsSpan().IndexOf(text.Slice(i, len)) < 0) break;
                    best = len;
                }
                if (best >= MinRun) Array.Fill(weak, true, i, best);
            }
        }
    }

    // abcd, 4321, xyz... : letters or digits stepping by +1 or -1.
    private static void MarkSequences(ReadOnlySpan<char> text, bool[] weak)
    {
        for (var start = 0; start < text.Length - 1;)
        {
            var step = text[start + 1] - text[start];
            if (!(step is 1 or -1) || !IsAlnum(text[start]) || !IsAlnum(text[start + 1]))
            {
                start++;
                continue;
            }
            var end = start + 1;
            while (end + 1 < text.Length && IsAlnum(text[end + 1]) && text[end + 1] - text[end] == step) end++;
            if (end - start + 1 >= MinRun) Array.Fill(weak, true, start, end - start + 1);
            start = end;
        }
    }

    // aaa, 111, !!!: three or more of the same character.
    private static void MarkRepeatedChars(ReadOnlySpan<char> text, bool[] weak)
    {
        for (var start = 0; start < text.Length;)
        {
            var end = start;
            while (end + 1 < text.Length && text[end + 1] == text[start]) end++;
            if (end - start + 1 >= 3) Array.Fill(weak, true, start, end - start + 1);
            start = end + 1;
        }
    }

    // A block of MinRepeatedBlock or more characters that already appeared earlier: the later copy adds nothing.
    private static void MarkRepeatedBlocks(ReadOnlySpan<char> text, bool[] weak)
    {
        var n = text.Length;
        for (var j = 1; j < n; j++)
        {
            for (var i = 0; i < j; i++)
            {
                var k = 0;
                while (j + k < n && i + k < j && text[i + k] == text[j + k]) k++;
                if (k >= MinRepeatedBlock) Array.Fill(weak, true, j, k);
            }
        }
    }

    private static bool IsDigit(char c) => c is >= '0' and <= '9';
    private static bool IsAlnum(char c) => c is >= '0' and <= '9' or >= 'a' and <= 'z';

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

    /// <summary>Shell-local only (never sent): the typed text has characters a code can never contain,
    /// usually because the keyboard layout is not English. Nothing is sent and nothing is counted.</summary>
    public const string WrongLayout = "wrong_layout";
}

/// <summary>
/// Decision logic around one recovery_release in the service: not configured first (never counted),
/// then the persistent limiter (<see cref="RecoveryAttemptLimiter"/>: 1 s spacing, 5 failures ->
/// escalating lockout 10 min / 1 h / 24 h, kept in recovery.attempts across restarts and reboots).
/// <see cref="Begin"/> records the attempt as a failure on disk BEFORE the PBKDF2 verification (so
/// cutting the power during the check still counts); <see cref="Complete"/> clears it on success.
/// Not thread-safe: the service serialises calls.
/// </summary>
public sealed class RecoveryGate
{
    private readonly RecoveryAttemptLimiter _limiter;

    public RecoveryGate(RecoveryAttemptLimiter limiter) => _limiter = limiter;

    public int ConsecutiveFailures => _limiter.ConsecutiveFailures;

    /// <summary>Length of the lockout in force (or the last one started).</summary>
    public TimeSpan CurrentLockout => _limiter.CurrentLockout;

    /// <summary>Null: call <see cref="Begin"/> and verify the code. Otherwise answer with this and do NOT verify.</summary>
    public RecoveryResultMessage? Precheck(DateTimeOffset now, bool configured)
    {
        if (!configured) return new RecoveryResultMessage(false, RecoveryErrors.NotConfigured, 0);
        var d = _limiter.Check(now);
        return d.Kind == AdminAttemptKind.Allowed ? null : new RecoveryResultMessage(false, AdminErrors.LockedOut, d.RetrySeconds);
    }

    /// <summary>Records the attempt (as a failure until <see cref="Complete"/> says otherwise). False: it could
    /// not be persisted; answer "error" and do NOT verify.</summary>
    public bool Begin(DateTimeOffset now) => _limiter.BeginAttempt(now);

    public RecoveryResultMessage Complete(DateTimeOffset now, bool verified)
    {
        if (verified)
        {
            _limiter.RecordSuccess();
            return new RecoveryResultMessage(true, null, 0);
        }
        var d = _limiter.Check(now);
        return d.Kind == AdminAttemptKind.LockedOut
            ? new RecoveryResultMessage(false, AdminErrors.LockedOut, d.RetrySeconds)
            : new RecoveryResultMessage(false, AdminErrors.InvalidCode, 0);
    }
}

/// <summary>Event-log texts of the recovery code. None takes the code (or its hash).</summary>
public static class RecoveryAudit
{
    public static string Accepted() => "Recovery code accepted: PC Guard stops enforcing, disables itself and stops on this PC";

    public static string Rejected(int consecutiveFailures)
        => $"Recovery code rejected ({consecutiveFailures.ToString(CultureInfo.InvariantCulture)} of {RecoveryAttemptLimiter.MaxFailures} consecutive failures)";

    public static string LockedOut(TimeSpan lockout)
        => $"Recovery code attempts locked out for {Duration(lockout)} after {RecoveryAttemptLimiter.MaxFailures} consecutive failures";

    public static string RefusedLockedOut(int retrySeconds)
        => $"Recovery code attempt refused: locked out for another {retrySeconds.ToString(CultureInfo.InvariantCulture)} s";

    public static string NotConfigured() => "Recovery code attempt refused: no recovery code is configured on this PC";

    public static string AttemptsUntrusted(string problem)
        => $"Recovery code attempt counter recovery.attempts is {problem}; recovery code attempts are locked out for 24 hours (an administrator can delete the file and restart the service)";

    public static string AttemptNotRecorded()
        => "Recovery code attempt refused: the attempt could not be recorded in recovery.attempts (nothing was checked)";

    public static string CodeBurned() => "Recovery code used: recovery.hash deleted (the code is single use; reinstall with a new code)";

    public static string BurnFailed(string error) => $"Recovery code used, but recovery.hash could not be deleted ({error})";

    public static string DisableFailed(int win32Error)
        => $"Recovery release: could not set the PcGuard service start type to Disabled (error {win32Error.ToString(CultureInfo.InvariantCulture)}); PC Guard keeps running without enforcing and retries every 30 s. Until that works a reboot starts it again with enforcement";

    public static string DisableRetried(int attempts)
        => $"Recovery release: PcGuard service start type set to Disabled after {attempts.ToString(CultureInfo.InvariantCulture)} retries; stopping";

    public static string ShellsTerminated(int count)
        => $"Recovery release: {count.ToString(CultureInfo.InvariantCulture)} PC Guard shell process(es) terminated";

    private static string Duration(TimeSpan t)
    {
        if (t < TimeSpan.FromHours(1)) return ((int)t.TotalMinutes).ToString(CultureInfo.InvariantCulture) + " minutes";
        var h = (int)t.TotalHours;
        return h == 1 ? "1 hour" : h.ToString(CultureInfo.InvariantCulture) + " hours";
    }
}
