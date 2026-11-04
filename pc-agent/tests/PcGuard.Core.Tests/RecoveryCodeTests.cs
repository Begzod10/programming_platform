using PcGuard.Core;

namespace PcGuard.Core.Tests;

// All codes and hashes in this file are intentionally fake test vectors.
public class RecoveryCodeValidationTests
{
    [Theory]
    [InlineData("Lab-PC-07 recovery")]
    [InlineData("abcdefghi1")]               // exactly 10
    [InlineData("a b c d e f")]              // inner spaces are allowed
    [InlineData("!~#$%^&*()_+=-")]           // ASCII punctuation
    [InlineData("1234567891")]               // ten digits, not on the deny list
    public void GoodCodesPass(string code)
    {
        Assert.Null(RecoveryCode.Validate(code));
        Assert.Null(RecoveryCode.Validate(code.AsSpan()));
    }

    [Fact]
    public void LengthLimitsAreTenAndHundredTwentyEight()
    {
        Assert.Contains("at least 10", RecoveryCode.Validate("abcdefgh1"));
        Assert.Null(RecoveryCode.Validate(new string('a', 64) + new string('b', 63) + "c"));
        Assert.Contains("at most 128", RecoveryCode.Validate(new string('a', 64) + new string('b', 64) + "c"));
        Assert.Contains("at least 10", RecoveryCode.Validate(""));
        Assert.Contains("at least 10", RecoveryCode.Validate((string?)null));
    }

    [Theory]
    [InlineData("abcdefghij\u00e9")]   // non-ASCII letter
    [InlineData("abcdefghij\t")]        // control character
    [InlineData("abcdef\nghij")]
    [InlineData("abcdefghij\u007f")]   // DEL
    [InlineData("\u0430bcdefghijk")]   // Cyrillic a
    [InlineData("abcdefghij\u3000k")]  // ideographic space
    public void OnlyPrintableAsciiAndSpace(string code)
        => Assert.Contains("printable ASCII", RecoveryCode.Validate(code));

    [Theory]
    [InlineData(" abcdefghij")]
    [InlineData("abcdefghij ")]
    public void NoLeadingOrTrailingSpace(string code)
        => Assert.Contains("start or end with a space", RecoveryCode.Validate(code));

    [Theory]
    [InlineData("aaaaaaaaaaaa")]
    [InlineData("ababababab")]
    public void AtLeastThreeDistinctCharacters(string code)
        => Assert.Contains("3 different", RecoveryCode.Validate(code));

    [Theory]
    [InlineData("123456")]
    [InlineData("000000")]
    public void SixDigitsAreRefusedAsTheTeacherCodeShape(string code)
        => Assert.Contains("6 digits", RecoveryCode.Validate(code));

    [Theory]
    [InlineData("0123456789")]
    [InlineData("1234567890")]
    [InlineData("password12")]
    [InlineData("PASSWORD12")]
    [InlineData("qwertyuiop")]
    [InlineData("QwertyUiop")]
    [InlineData("password123")]
    [InlineData("1q2w3e4r5t")]
    public void CommonWeakValuesAreRefused(string code)
        => Assert.Contains("too common", RecoveryCode.Validate(code));

    [Fact]
    public void ErrorMessagesNeverContainTheCode()
    {
        foreach (var code in new[] { "short1", "abcdefghij\u00e9", " abcdefghijk", "aaaaaaaaaaaa", "password12", new string('z', 140) + "xy" })
        {
            var e = RecoveryCode.Validate(code);
            Assert.NotNull(e);
            Assert.DoesNotContain(code, e);
        }
    }
}

public class RecoveryCodeHashTests
{
    private const string Code = "Test-Recovery 42";
    // independent vector: python hashlib.pbkdf2_hmac('sha256', b'Test-Recovery 42', bytes(range(16)), 310000, 32)
    private const string Vector = "pbkdf2-sha256$310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=";
    private static readonly byte[] Salt = Enumerable.Range(0, 16).Select(i => (byte)i).ToArray();

