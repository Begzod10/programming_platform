using System.Text;
using PcGuard.Core;

namespace PcGuard.Core.Tests;

// Only obviously fake vectors are used here ("Fake-Test-Code-0001" ...); no real code anywhere.
public class DefaultRecoveryCodeDecodeTests
{
    private const string Fake = "Fake-Test-Code-0001";

    private static byte[] B(string s) => Encoding.ASCII.GetBytes(s);

    [Fact]
    public void FileNameAndLimit()
    {
        Assert.Equal("default-recovery-code.txt", DefaultRecoveryCode.FileName);
        Assert.Equal(130, DefaultRecoveryCode.MaxFileBytes);
        Assert.Equal(RecoveryCode.MaxLength + 2, DefaultRecoveryCode.MaxFileBytes);
    }

    [Theory]
    [InlineData("")]
    [InlineData("\r\n")]
    [InlineData("\n")]
    [InlineData("\r")]
    public void ExactlyOneTrailingLineEndIsStripped(string ending)
    {
        using var d = DefaultRecoveryCode.Decode(B(Fake + ending));
        Assert.Equal(DefaultCodeStatus.Loaded, d.Status);
        Assert.Equal(Fake, new string(d.Code));
    }

    [Theory]
    [InlineData("\r\n\r\n")]
    [InlineData("\n\n")]
    [InlineData("\n\r")]
    public void OnlyOneLineEndIsStripped(string ending)
    {
        using var d = DefaultRecoveryCode.Decode(B(Fake + ending));
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Null(d.Code);
    }

    [Theory]
    [InlineData(" " + Fake)]
    [InlineData(Fake + " ")]
    [InlineData(Fake + " \r\n")]
    [InlineData("\t" + Fake)]
    public void NoOtherTrimming(string content)
    {
        using var d = DefaultRecoveryCode.Decode(B(content));
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Null(d.Code);
        Assert.DoesNotContain("Fake", d.Message);
    }

    [Fact]
    public void TwoLinesAreRefused()
    {
        using var d = DefaultRecoveryCode.Decode(B(Fake + "\r\nFake-Test-Code-0002\r\n"));
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("one line", d.Message);
        Assert.DoesNotContain("Fake", d.Message);
    }

    [Fact]
    public void Utf8BomIsRefused()
    {
        var bytes = new byte[] { 0xEF, 0xBB, 0xBF }.Concat(B(Fake)).ToArray();
        using var d = DefaultRecoveryCode.Decode(bytes);
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("byte order mark", d.Message);
    }

    [Fact]
    public void Utf16IsRefused()
    {
        using var d = DefaultRecoveryCode.Decode(Encoding.Unicode.GetPreamble().Concat(Encoding.Unicode.GetBytes(Fake)).ToArray());
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("printable ASCII", d.Message);
    }

    [Fact]
    public void NonAsciiIsRefused()
    {
        using var d = DefaultRecoveryCode.Decode(Encoding.UTF8.GetBytes("Fake-Test-Кod-0001"));
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("printable ASCII", d.Message);
    }

    [Theory]
    [InlineData("")]
    [InlineData("\r\n")]
    public void EmptyFileIsRefused(string content)
    {
        using var d = DefaultRecoveryCode.Decode(B(content));
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("empty", d.Message);
    }

    [Theory]
    [InlineData("Fake-Test-1")]          // too short
    [InlineData("password1234")]         // too easy to guess
    [InlineData("aaaaaabbbbbb")]         // too few distinct
    [InlineData("123456")]               // teacher code shape
    public void ExistingValidationApplies(string code)
    {
        using var d = DefaultRecoveryCode.Decode(B(code + "\r\n"));
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Null(d.Code);
        Assert.StartsWith("default-recovery-code.txt: The recovery code", d.Message);
        Assert.Contains(RecoveryCode.Validate(code)!, d.Message);
        Assert.DoesNotContain(code, d.Message);
    }

