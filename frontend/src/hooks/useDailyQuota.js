// Shared daily-quota state: today's lesson progress + games lock.
// Reads GET /daily/status (seed + 30s poll fallback) and listens to the
// existing notifications WebSocket for live {type:'quota'} frames and the
// 'games_unlocked' event. FAILS OPEN — guests and any backend hiccup resolve
// to "unlocked" so the lock can never wrongly trap a student.
import { useEffect, useState, useCallback } from 'react';
import { API_URL, headers, getToken } from '../api/search/base';
import { subscribeNotifications } from '../api/notificationsSocket';

const CACHE_KEY = 'quota:status';

export function useDailyQuota({ enabled = true } = {}) {
    const hasToken = !!getToken();
    const [status, setStatus] = useState(() => {
        try { const c = localStorage.getItem(CACHE_KEY); return c ? JSON.parse(c) : null; }
        catch { return null; }
    });
    const [loading, setLoading] = useState(enabled && hasToken);

    const apply = useCallback((partial) => {
        if (!partial) return;
        setStatus((prev) => {
            const next = { ...(prev || {}), ...partial };
            try { localStorage.setItem(CACHE_KEY, JSON.stringify(next)); } catch { /* ignore */ }
            return next;
        });
    }, []);

    const refresh = useCallback(async () => {
        if (!hasToken) return;
        try {
            const r = await fetch(`${API_URL}v1/daily/status`, { headers: headers() });
            if (r.ok) apply(await r.json());
            // 404 / 5xx → leave state as-is (fail-open); never hard-lock on a server blip
        } catch { /* ignore — cosmetic */ }
        finally { setLoading(false); }
    }, [hasToken, apply]);

    useEffect(() => {
        if (!enabled || !hasToken) { setLoading(false); return; }
        refresh();
        const id = setInterval(refresh, 30000);
        const unsub = subscribeNotifications((msg) => {
            if (!msg) return;
            if (msg.type === 'quota') apply(msg);
            if (msg.type === 'notification' && msg.notification?.type === 'games_unlocked') {
                apply({ unlocked: true });
            }
        });
        return () => { clearInterval(id); unsub(); };
    }, [enabled, hasToken, refresh, apply]);

    const unlocked = !hasToken ? true : (status ? !!status.unlocked : true);
    // True only once the server has actually answered — so the UI never shows a
    // fake lock/unlock state when the quota backend isn't present/reachable.
    const hasStatus = !!(status && status.quota_date);
    return {
        loading,
        unlocked,
        hasStatus,
        completed: status?.completed ?? 0,
        required: status?.required ?? 2,
        remaining: status?.remaining ?? Math.max(0, (status?.base_required ?? 2) - (status?.completed ?? 0)),
        baseRequired: status?.base_required ?? 2,
        carriedIn: status?.carried_in ?? 0,
        streak: status?.streak ?? null,
        nextLesson: status?.next_lesson ?? null,
        enabled: status?.enabled ?? true,
        enforceFrom: status?.enforce_from ?? null,
        penaltyPerLesson: status?.penalty_per_lesson ?? 0,
        quotaDate: status?.quota_date ?? null,
        restDay: status?.rest_day ?? false,
        completionBonus: status?.completion_bonus ?? 0,
        refresh,
    };
}
