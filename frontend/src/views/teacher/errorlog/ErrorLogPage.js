import { useCallback, useEffect, useMemo, useState } from 'react';
import './ErrorLogPage.css';
import { API_URL, headers } from '../../../api/search/base';

const ROLE_LABEL = {
    student: 'Talaba',
    teacher: "O'qituvchi",
};

function formatDateTime(iso) {
    const d = new Date(iso);
    return d.toLocaleString('uz-UZ', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
    });
}

/** Every unhandled 500 the app has ever hit, from ANY account — see
 * backend/app/core/exceptions.py's unhandled_exception_handler, the only
 * writer. Backend-gated to two specific usernames (not the general
 * teacher role — see backend/app/api/v1/endpoints/teacher/error_log.py's
 * _ALLOWED_USERNAMES); this page assumes it's only reachable by an
 * allowed account (TeacherSidebar.js/AppRouter.js hide the entry point
 * for everyone else), but still renders the 403 cleanly if someone
 * navigates here directly, same as any other backend-enforced boundary.
 */
export default function ErrorLogPage() {
    const [entries, setEntries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [forbidden, setForbidden] = useState(false);
    const [roleFilter, setRoleFilter] = useState('');
    const [openId, setOpenId] = useState(null);

    const load = useCallback(() => {
        setLoading(true);
        setError('');
        setForbidden(false);
        const qs = roleFilter ? `?role=${encodeURIComponent(roleFilter)}` : '';
        fetch(`${API_URL}v1/teacher/error-log${qs}`, { headers: headers() })
            .then((r) => {
                if (r.status === 403) { setForbidden(true); return null; }
                if (!r.ok) throw new Error('Server xatosi');
                return r.json();
            })
            .then((data) => { if (data) setEntries(data.items || []); })
            .catch((e) => setError("Ro'yxatni yuklab bo'lmadi: " + e.message))
            .finally(() => setLoading(false));
    }, [roleFilter]);

    useEffect(() => { load(); }, [load]);

    const roles = useMemo(
        () => Array.from(new Set(entries.map((e) => e.actor_role).filter(Boolean))),
        [entries]
    );

    const copyEntry = (entry) => {
        const text = `${entry.method} ${entry.path}\n${entry.error_type}: ${entry.message}\n\n${entry.traceback}`;
        navigator.clipboard.writeText(text).catch(() => {});
    };

    const deleteEntry = (id) => {
        fetch(`${API_URL}v1/teacher/error-log/${id}`, { method: 'DELETE', headers: headers() })
            .then((r) => { if (r.ok) setEntries((prev) => prev.filter((e) => e.id !== id)); })
            .catch(() => {});
    };

    if (forbidden) {
        return (
            <div className="err-page">
                <div className="err-forbidden">🔒 Bu bo'limni faqat administrator ko'ra oladi</div>
            </div>
        );
    }

    return (
        <div className="err-page">
            <div className="err-header">
                <div>
                    <h2>🐛 Xato jurnali</h2>
                    <p>Platformada yuz bergan barcha kutilmagan xatolar ({entries.length})</p>
                </div>
                {roles.length > 0 && (
                    <select
                        className="err-role-select"
                        value={roleFilter}
                        onChange={(e) => setRoleFilter(e.target.value)}
                    >
                        <option value="">Barcha rollar</option>
                        {roles.map((r) => (
                            <option key={r} value={r}>{ROLE_LABEL[r] || r}</option>
                        ))}
                    </select>
                )}
            </div>

            {loading ? (
                <div className="err-empty">⏳ Yuklanmoqda...</div>
            ) : error ? (
                <div className="err-empty" style={{ color: '#d63031' }}>{error}</div>
            ) : entries.length === 0 ? (
                <div className="err-empty">✅ Hozircha xato qayd etilmagan</div>
            ) : (
                <div className="err-list">
                    {entries.map((entry) => {
                        const open = openId === entry.id;
                        return (
                            <div key={entry.id} className="err-entry">
                                <button
                                    type="button"
                                    className="err-entry-head"
                                    onClick={() => setOpenId(open ? null : entry.id)}
                                >
                                    <span className="err-badge-500">500</span>
                                    <div className="err-entry-main">
                                        <div className="err-entry-meta">
                                            <span className="err-mono">{entry.method} {entry.path}</span>
                                            <span>·</span>
                                            <span>{formatDateTime(entry.created_at)}</span>
                                            {entry.actor_role && (
                                                <>
                                                    <span>·</span>
                                                    <span className="err-actor-chip">
                                                        {ROLE_LABEL[entry.actor_role] || entry.actor_role}
                                                        {entry.actor_username ? ` @${entry.actor_username}` : ''}
                                                    </span>
                                                </>
                                            )}
                                        </div>
                                        <p className="err-entry-summary">{entry.error_type}: {entry.message}</p>
                                    </div>
                                    <div className="err-entry-actions">
                                        <span
                                            role="button"
                                            tabIndex={0}
                                            className="err-icon-btn"
                                            onClick={(e) => { e.stopPropagation(); copyEntry(entry); }}
                                            title="Nusxa olish"
                                        >📋</span>
                                        <span
                                            role="button"
                                            tabIndex={0}
                                            className="err-icon-btn err-icon-btn-danger"
                                            onClick={(e) => { e.stopPropagation(); deleteEntry(entry.id); }}
                                            title="O'chirish"
                                        >🗑</span>
                                        <span className="err-chevron">{open ? '▲' : '▼'}</span>
                                    </div>
                                </button>
                                {open && (
                                    <pre className="err-traceback">{entry.traceback}</pre>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