    [Fact]
    public void HashWithAFixedSaltMatchesAnIndependentPbkdf2Vector()
        => Assert.Equal(Vector, RecoveryCode.Hash(Code.AsSpan(), Salt, 310_000));

    [Fact]
    public void HashUsesTheDocumentedFormatAndARandomSalt()
    {
        var a = RecoveryCode.Hash(Code);
        var b = RecoveryCode.Hash(Code.AsSpan());
        Assert.NotEqual(a, b); // fresh 16-byte salt each time
        foreach (var h in new[] { a, b })
        {
            var parts = h.Split('$');
            Assert.Equal(4, parts.Length);
            Assert.Equal("pbkdf2-sha256", parts[0]);
            Assert.True(int.Parse(parts[1]) >= 310_000);
            Assert.Equal(16, Convert.FromBase64String(parts[2]).Length);
            Assert.Equal(32, Convert.FromBase64String(parts[3]).Length);
            Assert.DoesNotContain(Code, h);
            Assert.True(RecoveryCode.IsWellFormedStored(h));
            Assert.True(RecoveryCode.Verify(Code, h));
        }
        Assert.Equal(RecoveryCode.Iterations, int.Parse(a.Split('$')[1]));
    }

    [Fact]
    public void HashRefusesAnInvalidCodeOrBadParametersWithoutEchoingTheCode()
    {
        var e = Assert.Throws<ArgumentException>(() => RecoveryCode.Hash("weak12"));
        Assert.DoesNotContain("weak12", e.Message);
        Assert.Throws<ArgumentException>(() => RecoveryCode.Hash(Code.AsSpan(), new byte[15], 310_000));
        Assert.Throws<ArgumentException>(() => RecoveryCode.Hash(Code.AsSpan(), Salt, 309_999));
        Assert.Throws<ArgumentException>(() => RecoveryCode.Hash(Code.AsSpan(), Salt, RecoveryCode.MaxIterations + 1));
    }

    [Fact]
    public void VerifyAcceptsOnlyTheExactCode()
    {
        Assert.True(RecoveryCode.Verify(Code, Vector));
        Assert.False(RecoveryCode.Verify("test-recovery 42", Vector)); // case matters
        Assert.False(RecoveryCode.Verify("Test-Recovery 42 ", Vector));
        Assert.False(RecoveryCode.Verify("Test-Recovery 4", Vector));
        Assert.False(RecoveryCode.Verify("", Vector));
        Assert.False(RecoveryCode.Verify(null, Vector));
        Assert.False(RecoveryCode.Verify(new string('a', 129), Vector));
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("garbage")]
    [InlineData("pbkdf2-sha256$310000$AAECAwQFBgcICQoLDA0ODw==")]                                                            // 3 parts
    [InlineData("pbkdf2-sha1$310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=")]                  // scheme
    [InlineData("PBKDF2-SHA256$310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=")]                // scheme case
    [InlineData("pbkdf2-sha256$1000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=")]                  // too few iterations
    [InlineData("pbkdf2-sha256$99999999$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=")]              // too many
    [InlineData("pbkdf2-sha256$0310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=")]               // leading zero
    [InlineData("pbkdf2-sha256$+310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=")]
    [InlineData("pbkdf2-sha256$ 310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=")]
    [InlineData("pbkdf2-sha256$310000$AAECAwQFBgcICQoLDA0O$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=")]                    // salt 14 bytes
    [InlineData("pbkdf2-sha256$310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ss===")]                 // bad b64
    [InlineData("pbkdf2-sha256$310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFZ=")]                // non-canonical b64
    [InlineData("pbkdf2-sha256$310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=\n")]              // trailing newline
    [InlineData(" pbkdf2-sha256$310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=")]
    [InlineData("pbkdf2-sha256$310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=$x")]
    [InlineData("pbkdf2-sha256$310000$AAECAwQFBgcICQoLDA0ODw==$ZHV4ZTVNcEhKenJLQUpJT3UzMDBtc1U4dEwxazVnMWFMRFlEYVkwc3NGWT0=")] // hash 44 bytes
    public void MalformedStoredValuesAreRejectedAndNeverThrow(string? stored)
    {
        Assert.False(RecoveryCode.IsWellFormedStored(stored));
        Assert.False(RecoveryCode.Verify(Code, stored));
    }

