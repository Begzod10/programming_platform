using System.Text;
using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class BoundedLineReaderTests
{
    private static async Task<List<string>> ReadAll(byte[] data, int max, int chunk = 4096)
    {
        var r = new BoundedLineReader(new MemoryStream(data), max, chunk);
        var lines = new List<string>();
        while (await r.ReadLineAsync(CancellationToken.None) is { } l) lines.Add(l);
        return lines;
    }

    private static byte[] B(string s) => Encoding.UTF8.GetBytes(s);

    [Fact]
    public async Task SplitsOnNewlineAndStripsCr()
        => Assert.Equal(new[] { "a", "bc", "", "d" }, await ReadAll(B("a\nbc\r\n\nd\n"), 100));

    [Fact]
    public async Task ReturnsTrailingPartialLineAtEof()
        => Assert.Equal(new[] { "a", "tail" }, await ReadAll(B("a\ntail"), 100));

    [Fact]
    public async Task EmptyStreamReturnsNull()
        => Assert.Empty(await ReadAll(Array.Empty<byte>(), 100));

    [Fact]
    public async Task OversizedLineIsSkippedAndReadingContinues()
    {
        var data = B("ok1\n" + new string('x', 50) + "\nok2\n" + new string('y', 11));
        Assert.Equal(new[] { "ok1", "ok2" }, await ReadAll(data, 10, chunk: 3));
    }

    [Fact]
    public async Task LineExactlyAtLimitIsKept()
        => Assert.Equal(new[] { "0123456789" }, await ReadAll(B("0123456789\n"), 10, chunk: 4));

    [Fact]
    public async Task MultiByteCharactersAcrossChunksDecode()
        => Assert.Equal(new[] { "o'quvchi ğ ş 你好", "x" }, await ReadAll(B("o'quvchi ğ ş 你好\nx\n"), 100, chunk: 1));

    [Fact]
    public void DefaultLimitIsOneMiB() => Assert.Equal(1024 * 1024, BoundedLineReader.DefaultMaxLineBytes);
}
