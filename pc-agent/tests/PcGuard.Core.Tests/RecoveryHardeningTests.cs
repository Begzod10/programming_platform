using System.Text;
using PcGuard.Core;

namespace PcGuard.Core.Tests;

// All codes and hashes in this file are intentionally fake test vectors.

/// <summary>In-memory recovery.attempts for the limiter tests.</summary>
internal sealed class MemoryAttemptStore : IRecoveryAttemptStore
{
    public string? Text { get; set; }
    public RecoveryAttemptFileStatus Status { get; set; } = RecoveryAttemptFileStatus.Missing;
    public bool FailWrites { get; set; }
    public int Writes { get; private set; }
    public int Deletes { get; private set; }

    public RecoveryAttemptFileStatus Read(out string? text)
    {
        text = Status == RecoveryAttemptFileStatus.Ok ? Text : null;
        return Status;
    }

    public bool Write(string text)
    {
        if (FailWrites) return false;
        Writes++;
        Text = text;
        Status = RecoveryAttemptFileStatus.Ok;
        return true;
    }

    public bool Delete()
    {
        Deletes++;
        Text = null;
        Status = RecoveryAttemptFileStatus.Missing;
        return true;
    }
}

public class RecoveryAttemptStateTests
{
    private static readonly DateTimeOffset T0 = new(2026, 11, 4, 10, 0, 0, TimeSpan.Zero);

    [Fact]
    public void FormatAndParseRoundTrip()
    {
        var s = new RecoveryAttemptState(3, 1, T0);
        var text = s.Format();
        Assert.Equal("v1;failures=3;lockouts=1;until=" + T0.ToUnixTimeSeconds(), text);
        Assert.Equal(s, RecoveryAttemptState.Parse(text));
        Assert.Equal(new RecoveryAttemptState(0, 0, null), RecoveryAttemptState.Parse("v1;failures=0;lockouts=0;until=0"));
        Assert.Equal(new RecoveryAttemptState(2, 0, null), RecoveryAttemptState.Parse(" v1;failures=2;lockouts=0;until=0\r\n")); // surrounding whitespace
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("garbage")]
    [InlineData("v2;failures=1;lockouts=0;until=0")]
    [InlineData("v1;failures=1;lockouts=0")]
    [InlineData("v1;failures=-1;lockouts=0;until=0")]
    [InlineData("v1;failures=1;lockouts=0;until=x")]
    [InlineData("v1;lockouts=0;failures=1;until=0")]
    [InlineData("v1;failures=99;lockouts=0;until=0")]
    [InlineData("v1;failures=1;lockouts=0;until=0;x=1")]
    [InlineData("v1;failures=01;lockouts=0;until=0")]
    [InlineData("v1;failures=1;lockouts=99999;until=0")]
    [InlineData("v1;failures=1;lockouts=0;until=99999999999999")]
    public void CorruptTextIsRejectedAndNeverThrows(string? text)
        => Assert.Null(RecoveryAttemptState.Parse(text));
}

public class RecoveryAttemptLimiterTests
{
    private static readonly DateTimeOffset T0 = new(2026, 11, 4, 10, 0, 0, TimeSpan.Zero);

    private static DateTimeOffset FailFive(RecoveryAttemptLimiter l, DateTimeOffset t)
    {
        for (var i = 0; i < RecoveryAttemptLimiter.MaxFailures; i++)
        {
            Assert.Equal(AdminAttemptKind.Allowed, l.Check(t).Kind);
            Assert.True(l.BeginAttempt(t));
            t = t.AddSeconds(2);
        }
        return t;
    }

    [Fact]
    public void LockoutsEscalateTenMinutesOneHourTwentyFourHours()
    {
        Assert.Equal(TimeSpan.FromMinutes(10), RecoveryAttemptLimiter.LockoutFor(0));
        Assert.Equal(TimeSpan.FromHours(1), RecoveryAttemptLimiter.LockoutFor(1));
        Assert.Equal(TimeSpan.FromHours(24), RecoveryAttemptLimiter.LockoutFor(2));
        Assert.Equal(TimeSpan.FromHours(24), RecoveryAttemptLimiter.LockoutFor(7));

        var l = new RecoveryAttemptLimiter(new MemoryAttemptStore(), T0);
        var t = FailFive(l, T0);
        var d = l.Check(t);
        Assert.Equal(AdminAttemptKind.LockedOut, d.Kind);
        Assert.InRange(d.RetrySeconds, 590, 600);
        t = t.AddMinutes(10);

        t = FailFive(l, t);
        Assert.InRange(l.Check(t).RetrySeconds, 3590, 3600);
        Assert.Equal(TimeSpan.FromHours(1), l.CurrentLockout);
        t = t.AddHours(1);

        t = FailFive(l, t);
        Assert.InRange(l.Check(t).RetrySeconds, 86390, 86400);
        t = t.AddHours(24);

        t = FailFive(l, t);
        Assert.InRange(l.Check(t).RetrySeconds, 86390, 86400); // stays at 24 h
        Assert.Equal(4, l.Lockouts);
    }