    [Fact]
    public void WrongHashOfTheRightShapeIsRejected()
    {
        var tampered = Vector[..^2] + "A="; // last hash byte changed, still canonical base64
        Assert.True(RecoveryCode.IsWellFormedStored(tampered));
        Assert.False(RecoveryCode.Verify(Code, tampered));
    }

    [Fact]
    public void StoredFormIsShortEnoughForTheFileLimit()
        => Assert.True(Vector.Length <= RecoveryCode.MaxStoredLength);
}

public class RecoveryGateTests
{
    private static readonly DateTimeOffset T0 = new(2026, 11, 4, 10, 0, 0, TimeSpan.Zero);

    [Fact]
    public void NotConfiguredIsAnsweredFirstAndNotCounted()
    {
        var gate = new RecoveryGate(new AdminAttemptLimiter());
        for (var i = 0; i < 10; i++)
        {
            var r = gate.Precheck(T0.AddSeconds(i * 0.1), configured: false);
            Assert.NotNull(r);
            Assert.False(r!.Ok);
            Assert.Equal(RecoveryErrors.NotConfigured, r.Error);
        }
        Assert.Equal(0, gate.ConsecutiveFailures);
        Assert.Null(gate.Precheck(T0, configured: true));
    }

    [Fact]
    public void SuccessIsOkAndResetsTheCounter()
    {
        var gate = new RecoveryGate(new AdminAttemptLimiter());
        Assert.Equal(AdminErrors.InvalidCode, gate.Complete(T0, verified: false).Error);
        Assert.Equal(1, gate.ConsecutiveFailures);
        Assert.Null(gate.Precheck(T0.AddSeconds(2), true));
        var ok = gate.Complete(T0.AddSeconds(2), verified: true);
        Assert.True(ok.Ok);
        Assert.Null(ok.Error);
        Assert.Equal(0, gate.ConsecutiveFailures);
    }

    [Fact]
    public void OneSecondSpacingBetweenFailures()
    {
        var gate = new RecoveryGate(new AdminAttemptLimiter());
        gate.Complete(T0, false);
        var wait = gate.Precheck(T0.AddMilliseconds(400), true);
        Assert.NotNull(wait);
        Assert.Equal(AdminErrors.LockedOut, wait!.Error);
        Assert.Equal(1, wait.RetrySeconds);
        Assert.Equal(1, gate.ConsecutiveFailures); // spacing refusal is not a failure
        Assert.Null(gate.Precheck(T0.AddSeconds(1), true));
    }

    [Fact]
    public void FiveFailuresLockOutForTenMinutesEvenForTheRightCode()
    {
        var gate = new RecoveryGate(new AdminAttemptLimiter());
        var t = T0;
        for (var i = 1; i <= 4; i++)
        {
            Assert.Null(gate.Precheck(t, true));
            Assert.Equal(AdminErrors.InvalidCode, gate.Complete(t, false).Error);
            t = t.AddSeconds(2);
        }
        Assert.Null(gate.Precheck(t, true));
        var fifth = gate.Complete(t, false);
        Assert.Equal(AdminErrors.LockedOut, fifth.Error);
        Assert.Equal(600, fifth.RetrySeconds);
        Assert.Equal(5, gate.ConsecutiveFailures);

        var during = gate.Precheck(t.AddMinutes(9), true);
        Assert.Equal(AdminErrors.LockedOut, during!.Error);
        Assert.Equal(60, during.RetrySeconds);

        Assert.Null(gate.Precheck(t.AddMinutes(10), true)); // over: counting starts again
        Assert.True(gate.Complete(t.AddMinutes(10), true).Ok);
    }
}

