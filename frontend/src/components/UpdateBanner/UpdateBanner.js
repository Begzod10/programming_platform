import { useCallback, useEffect, useRef, useState } from 'react';
import './UpdateBanner.css';

// A tab left open across a frontend deploy keeps running the old JS bundle
// indefinitely — this app has no service worker or other mechanism that
// forces a reload. Found to be a real, recurring problem (not theoretical):
// the ZIP-upload 422 fix landed, and students with an already-open tab kept
// hitting the pre-fix bug, retrying and creating a fresh empty project on
// every failed attempt, for as long as their tab stayed open.
//
// Detects a new deploy by polling CRA's own build manifest
// (asset-manifest.json, written fresh on every `npm run build` with
// content-hashed filenames) and comparing main.js's hash against the one
// captured at page load. No backend involvement needed — the manifest is
// just another static file this app already serves.
const POLL_INTERVAL_MS = 3 * 60 * 1000; // 3 min
const RESHOW_AFTER_DISMISS_MS = 25 * 60 * 1000; // 25 min

async function fetchMainJsHash() {
    // cache: 'no-store' — the whole point is detecting a change, a cached
    // manifest would defeat it.
    const res = await fetch('/asset-manifest.json', { cache: 'no-store' });
    if (!res.ok) return null;
    const data = await res.json();
    return data?.files?.['main.js'] || null;
}

const UpdateBanner = () => {
    const [updateAvailable, setUpdateAvailable] = useState(false);
    const baselineRef = useRef(null);
    const dismissedAtRef = useRef(null);

    const checkForUpdate = useCallback(async () => {
        if (document.visibilityState !== 'visible') return;
        const current = await fetchMainJsHash().catch(() => null);
        if (!current) return; // network hiccup — don't flag a false update

        if (baselineRef.current === null) {
            baselineRef.current = current;
            return;
        }
        if (current === baselineRef.current) return;

        const dismissedAt = dismissedAtRef.current;
        const longEnoughSinceDismiss =
            dismissedAt === null || Date.now() - dismissedAt >= RESHOW_AFTER_DISMISS_MS;
        if (longEnoughSinceDismiss) {
            setUpdateAvailable(true);
        }
    }, []);

    useEffect(() => {
        checkForUpdate(); // captures the baseline on first run
        const interval = setInterval(checkForUpdate, POLL_INTERVAL_MS);

        const onVisible = () => {
            if (document.visibilityState === 'visible') checkForUpdate();
        };
        document.addEventListener('visibilitychange', onVisible);

        return () => {
            clearInterval(interval);
            document.removeEventListener('visibilitychange', onVisible);
        };
    }, [checkForUpdate]);

    if (!updateAvailable) return null;

    const dismiss = () => {
        dismissedAtRef.current = Date.now();
        setUpdateAvailable(false);
    };

    return (
        <div className="ub-banner" role="status">
            <span>Yangi versiya chiqdi — sahifani yangilang.</span>
            <div className="ub-actions">
                <button className="ub-refresh" onClick={() => window.location.reload()}>
                    Yangilash
                </button>
                <button className="ub-dismiss" onClick={dismiss} aria-label="Yopish">✕</button>
            </div>
        </div>
    );
};

export default UpdateBanner;