    [Fact]
    public void EveryAttemptIsPersistedBeforeVerification()
    {
        var store = new MemoryAttemptStore();
        var l = new RecoveryAttemptLimiter(store, T0);
        Assert.True(l.BeginAttempt(T0));
        // the attempt counts even if the PC loses power now (no Complete ever runs)
        Assert.Equal("v1;failures=1;lockouts=0;until=0", store.Text);

        var restarted = new RecoveryAttemptLimiter(store, T0.AddMinutes(1));
        Assert.Equal(1, restarted.ConsecutiveFailures);
        Assert.Null(restarted.LoadProblem);
    }

    [Fact]
    public void ARebootDoesNotResetTheCounterOrTheLockout()
    {
        var store = new MemoryAttemptStore();
        var l = new RecoveryAttemptLimiter(store, T0);
        var t = FailFive(l, T0);

        var afterReboot = new RecoveryAttemptLimiter(store, t.AddMinutes(2));
        var d = afterReboot.Check(t.AddMinutes(2));
        Assert.Equal(AdminAttemptKind.LockedOut, d.Kind);
        Assert.InRange(d.RetrySeconds, 400, 600);

        // after the lockout: counting starts again, but the next lockout is the escalated one
        var later = t.AddMinutes(11);
        var again = new RecoveryAttemptLimiter(store, later);
        Assert.Equal(AdminAttemptKind.Allowed, again.Check(later).Kind);
        Assert.Equal(0, again.ConsecutiveFailures);
        FailFive(again, later);
        Assert.Equal(TimeSpan.FromHours(1), again.CurrentLockout);
    }

    [Fact]
    public void FourFailuresThenRebootStillNeedOnlyOneMoreForTheLockout()
    {
        var store = new MemoryAttemptStore();
        var l = new RecoveryAttemptLimiter(store, T0);
        var t = T0;
        for (var i = 0; i < 4; i++) { l.BeginAttempt(t); t = t.AddSeconds(2); }

        var r = new RecoveryAttemptLimiter(store, t.AddMinutes(2));
        Assert.Equal(4, r.ConsecutiveFailures);
        Assert.True(r.BeginAttempt(t.AddMinutes(2)));
        Assert.Equal(AdminAttemptKind.LockedOut, r.Check(t.AddMinutes(2)).Kind);
    }

    [Fact]
    public void SuccessDeletesTheFileAndResetsTheEscalation()
    {
        var store = new MemoryAttemptStore();
        var l = new RecoveryAttemptLimiter(store, T0);
        var t = FailFive(l, T0).AddMinutes(10);
        Assert.True(l.BeginAttempt(t));
        Assert.True(l.RecordSuccess());
        Assert.Null(store.Text);
        Assert.Equal(1, store.Deletes);
        Assert.Equal(0, l.ConsecutiveFailures);
        Assert.Equal(0, l.Lockouts);
        FailFive(l, t.AddSeconds(5));
        Assert.Equal(TimeSpan.FromMinutes(10), l.CurrentLockout);
    }

    [Fact]
    public void AMissingFileAtStartIsAFreshStart()
    {
        var l = new RecoveryAttemptLimiter(new MemoryAttemptStore(), T0);
        Assert.Null(l.LoadProblem);
        Assert.Equal(0, l.ConsecutiveFailures);
        Assert.Equal(AdminAttemptKind.Allowed, l.Check(T0).Kind);
    }

    [Fact]
    public void AFileThatDisappearsWhileRunningNeverResetsTheLockout()
    {
        var store = new MemoryAttemptStore();
        var l = new RecoveryAttemptLimiter(store, T0);
        var t = FailFive(l, T0);
        store.Delete(); // in memory the lockout stays
        Assert.Equal(AdminAttemptKind.LockedOut, l.Check(t.AddMinutes(1)).Kind);
    }