    [Fact]
    public void MaxLengthCodeWithCrLfFits()
    {
        var code = string.Concat(Enumerable.Range(0, 128).Select(i => (char)('!' + (i * 37 % 90))));
        Assert.Null(RecoveryCode.Validate(code));
        using var d = DefaultRecoveryCode.Decode(B(code + "\r\n"));
        Assert.Equal(DefaultCodeStatus.Loaded, d.Status);
        Assert.Equal(128, d.Code!.Length);
    }

    [Fact]
    public void OversizeIsRefusedWithoutDecoding()
    {
        using var d = DefaultRecoveryCode.Decode(new byte[131]);
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("130 bytes", d.Message);
    }

    [Fact]
    public void CodeLongerThanMaxIsRefused()
    {
        using var d = DefaultRecoveryCode.Decode(B(new string('x', 64) + "Fake-Test-Code-0001-" + new string('y', 46)));
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("at most 128", d.Message);
    }

    [Fact]
    public void DisposeZeroesTheCode()
    {
        var d = DefaultRecoveryCode.Decode(B(Fake));
        var code = d.Code!;
        d.Dispose();
        Assert.All(code, c => Assert.Equal('\0', c));
        Assert.Null(d.Code);
    }

    [Fact]
    public void LoadedMessageNeverContainsTheCode()
    {
        using var d = DefaultRecoveryCode.Decode(B(Fake));
        Assert.DoesNotContain("Fake", d.Message ?? "");
    }
}

public class DefaultRecoveryCodeLoadTests
{
    private const string Fake = "Fake-Test-Code-0001";
    private static readonly IReadOnlyList<AceInfo> AdminOnly = new[]
    {
        new AceInfo("f", "S-1-5-18", true, AceRights.FullControl),
        new AceInfo("f", "S-1-5-32-544", true, AceRights.FullControl),
    };

    private sealed class Io
    {
        public byte[] Content = Encoding.ASCII.GetBytes(Fake + "\r\n");
        public IReadOnlyList<AceInfo> Aces = AdminOnly;
        public int Reads;
        public int AclReads;
        public int? AskedMax;
        public byte[]? Returned;
        public Exception? ThrowOnRead;

        public IReadOnlyList<AceInfo> ReadAces() { AclReads++; return Aces; }

        public byte[] Read(int max)
        {
            Reads++;
            AskedMax = max;
            if (ThrowOnRead is not null) throw ThrowOnRead;
            Returned = Content.Take(max).ToArray();
            return Returned;
        }
    }

    private static DefaultCodeFile File(long length = 21, bool dir = false, bool reparse = false) => new(dir, reparse, length);

    [Fact]
    public void AbsentFile()
    {
        var io = new Io();
        using var d = DefaultRecoveryCode.Load(true, null, io.ReadAces, io.Read);
        Assert.Equal(DefaultCodeStatus.Absent, d.Status);
        Assert.Null(d.Message);
        Assert.Equal(0, io.Reads);
    }

    [Fact]
    public void LoadedWhenEverythingIsFine()
    {
        var io = new Io();
        using var d = DefaultRecoveryCode.Load(true, File(), io.ReadAces, io.Read);
        Assert.Equal(DefaultCodeStatus.Loaded, d.Status);
        Assert.Equal(Fake, new string(d.Code));
        Assert.Equal(DefaultRecoveryCode.MaxFileBytes + 1, io.AskedMax);
        Assert.All(io.Returned!, b => Assert.Equal(0, b)); // the byte buffer is zeroed after decoding
    }

    [Fact]
    public void IgnoredWithoutAPassedPackageCheck()
    {
        var io = new Io();
        using var d = DefaultRecoveryCode.Load(false, File(), io.ReadAces, io.Read);
        Assert.Equal(DefaultCodeStatus.Ignored, d.Status);
        Assert.Contains("--allow-writable-package", d.Message);
        Assert.Contains("ignored", d.Message);
        Assert.Equal(0, io.Reads);
        Assert.Equal(0, io.AclReads);
    }

    [Fact]
    public void LinkIsRefusedUnread()
    {
        var io = new Io();
        using var d = DefaultRecoveryCode.Load(true, File(reparse: true), io.ReadAces, io.Read);
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("link", d.Message);
        Assert.Equal(0, io.Reads);
    }

