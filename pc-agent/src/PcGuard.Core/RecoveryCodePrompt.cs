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

/// <param name="Hash">The stored form (see <see cref="RecoveryCode"/>) when <see cref="Outcome"/> is Set; otherwise null.</param>
public sealed record RecoveryPromptResult(RecoveryPromptOutcome Outcome, string? Hash);

/// <summary>
/// Setup's interactive recovery code question: hidden entry, validation, a second hidden entry to
/// confirm; an invalid code or a mismatch asks again, and after <see cref="MaxTries"/> failed tries
/// the install is aborted with nothing changed. An empty first entry (or no console) means no code.
/// Every char[] the reader returns is zeroed here as soon as it is no longer needed. Messages passed
/// to <c>error</c> never contain the code.
/// </summary>
public static class RecoveryCodePrompt
{
    public const int MaxTries = 3;
    public const string FirstPrompt = "Recovery code for this PC (at least 10 characters; typed hidden; empty = none): ";
    public const string ConfirmPrompt = "Type the recovery code again to confirm: ";

    /// <param name="readHidden">Shows the prompt and returns the typed characters (exact length), or null when there is no console.</param>
    /// <param name="error">Prints one error line.</param>
    /// <param name="hash">Hashes a validated code; default <see cref="RecoveryCode.Hash(ReadOnlySpan{char})"/>.</param>
    public static RecoveryPromptResult Run(Func<string, char[]?> readHidden, Action<string> error, Func<char[], string>? hash = null)
    {
        hash ??= c => RecoveryCode.Hash(c.AsSpan());
        for (var attempt = 1; attempt <= MaxTries; attempt++)
        {
            var first = readHidden(FirstPrompt);
            if (first is null) return new RecoveryPromptResult(RecoveryPromptOutcome.NotSet, null);
            try
            {
                if (first.Length == 0) return new RecoveryPromptResult(RecoveryPromptOutcome.NotSet, null);
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