    [Theory]
    [InlineData(RecoveryAttemptFileStatus.Untrusted, null)]
    [InlineData(RecoveryAttemptFileStatus.Ok, "garbage")]
    [InlineData(RecoveryAttemptFileStatus.Ok, "v1;failures=0;lockouts=0;until=abc")]
    public void AnUntrustedOrCorruptFileLocksOutForTwentyFourHours(RecoveryAttemptFileStatus status, string? text)
    {
        var store = new MemoryAttemptStore { Status = status, Text = text };
        var l = new RecoveryAttemptLimiter(store, T0);
        Assert.NotNull(l.LoadProblem);
        var d = l.Check(T0);
        Assert.Equal(AdminAttemptKind.LockedOut, d.Kind);
        Assert.Equal(86400, d.RetrySeconds);
        Assert.Equal(AdminAttemptKind.LockedOut, l.Check(T0.AddHours(23)).Kind);
        Assert.Equal(AdminAttemptKind.Allowed, l.Check(T0.AddHours(24)).Kind);
        // the 24 h state was written back, so a reboot does not shorten it
        Assert.Equal(RecoveryAttemptFileStatus.Ok, store.Status);
        var r = new RecoveryAttemptLimiter(store, T0.AddHours(1));
        Assert.Null(r.LoadProblem);
        Assert.Equal(AdminAttemptKind.LockedOut, r.Check(T0.AddHours(1)).Kind);
    }

    [Fact]
    public void AClockSetBackNeverExtendsALockoutBeyondItsLength()
    {
        var store = new MemoryAttemptStore();
        var l = new RecoveryAttemptLimiter(store, T0);
        var t = FailFive(l, T0);
        var back = t.AddDays(-30);
        var d = l.Check(back);
        Assert.Equal(AdminAttemptKind.LockedOut, d.Kind);
        Assert.Equal(600, d.RetrySeconds);

        var fromFile = new RecoveryAttemptLimiter(store, t.AddDays(-30));
        Assert.Equal(600, fromFile.Check(t.AddDays(-30)).RetrySeconds);
    }

    [Fact]
    public void APersistFailureRefusesTheAttemptButStillCountsItInMemory()
    {
        var store = new MemoryAttemptStore { FailWrites = true };
        var l = new RecoveryAttemptLimiter(store, T0);
        Assert.False(l.BeginAttempt(T0));
        Assert.Equal(1, l.ConsecutiveFailures);
    }

    [Fact]
    public void SpacingIsOneSecondAndNeverCounted()
    {
        var l = new RecoveryAttemptLimiter(new MemoryAttemptStore(), T0);
        l.BeginAttempt(T0);
        var d = l.Check(T0.AddMilliseconds(300));
        Assert.Equal(AdminAttemptKind.Wait, d.Kind);
        Assert.Equal(1, d.RetrySeconds);
        Assert.Equal(1, l.ConsecutiveFailures);
        Assert.Equal(AdminAttemptKind.Allowed, l.Check(T0.AddSeconds(1)).Kind);
    }

    [Fact]
    public void BeginIsRefusedWhileLockedOut()
    {
        var l = new RecoveryAttemptLimiter(new MemoryAttemptStore(), T0);
        var t = FailFive(l, T0);
        Assert.False(l.BeginAttempt(t));
        Assert.Equal(5, l.ConsecutiveFailures);
    }
}

public class RecoveryTransferFileTests
{
    private const string Vector = "pbkdf2-sha256$310000$AAECAwQFBgcICQoLDA0ODw==$duxe5MpHJzrKAJIOu300msU8tL1k5g1aLDYDaY0ssFY=";

    [Fact]
    public void ContentIsTheExactAsciiHashWithoutBomOrNewline()
    {
        var bytes = RecoveryCode.ToTransferBytes(Vector);
        Assert.Equal(Encoding.ASCII.GetBytes(Vector), bytes);
        Assert.True(bytes.Length <= RecoveryCode.MaxStoredFileBytes);
        Assert.Equal(136, RecoveryCode.MaxStoredFileBytes);
        Assert.Equal("recovery-hash.in", RecoveryCode.TransferFileName);
    }

    [Theory]
    [InlineData("")]
    [InlineData("Fake-Plain-Code-1")]
    [InlineData(Vector + "\n")]
    public void OnlyAStoredHashIsAccepted(string value)
    {
        var e = Assert.Throws<ArgumentException>(() => RecoveryCode.ToTransferBytes(value));
        if (value.Length > 0) Assert.DoesNotContain(value.Trim(), e.Message);
    }
}

