using System.Globalization;
using System.Text;
using System.Text.Json;

namespace PcGuard.Core;

/// <summary>
/// Messages exchanged between the guard service and the shell over the named pipe.
/// Wire format: one JSON object per line (no embedded newlines), property <c>t</c> selects the
/// kind, lower_snake keys. Unknown kinds, malformed JSON and missing/wrong-typed required fields
/// raise <see cref="FormatException"/>; unknown extra properties are ignored.
/// </summary>
public abstract record PipeMessage(string T)
{
    /// <summary>Upper bound for each of <c>windowed</c> and <c>browsers</c> in a snapshot.</summary>
    public const int MaxSnapshotEntries = 2000;

    public static string Serialize(PipeMessage message)
    {
        ArgumentNullException.ThrowIfNull(message);
        using var buffer = new MemoryStream();
        using (var w = new Utf8JsonWriter(buffer)) // not indented => single line; strings escape \n
        {
            w.WriteStartObject();
            w.WriteString("t", message.T);
            switch (message)
            {
                case LoginMessage m:
                    w.WriteString("username", m.Username);
                    w.WriteString("password", m.Password);
                    break;
                case LogoutMessage:
                case AliveMessage:
                    break;
                case SnapshotMessage m:
                    WriteSnapshot(w, m.Snapshot);
                    break;
                case LoginResultMessage m:
                    w.WriteBoolean("ok", m.Ok);
                    WriteNullableString(w, "error", m.Error);
                    break;
                case StateMessage m:
                    w.WriteBoolean("locked", m.Locked);
                    w.WriteString("reason", m.Reason);
                    w.WriteNumber("remaining", m.Remaining);
                    WriteNullableString(w, "student", m.Student);
                    break;
                case TextMessage m:
                    w.WriteString("text", m.Text);
                    break;
                case CloseWindowMessage m:
                    w.WriteNumber("hwnd", m.Hwnd);
                    break;
                case AdminUnlockMessage m:
                    w.WriteString("username", m.Username);
                    w.WriteString("password", m.Password);
                    w.WriteNumber("minutes", m.Minutes);
                    break;
                case AdminEndMessage:
                    break;
                case AdminResultMessage m:
                    w.WriteBoolean("ok", m.Ok);
                    WriteNullableString(w, "error", m.Error);
                    w.WriteNumber("retry_seconds", m.RetrySeconds);
                    break;
                case MaintenanceMessage m:
                    w.WriteBoolean("active", m.Active);
                    WriteNullableString(w, "until_utc", m.Active && m.UntilUtc is { } u
                        ? u.UtcDateTime.ToString("O", CultureInfo.InvariantCulture)
                        : null);
                    break;
                default:
                    throw new FormatException($"Unknown pipe message type {message.GetType().Name}");
            }
            w.WriteEndObject();
        }
        return Encoding.UTF8.GetString(buffer.ToArray());
    }

    public static PipeMessage Parse(string line)
    {
        if (string.IsNullOrWhiteSpace(line)) throw new FormatException("Empty pipe message");
        JsonDocument doc;
        try { doc = JsonDocument.Parse(line); }
        catch (JsonException e) { throw new FormatException("Invalid pipe message JSON", e); }

        using (doc)
        {
            var r = doc.RootElement;
            if (r.ValueKind != JsonValueKind.Object) throw new FormatException("Pipe message must be a JSON object");
            var kind = OptString(r, "t");
            return kind switch
            {
                "login" => new LoginMessage(ReqString(r, "username"), ReqString(r, "password")),
                "logout" => new LogoutMessage(),
                "alive" => new AliveMessage(),
                "snapshot" => new SnapshotMessage(ParseSnapshot(r)),
                "login_result" => new LoginResultMessage(ReqBool(r, "ok"), OptString(r, "error")),
                "state" => new StateMessage(
                    ReqBool(r, "locked"),
                    OptString(r, "reason") ?? "unknown",
                    r.TryGetProperty("remaining", out var rem) && rem.ValueKind == JsonValueKind.Number && rem.TryGetInt32(out var n) ? n : 0,
                    OptString(r, "student")),
                "message" => new TextMessage(ReqString(r, "text")),
                "close_window" => new CloseWindowMessage(
                    r.TryGetProperty("hwnd", out var h) && h.ValueKind == JsonValueKind.Number && h.TryGetInt64(out var hv)
                        ? hv
                        : throw new FormatException("'hwnd' missing or not an integer")),
                // minutes: anything but a 32-bit integer reads as 0, which the service rejects with
                // invalid_duration (only 15, 60 and 240 are ever accepted)
                "admin_unlock" => new AdminUnlockMessage(ReqString(r, "username"), ReqString(r, "password"),
                    TryInt(r, "minutes", out var minutes) ? minutes : 0),
                "admin_end" => new AdminEndMessage(),
                "admin_result" => new AdminResultMessage(ReqBool(r, "ok"), OptString(r, "error"),
                    TryInt(r, "retry_seconds", out var retry) ? Math.Max(0, retry) : 0),
                "maintenance" => ParseMaintenance(r),
                _ => throw new FormatException("Unknown pipe message kind"),
            };
        }
    }

