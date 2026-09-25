/* Offline service worker for the kids' games (/play and the logged-in
 * early-learning routes). Registered ONLY from EarlyLearning.js with a
 * scope of that route, so it never touches login, courses or anything
 * else in the app. The game DATA itself is cached in localStorage by
 * EarlyLearning.js — this worker's job is just to make the page itself
 * (index.html + its hashed JS/CSS) load with no network.
 *
 * - Navigations: network-first (5s timeout), falling back to the cached
 *   index.html shell — so a fresh deploy is picked up as soon as there's a
 *   connection, and a dead/flaky wifi still opens the app.
 * - /static/*, icons, manifest: cache-first (build filenames are content-
 *   hashed, so a cached copy is never stale under the same URL).
 * - Everything else (API calls, uploads, cross-origin) is left alone.
 *
 * To remove it everywhere, deploy a version of this file that calls
 * self.registration.unregister() on activate.
 */
const CACHE = 'el-offline-v1';
const SHELL = '/index.html';
const MAX_ENTRIES = 80;
const NAV_TIMEOUT_MS = 5000;

async function precacheShell() {
    const cache = await caches.open(CACHE);
    const res = await fetch(SHELL, { cache: 'no-cache' });
    if (!res.ok) return;
    const html = await res.clone().text();
    await cache.put(SHELL, res);
    // Pages already loaded before this worker installed never went through
    // it, so pull the shell's own JS/CSS in now instead of waiting for a
    // second visit to populate the cache.
    const assets = new Set(html.match(/\/static\/(?:js|css)\/[^"'\s>]+/g) || []);
    ['/manifest.json', '/favicon.ico', '/favicon-192.png', '/logo192.png'].forEach((a) => assets.add(a));
    await Promise.all([...assets].map(async (a) => {
        try {
            const r = await fetch(a);
            if (r.ok) await cache.put(a, r);
        } catch {
            // One missing asset shouldn't fail the whole install.
        }
    }));
}

self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(precacheShell().catch(() => {}));
});

self.addEventListener('activate', (event) => {
    event.waitUntil((async () => {
        const keys = await caches.keys();
        await Promise.all(
            keys.filter((k) => k.startsWith('el-offline-') && k !== CACHE).map((k) => caches.delete(k))
        );
        await self.clients.claim();
    })());
});

async function trim(cache) {
    const keys = await cache.keys();
    for (let i = 0; i < keys.length - MAX_ENTRIES; i++) {
        await cache.delete(keys[i]);
    }
}

async function networkFirstShell(request) {
    const cache = await caches.open(CACHE);
    try {
        const res = await Promise.race([
            fetch(request),
            new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), NAV_TIMEOUT_MS)),
        ]);
        const type = res.headers.get('content-type') || '';
        if (res.ok && type.includes('text/html')) {
            cache.put(SHELL, res.clone());
        }
        return res;
    } catch {
        const cached = await cache.match(SHELL);
        return cached || Response.error();
    }
}

async function cacheFirst(request) {
    const cache = await caches.open(CACHE);
    const hit = await cache.match(request);
    if (hit) return hit;
    const res = await fetch(request);
    if (res.ok) {
        cache.put(request, res.clone()).then(() => trim(cache)).catch(() => {});
    }
    return res;
}

self.addEventListener('fetch', (event) => {
    const req = event.request;
    if (req.method !== 'GET') return;
    const url = new URL(req.url);
    if (url.origin !== self.location.origin) return;

    if (req.mode === 'navigate') {
        event.respondWith(networkFirstShell(req));
        return;
    }
    if (/^\/(static\/|favicon|manifest\.json|logo)/.test(url.pathname)) {
        event.respondWith(cacheFirst(req));
    }
});
