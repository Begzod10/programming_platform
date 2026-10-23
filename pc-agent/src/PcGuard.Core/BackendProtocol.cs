using System.Globalization;
using System.Text;
using System.Text.Json;

namespace PcGuard.Core;

public enum UsageOutcome
{
    /// <summary>Stored: remove the batch from the queue.</summary>
    Ok,
    /// <summary>The server refused this batch for good (422 etc.): drop it, never retry forever.</summary>
    DropBatch,
    /// <summary>401/403: the token is dead. The batch is dropped as well.</summary>
    TokenDead,
    /// <summary>Transient (network, 408, 429, 5xx): keep the batch and retry later.</summary>
    Retry,
}

public enum ServerFrameKind { Unknown, State, Pong, Message }

public sealed record ServerFrame(ServerFrameKind Kind, PcRules? State = null, string? Text = null);

/// <summary>
/// Pure helpers for the backend wire contract (/pc/login, /pc/logout, /pc/state, /pc/usage, /pc/ws).
/// Nothing here logs; callers must never log request bodies, passwords or tokens.
/// </summary>
public static class BackendProtocol
{
    /// <summary>Joins <paramref name="relative"/> under the base URL, keeping its path prefix (e.g. /api/v1).</summary>
    public static Uri Endpoint(Uri baseUrl, string relative)
        => new(baseUrl.AbsoluteUri.TrimEnd('/') + "/" + relative.TrimStart('/'));

    /// <summary>ws(s)://.../pc/ws?token=... The result contains the token: never log it.</summary>
    public static Uri WebSocketUri(Uri baseUrl, string token)
    {
        var scheme = baseUrl.Scheme switch
        {
            "https" => "wss",
            "http" => "ws",
            _ => throw new ArgumentException("Backend base URL must be http or https", nameof(baseUrl)),
        };
        var b = new UriBuilder(Endpoint(baseUrl, "pc/ws"))
        {
            Scheme = scheme,
            Port = baseUrl.IsDefaultPort ? -1 : baseUrl.Port,
            Query = "token=" + Uri.EscapeDataString(token),
        };
        return b.Uri;
    }

    public static string LoginBody(string username, string password, string hostname, string machineKey)
        => Write(w =>
        {
            w.WriteStartObject();
            w.WriteString("username", username);
            w.WriteString("password", password);
            w.WriteString("hostname", hostname);
            w.WriteString("machine_key", machineKey);
            w.WriteEndObject();
        });

    /// <summary>Short, language-neutral codes shown by the shell.</summary>
    public static string LoginErrorCode(int status) => status switch
    {
        401 or 422 => "bad_credentials",
        403 => "not_a_student",
        429 => "rate_limited",
        _ => "offline",
    };

    /// <summary>Parses the 200 body of /pc/login: <c>{token, state}</c>.</summary>
    public static (string Token, PcRules State) ParseLoginResponse(string body)
    {
        JsonDocument doc;
        try { doc = JsonDocument.Parse(body); }
        catch (JsonException e) { throw new FormatException("Invalid login response", e); }
        using (doc)
        {
            var r = doc.RootElement;
            if (r.ValueKind != JsonValueKind.Object) throw new FormatException("Login response must be an object");
            var token = r.TryGetProperty("token", out var t) && t.ValueKind == JsonValueKind.String ? t.GetString() : null;
            if (string.IsNullOrEmpty(token)) throw new FormatException("Login response has no token");
            if (!r.TryGetProperty("state", out var s) || s.ValueKind != JsonValueKind.Object)
                throw new FormatException("Login response has no state");
            return (token, StateParser.Parse(s.GetRawText()));
        }
    }

    public const int MaxUsageBatch = 500;

    public static string UsageBody(IReadOnlyList<UsageEvent> events)
    {
        if (events.Count > MaxUsageBatch) throw new ArgumentException("At most 500 events per batch", nameof(events));
        return Write(w =>
        {
            w.WriteStartObject();
            w.WriteStartArray("events");
            foreach (var e in events)
            {
                w.WriteStartObject();
                w.WriteString("app_name", e.AppName);
                w.WriteString("started_at", Iso(e.StartedAt));
                w.WriteString("ended_at", Iso(e.EndedAt));
                w.WriteBoolean("was_locked", e.WasLocked);
                w.WriteEndObject();
            }
            w.WriteEndArray();
            w.WriteEndObject();
        });
    }

    public static UsageOutcome ClassifyUsage(int status) => status switch
    {
        >= 200 and < 300 => UsageOutcome.Ok,
        401 or 403 => UsageOutcome.TokenDead,
        408 or 429 => UsageOutcome.Retry,
        >= 400 and < 500 => UsageOutcome.DropBatch,
        _ => UsageOutcome.Retry,
    };

    public static string Heartbeat(string? foregroundApp)
        => Write(w =>
        {
            w.WriteStartObject();
            w.WriteString("type", "hb");
            if (string.IsNullOrWhiteSpace(foregroundApp)) w.WriteNull("app");
            else w.WriteString("app", foregroundApp);
            w.WriteEndObject();
        });

    /// <summary>Malformed JSON or an invalid state frame throws FormatException; unknown kinds return Unknown.</summary>
    public static ServerFrame ParseServerFrame(string json)
    {
        JsonDocument doc;
        try { doc = JsonDocument.Parse(json); }
        catch (JsonException e) { throw new FormatException("Invalid server frame", e); }
        using (doc)
        {
            var r = doc.RootElement;
            if (r.ValueKind != JsonValueKind.Object) throw new FormatException("Server frame must be an object");
            var type = r.TryGetProperty("type", out var t) && t.ValueKind == JsonValueKind.String ? t.GetString() : null;
            switch (type)
            {
                case "state":
                    return new ServerFrame(ServerFrameKind.State, State: StateParser.Parse(json));
                case "pong":
                    return new ServerFrame(ServerFrameKind.Pong);
                case "message":
                    return r.TryGetProperty("text", out var x) && x.ValueKind == JsonValueKind.String
                        ? new ServerFrame(ServerFrameKind.Message, Text: x.GetString())
                        : new ServerFrame(ServerFrameKind.Unknown);
                default:
                    return new ServerFrame(ServerFrameKind.Unknown);
            }
        }
    }

    private static string Iso(DateTimeOffset d) => d.ToString("yyyy-MM-dd'T'HH:mm:ss.fffzzz", CultureInfo.InvariantCulture);

    private static string Write(Action<Utf8JsonWriter> body)
    {
        using var ms = new MemoryStream();
        using (var w = new Utf8JsonWriter(ms)) body(w);
        return Encoding.UTF8.GetString(ms.ToArray());
    }
}
