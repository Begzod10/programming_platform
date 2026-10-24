import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useHttp } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import { listDevices, patchDevice, sendCommand } from './pcApi';
import { formatSeen } from './pcReportMath';
import useMyGroups from './useMyGroups';
import { errorMessage } from './pcErrors';
import { pcStrings, REASON_KEYS } from './pcStrings';

const POLL_MS = 5000;
const CONFIRM_MS = 4000;
const MAX_MESSAGE = 500;


const ARM_GUARD_MS = 600;   // a tap on an armed button this soon after arming is ignored

export default function DevicesTab() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const t = pcStrings(lang);

    const [devices, setDevices] = useState(null);   // null = first load pending
    const [loadFailed, setLoadFailed] = useState(false);
    const groups = useMyGroups(request);
    const [busy, setBusy] = useState(false);
    const [notice, setNotice] = useState(null);     // { ok, text }
    const [confirmKey, setConfirmKey] = useState(null);
    const [groupId, setGroupId] = useState('');
    const [target, setTarget] = useState('all');
    const [targetDevice, setTargetDevice] = useState('');
    const [text, setText] = useState('');
    const confirmTimer = useRef(null);
    const armedAt = useRef(0);
    const busyRef = useRef(false);

    const aliveRef = useRef(true);
    const inflight = useRef(0);
    const seqIssued = useRef(0);
    const seqApplied = useRef(0);

    // Every load gets a sequence number; a response older than the newest
    // applied one is dropped. `poll` ticks skip while a request is pending.
    const load = useCallback(({ poll = false } = {}) => {
        if (poll && inflight.current > 0) return Promise.resolve();
        const seq = ++seqIssued.current;
        inflight.current += 1;
        return listDevices(request)
            .then(d => {
                if (!aliveRef.current || seq < seqApplied.current) return;
                seqApplied.current = seq;
                setDevices(Array.isArray(d) ? d : []);
                setLoadFailed(false);
            })
            .catch(() => {
                if (!aliveRef.current || seq < seqApplied.current) return;
                setLoadFailed(true);
            })
            .finally(() => { inflight.current -= 1; });
    }, [request]);

    // Poll every 5 s; skip while hidden; refresh at once when visible again.
    useEffect(() => {
        aliveRef.current = true;
        load();
        const id = setInterval(() => {
            if (document.visibilityState === 'hidden') return;
            load({ poll: true });
        }, POLL_MS);
        const onVisible = () => {
            if (document.visibilityState !== 'hidden') load();
        };
        document.addEventListener('visibilitychange', onVisible);
        return () => {
            aliveRef.current = false;
            clearInterval(id);
            document.removeEventListener('visibilitychange', onVisible);
        };
    }, [load]);

    useEffect(() => () => clearTimeout(confirmTimer.current), []);

    const disarm = () => {
        clearTimeout(confirmTimer.current);
        setConfirmKey(null);
    };

    // Runs one action with double-click protection and notice handling.
    const run = async (fn, okText, warn = false) => {
        if (busyRef.current) return false;
        busyRef.current = true;
        disarm();
        setBusy(true);
        setNotice(null);
        try {
            await fn();
            setNotice({ ok: !warn, warn, text: okText });
            load();
            return true;
        } catch (e) {
            setNotice({ ok: false, text: errorMessage(e, t.failed) });
            return false;
        } finally {
            busyRef.current = false;
            setBusy(false);
        }
    };

    const command = (scope_type, scope_id, type, payload) =>
        run(() => sendCommand(request, { scope_type, scope_id, type, ...(payload ? { payload } : {}) }),
            type === 'message' ? t.messageSent : t.sent);

    const confirmed = (key, fn) => {
        if (confirmKey === key) {
            if (Date.now() - armedAt.current < ARM_GUARD_MS) return;   // accidental double-tap
            disarm();
            fn();
        } else {
            armedAt.current = Date.now();
            setConfirmKey(key);
            clearTimeout(confirmTimer.current);
            confirmTimer.current = setTimeout(() => setConfirmKey(null), CONFIRM_MS);
        }
    };

    const sendMessage = async () => {
        const body = text.trim();
        if (!body) return;
        let scope_type = target;
        let scope_id = null;
        if (target === 'group') scope_id = groupId ? Number(groupId) : null;
        if (target === 'device') scope_id = targetDevice ? Number(targetDevice) : null;
        if (scope_type !== 'all' && scope_id == null) return;
        let online = 0;
        if (target === 'all') online = (devices || []).filter(d => d.online).length;
        if (target === 'group') online = (devices || []).filter(d => d.online && d.group_id === scope_id).length;
        if (target === 'device') online = (devices || []).filter(d => d.online && d.id === scope_id).length;
        const okText = online > 0 ? `${t.messageSentTo} ${online}` : t.messageNoPc;
        const ok = await run(() => sendCommand(request, { scope_type, scope_id, type: 'message', payload: { text: body } }),
            okText, online === 0);
        if (ok) setText('');
    };

    const changeGroup = (device, value) =>
        run(() => patchDevice(request, device.id, value === '' ? null : Number(value)), t.groupChanged);

    const reasonText = (r) => (REASON_KEYS[r] ? t[REASON_KEYS[r]] : t.reasonUnknown);
    const noStudent = (d) => d.reason === 'no_student';
    const gid = groupId ? Number(groupId) : null;
    const messageDisabled = busy || !text.trim()
        || (target === 'group' && gid == null) || (target === 'device' && !targetDevice);

    return (
        <div className="pc-devices">
            {notice && (
                <div className={`pc-notice ${notice.ok ? 'ok' : notice.warn ? 'warn' : 'err'}`} role={notice.ok || notice.warn ? 'status' : 'alert'}>
                    <span>{notice.text}</span>
                    <button type="button" className="pc-notice-x" aria-label={t.dismiss}
                        onClick={() => setNotice(null)}>×</button>
                </div>
            )}

            <section className="pc-panel" data-testid="pc-all-bar">
                <h3>{t.allPcs}</h3>
                <div className="pc-btn-row">
                    <button type="button" className="pc-btn pc-btn-fixed danger" disabled={busy}
                        onClick={() => confirmed('lock', () => command('all', null, 'lock'))}>
                        {confirmKey === 'lock' ? t.confirm : t.lockAll}
                    </button>
                    <button type="button" className="pc-btn pc-btn-fixed" disabled={busy}
                        onClick={() => confirmed('unlock', () => command('all', null, 'unlock'))}>
                        {confirmKey === 'unlock' ? t.confirm : t.unlockAll}
                    </button>
                </div>
                <div className="pc-btn-row pc-resume-row">
                    <button type="button" className="pc-btn pc-btn-fixed" disabled={busy}
                        onClick={() => command('all', null, 'clear')}>{t.resumeAll}</button>
                </div>
            </section>

            <section className="pc-panel" data-testid="pc-group-bar">
                <h3>{t.groupScope}</h3>
                <select className="pc-select" value={groupId} aria-label={t.groupScope}
                    onChange={e => setGroupId(e.target.value)}>
                    <option value="">{t.pickGroup}</option>
                    {groups.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
                </select>
                <div className="pc-btn-row">
                    <button type="button" className="pc-btn danger" disabled={busy || gid == null}
                        onClick={() => command('group', gid, 'lock')}>{t.lock}</button>
                    <button type="button" className="pc-btn" disabled={busy || gid == null}
                        onClick={() => command('group', gid, 'unlock')}>{t.unlock}</button>
                    <button type="button" className="pc-btn" disabled={busy || gid == null}
                        onClick={() => command('group', gid, 'clear')}>{t.resume}</button>
                </div>
            </section>

            <p className="pc-muted" data-testid="pc-cmd-explain">{t.cmdExplain}</p>

            <section className="pc-panel" data-testid="pc-message-box">
                <h3>{t.message}</h3>
                <textarea className="pc-textarea" value={text} maxLength={MAX_MESSAGE} rows={3}
                    placeholder={t.messagePlaceholder} aria-label={t.message}
                    onChange={e => setText(e.target.value)} />
                <div className="pc-counter">{text.length}/{MAX_MESSAGE}</div>
                <div className="pc-btn-row">
                    <select className="pc-select" value={target} aria-label={t.target}
                        onChange={e => setTarget(e.target.value)}>
                        <option value="all">{t.targetAll}</option>
                        <option value="group">{t.targetGroup}</option>
                        <option value="device">{t.targetDevice}</option>
                    </select>
                    {target === 'device' && (
                        <select className="pc-select" value={targetDevice} aria-label={t.pickDevice}
                            onChange={e => setTargetDevice(e.target.value)}>
                            <option value="">{t.pickDevice}</option>
                            {(devices || []).map(d => <option key={d.id} value={d.id}>{d.hostname}</option>)}
                        </select>
                    )}
                    {target === 'group' && (
                        <span className="pc-muted">
                            {gid == null ? t.pickGroupHint : (groups.find(g => g.id === gid)?.name || '')}
                        </span>
                    )}
                    <button type="button" className="pc-btn primary" disabled={messageDisabled}
                        onClick={sendMessage}>{t.send}</button>
                </div>
            </section>

            {devices === null && !loadFailed && <p className="pc-muted">{t.loading}</p>}
            {loadFailed && devices === null && <p className="pc-notice err" role="alert">{t.loadError}</p>}
            {loadFailed && devices !== null && <p className="pc-muted">{t.staleHint}</p>}
            {devices && devices.length === 0 && <p className="pc-muted">{t.noDevices}</p>}

            <div className="pc-grid">
                {(devices || []).map(d => (
                    <article key={d.id} className="pc-card" data-testid={`pc-card-${d.id}`}>
                        <header className="pc-card-head">
                            <strong className="pc-host">{d.hostname}</strong>
                            <span className={`pc-badge ${d.online ? 'on' : 'off'}`}>
                                {d.online ? t.online : t.offline}
                            </span>
                        </header>
                        <div className="pc-badges">
                            <span className={`pc-badge ${d.locked ? 'locked' : 'open'}`}>
                                {d.locked ? t.locked : t.unlocked}
                            </span>
                            <span className="pc-muted">{reasonText(d.reason)}</span>
                        </div>
                        <dl className="pc-meta">
                            <dt>{t.student}</dt>
                            <dd data-testid="pc-student">{d.student?.full_name || '—'}</dd>
                            <dt>{t.lastApp}</dt>
                            <dd>{d.last_app || '—'}</dd>
                            <dt>{t.lastSeen}</dt>
                            <dd>{formatSeen(d.last_seen_at, new Date(), t.never)}</dd>
                        </dl>
                        <select className="pc-select" aria-label={`${t.deviceGroup} ${d.hostname}`}
                            value={d.group_id == null ? '' : String(d.group_id)} disabled={busy}
                            onChange={e => changeGroup(d, e.target.value)}>
                            <option value="">{t.noGroup}</option>
                            {d.group_id != null && !groups.some(g => g.id === d.group_id) && (
                                <option value={d.group_id} disabled>{t.otherGroup} #{d.group_id}</option>
                            )}
                            {groups.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
                        </select>
                        {noStudent(d) && <p className="pc-muted">{t.noStudentHint}</p>}
                        <div className="pc-btn-row">
                            <button type="button" className="pc-btn danger" disabled={busy || !d.online || noStudent(d)}
                                aria-label={`${t.lock} ${d.hostname}`}
                                onClick={() => command('device', d.id, 'lock')}>{t.lock}</button>
                            <button type="button" className="pc-btn" disabled={busy || !d.online || noStudent(d)}
                                aria-label={`${t.unlock} ${d.hostname}`}
                                onClick={() => command('device', d.id, 'unlock')}>{t.unlock}</button>
                            <button type="button" className="pc-btn" disabled={busy || !d.online || noStudent(d)}
                                aria-label={`${t.resume} ${d.hostname}`}
                                onClick={() => command('device', d.id, 'clear')}>{t.resume}</button>
                        </div>
                    </article>
                ))}
            </div>
        </div>
    );
}
