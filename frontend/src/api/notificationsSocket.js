// ── Realtime notifications WebSocket ────────────────────────────────────────
// One shared connection for the whole app (the header bell and the
// notifications page both subscribe to it). Auto-reconnects with capped
// exponential backoff, sends a heartbeat so proxies don't drop an idle socket,
// and reconnects when the tab regains focus or the network comes back.
//
// Server → client frames:
//   { type: 'unread',       unread_count }                 (on connect / after read)
//   { type: 'notification', notification, unread_count }   (when one is emitted)
import { API_URL_DOC, getToken } from './search/base';

let socket = null;
let reconnectTimer = null;
let heartbeat = null;
let backoff = 1000;
const listeners = new Set();

function buildUrl() {
    const token = getToken();
    if (!token) return null; // not signed in — nothing to connect to
    // https://host/ -> wss://host/ ,  http://host/ -> ws://host/
    const base = API_URL_DOC.replace(/^http(s?):\/\//i, (_, s) => `ws${s}://`);
    return `${base}api/v1/notifications/ws?token=${encodeURIComponent(token)}`;
}

function clearHeartbeat() {
    if (heartbeat) { clearInterval(heartbeat); heartbeat = null; }
}

function emit(msg) {
    listeners.forEach((fn) => { try { fn(msg); } catch { /* a bad listener must not kill the socket */ } });
}

function scheduleReconnect() {
    if (reconnectTimer) return;
    reconnectTimer = setTimeout(() => {
        reconnectTimer = null;
        backoff = Math.min(backoff * 2, 30000);
        connect();
    }, backoff);
}

function connect() {
    if (socket || !listeners.size) return;      // already open, or nobody listening
    const url = buildUrl();
    if (!url) return;                            // signed out — stop (a later subscribe retries)
    let ws;
    try { ws = new WebSocket(url); } catch { scheduleReconnect(); return; }
    socket = ws;

    ws.onopen = () => {
        backoff = 1000;
        clearHeartbeat();
        heartbeat = setInterval(() => {
            try { if (ws.readyState === WebSocket.OPEN) ws.send('ping'); } catch { /* ignore */ }
        }, 25000);
    };
    ws.onmessage = (e) => {
        if (e.data === 'pong') return;
        let msg; try { msg = JSON.parse(e.data); } catch { return; }
        emit(msg);
    };
    ws.onerror = () => { try { ws.close(); } catch { /* ignore */ } };
    ws.onclose = () => {
        clearHeartbeat();
        if (socket === ws) socket = null;
        if (listeners.size) scheduleReconnect();  // keep trying while anyone cares
    };
}

/** Subscribe to realtime notification frames. Returns an unsubscribe fn.
 *  The connection is opened lazily on the first subscriber and kept alive for
 *  the session (the header is effectively always mounted). */
export function subscribeNotifications(fn) {
    listeners.add(fn);
    connect();
    return () => { listeners.delete(fn); };
}

/** Close the socket and stop reconnecting (call on logout). */
export function closeNotificationsSocket() {
    listeners.clear();
    if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
    clearHeartbeat();
    if (socket) { try { socket.close(); } catch { /* ignore */ } socket = null; }
}

if (typeof window !== 'undefined') {
    const revive = () => { if (!socket && listeners.size) { backoff = 1000; connect(); } };
    window.addEventListener('online', revive);
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') revive();
    });
}
