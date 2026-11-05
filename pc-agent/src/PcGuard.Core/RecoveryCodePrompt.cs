using System.Runtime.CompilerServices;

[assembly: InternalsVisibleTo("PcGuard.Core.Tests")]

namespace PcGuard.Core;

/// <summary>
/// Keystroke buffer for a hidden console prompt (Setup's recovery code question): no echo, Backspace
/// removes the last character, Escape clears the line, Enter finishes; keys without a character and
/// control characters are ignored; characters beyond the capacity are dropped (so a capacity of
/// MaxLength + 1 lets the validation report "too long"). The buffer is a char[] that is zeroed on
/// every removal, on <see cref="TakeCopy"/> and on <see cref="Dispose"/>; no string of the text is made.
/// </summary>
public sealed class HiddenLineEditor : IDisposable
{
    private readonly char[] _buffer;

    public HiddenLineEditor(int capacity)
    {
        if (capacity < 1) throw new ArgumentOutOfRangeException(nameof(capacity));
        _buffer = new char[capacity];
    }

    public int Length { get; private set; }

    public ReadOnlySpan<char> Text => _buffer.AsSpan(0, Length);

    internal char[] RawBufferForTests => _buffer;

    /// <summary>Applies one key; true when Enter finished the line.</summary>
    public bool Process(ConsoleKey key, char keyChar)
    {
        switch (key)
        {
            case ConsoleKey.Enter:
                return true;
            case ConsoleKey.Backspace:
                if (Length > 0) _buffer[--Length] = '\0';
                return false;
            case ConsoleKey.Escape:
                Clear();
                return false;
        }
        if (keyChar == '\0' || char.IsControl(keyChar)) return false;
        if (Length < _buffer.Length) _buffer[Length++] = keyChar;
        return false;
    }

    /// <summary>An exact-length copy for the caller (who must zero it); the editor's own buffer is wiped.</summary>
    public char[] TakeCopy()
    {
        var copy = Text.ToArray();
        Clear();
        return copy;
    }

    public void Clear()
    {
        Array.Clear(_buffer);
        Length = 0;
    }

    public void Dispose() => Clear();
}

public enum RecoveryPromptOutcome { NotSet, Set, Aborted }

/// <summary>Where the recovery code of an install came from (shown in Setup's summary).</summary>
public enum RecoveryCodeSource { None, Typed, Default }

/// <param name="Hash">The stored form (see <see cref="RecoveryCode"/>) when <see cref="Outcome"/> is Set; otherwise null.</param>
public sealed record RecoveryPromptResult(RecoveryPromptOutcome Outcome, string? Hash)
{
    /// <summary>Typed or Default when <see cref="Outcome"/> is Set; otherwise None.</summary>
    public RecoveryCodeSource Source { get; init; } = Outcome == RecoveryPromptOutcome.Set ? RecoveryCodeSource.Typed : RecoveryCodeSource.None;
}

/// <summary>
/// Setup's interactive recovery code question: hidden entry, validation, a second hidden entry to
/// confirm; an invalid code or a mismatch asks again, and after <see cref="MaxTries"/> failed tries
/// the install is aborted with nothing changed. An empty first entry (or no console) means no code;
/// an empty entry AFTER a failed try is confirmed first ("Install without a recovery code? (y/N)":
/// yes = no code, anything else = ask for the code again without using a try, no console = abort).
/// Every char[] the reader returns is zeroed here as soon as it is no longer needed. Messages passed
/// to <c>error</c> never contain the code.
/// </summary>
public static class RecoveryCodePrompt
{
    public const int MaxTries = 3;
    public const string FirstPrompt = "Recovery code for this PC (at least 12 characters; typed hidden; empty = none): ";
    public const string ConfirmPrompt = "Type the recovery code again to confirm: ";
    public const string NoCodeConfirmPrompt = "Install without a recovery code? (y/N): ";
    public const string DefaultPrompt = "A default recovery code file was found (" + DefaultRecoveryCode.FileName + "). Press Enter to use it, type another code, or type - (a single dash) to install without a recovery code: ";

    /// <summary>The value after "Recovery code:" in Setup's summary before YES.</summary>
    public static string SummaryText(RecoveryCodeSource source) => source switch
    {
        RecoveryCodeSource.Default => "set (from " + DefaultRecoveryCode.FileName + ")",
        RecoveryCodeSource.Typed => "set (typed)",
        _ => "NOT set (no offline way out)",
    };