    // ISO-8601 with an explicit offset or Z (what Serialize writes is the "O" round-trip form)
    private static readonly string[] IsoFormats = { "yyyy-MM-dd'T'HH:mm:ssK", "yyyy-MM-dd'T'HH:mm:ss.FFFFFFFK" };

    private static MaintenanceMessage ParseMaintenance(JsonElement r)
    {
        if (!ReqBool(r, "active")) return new MaintenanceMessage(false, null);
        var raw = OptString(r, "until_utc") ?? throw new FormatException("'until_utc' missing for active maintenance");
        if (!DateTimeOffset.TryParseExact(raw, IsoFormats, CultureInfo.InvariantCulture, DateTimeStyles.AdjustToUniversal, out var until))
            throw new FormatException("'until_utc' is not an ISO-8601 time");
        return new MaintenanceMessage(true, until.ToUniversalTime());
    }

    private static void WriteSnapshot(Utf8JsonWriter w, Snapshot s)
    {
        if (s.Windowed.Count > MaxSnapshotEntries || s.Browsers.Count > MaxSnapshotEntries)
            throw new FormatException("Snapshot too large");
        w.WriteStartArray("windowed");
        foreach (var p in s.Windowed)
        {
            w.WriteStartObject();
            w.WriteNumber("pid", p.Pid);
            w.WriteString("exe", p.Exe);
            w.WriteEndObject();
        }
        w.WriteEndArray();
        WriteNullableString(w, "foreground", s.Foreground);
        w.WriteStartArray("browsers");
        foreach (var b in s.Browsers)
        {
            w.WriteStartObject();
            w.WriteNumber("hwnd", b.Hwnd);
            w.WriteNumber("pid", b.Pid);
            WriteNullableString(w, "host", b.Host);
            w.WriteBoolean("readable", b.Readable);
            w.WriteEndObject();
        }
        w.WriteEndArray();
    }

    private static Snapshot ParseSnapshot(JsonElement r)
    {
        var windowed = new List<WindowedProc>();
        foreach (var e in Entries(r, "windowed"))
        {
            if (e.ValueKind != JsonValueKind.Object) continue;
            var exe = OptString(e, "exe");
            if (TryInt(e, "pid", out var pid) && !string.IsNullOrWhiteSpace(exe))
                windowed.Add(new WindowedProc(pid, exe));
        }

        var browsers = new List<BrowserWindow>();
        foreach (var e in Entries(r, "browsers"))
        {
            if (e.ValueKind != JsonValueKind.Object) continue;
            if (e.TryGetProperty("hwnd", out var h) && h.ValueKind == JsonValueKind.Number && h.TryGetInt64(out var hwnd)
                && TryInt(e, "pid", out var pid))
            {
                var host = OptString(e, "host");
                // absent or wrongly typed "readable" means true (older shells stay valid)
                var readable = !(e.TryGetProperty("readable", out var rd) && rd.ValueKind == JsonValueKind.False);
                browsers.Add(new BrowserWindow(hwnd, pid, string.IsNullOrWhiteSpace(host) ? null : host, readable));
            }
        }

        var fg = OptString(r, "foreground");
        return new Snapshot(windowed, string.IsNullOrWhiteSpace(fg) ? null : fg, browsers);
    }

