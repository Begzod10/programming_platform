import { useCallback, useEffect, useRef } from 'react';
import { API_URL_DOC, getToken } from '../api/search/base';

function wsUrl(basePath, entityId) {
    const base = API_URL_DOC.replace(/^http/, 'ws').replace(/\/$/, '');
    const token = encodeURIComponent(getToken() || '');
    return `${base}/api/v1/${basePath}/${entityId}/ws?token=${token}`;
}

// Keeps a WS alive for the given entityId under basePath (default
// 'game-sessions', so both existing call sites keep working unchanged) —
// reconnects on close, pings every 25s to hold it open. Originally shared by
// just the student/teacher team-game pages (which used to each carry their
// own byte-for-byte copy of this, and had already drifted: one dropped
// onDeleted/onMessage from its reconnect callback's dependency array, a
// stale-closure bug once those callbacks stop being referentially stable);
// generalized with a basePath param so the team-projects realtime feature
// could reuse the exact same connect/reconnect/ping mechanics instead of a
// second hand-copy.
export function useSessionSocket(sessionId, onUpdate, onDeleted, onMessage, basePath = 'game-sessions') {
    const wsRef = useRef(null);
    const pingRef = useRef(null);
    const mountedRef = useRef(true);
    const reconnectRef = useRef(null);

    const connect = useCallback(() => {
        if (!sessionId || !mountedRef.current) return;
        const ws = new WebSocket(wsUrl(basePath, sessionId));
        wsRef.current = ws;

        ws.onmessage = (e) => {
            try {
                const msg = JSON.parse(e.data);
                if (msg.type === 'session_update') onUpdate(msg.data);
                if (msg.type === 'session_deleted' && onDeleted) onDeleted();
                if (onMessage) onMessage(msg);
            } catch {}
        };

        ws.onopen = () => {
            clearTimeout(reconnectRef.current);
            pingRef.current = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) ws.send('ping');
            }, 25000);
        };

        ws.onclose = () => {
            clearInterval(pingRef.current);
            if (mountedRef.current) {
                reconnectRef.current = setTimeout(connect, 3000);
            }
        };

        ws.onerror = () => ws.close();
    }, [sessionId, onUpdate, onDeleted, onMessage, basePath]);

    useEffect(() => {
        mountedRef.current = true;
        connect();
        return () => {
            mountedRef.current = false;
            clearTimeout(reconnectRef.current);
            clearInterval(pingRef.current);
            const ws = wsRef.current;
            wsRef.current = null;
            if (ws) {
                // Detach first: onclose fires AFTER this cleanup, by which time
                // a re-run of this effect (id changed / set to null) has set
                // mountedRef true again — the stale handler would then
                // "reconnect" to the room we just deliberately left.
                ws.onclose = null;
                ws.onerror = null;
                ws.close();
            }
        };
    }, [connect]);

    // Added for the duel game (the first WS feature where the CLIENT sends
    // messages, not just listens) — existing callers ignore the return value.
    const send = useCallback((payload) => {
        const ws = wsRef.current;
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(typeof payload === 'string' ? payload : JSON.stringify(payload));
            return true;
        }
        return false;
    }, []);

    return { send };
}