public class RecoveryAuditTests
{
    [Fact]
    public void TextsAreFixedAndCarryNoCode()
    {
        Assert.Equal("Recovery code accepted: PC Guard stopped and disabled on this PC", RecoveryAudit.Accepted());
        Assert.Equal("Recovery code rejected (3 of 5 consecutive failures)", RecoveryAudit.Rejected(3));
        Assert.Equal("Recovery code attempts locked out for 10 minutes after 5 consecutive failures", RecoveryAudit.LockedOut());
        Assert.Equal("Recovery code attempt refused: locked out for another 42 s", RecoveryAudit.RefusedLockedOut(42));
        Assert.Equal("Recovery code attempt refused: no recovery code is configured on this PC", RecoveryAudit.NotConfigured());
        Assert.Contains("error 5", RecoveryAudit.DisableFailed(5));
        Assert.Contains("start again after a reboot", RecoveryAudit.DisableFailed(5));
    }
}

public class RecoveryPipeMessageTests
{
    private static T RoundTrip<T>(T msg) where T : PipeMessage
    {
        var line = PipeMessage.Serialize(msg);
        Assert.DoesNotContain('\n', line);
        return Assert.IsType<T>(PipeMessage.Parse(line));
    }

    [Fact]
    public void ReleaseRoundTripsWithExactWireFormat()
    {
        Assert.Equal("{\"t\":\"recovery_release\",\"id\":3,\"code\":\"fake code 1\"}",
            PipeMessage.Serialize(new RecoveryReleaseMessage(3, "fake code 1")));
        var m = RoundTrip(new RecoveryReleaseMessage(9, "a \"quoted\" one\\"));
        Assert.Equal(9, m.Id);
        Assert.Equal("a \"quoted\" one\\", m.Code);
    }

    [Fact]
    public void ReleaseToStringRedactsTheCode()
    {
        var m = new RecoveryReleaseMessage(5, "fake-secret-77");
        Assert.DoesNotContain("fake-secret-77", m.ToString());
        Assert.Contains("***", m.ToString());
        Assert.Contains("Id = 5", m.ToString());
        Assert.DoesNotContain("fake-secret-77", new Wrapper(m).ToString());
    }

    private sealed record Wrapper(PipeMessage Inner);

    [Fact]
    public void ResultRoundTripsWithItsId()
    {
        Assert.Equal("{\"t\":\"recovery_result\",\"id\":4,\"ok\":false,\"error\":\"locked_out\",\"retry_seconds\":600}",
            PipeMessage.Serialize(new RecoveryResultMessage(false, AdminErrors.LockedOut, 600) { Id = 4 }));
        var ok = RoundTrip(new RecoveryResultMessage(true, null, 0) { Id = 8 });
        Assert.True(ok.Ok);
        Assert.Null(ok.Error);
        Assert.Equal(8, ok.Id);
        var nc = RoundTrip(new RecoveryResultMessage(false, RecoveryErrors.NotConfigured, 0) { Id = 2 });
        Assert.Equal("not_configured", nc.Error);
        var neg = Assert.IsType<RecoveryResultMessage>(PipeMessage.Parse("{\"t\":\"recovery_result\",\"id\":1,\"ok\":false,\"error\":\"x\",\"retry_seconds\":-5}"));
        Assert.Equal(0, neg.RetrySeconds);
    }

    [Fact]
    public void ReleasedRoundTrips()
    {
        Assert.Equal("{\"t\":\"released\"}", PipeMessage.Serialize(new ReleasedMessage()));
        RoundTrip(new ReleasedMessage());
    }

    [Theory]
    [InlineData("{\"t\":\"recovery_release\"}")]
    [InlineData("{\"t\":\"recovery_release\",\"id\":1}")]
    [InlineData("{\"t\":\"recovery_release\",\"code\":\"abcdefghijk\"}")]
    [InlineData("{\"t\":\"recovery_release\",\"id\":1,\"code\":5}")]
    [InlineData("{\"t\":\"recovery_release\",\"id\":\"1\",\"code\":\"abcdefghijk\"}")]
    [InlineData("{\"t\":\"recovery_result\",\"ok\":true}")]
    [InlineData("{\"t\":\"recovery_result\",\"id\":1}")]
    public void MalformedFramesAreRejected(string line)
        => Assert.Throws<FormatException>(() => PipeMessage.Parse(line));
}

