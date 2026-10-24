import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useHttp } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import { getAllowlist, putAllowlist } from './pcApi';
import { errorMessage } from './pcErrors';
import { pcStrings } from './pcStrings';
import { normalizeExe } from './pcReportMath';
import useMyGroups from './useMyGroups';

const clean = (list) => (Array.isArray(list) ? list : [])
    .map(e => ({ exe: e.exe, publisher: (e.publisher || '').trim() || null }));
const sameList = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const ERR_KEYS = { empty: 'errEmpty', ext: 'errExt', path: 'errPath', dup: 'errDup', max: 'errMax' };

export default function AllowlistTab() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const t = pcStrings(lang);
    const groups = useMyGroups(request);

    const [scope, setScope] = useState('');          // '' = global
    const [pendingScope, setPendingScope] = useState(null);
    const [saved, setSaved] = useState([]);          // server copy of this scope's own list
    const [entries, setEntries] = useState([]);      // local edits
    const [effective, setEffective] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState(null);
    const [busy, setBusy] = useState(false);
    const [notice, setNotice] = useState(null);      // { ok, text }
    const [exe, setExe] = useState('');
    const [pub, setPub] = useState('');
    const [inputErr, setInputErr] = useState(null);
    const seq = useRef(0);
    const alive = useRef(true);
    useEffect(() => () => { alive.current = false; }, []);

    const apply = (data) => {
        const own = clean(data?.entries);
        setSaved(own);
        setEntries(own);
        setEffective(clean(data?.effective));
    };

    const load = useCallback((sc) => {
        const id = ++seq.current;
        setLoading(true);
        setLoadError(null);
        setNotice(null);
        return getAllowlist(request, sc === '' ? null : Number(sc))
            .then(d => { if (alive.current && id === seq.current) { apply(d); setLoading(false); } })
            .catch(e => {
                if (!alive.current || id !== seq.current) return;
                setLoadError(errorMessage(e, t.loadError));
                setLoading(false);
            });
    }, [request, t.loadError]);

    useEffect(() => { load(scope); }, [load, scope]);

    const dirty = !sameList(entries.map(e => ({ exe: e.exe, publisher: e.publisher })), saved);
    const empty = entries.length === 0;
    const saveDisabled = busy || loading || empty || !dirty;

    const changeScope = (value) => {
        if (value === scope) return;
        if (dirty) { setPendingScope(value); return; }
        setScope(value);
    };
    const confirmSwitch = () => { setScope(pendingScope); setPendingScope(null); };

    const addEntry = () => {
        const r = normalizeExe(exe, entries.map(e => e.exe));
        if (!r.ok) { setInputErr(t[ERR_KEYS[r.reason]]); return; }
        setEntries([...entries, { exe: r.value, publisher: pub.trim() || null }]);
        setExe(''); setPub(''); setInputErr(null); setNotice(null);
    };
    const removeEntry = (name) => { setEntries(entries.filter(e => e.exe !== name)); setNotice(null); };
    const setPublisher = (name, value) =>
        setEntries(entries.map(e => (e.exe === name ? { ...e, publisher: value.trim() ? value : null } : e)));

    const onSave = async () => {
        if (saveDisabled) return;
        setBusy(true);
        setNotice(null);
        try {
            const payload = entries.map(e => ({ exe: e.exe, publisher: (e.publisher || '').trim() || null }));
            const d = await putAllowlist(request, scope === '' ? null : Number(scope), payload);
            if (!alive.current) return;
            apply(d);
            setNotice({ ok: true, text: t.saved });
        } catch (e) {
            if (alive.current) setNotice({ ok: false, text: errorMessage(e, t.failed) });
        } finally {
            if (alive.current) setBusy(false);
        }
    };

    return (
        <div className="pc-devices">
            <section className="pc-panel">
                <label className="pc-field-label" htmlFor="pc-al-scope">{t.scope}</label>
                <select id="pc-al-scope" className="pc-select" aria-label={t.scope} value={scope}
                    onChange={e => changeScope(e.target.value)}>
                    <option value="">{t.scopeGlobal}</option>
                    {groups.map(g => <option key={g.id} value={String(g.id)}>{g.name}</option>)}
                </select>
                {pendingScope !== null && (
                    <div className="pc-notice err" role="alertdialog" aria-label={t.discardAsk}>
                        <span>{t.discardAsk}</span>
                        <div className="pc-btn-row">
                            <button type="button" className="pc-btn danger" onClick={confirmSwitch}>{t.discard}</button>
                            <button type="button" className="pc-btn" onClick={() => setPendingScope(null)}>{t.keepEditing}</button>
                        </div>
                    </div>
                )}
            </section>

            {loading && <p className="pc-muted">{t.loading}</p>}
            {loadError && <p className="pc-notice err" role="alert">{loadError}</p>}

            {!loading && !loadError && (
                <>
                    {notice && (
                        <div className={`pc-notice ${notice.ok ? 'ok' : 'err'}`} role={notice.ok ? 'status' : 'alert'}>
                            <span>{notice.text}</span>
                            <button type="button" className="pc-notice-x" aria-label={t.dismiss}
                                onClick={() => setNotice(null)}>×</button>
                        </div>
                    )}
                    <section className="pc-panel">
                        <h3>{t.yourEntries}</h3>
                        {empty && <p className="pc-muted">{t.listEmpty}</p>}
                        <ul className="pc-list" data-testid="pc-al-entries">
                            {entries.map(e => (
                                <li key={e.exe}>
                                    <span className="pc-exe">{e.exe}</span>
                                    <input className="pc-input" value={e.publisher || ''} placeholder={t.publisher}
                                        aria-label={`${t.publisher}: ${e.exe}`}
                                        onChange={ev => setPublisher(e.exe, ev.target.value)} />
                                    <button type="button" className="pc-btn danger" aria-label={`${t.remove} ${e.exe}`}
                                        onClick={() => removeEntry(e.exe)}>{t.remove}</button>
                                </li>
                            ))}
                        </ul>
                        <div className="pc-form-row">
                            <input className="pc-input" value={exe} placeholder={t.exePlaceholder}
                                aria-label={t.exeName} maxLength={200}
                                onChange={ev => { setExe(ev.target.value); setInputErr(null); }}
                                onKeyDown={ev => { if (ev.key === 'Enter') addEntry(); }} />
                            <input className="pc-input" value={pub} placeholder={t.publisher}
                                aria-label={t.publisher} maxLength={200} onChange={ev => setPub(ev.target.value)} />
                            <button type="button" className="pc-btn" onClick={addEntry}>{t.add}</button>
                        </div>
                        <p className="pc-muted">{t.publisherNote}</p>
                        {inputErr && <p className="pc-notice err" role="alert">{inputErr}</p>}
                        {empty && <p className="pc-muted">{t.emptyHint}</p>}
                        <div className="pc-btn-row">
                            <button type="button" className="pc-btn primary" disabled={saveDisabled}
                                onClick={onSave}>{t.save}</button>
                        </div>
                    </section>

                    <section className="pc-panel">
                        <h3>{t.effectiveList}</h3>
                        <ul className="pc-list readonly" data-testid="pc-al-effective">
                            {effective.map(e => (
                                <li key={e.exe}>
                                    <span className="pc-exe">{e.exe}</span>
                                    {e.publisher && <span className="pc-muted">{e.publisher}</span>}
                                </li>
                            ))}
                        </ul>
                    </section>
                </>
            )}
        </div>
    );
}