public class RecoveryPolicyDetailTests
{
    [Fact]
    public void ConstantsMatchThePolicy()
    {
        Assert.Equal(12, RecoveryCode.MinLength);
        Assert.Equal(6, RecoveryCode.MinDistinct);
        Assert.Equal(8, RecoveryCode.MinUnguessable);
    }

    [Theory]
    [InlineData("Xq7!mZ2#pL9v", true)]
    [InlineData("abc def ~!", true)]
    [InlineData("", true)]
    [InlineData("код", false)]   // Cyrillic typed on a RU layout
    [InlineData("abcé", false)]
    [InlineData("abc\t", false)]
    [InlineData("abc\u007f", false)]
    public void PrintableAsciiCheck(string text, bool ok)
        => Assert.Equal(ok, RecoveryCode.IsPrintableAscii(text));

    [Fact]
    public void AWordInsideALongRandomCodeIsFine()
        => Assert.Null(RecoveryCode.Validate("maktab-Xq7!mZ2#pL9v"));

    [Fact]
    public void ATypicalTeacherCodeWithSchoolAndYearIsRefused()
    {
        Assert.Contains("too easy to guess", RecoveryCode.Validate("Maktab-2025-Kompyuter"));
        Assert.Contains("too easy to guess", RecoveryCode.Validate("1234-qwerty-2024"));
        Assert.Contains("too easy to guess", RecoveryCode.Validate("Password!2026"));
    }
}

public class RecoveryLayoutUiStringsTests
{
    [Fact]
    public void WrongLayoutErrorExistsInBothLanguagesAndNamesEnglish()
    {
        var uz = UiStrings.RecoveryError(UiLang.Uz, RecoveryErrors.WrongLayout, 0);
        var ru = UiStrings.RecoveryError(UiLang.Ru, RecoveryErrors.WrongLayout, 0);
        Assert.NotEqual(uz, ru);
        Assert.Contains("EN", uz);
        Assert.Contains("EN", ru);
        Assert.NotEqual(UiStrings.RecoveryError(UiLang.Uz, AdminErrors.Error, 0), uz);
        Assert.NotEqual(UiStrings.RecoveryError(UiLang.Ru, AdminErrors.Error, 0), ru);
        Assert.NotEqual(UiStrings.RecoveryError(UiLang.Uz, AdminErrors.InvalidCode, 0), uz);
    }

    [Fact]
    public void DisableFailedNoticeIsBilingualAndShort()
    {
        var n = UiStrings.RecoveryDisableFailedNotice();
        Assert.Contains("PC Guard", n);
        Assert.Contains("\n", n);
        Assert.True(n.Length <= 500);
    }

    [Fact]
    public void HintNoLongerPromisesUntilReinstall()
    {
        foreach (var l in new[] { UiLang.Uz, UiLang.Ru })
            Assert.False(string.IsNullOrWhiteSpace(UiStrings.RecoveryHint(l)));
        Assert.Contains("bir marta", UiStrings.RecoveryHint(UiLang.Uz));
        Assert.Contains("один раз", UiStrings.RecoveryHint(UiLang.Ru));
    }
}

public class ShellServiceCheckTests
{
    [Fact]
    public void ServerIsVerifiedOnlyWhenItIsTheServiceProcess()
    {
        var running = new ServiceProbe(ShellServiceCheck.Running, ShellServiceCheck.AutoStart, 4242);
        Assert.Equal(PipeServerTrust.Verified, ShellServiceCheck.ClassifyServer(4242, running));
        Assert.Equal(PipeServerTrust.Mismatch, ShellServiceCheck.ClassifyServer(777, running));
        var stopped = new ServiceProbe(ShellServiceCheck.Stopped, ShellServiceCheck.AutoStart, 0);
        Assert.Equal(PipeServerTrust.Mismatch, ShellServiceCheck.ClassifyServer(777, stopped)); // squatter while the service is down
        Assert.Equal(PipeServerTrust.Mismatch, ShellServiceCheck.ClassifyServer(0, stopped));
        Assert.Equal(PipeServerTrust.Unknown, ShellServiceCheck.ClassifyServer(null, running));
        Assert.Equal(PipeServerTrust.Unknown, ShellServiceCheck.ClassifyServer(4242, null));
    }