    private static IEnumerable<JsonElement> Entries(JsonElement r, string name)
    {
        if (!r.TryGetProperty(name, out var a) || a.ValueKind != JsonValueKind.Array) return Array.Empty<JsonElement>();
        if (a.GetArrayLength() > MaxSnapshotEntries) throw new FormatException($"Snapshot '{name}' too large");
        return a.EnumerateArray().ToList();
    }

    private static bool TryInt(JsonElement e, string name, out int value)
    {
        value = 0;
        return e.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.Number && v.TryGetInt32(out value);
    }

    private static void WriteNullableString(Utf8JsonWriter w, string name, string? value)
    {
        if (value is null) w.WriteNull(name);
        else w.WriteString(name, value);
    }

    private static string? OptString(JsonElement o, string name)
        => o.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.String ? v.GetString() : null;

    private static string ReqString(JsonElement o, string name)
        => OptString(o, name) ?? throw new FormatException($"'{name}' missing or not a string");

    private static bool ReqBool(JsonElement o, string name)
        => o.TryGetProperty(name, out var v) && v.ValueKind is JsonValueKind.True or JsonValueKind.False
            ? v.GetBoolean()
            : throw new FormatException($"'{name}' missing or not a boolean");
}

/// <summary>shell -> service. The password must never be logged or persisted.</summary>
public sealed record LoginMessage(string Username, string Password) : PipeMessage("login")
{
    public override string ToString() => $"LoginMessage {{ T = {T}, Username = {Username}, Password = *** }}";
}

/// <summary>shell -> service.</summary>
public sealed record LogoutMessage() : PipeMessage("logout");

/// <summary>
/// shell -> service: liveness only, sent on ticks where the shell deliberately sends no snapshot
/// (non-Default input desktop). Never makes a snapshot fresh.
/// </summary>
public sealed record AliveMessage() : PipeMessage("alive");

/// <summary>shell -> service, every ~2 s.</summary>
public sealed record SnapshotMessage(Snapshot Snapshot) : PipeMessage("snapshot");

/// <summary>service -> shell. Error is a short code: bad_credentials, not_a_student, rate_limited, offline.</summary>
public sealed record LoginResultMessage(bool Ok, string? Error) : PipeMessage("login_result");

/// <summary>service -> shell.</summary>
public sealed record StateMessage(bool Locked, string Reason, int Remaining, string? Student) : PipeMessage("state");

/// <summary>service -> shell (wire kind "message").</summary>
public sealed record TextMessage(string Text) : PipeMessage("message");

/// <summary>service -> shell: close this top-level window (browser host rule).</summary>
public sealed record CloseWindowMessage(long Hwnd) : PipeMessage("close_window");

/// <summary>
/// shell -> service: administrator maintenance unlock request (local Windows administrator account).
/// The password must never be logged or persisted: <see cref="PrintMembers"/> (and so ToString, also
/// when this record is printed inside another one) redacts it.
/// </summary>
public sealed record AdminUnlockMessage(string Username, string Password, int Minutes) : PipeMessage("admin_unlock")
{
    protected override bool PrintMembers(StringBuilder builder)
    {
        base.PrintMembers(builder);
        builder.Append(", Username = ").Append(Username).Append(", Password = ***, Minutes = ").Append(Minutes);
        return true;
    }
}

/// <summary>shell -> service: end maintenance mode now (no password needed: ending only re-locks).</summary>
public sealed record AdminEndMessage() : PipeMessage("admin_end");

/// <summary>service -> shell. Error is one of <see cref="AdminErrors"/>; RetrySeconds is set for locked_out.</summary>
public sealed record AdminResultMessage(bool Ok, string? Error, int RetrySeconds) : PipeMessage("admin_result");

/// <summary>service -> shell: maintenance state; sent on connect and on every change. UntilUtc is null when inactive.</summary>
public sealed record MaintenanceMessage(bool Active, DateTimeOffset? UntilUtc) : PipeMessage("maintenance");
