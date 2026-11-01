using System.Text.Json;

namespace PcGuard.Core;

public static class StateParser
{
    public static PcRules Parse(string json)
    {
        JsonDocument doc;
        try { doc = JsonDocument.Parse(json); }
        catch (JsonException e) { throw new FormatException("Invalid state JSON", e); }

        using (doc)
        {
            var root = doc.RootElement;
            if (root.ValueKind != JsonValueKind.Object)
                throw new FormatException("State must be a JSON object");

            if (!root.TryGetProperty("locked", out var lockedEl)
                || (lockedEl.ValueKind != JsonValueKind.True && lockedEl.ValueKind != JsonValueKind.False))
                throw new FormatException("'locked' missing or not a boolean");

            var reason = Str(root, "reason") ?? "unknown";
            var remaining = root.TryGetProperty("remaining", out var r) && r.ValueKind == JsonValueKind.Number && r.TryGetInt32(out var n) ? n : 0;

            string? student = null;
            if (root.TryGetProperty("student", out var st) && st.ValueKind == JsonValueKind.Object)
                student = Str(st, "full_name");

            var allow = new List<AllowEntry>();
            if (root.TryGetProperty("allowlist", out var al) && al.ValueKind == JsonValueKind.Array)
            {
                foreach (var e in al.EnumerateArray())
                {
                    if (e.ValueKind != JsonValueKind.Object) continue;
                    var exe = Str(e, "exe")?.Trim().ToLowerInvariant();
                    if (string.IsNullOrEmpty(exe)) continue;
                    var pub = Str(e, "publisher");
                    allow.Add(new AllowEntry(exe, string.IsNullOrWhiteSpace(pub) ? null : pub));
                }
            }

            var hosts = new List<string>();
            if (root.TryGetProperty("browser_hosts", out var bh) && bh.ValueKind == JsonValueKind.Array)
            {
                foreach (var h in bh.EnumerateArray())
                {
                    if (h.ValueKind != JsonValueKind.String) continue;
                    var v = h.GetString()?.Trim().ToLowerInvariant();
                    if (!string.IsNullOrEmpty(v)) hosts.Add(v);
                }
            }

            return new PcRules(lockedEl.GetBoolean(), reason, remaining, student, allow, hosts);
        }
    }

    private static string? Str(JsonElement obj, string name)
        => obj.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.String ? v.GetString() : null;
}
