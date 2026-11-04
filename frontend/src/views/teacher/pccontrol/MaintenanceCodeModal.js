import React, { useState, useEffect, useRef } from 'react';
import { createMaintenanceCode } from './pcApi';
import { maintenanceError } from './pcErrors';

const OPTIONS = [[15, 'maint15'], [60, 'maint60'], [240, 'maint240']];

// The server may send a naive ISO timestamp; treat it as UTC.
const parseExpiry = (iso) => {
    const s = String(iso || '');
    return Date.parse(/(Z|[+-]\d\d:?\d\d)$/.test(s) ? s : `${s}Z`);
};
const fmtLeft = (ms) => {
    const total = Math.max(0, Math.ceil(ms / 1000));
    return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`;
};
const spaced = (c) => (c.length === 6 ? `${c.slice(0, 3)} ${c.slice(3)}` : c);

// The plain code lives in component state only: never stored, logged or put
// in a URL. Unmounting (close) drops it.
export default function MaintenanceCodeModal({ request, device, t, onClose }) {
    const [minutes, setMinutes] = useState(60);
    const [busy, setBusy] = useState(false);
    const [result, setResult] = useState(null);   // { code, expiresAt }
    const [error, setError] = useState(null);
    const [copied, setCopied] = useState(false);
    const [now, setNow] = useState(Date.now());
    const alive = useRef(true);

    useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
    useEffect(() => {
        if (!result) return undefined;
        const id = setInterval(() => setNow(Date.now()), 1000);
        return () => clearInterval(id);
    }, [result]);
    useEffect(() => {
        const onKey = (e) => { if (e.key === 'Escape') onClose(); };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    }, [onClose]);

    const create = async () => {
        if (busy) return;
        setBusy(true);
        setError(null);
        setCopied(false);
        try {
            const r = await createMaintenanceCode(request, device.id, minutes);
            if (!alive.current) return;
            setResult({ code: String(r.code), expiresAt: parseExpiry(r.expires_at) });
            setNow(Date.now());
        } catch (e) {
            if (alive.current) { setResult(null); setError(maintenanceError(e, t)); }
        } finally {
            if (alive.current) setBusy(false);
        }
    };

    const copy = async () => {
        try {
            await navigator.clipboard.writeText(result.code);
            setCopied(true);
        } catch (e) { /* clipboard unavailable: the code is selectable on screen */ }
    };

    const left = result ? result.expiresAt - now : 0;
    const expired = !!result && left <= 0;

    return (
        <div className="pc-modal-back" onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
            <div className="pc-modal" role="dialog" aria-modal="true" aria-label={`${t.maintTitle} ${device.hostname}`}>
                <h3>{t.maintTitle}: {device.hostname}</h3>
                <label className="pc-field-label" htmlFor="pc-maint-minutes">{t.maintDuration}</label>
                <select id="pc-maint-minutes" className="pc-select" value={String(minutes)} disabled={busy}
                    onChange={e => setMinutes(Number(e.target.value))}>
                    {OPTIONS.map(([m, k]) => <option key={m} value={m}>{t[k]}</option>)}
                </select>
                {error && <div className="pc-notice err" role="alert">{error}</div>}
                {result && (
                    <>
                        <div className={`pc-maint-code${expired ? ' expired' : ''}`} data-testid="pc-maint-code">
                            {spaced(result.code)}
                        </div>
                        <div className={`pc-maint-left${expired ? ' expired' : ''}`} data-testid="pc-maint-left" aria-live="off">
                            {expired ? t.maintExpired : `${t.maintLeft} ${fmtLeft(left)}`}
                        </div>
                        <p className="pc-muted">{t.maintNote}</p>
                    </>
                )}
                <div className="pc-btn-row">
                    {result && !expired && (
                        <button type="button" className="pc-btn" onClick={copy}>{copied ? t.maintCopied : t.maintCopy}</button>
                    )}
                    <button type="button" className="pc-btn primary" disabled={busy} onClick={create}>
                        {t.maintCreate}
                    </button>
                    <button type="button" className="pc-btn" onClick={onClose}>{t.maintClose}</button>
                </div>
            </div>
        </div>
    );
}