    [Fact]
    public void DirectoryIsRefusedUnread()
    {
        var io = new Io();
        using var d = DefaultRecoveryCode.Load(true, File(dir: true), io.ReadAces, io.Read);
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("not a regular file", d.Message);
        Assert.Equal(0, io.Reads);
    }

    [Fact]
    public void OversizeIsRefusedUnread()
    {
        var io = new Io();
        using var d = DefaultRecoveryCode.Load(true, File(length: 131), io.ReadAces, io.Read);
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("130 bytes", d.Message);
        Assert.Equal(0, io.Reads);
    }

    [Fact]
    public void FileThatGrewWhileReadingIsRefused()
    {
        var io = new Io { Content = new byte[200] };
        using var d = DefaultRecoveryCode.Load(true, File(length: 20), io.ReadAces, io.Read);
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("130 bytes", d.Message);
    }

    [Theory]
    [InlineData("S-1-5-32-545", AceRights.Read)]
    [InlineData("S-1-5-11", AceRights.ReadData)]
    [InlineData("S-1-1-0", AceRights.GenericRead)]
    [InlineData("S-1-5-4", AceRights.Modify)]
    [InlineData("S-1-5-32-545", AceRights.WriteData)]
    public void StandardUsersMustNotReadOrChangeTheFile(string sid, AceRights rights)
    {
        var io = new Io { Aces = AdminOnly.Append(new AceInfo("f", sid, true, rights)).ToList() };
        using var d = DefaultRecoveryCode.Load(true, File(), io.ReadAces, io.Read);
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("standard users", d.Message);
        Assert.Equal(0, io.Reads);
    }

    [Fact]
    public void DenyEntriesAndOtherSidsAreFine()
    {
        var io = new Io { Aces = AdminOnly.Append(new AceInfo("f", "S-1-5-32-545", false, AceRights.FullControl))
            .Append(new AceInfo("f", "S-1-5-21-1-2-3-1001", true, AceRights.FullControl)).ToList() };
        using var d = DefaultRecoveryCode.Load(true, File(), io.ReadAces, io.Read);
        Assert.Equal(DefaultCodeStatus.Loaded, d.Status);
    }

    [Fact]
    public void ReadErrorsAreReportedNotThrown()
    {
        var io = new Io { ThrowOnRead = new IOException("sharing violation") };
        using var d = DefaultRecoveryCode.Load(true, File(), io.ReadAces, io.Read);
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.Contains("could not be read", d.Message);
    }

    [Fact]
    public void InvalidContentZeroesTheBytesToo()
    {
        var io = new Io { Content = Encoding.ASCII.GetBytes("password1234\r\n") };
        using var d = DefaultRecoveryCode.Load(true, File(14), io.ReadAces, io.Read);
        Assert.Equal(DefaultCodeStatus.Invalid, d.Status);
        Assert.All(io.Returned!, b => Assert.Equal(0, b));
        Assert.DoesNotContain("password1234", d.Message);
    }
}

public class DefaultRecoveryCodePromptTests
{
    private const string Fake = "Fake-Test-Code-0001";

    private sealed class Script
    {
        private readonly Queue<string?> _answers;
        public List<char[]> Given { get; } = new();
        public List<string> Prompts { get; } = new();
        public List<string> Errors { get; } = new();
        public List<string> Hashed { get; } = new();
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

        public string Hash(char[] code)
        {
            Hashed.Add(new string(code));
            return "HASH(" + code.Length + ")";
        }

        public void AssertAllWiped() => Assert.All(Given, a => Assert.All(a, c => Assert.Equal('\0', c)));
    }

    [Fact]
    public void PromptText()
    {
        Assert.Equal("A default recovery code file was found (default-recovery-code.txt). Press Enter to use it, type another code, or type - (a single dash) to install without a recovery code: ",
            RecoveryCodePrompt.DefaultPrompt);
    }

    [Fact]
    public void EnterUsesTheDefault()
    {
        var s = new Script("");
        var r = RecoveryCodePrompt.RunWithDefault(Fake.ToCharArray(), s.Read, s.Errors.Add, s.Hash);
        Assert.Equal(RecoveryPromptOutcome.Set, r.Outcome);
        Assert.Equal(RecoveryCodeSource.Default, r.Source);
        Assert.Equal("HASH(19)", r.Hash);
        Assert.Equal(new[] { Fake }, s.Hashed);
        Assert.Equal(new[] { RecoveryCodePrompt.DefaultPrompt }, s.Prompts);
        Assert.Empty(s.Errors);
    }