public class RecoveryUiStringsTests
{
    [Fact]
    public void LinkTextsInBothLanguages()
    {
        Assert.Equal("Tiklash kodi", UiStrings.RecoveryLink(UiLang.Uz));
        Assert.Equal("Код восстановления", UiStrings.RecoveryLink(UiLang.Ru));
        foreach (var l in new[] { UiLang.Uz, UiLang.Ru })
        {
            Assert.False(string.IsNullOrWhiteSpace(UiStrings.RecoveryTitle(l)));
            Assert.False(string.IsNullOrWhiteSpace(UiStrings.RecoveryCodeLabel(l)));
            Assert.False(string.IsNullOrWhiteSpace(UiStrings.RecoveryHint(l)));
        }
        Assert.NotEqual(UiStrings.RecoveryTitle(UiLang.Uz), UiStrings.RecoveryTitle(UiLang.Ru));
    }

    [Fact]
    public void ErrorsMapEveryCode()
    {
        foreach (var l in new[] { UiLang.Uz, UiLang.Ru })
        {
            var invalid = UiStrings.RecoveryError(l, AdminErrors.InvalidCode, 0);
            var none = UiStrings.RecoveryError(l, RecoveryErrors.NotConfigured, 0);
            var locked = UiStrings.RecoveryError(l, AdminErrors.LockedOut, 37);
            var generic = UiStrings.RecoveryError(l, AdminErrors.Error, 0);
            Assert.Contains("37", locked);
            Assert.Equal(generic, UiStrings.RecoveryError(l, null, 0));
            Assert.Equal(generic, UiStrings.RecoveryError(l, "whatever", 0));
            Assert.Equal(4, new[] { invalid, none, locked, generic }.Distinct().Count());
        }
        Assert.Equal("Bu kompyuterda tiklash kodi o'rnatilmagan", UiStrings.RecoveryError(UiLang.Uz, RecoveryErrors.NotConfigured, 0));
        Assert.Equal("На этом компьютере код восстановления не задан", UiStrings.RecoveryError(UiLang.Ru, RecoveryErrors.NotConfigured, 0));
    }
}

public class HiddenLineEditorTests
{
    [Fact]
    public void TypesBackspacesAndFinishesOnEnter()
    {
        using var ed = new HiddenLineEditor(RecoveryCode.MaxLength + 1);
        foreach (var c in "abcx") Assert.False(ed.Process(ConsoleKey.A, c));
        Assert.False(ed.Process(ConsoleKey.Backspace, '\b'));
        Assert.False(ed.Process(ConsoleKey.LeftArrow, '\0')); // no char: ignored
        Assert.False(ed.Process(ConsoleKey.Tab, '\t'));       // control char: ignored
        Assert.False(ed.Process(ConsoleKey.Spacebar, ' '));
        Assert.True(ed.Process(ConsoleKey.Enter, '\r'));
        Assert.Equal("abc ", new string(ed.Text));
        var copy = ed.TakeCopy();
        Assert.Equal("abc ", new string(copy));
        Assert.Equal(0, ed.Length); // taken: the editor's buffer is wiped
    }

    [Fact]
    public void BackspaceOnEmptyAndEscapeClear()
    {
        using var ed = new HiddenLineEditor(20);
        ed.Process(ConsoleKey.Backspace, '\b');
        Assert.Equal(0, ed.Length);
        foreach (var c in "secret") ed.Process(ConsoleKey.A, c);
        ed.Process(ConsoleKey.Escape, '\u001b');
        Assert.Equal(0, ed.Length);
    }

    [Fact]
    public void ExtraCharactersBeyondCapacityAreDropped()
    {
        using var ed = new HiddenLineEditor(5);
        foreach (var c in "abcdefgh") ed.Process(ConsoleKey.A, c);
        Assert.Equal(5, ed.Length);
        Assert.Equal("abcde", new string(ed.Text));
    }

    [Fact]
    public void ClearZeroesTheBuffer()
    {
        var ed = new HiddenLineEditor(8);
        foreach (var c in "abc") ed.Process(ConsoleKey.A, c);
        var raw = ed.RawBufferForTests;
        ed.Dispose();
        Assert.All(raw, c => Assert.Equal('\0', c));
        Assert.Equal(0, ed.Length);
    }
}

