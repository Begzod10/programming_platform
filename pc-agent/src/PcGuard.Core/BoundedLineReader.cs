using System.Text;

namespace PcGuard.Core;

/// <summary>
/// Reads UTF-8 '\n'-terminated lines from a stream without ever buffering more than
/// <c>maxLineBytes</c> per line: a longer line is discarded up to its newline and reading continues.
/// A trailing '\r' is stripped. Returns null at end of stream. Not thread-safe.
/// A login line carries the student's password, so every consumed byte is zeroed from both internal
/// buffers as soon as it has been copied or decoded (the returned string is immutable and cannot be
/// scrubbed, which is unavoidable in managed code).
/// </summary>
public sealed class BoundedLineReader
{
    public const int DefaultMaxLineBytes = 1024 * 1024;

    private readonly Stream _stream;
    private readonly int _max;
    private readonly byte[] _buf;
    private int _pos;
    private int _len;
    private readonly MemoryStream _line = new();
    private bool _skipping;

    public BoundedLineReader(Stream stream, int maxLineBytes = DefaultMaxLineBytes, int bufferSize = 4096)
    {
        ArgumentNullException.ThrowIfNull(stream);
        ArgumentOutOfRangeException.ThrowIfLessThan(maxLineBytes, 1);
        ArgumentOutOfRangeException.ThrowIfLessThan(bufferSize, 1);
        _stream = stream;
        _max = maxLineBytes;
        _buf = new byte[bufferSize];
    }

    public async Task<string?> ReadLineAsync(CancellationToken ct)
    {
        while (true)
        {
            if (_pos == _len)
            {
                _len = await _stream.ReadAsync(_buf.AsMemory(0, _buf.Length), ct).ConfigureAwait(false);
                _pos = 0;
                if (_len == 0)
                {
                    var skipped = _skipping;
                    _skipping = false;
                    if (_line.Length == 0 || skipped) { _line.SetLength(0); return null; }
                    return TakeLine();
                }
            }

            var nl = Array.IndexOf(_buf, (byte)'\n', _pos, _len - _pos);
            var end = nl < 0 ? _len : nl;
            if (!_skipping)
            {
                if (_line.Length + (end - _pos) > _max)
                {
                    _skipping = true;
                    Scrub();
                }
                else
                {
                    _line.Write(_buf, _pos, end - _pos);
                }
            }
            var consumedTo = nl < 0 ? _len : nl + 1;
            Array.Clear(_buf, _pos, consumedTo - _pos); // scrub consumed bytes (may include a password)
            _pos = consumedTo;
            if (nl < 0) continue;

            if (_skipping)
            {
                _skipping = false; // oversized line dropped; carry on with the next one
                continue;
            }
            return TakeLine();
        }
    }

    private string TakeLine()
    {
        var bytes = _line.GetBuffer();
        var n = (int)_line.Length;
        if (n > 0 && bytes[n - 1] == (byte)'\r') n--;
        var s = Encoding.UTF8.GetString(bytes, 0, n);
        Scrub();
        return s;
    }

    // Zero the assembled-line buffer so a password does not linger in memory, then reset it.
    private void Scrub()
    {
        var bytes = _line.GetBuffer();
        Array.Clear(bytes, 0, (int)_line.Length);
        _line.SetLength(0);
    }
}