    [Fact]
    public void ReleasedIsHonouredOnlyFromAVerifiedServer()
    {
        Assert.True(ShellServiceCheck.HonourReleased(PipeServerTrust.Verified));
        Assert.False(ShellServiceCheck.HonourReleased(PipeServerTrust.Unknown));
        Assert.False(ShellServiceCheck.HonourReleased(PipeServerTrust.Mismatch));
    }

    [Fact]
    public void ExitOnlyWhenTheServiceIsStoppedAndDisabled()
    {
        Assert.True(ShellServiceCheck.ShouldExit(new ServiceProbe(ShellServiceCheck.Stopped, ShellServiceCheck.Disabled, 0)));
        Assert.False(ShellServiceCheck.ShouldExit(new ServiceProbe(ShellServiceCheck.Stopped, ShellServiceCheck.AutoStart, 0))); // crash: SCM restarts it
        Assert.False(ShellServiceCheck.ShouldExit(new ServiceProbe(ShellServiceCheck.StopPending, ShellServiceCheck.Disabled, 12)));
        Assert.False(ShellServiceCheck.ShouldExit(new ServiceProbe(ShellServiceCheck.Running, ShellServiceCheck.Disabled, 12)));
        Assert.False(ShellServiceCheck.ShouldExit(null)); // cannot tell: keep trying
    }
}

public class RecoveryPromptNoCodeConfirmTests
{
    private sealed class Script
    {
        private readonly Queue<string?> _answers;
        private readonly Queue<bool?> _confirms;
        public List<string> Prompts { get; } = new();
        public List<string> Errors { get; } = new();
        public List<string> Confirms { get; } = new();
        public Script(string?[] answers, params bool?[] confirms)
        {
            _answers = new Queue<string?>(answers);
            _confirms = new Queue<bool?>(confirms);
        }

        public char[]? Read(string prompt)
        {
            Prompts.Add(prompt);
            return _answers.Dequeue()?.ToCharArray();
        }

        public bool? Confirm(string prompt)
        {
            Confirms.Add(prompt);
            return _confirms.Dequeue();
        }
    }

    private static string FakeHash(char[] code) => "HASH(" + code.Length + ")";

    [Fact]
    public void EmptyFirstAnswerOnTheFirstTryNeedsNoConfirmation()
    {
        var s = new Script(new[] { "" });
        var r = RecoveryCodePrompt.Run(s.Read, s.Errors.Add, FakeHash, s.Confirm);
        Assert.Equal(RecoveryPromptOutcome.NotSet, r.Outcome);
        Assert.Empty(s.Confirms);
    }

    [Fact]
    public void EmptyAnswerAfterAFailedTryAsksAndYesMeansNone()
    {
        var s = new Script(new[] { "short", "" }, true);
        var r = RecoveryCodePrompt.Run(s.Read, s.Errors.Add, FakeHash, s.Confirm);
        Assert.Equal(RecoveryPromptOutcome.NotSet, r.Outcome);
        Assert.Equal(new[] { RecoveryCodePrompt.NoCodeConfirmPrompt }, s.Confirms);
        Assert.Equal("Install without a recovery code? (y/N): ", RecoveryCodePrompt.NoCodeConfirmPrompt);
    }

    [Fact]
    public void NoMeansAskForTheCodeAgainWithoutUsingATry()
    {
        var s = new Script(new[] { "short", "", "Fake-Recovery 77", "Fake-Recovery 77" }, false);
        var r = RecoveryCodePrompt.Run(s.Read, s.Errors.Add, FakeHash, s.Confirm);
        Assert.Equal(RecoveryPromptOutcome.Set, r.Outcome);
        Assert.Equal("HASH(16)", r.Hash);
    }

    [Fact]
    public void NoAfterAMismatchThenTwoMoreFailuresStillAborts()
    {
        var s = new Script(new[] { "Fake-Recovery 77", "Fake-Recovery 78", "", "short", "short" }, false);
        var r = RecoveryCodePrompt.Run(s.Read, s.Errors.Add, FakeHash, s.Confirm);
        Assert.Equal(RecoveryPromptOutcome.Aborted, r.Outcome);
    }

    [Fact]
    public void NoConsoleAtTheConfirmationAborts()
    {
        var s = new Script(new[] { "short", "" }, new bool?[] { null });
        Assert.Equal(RecoveryPromptOutcome.Aborted, RecoveryCodePrompt.Run(s.Read, s.Errors.Add, FakeHash, s.Confirm).Outcome);
    }
}
