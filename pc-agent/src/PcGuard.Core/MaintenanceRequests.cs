namespace PcGuard.Core;

/// <summary>
/// Shell side of the maintenance_redeem / admin_result request ids. At most one request is pending;
/// <see cref="Begin"/> hands out a fresh id (never reused within the shell process), and only the
/// answer carrying the pending id is accepted, once. A superseded, timed-out or cancelled request's
/// late answer is ignored, so it can never show up in a dialog opened later. Not thread-safe: the
/// shell uses it on its UI thread only.
/// </summary>
public sealed class MaintenanceRequestTracker
{
    private int _last;

    /// <summary>The id of the request waiting for its admin_result; null when none.</summary>
    public int? Pending { get; private set; }

    /// <summary>Starts a new request (replacing any pending one) and returns its id (always &gt; 0).</summary>
    public int Begin()
    {
        _last = _last == int.MaxValue ? 1 : _last + 1;
        Pending = _last;
        return _last;
    }

    /// <summary>True exactly once, for the pending id; the request is then no longer pending.</summary>
    public bool Accept(int id)
    {
        if (Pending != id) return false;
        Pending = null;
        return true;
    }

    /// <summary>Drops the pending request (timeout, dialog closed): its answer will be ignored.</summary>
    public void Cancel() => Pending = null;
}

/// <summary>
/// Service side: holds only the latest maintenance_redeem until the command loop takes it (like a
/// pending login). A code replaced before it was checked must still get exactly one admin_result:
/// <see cref="Offer"/> returns it so the caller answers it with <see cref="SupersededReply"/>.
/// Thread-safe.
/// </summary>
public sealed class MaintenanceRedeemSlot
{
    private readonly object _lock = new();
    private MaintenanceRedeemMessage? _pending;

    /// <summary>Stores <paramref name="message"/>; returns the request it replaced (not checked), or null.</summary>
    public MaintenanceRedeemMessage? Offer(MaintenanceRedeemMessage message)
    {
        ArgumentNullException.ThrowIfNull(message);
        lock (_lock)
        {
            var replaced = _pending;
            _pending = message;
            return replaced;
        }
    }

    /// <summary>Takes the pending request (and forgets it); null when none.</summary>
    public MaintenanceRedeemMessage? Take()
    {
        lock (_lock)
        {
            var m = _pending;
            _pending = null;
            return m;
        }
    }

    /// <summary>The answer for a request replaced by a newer one before it was checked.</summary>
    public static AdminResultMessage SupersededReply(int id) => new(false, AdminErrors.Error, 0) { Id = id };
}