    [Fact]
    public void DashMeansNone()
    {
        var s = new Script("-");
        var r = RecoveryCodePrompt.RunWithDefault(Fake.ToCharArray(), s.Read, s.Errors.Add, s.Hash);
        Assert.Equal(RecoveryPromptOutcome.NotSet, r.Outcome);
        Assert.Equal(RecoveryCodeSource.None, r.Source);
        Assert.Null(r.Hash);
        Assert.Empty(s.Hashed);
        s.AssertAllWiped();
    }

    [Fact]
    public void TypedCodeIsConfirmedAndUsed()
    {
        var s = new Script("Fake-Test-Code-0002", "Fake-Test-Code-0002");
        var r = RecoveryCodePrompt.RunWithDefault(Fake.ToCharArray(), s.Read, s.Errors.Add, s.Hash);
        Assert.Equal(RecoveryPromptOutcome.Set, r.Outcome);
        Assert.Equal(RecoveryCodeSource.Typed, r.Source);
        Assert.Equal(new[] { "Fake-Test-Code-0002" }, s.Hashed);
        Assert.Equal(new[] { RecoveryCodePrompt.DefaultPrompt, RecoveryCodePrompt.ConfirmPrompt }, s.Prompts);
        s.AssertAllWiped();
    }

    [Fact]
    public void InvalidTypedCodeAsksAgainAndEnterThenUsesTheDefault()
    {
        var s = new Script("short", "");
        var r = RecoveryCodePrompt.RunWithDefault(Fake.ToCharArray(), s.Read, s.Errors.Add, s.Hash);
        Assert.Equal(RecoveryCodeSource.Default, r.Source);
        Assert.Single(s.Errors);
        Assert.Contains("at least 12", s.Errors[0]);
        Assert.Equal(new[] { RecoveryCodePrompt.DefaultPrompt, RecoveryCodePrompt.DefaultPrompt }, s.Prompts);
        s.AssertAllWiped();
    }

    [Fact]
    public void MismatchCountsAsAFailedTry()
    {
        var s = new Script("Fake-Test-Code-0002", "Fake-Test-Code-0003", "-");
        var r = RecoveryCodePrompt.RunWithDefault(Fake.ToCharArray(), s.Read, s.Errors.Add, s.Hash);
        Assert.Equal(RecoveryPromptOutcome.NotSet, r.Outcome);
        Assert.Contains("do not match", s.Errors[0]);
        s.AssertAllWiped();
    }

    [Fact]
    public void ThreeFailedTypedTriesAbort()
    {
        var s = new Script("short", "password1234", "Fake-Test-Code-0002", "Fake-Test-Code-0009");
        var r = RecoveryCodePrompt.RunWithDefault(Fake.ToCharArray(), s.Read, s.Errors.Add, s.Hash);
        Assert.Equal(RecoveryPromptOutcome.Aborted, r.Outcome);
        Assert.Contains("Nothing was changed", s.Errors[^1]);
        Assert.All(s.Errors, e => Assert.DoesNotContain("Fake", e));
        s.AssertAllWiped();
    }

    [Fact]
    public void NoConsoleMeansNone()
    {
        var s = new Script(new string?[] { null });
        var r = RecoveryCodePrompt.RunWithDefault(Fake.ToCharArray(), s.Read, s.Errors.Add, s.Hash);
        Assert.Equal(RecoveryPromptOutcome.NotSet, r.Outcome);
        Assert.Empty(s.Hashed);
    }

    [Fact]
    public void NoConsoleAtTheConfirmationAborts()
    {
        var s = new Script("Fake-Test-Code-0002", null);
        var r = RecoveryCodePrompt.RunWithDefault(Fake.ToCharArray(), s.Read, s.Errors.Add, s.Hash);
        Assert.Equal(RecoveryPromptOutcome.Aborted, r.Outcome);
        s.AssertAllWiped();
    }