public class RecoveryCodePromptTests
{
    private sealed class Script
    {
        private readonly Queue<string?> _answers;
        public List<char[]> Given { get; } = new();
        public List<string> Prompts { get; } = new();
        public List<string> Errors { get; } = new();
        public Script(params string?[] answers) => _answers = new Queue<string?>(answers);

        public char[]? Read(string prompt)
        {
            Prompts.Add(prompt);
            var a = _answers.Dequeue();
            if (a is null) return null;
            var arr = a.ToCharArray();
            Given.Add(arr);
            return arr;
        }

        public void AssertAllWiped() => Assert.All(Given, a => Assert.All(a, c => Assert.Equal('\0', c)));
    }

    private static string FakeHash(char[] code) => "HASH(" + code.Length + ")";

    [Fact]
    public void EmptyFirstAnswerMeansNone()
    {
        var s = new Script("");
        var r = RecoveryCodePrompt.Run(s.Read, s.Errors.Add, FakeHash);
        Assert.Equal(RecoveryPromptOutcome.NotSet, r.Outcome);
        Assert.Null(r.Hash);
        Assert.Single(s.Prompts);
        Assert.Equal(RecoveryCodePrompt.FirstPrompt, s.Prompts[0]);
        Assert.Equal("Recovery code for this PC (at least 10 characters; typed hidden; empty = none): ", RecoveryCodePrompt.FirstPrompt);
    }

    [Fact]
    public void NoConsoleMeansNone()
    {
        var s = new Script(new string?[] { null });
        Assert.Equal(RecoveryPromptOutcome.NotSet, RecoveryCodePrompt.Run(s.Read, s.Errors.Add, FakeHash).Outcome);
    }

    [Fact]
    public void MatchingEntriesAreHashedAndWiped()
    {
        var s = new Script("Fake-Recovery 1", "Fake-Recovery 1");
        var r = RecoveryCodePrompt.Run(s.Read, s.Errors.Add, FakeHash);
        Assert.Equal(RecoveryPromptOutcome.Set, r.Outcome);
        Assert.Equal("HASH(15)", r.Hash);
        Assert.Equal(new[] { RecoveryCodePrompt.FirstPrompt, RecoveryCodePrompt.ConfirmPrompt }, s.Prompts);
        Assert.Empty(s.Errors);
        s.AssertAllWiped();
    }

    [Fact]
    public void RealHasherProducesAVerifiableHash()
    {
        var s = new Script("Fake-Recovery 2", "Fake-Recovery 2");
        var r = RecoveryCodePrompt.Run(s.Read, s.Errors.Add);
        Assert.Equal(RecoveryPromptOutcome.Set, r.Outcome);
        Assert.True(RecoveryCode.Verify("Fake-Recovery 2", r.Hash));
        s.AssertAllWiped();
    }

    [Fact]
    public void MismatchAsksAgain()
    {
        var s = new Script("Fake-Recovery 1", "Fake-Recovery 2", "Fake-Recovery 3", "Fake-Recovery 3");
        var r = RecoveryCodePrompt.Run(s.Read, s.Errors.Add, FakeHash);
        Assert.Equal(RecoveryPromptOutcome.Set, r.Outcome);
        Assert.Single(s.Errors);
        Assert.Contains("do not match", s.Errors[0]);
        s.AssertAllWiped();
    }

    [Fact]
    public void WeakOrShortCodesAreRefusedWithTheReason()
    {
        var s = new Script("short", "password12", "Fake-Recovery 4", "Fake-Recovery 4");
        var r = RecoveryCodePrompt.Run(s.Read, s.Errors.Add, FakeHash);
        Assert.Equal(RecoveryPromptOutcome.Set, r.Outcome);
        Assert.Equal(2, s.Errors.Count);
        Assert.Contains("at least 10", s.Errors[0]);
        Assert.Contains("too common", s.Errors[1]);
        s.AssertAllWiped();
    }

