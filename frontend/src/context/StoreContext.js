import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { API_URL, useHttp, headers } from '../api/search/base';

/**
 * Points-economy store context.
 *
 * Owns two concerns app-wide:
 *   1. The student's coin balance (spendable `total_points`) and a small
 *      recent-ledger tail, so the sidebar chip and the store page don't
 *      each fetch their own copy.
 *   2. Equipped cosmetics — theme tokens and font family — applied to
 *      the document root as CSS variables the moment they change, so
 *      buying a theme feels instant instead of requiring a reload.
 *
 * The provider is a no-op for unauthenticated pages: it only fetches
 * when a token is present in storage. Views that need the wallet call
 * `useStore()` and refresh it explicitly after a purchase.
 *
 * The equipped-theme snapshot is cached in localStorage so a refresh
 * doesn't flash the default theme before the wallet endpoint returns.
 */

const StoreContext = createContext(null);

const LS_THEME_KEY = 'store:equippedTheme';   // {tokens, mode}
const LS_FONT_KEY  = 'store:equippedFont';    // {family, stack, target}
const LS_SOUND_KEY = 'store:equippedSound';   // {submit_ok_url, ...}


function safeParse(raw) {
    if (!raw) return null;
    try { return JSON.parse(raw); } catch { return null; }
}

function readCachedEquipped() {
    return {
        theme: safeParse(localStorage.getItem(LS_THEME_KEY)),
        font:  safeParse(localStorage.getItem(LS_FONT_KEY)),
        sound: safeParse(localStorage.getItem(LS_SOUND_KEY)),
    };
}

/** Write the CSS variables from an equipped theme's `asset_ref.tokens`
 *  onto :root. Called on mount + whenever the equipped theme changes.
 *  Passing null clears the previous set (so unequipping reverts). */
function applyTheme(theme) {
    const root = document.documentElement;
    // Clear any tokens we set previously so unequipping actually reverts.
    const stamped = root.dataset.storeThemeKeys ? root.dataset.storeThemeKeys.split(',') : [];
    stamped.forEach(key => root.style.removeProperty(key));
    root.style.removeProperty('color-scheme');
    delete root.dataset.storeTheme;
    delete root.dataset.storeThemeKeys;
    root.classList.remove('store-theme-dark', 'store-theme-light');

    if (!theme || !theme.tokens) return;
    const keys = [];
    Object.entries(theme.tokens).forEach(([k, v]) => {
        root.style.setProperty(k, v);
        keys.push(k);
    });
    root.dataset.storeThemeKeys = keys.join(',');
    if (theme.mode) {
        root.style.setProperty('color-scheme', theme.mode);
        root.dataset.storeTheme = theme.mode;
        root.classList.add(theme.mode === 'dark' ? 'store-theme-dark' : 'store-theme-light');
    }
}

function applyFont(font) {
    const root = document.documentElement;
    // Reset previous overrides.
    root.style.removeProperty('--font-ui');
    root.style.removeProperty('--font-mono');
    if (!font || !font.stack) return;
    const target = font.target === 'mono' ? '--font-mono' : '--font-ui';
    root.style.setProperty(target, font.stack);
}


export function StoreProvider({ children }) {
    const { request } = useHttp();
    const [balance, setBalance] = useState(null);
    const [lifetimePoints, setLifetimePoints] = useState(null);
    const [recent, setRecent] = useState([]);
    const [inventory, setInventory] = useState([]);
    const [loading, setLoading] = useState(false);

    // Hydrate equipped cosmetics from cache FIRST so there's no flash of
    // the default theme on hard-refresh.
    const [equipped, setEquipped] = useState(() => readCachedEquipped());

    const isAuthed = () => {
        try {
            return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));
        } catch { return false; }
    };

    // Apply cached equipped cosmetics on first mount.
    useEffect(() => {
        applyTheme(equipped.theme);
        applyFont(equipped.font);
        // No global side-effect for sound — the celebration hook reads it.
    }, []);  // eslint-disable-line

    const refreshWallet = useCallback(async () => {
        if (!isAuthed()) return null;
        try {
            const data = await request(`${API_URL}v1/store/wallet?limit=10`, 'GET', null, headers());
            if (data && typeof data === 'object') {
                setBalance(data.balance_coins ?? 0);
                setLifetimePoints(data.lifetime_points ?? 0);
                setRecent(Array.isArray(data.recent) ? data.recent : []);
            }
            return data;
        } catch {
            return null;
        }
    }, [request]);

    const refreshInventory = useCallback(async () => {
        if (!isAuthed()) return null;
        try {
            const data = await request(`${API_URL}v1/store/inventory`, 'GET', null, headers());
            const rows = Array.isArray(data) ? data : [];
            setInventory(rows);
            // Derive equipped from inventory — a single source of truth
            // beats caching separately and drifting.
            const nextEquipped = {
                theme: null, font: null, sound: null,
            };
            rows.forEach(r => {
                if (!r.is_equipped) return;
                if (r.kind === 'theme')      nextEquipped.theme = r.asset_ref;
                else if (r.kind === 'font')  nextEquipped.font  = r.asset_ref;
                else if (r.kind === 'sound_pack') nextEquipped.sound = r.asset_ref;
            });
            setEquipped(nextEquipped);
            try {
                if (nextEquipped.theme) localStorage.setItem(LS_THEME_KEY, JSON.stringify(nextEquipped.theme));
                else localStorage.removeItem(LS_THEME_KEY);
                if (nextEquipped.font) localStorage.setItem(LS_FONT_KEY, JSON.stringify(nextEquipped.font));
                else localStorage.removeItem(LS_FONT_KEY);
                if (nextEquipped.sound) localStorage.setItem(LS_SOUND_KEY, JSON.stringify(nextEquipped.sound));
                else localStorage.removeItem(LS_SOUND_KEY);
            } catch { /* storage disabled — skip cache */ }
            applyTheme(nextEquipped.theme);
            applyFont(nextEquipped.font);
            return rows;
        } catch {
            return null;
        }
    }, [request]);

    const refreshAll = useCallback(async () => {
        setLoading(true);
        await Promise.all([refreshWallet(), refreshInventory()]);
        setLoading(false);
    }, [refreshWallet, refreshInventory]);

    // Initial load when the app mounts + when auth changes (login/logout).
    useEffect(() => {
        if (!isAuthed()) return;
        refreshAll();
        const onLogout = () => {
            setBalance(null);
            setLifetimePoints(null);
            setRecent([]);
            setInventory([]);
        };
        window.addEventListener('auth:logout', onLogout);
        return () => window.removeEventListener('auth:logout', onLogout);
    }, [refreshAll]);

    const value = useMemo(() => ({
        balance,
        lifetimePoints,
        recent,
        inventory,
        equipped,
        loading,
        refreshWallet,
        refreshInventory,
        refreshAll,
    }), [balance, lifetimePoints, recent, inventory, equipped, loading,
         refreshWallet, refreshInventory, refreshAll]);

    return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}


export function useStore() {
    const ctx = useContext(StoreContext);
    if (!ctx) {
        // Called from a subtree not wrapped by StoreProvider (e.g. tests) —
        // return safe defaults so callers don't blow up.
        return {
            balance: null,
            lifetimePoints: null,
            recent: [],
            inventory: [],
            equipped: { theme: null, font: null, sound: null },
            loading: false,
            refreshWallet: async () => null,
            refreshInventory: async () => null,
            refreshAll: async () => null,
        };
    }
    return ctx;
}