    [Fact]
    public void TheDefaultBufferIsNotWipedByThePrompt()
    {
        // the caller owns it (DefaultCodeLoad.Dispose zeroes it)
        var d = Fake.ToCharArray();
        RecoveryCodePrompt.RunWithDefault(d, new Script("-").Read, _ => { }, _ => "H");
        Assert.Equal(Fake, new string(d));
    }

    [Fact]
    public void RealHasherOnTheDefault()
    {
        var s = new Script("");
        var r = RecoveryCodePrompt.RunWithDefault(Fake.ToCharArray(), s.Read, s.Errors.Add);
        Assert.True(RecoveryCode.Verify(Fake, r.Hash));
    }

    [Fact]
    public void ClassicRunReportsTypedSource()
    {
        var s = new Script("Fake-Test-Code-0002", "Fake-Test-Code-0002");
        Assert.Equal(RecoveryCodeSource.Typed, RecoveryCodePrompt.Run(s.Read, s.Errors.Add, s.Hash).Source);
        Assert.Equal(RecoveryCodeSource.None, RecoveryCodePrompt.Run(new Script("").Read, _ => { }, s.Hash).Source);
    }

    [Fact]
    public void SummaryText()
    {
        Assert.Equal("set (from default-recovery-code.txt)", RecoveryCodePrompt.SummaryText(RecoveryCodeSource.Default));
        Assert.Equal("set (typed)", RecoveryCodePrompt.SummaryText(RecoveryCodeSource.Typed));
        Assert.Equal("NOT set (no offline way out)", RecoveryCodePrompt.SummaryText(RecoveryCodeSource.None));
    }
}

public class DefaultRecoveryCodeSetupArgsTests
{
    [Fact]
    public void DefaultRecoveryCodeFlag()
    {
        var a = SetupArgs.Parse(new[] { "--install", "--backend-url", "https://x.uz/api/v1", "--default-recovery-code", "--no-pause" });
        Assert.Null(a.Error);
        Assert.True(a.DefaultRecoveryCode);
        Assert.False(a.NoRecoveryCode);
        Assert.False(SetupArgs.Parse(new[] { "--install" }).DefaultRecoveryCode);
        Assert.True(SetupArgs.Parse(new[] { "--install", "--DEFAULT-RECOVERY-CODE" }).DefaultRecoveryCode);
    }

    [Fact]
    public void NeedsInstall()
    {
        Assert.Equal("--default-recovery-code can only be used together with --install.", SetupArgs.Parse(new[] { "--default-recovery-code" }).Error);
        Assert.Equal("--default-recovery-code can only be used together with --install.", SetupArgs.Parse(new[] { "--uninstall", "--default-recovery-code" }).Error);
    }

    [Fact]
    public void ExclusiveWithNoRecoveryCode()
    {
        Assert.Equal("--default-recovery-code and --no-recovery-code cannot be combined.",
            SetupArgs.Parse(new[] { "--install", "--no-recovery-code", "--default-recovery-code" }).Error);
        Assert.Equal("--default-recovery-code and --no-recovery-code cannot be combined.",
            SetupArgs.Parse(new[] { "--install", "--default-recovery-code", "--no-recovery-code" }).Error);
    }

    [Theory]
    [InlineData("--default-recovery-code=Fake-Secret-123")]
    [InlineData("--default-recovery-code:Fake-Secret-123")]
    [InlineData("--default-recovery-codeFake-Secret-123")]
    public void AnAttachedValueIsRefusedWithoutEcho(string flag)
    {
        var a = SetupArgs.Parse(new[] { "--install", flag });
        Assert.NotNull(a.Error);
        Assert.Contains("takes no value", a.Error);
        Assert.DoesNotContain("Fake-Secret", a.Error);
    }

    [Fact]
    public void AFollowingWordIsRefusedWithoutEcho()
    {
        var a = SetupArgs.Parse(new[] { "--install", "--default-recovery-code", "Fake-Secret-456" });
        Assert.NotNull(a.Error);
        Assert.Contains("takes no value", a.Error);
        Assert.DoesNotContain("Fake-Secret", a.Error);
    }
}