    /// <summary>
    /// The question when a valid <see cref="DefaultRecoveryCode.FileName"/> was loaded: hidden entry;
    /// empty = use <paramref name="defaultCode"/>; exactly "-" = no code; anything else is a typed code
    /// (validated and confirmed as in <see cref="Run"/>; an invalid one or a mismatch asks this question
    /// again, <see cref="MaxTries"/> failed tries abort). No console = no code. Every typed char[] is
    /// zeroed here; <paramref name="defaultCode"/> belongs to the caller and is not zeroed here.
    /// </summary>
    public static RecoveryPromptResult RunWithDefault(char[] defaultCode, Func<string, char[]?> readHidden, Action<string> error,
        Func<char[], string>? hash = null)
    {
        ArgumentNullException.ThrowIfNull(defaultCode);
        hash ??= c => RecoveryCode.Hash(c.AsSpan());
        for (var attempt = 1; attempt <= MaxTries; attempt++)
        {
            var first = readHidden(DefaultPrompt);
            if (first is null) return new RecoveryPromptResult(RecoveryPromptOutcome.NotSet, null);
            try
            {
                if (first.Length == 0)
                    return new RecoveryPromptResult(RecoveryPromptOutcome.Set, hash(defaultCode)) { Source = RecoveryCodeSource.Default };
                if (first.Length == 1 && first[0] == '-')
                    return new RecoveryPromptResult(RecoveryPromptOutcome.NotSet, null);
                if (RecoveryCode.Validate(first) is { } invalid)
                {
                    error(invalid);
                    continue;
                }
                var second = readHidden(ConfirmPrompt);
                if (second is null)
                {
                    error("No input for the confirmation. Installation aborted. Nothing was changed.");
                    return new RecoveryPromptResult(RecoveryPromptOutcome.Aborted, null);
                }
                try
                {
                    if (!first.AsSpan().SequenceEqual(second))
                    {
                        error("The two entries do not match.");
                        continue;
                    }
                    return new RecoveryPromptResult(RecoveryPromptOutcome.Set, hash(first)) { Source = RecoveryCodeSource.Typed };
                }
                finally
                {
                    Array.Clear(second);
                }
            }
            finally
            {
                Array.Clear(first);
            }
        }
        error($"No valid recovery code after {MaxTries} tries. Installation aborted. Nothing was changed.");
        return new RecoveryPromptResult(RecoveryPromptOutcome.Aborted, null);
    }

    /// <param name="readHidden">Shows the prompt and returns the typed characters (exact length), or null when there is no console.</param>
    /// <param name="error">Prints one error line.</param>
    /// <param name="hash">Hashes a validated code; default <see cref="RecoveryCode.Hash(ReadOnlySpan{char})"/>.</param>
    /// <param name="confirmNoCode">Asks a yes/no question: true = yes, false = no, null = no console. When
    /// null itself, an empty entry after a failed try means no code without asking.</param>
    public static RecoveryPromptResult Run(Func<string, char[]?> readHidden, Action<string> error,
        Func<char[], string>? hash = null, Func<string, bool?>? confirmNoCode = null)
    {
        hash ??= c => RecoveryCode.Hash(c.AsSpan());
        var attempt = 1;
        var failedBefore = false;
        while (attempt <= MaxTries)
        {
            var first = readHidden(FirstPrompt);
            if (first is null) return new RecoveryPromptResult(RecoveryPromptOutcome.NotSet, null);
            try
            {
                if (first.Length == 0)
                {
                    if (!failedBefore || confirmNoCode is null) return new RecoveryPromptResult(RecoveryPromptOutcome.NotSet, null);
                    var answer = confirmNoCode(NoCodeConfirmPrompt);
                    if (answer is null)
                    {
                        error("No answer. Installation aborted. Nothing was changed.");
                        return new RecoveryPromptResult(RecoveryPromptOutcome.Aborted, null);
                    }
                    if (answer.Value) return new RecoveryPromptResult(RecoveryPromptOutcome.NotSet, null);
                    continue; // ask for the code again; this does not use a try
                }
                if (RecoveryCode.Validate(first) is { } invalid)
                {
                    error(invalid);
                    failedBefore = true;
                    attempt++;
                    continue;
                }

                var second = readHidden(ConfirmPrompt);
                if (second is null)
                {
                    error("No input for the confirmation. Installation aborted. Nothing was changed.");
                    return new RecoveryPromptResult(RecoveryPromptOutcome.Aborted, null);
                }
                try
                {
                    if (!first.AsSpan().SequenceEqual(second))
                    {
                        error("The two entries do not match.");
                        failedBefore = true;
                        attempt++;
                        continue;
                    }
                    return new RecoveryPromptResult(RecoveryPromptOutcome.Set, hash(first));
                }
                finally
                {
                    Array.Clear(second);
                }
            }
            finally
            {
                Array.Clear(first);
            }
        }
        error($"No valid recovery code after {MaxTries} tries. Installation aborted. Nothing was changed.");
        return new RecoveryPromptResult(RecoveryPromptOutcome.Aborted, null);
    }
}