    [Fact]
    public void ThreeFailedTriesAbort()
    {
        var s = new Script("Fake-Recovery 1", "Fake-Recovery 9", "short", "Fake-Recovery 5", "Fake-recovery 5");
        var r = RecoveryCodePrompt.Run(s.Read, s.Errors.Add, FakeHash);
        Assert.Equal(RecoveryPromptOutcome.Aborted, r.Outcome);
        Assert.Null(r.Hash);
        Assert.Contains("Nothing was changed", s.Errors[^1]);
        Assert.All(s.Errors, e => Assert.DoesNotContain("Fake-Recovery", e));
        s.AssertAllWiped();
    }

    [Fact]
    public void NoConsoleAtTheConfirmationAborts()
    {
        var s = new Script("Fake-Recovery 1", null);
        Assert.Equal(RecoveryPromptOutcome.Aborted, RecoveryCodePrompt.Run(s.Read, s.Errors.Add, FakeHash).Outcome);
        s.AssertAllWiped();
    }
}

public class RecoverySetupArgsTests
{
    [Fact]
    public void NoRecoveryCodeFlag()
    {
        var a = SetupArgs.Parse(new[] { "--install", "--backend-url", "https://x.uz/api/v1", "--no-recovery-code", "--no-pause" });
        Assert.Null(a.Error);
        Assert.True(a.NoRecoveryCode);
        Assert.False(SetupArgs.Parse(new[] { "--install" }).NoRecoveryCode);
        Assert.True(SetupArgs.Parse(new[] { "--install", "--NO-RECOVERY-CODE" }).NoRecoveryCode);
        Assert.Equal("--no-recovery-code can only be used together with --install.", SetupArgs.Parse(new[] { "--no-recovery-code" }).Error);
        Assert.Equal("--no-recovery-code can only be used together with --install.", SetupArgs.Parse(new[] { "--uninstall", "--no-recovery-code" }).Error);
    }

    [Theory]
    [InlineData("--recovery-code")]
    [InlineData("--recovery-code=Fake-Secret-123")]
    [InlineData("--RECOVERY-CODE")]
    [InlineData("--recovery-code-hash")]
    public void TheCodeIsNeverAcceptedOnTheCommandLine(string flag)
    {
        var a = SetupArgs.Parse(new[] { "--install", flag, "Fake-Secret-456" });
        Assert.NotNull(a.Error);
        Assert.Contains("never accepted on the command line", a.Error);
        Assert.DoesNotContain("Fake-Secret", a.Error);
    }
}

public class RecoveryPowerShellCommandTests
{
    private const string Vector = "pbkdf2-sha256$310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=";

    [Fact]
    public void HashIsPassedAsOneArgument()
    {
        var c = PowerShellCommand.BuildInstall(@"C:\t\install.ps1", "https://x.uz/api/v1", @"C:\P\dist", @"C:\Windows",
            new[] { "anydesk.exe" }, Vector);
        Assert.Equal(
            new[]
            {
                "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", @"C:\t\install.ps1",
                "-BackendBaseUrl", "https://x.uz/api/v1", "-DistDir", @"C:\P\dist",
                "-ExtraAllowedApps", "anydesk.exe", "-RecoveryCodeHash", Vector,
            },
            c.Arguments);
    }

    [Fact]
    public void OmittedWhenNull()
    {
        var c = PowerShellCommand.BuildInstall(@"C:\t\install.ps1", "https://x.uz/api/v1", @"C:\P\dist", @"C:\Windows", null, null);
        Assert.DoesNotContain("-RecoveryCodeHash", c.Arguments);
    }

    [Theory]
    [InlineData("")]
    [InlineData("Fake-Plain-Code-1")]
    [InlineData("pbkdf2-sha256$1$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=")]
    public void ANonHashIsRefusedWithoutEchoingIt(string value)
    {
        var e = Assert.Throws<ArgumentException>(() =>
            PowerShellCommand.BuildInstall(@"C:\t\install.ps1", "https://x.uz/api/v1", @"C:\P\dist", @"C:\Windows", null, value));
        if (value.Length > 0) Assert.DoesNotContain(value, e.Message);
    }
}
