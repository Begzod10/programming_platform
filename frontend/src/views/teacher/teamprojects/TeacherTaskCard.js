import { useEffect, useRef, useState } from 'react';
import ReactDOM from 'react-dom';
import {
    CalendarClock, Check, Clock3, Ellipsis, Info, Link2, Pencil, Trash2,
} from 'lucide-react';
import { pickLang, pickLangList } from '../../../utils/pickLang';

export const TASK_STATUS_LABELS = {
    assigned: 'Boshlanmagan', submitted: 'Tekshirilmoqda',
    changes_requested: "O'zgartirish kerak", approved: 'Tasdiqlandi',
    blocked: "Muddati o'tgan", reassigned: 'Qayta tayinlandi',
};

const LEVEL_LABEL = { Beginner: "Boshlang'ich", Intermediate: "O'rta", Advanced: "Ilg'or" };

export const fmtDate = (iso) => {
    if (!iso) return null;
    try {
        return new Date(iso).toLocaleString('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
        return iso;
    }
};

// "5 kun qoldi" / "Bugun tugaydi" / "Muddati o'tgan" with a tone for colouring.
// Nothing for approved work or a missing deadline — a finished task isn't "late".
export const deadlineInfo = (iso, status, now = Date.now()) => {
    if (!iso || status === 'approved') return null;
    const ms = new Date(iso).getTime();
    if (Number.isNaN(ms)) return null;
    const days = Math.ceil((ms - now) / 86400000);
    if (days < 0) return { text: "Muddati o'tgan", tone: 'late' };
    if (days === 0) return { text: 'Bugun tugaydi', tone: 'soon' };
    return { text: `${days} kun qoldi`, tone: days <= 2 ? 'soon' : 'ok' };
};

export const initials = (name) => {
    const parts = String(name || '').trim().split(/\s+/).filter(Boolean);
    if (parts.length === 0) return '?';
    return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : '')).toUpperCase();
};

const AVATAR_COLORS = [
    ['#dbeafe', '#1d4ed8'], ['#dcfce7', '#15803d'], ['#fef3c7', '#b45309'],
    ['#fae8ff', '#a21caf'], ['#ffe4e6', '#be123c'], ['#cffafe', '#0e7490'],
];
const avatarColors = (name) => {
    let h = 0;
    for (const ch of String(name || '')) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
    return AVATAR_COLORS[h % AVATAR_COLORS.length];
};

export const Avatar = ({ name, size = 28 }) => {
    const [bg, fg] = avatarColors(name);
    return (
        <span
            className="ttd-avatar" aria-hidden="true"
            style={{ width: size, height: size, background: bg, color: fg, fontSize: Math.round(size * 0.38) }}
        >
            {initials(name)}
        </span>
    );
};

// Full-detail view for one task — everything TaskRow's compact card
// leaves out: the interface contract (which files to produce, what they
// consume/produce — the "qayerda bo'lishi kerak, qanday qilinishi kerak"
// spec a teacher/student actually needs), resolved dependency titles
// (depends_on is a list of other tasks' `order`, not names, on the wire),
// deadline, hours estimate, and the AI review's full breakdown (not just
// the one-line feedback TaskRow shows inline).
export const TaskDetailModal = ({ task, allTasks, onClose, lang }) => {
    const contract = task.interface_contract || {};
    const dependsOnTasks = (task.depends_on || [])
        .map(order => allTasks.find(t => t.order === order))
        .filter(Boolean);
    const feedback = task.ai_feedback;

    return ReactDOM.createPortal(
        <div className="ttp-overlay" onClick={onClose}>
            <div className="ttp-modal ttp-modal--wide" onClick={e => e.stopPropagation()}>
                <div className="ttp-modal-head">
                    <h3>{pickLang(task, 'title', lang)}</h3>
                    <button className="ttp-close" onClick={onClose}>✕</button>
                </div>
                <div className="ttp-modal-body">
                    <div className="ttd-detail-row">
                        <span className={`ttp-status ttp-status--${task.status}`}>
                            {TASK_STATUS_LABELS[task.status] || task.status}
                        </span>
                        <span className="ttp-muted">Bajaruvchi: {task.assigned_student_name || '—'}</span>
                        <span className="ttp-muted">{task.estimated_hours} soat</span>
                        {task.deadline_at && <span className="ttp-muted">Muddat: {fmtDate(task.deadline_at)}</span>}
                    </div>

                    <p className="ttd-task-desc">{pickLang(task, 'description', lang)}</p>

                    {task.acceptance_criteria?.length > 0 && (
                        <div className="ttd-detail-section">
                            <h5>Qabul mezonlari</h5>
                            <ul className="ttd-criteria">
                                {pickLangList(task, 'acceptance_criteria', lang).map((c, i) => <li key={i}>{c}</li>)}
                            </ul>
                        </div>
                    )}

                    {(contract.files?.length > 0 || contract.produces?.length > 0 || contract.consumes?.length > 0) && (
                        <div className="ttd-detail-section">
                            <h5>Interfeys shartnomasi</h5>
                            {contract.files?.length > 0 && (
                                <p><strong>Fayllar:</strong> {contract.files.join(', ')}</p>
                            )}
                            {contract.produces?.length > 0 && (
                                <p><strong>Bu vazifa yaratadi:</strong> {contract.produces.join(', ')}</p>
                            )}
                            {contract.consumes?.length > 0 && (
                                <p><strong>Bu vazifa foydalanadi:</strong> {contract.consumes.join(', ')}</p>
                            )}
                        </div>
                    )}

                    {dependsOnTasks.length > 0 && (
                        <div className="ttd-detail-section">
                            <h5>Bog'liq vazifalar (avval tugashi kerak)</h5>
                            <ul className="ttd-criteria">
                                {dependsOnTasks.map(t => (
                                    <li key={t.id}>{pickLang(t, 'title', lang)} — <em>{t.assigned_student_name || '—'}</em></li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {(task.submission_url || task.submitted_at) && (
                        <div className="ttd-detail-section">
                            <h5>Topshirilgan ish</h5>
                            {task.submission_url && (
                                <a href={task.submission_url} target="_blank" rel="noreferrer" className="ttd-link">
                                    {task.submission_url}
                                </a>
                            )}
                            {task.submitted_at && <p className="ttp-muted">Topshirilgan: {fmtDate(task.submitted_at)}</p>}
                        </div>
                    )}

                    {feedback && (
                        <div className="ttd-detail-section">
                            <h5>AI baholashi {task.ai_score != null ? `— ${task.ai_score}/100` : ''}</h5>
                            <div className={`ttd-feedback${task.status === 'approved' ? ' ttd-feedback--ok' : ''}`}>
                                <p>{feedback.feedback}</p>
                            </div>
                            {feedback.criteria_results?.length > 0 && (
                                <ul className="ttd-criteria">
                                    {feedback.criteria_results.map((c, i) => (
                                        <li key={i}>
                                            {c.met ? '✅' : '❌'} {c.criterion || c.text || JSON.stringify(c)}
                                        </li>
                                    ))}
                                </ul>
                            )}
                            {feedback.contract_violations?.length > 0 && (
                                <div className="ttd-feedback">
                                    <strong>Shartnoma buzilishlari:</strong>
                                    <ul className="ttd-criteria">
                                        {feedback.contract_violations.map((v, i) => <li key={i}>{v}</li>)}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>,
        document.body,
    );
};

// One task as a card: what/who/how hard/when at a glance, the main review
// actions in a single row, and the rarely-used ones (reassign, delete) tucked
// into a "⋯" menu instead of three stacked controls.
export const TaskCard = ({ task, members, allTasks, onReassign, onDelete, onReview, lang }) => {
    const [showDetail, setShowDetail] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false);
    const [reassignTo, setReassignTo] = useState('');
    const menuRef = useRef(null);

    useEffect(() => {
        if (!menuOpen) return undefined;
        const onDown = (e) => { if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false); };
        const onKey = (e) => { if (e.key === 'Escape') setMenuOpen(false); };
        document.addEventListener('mousedown', onDown);
        document.addEventListener('keydown', onKey);
        return () => {
            document.removeEventListener('mousedown', onDown);
            document.removeEventListener('keydown', onKey);
        };
    }, [menuOpen]);

    const feedback = task.ai_feedback;
    const reviewable = task.status === 'submitted' || task.status === 'changes_requested';
    const criteria = pickLangList(task, 'acceptance_criteria', lang);
    const dependsOn = (task.depends_on || []).filter(order => allTasks.some(t => t.order === order));
    const deadline = deadlineInfo(task.deadline_at, task.status);
    const others = members.filter(m => m.student_id !== task.assigned_student_id);

    return (
        <article className={`ttd-card ttd-card--${task.status}`}>
            <header className="ttd-card-top">
                <span className="ttd-card-num" title={`Vazifa #${task.order + 1}`}>{task.order + 1}</span>
                <span className={`ttp-status ttp-status--${task.status}`}>
                    {TASK_STATUS_LABELS[task.status] || task.status}
                </span>
            </header>

            <h4 className="ttd-card-title">{pickLang(task, 'title', lang)}</h4>

            <div className="ttd-assignee">
                <Avatar name={task.assigned_student_name} />
                <span className="ttd-assignee-name">{task.assigned_student_name || '—'}</span>
                {task.required_level && (
                    <span className={`ttd-level ttd-level--${String(task.required_level).toLowerCase()}`}>
                        {LEVEL_LABEL[task.required_level] || task.required_level}
                    </span>
                )}
            </div>

            <p className="ttd-card-desc">{pickLang(task, 'description', lang)}</p>

            {criteria.length > 0 && (
                <ul className="ttd-card-criteria">
                    {criteria.slice(0, 2).map((c, i) => (
                        <li key={i}><Check size={13} aria-hidden="true" /><span>{c}</span></li>
                    ))}
                    {criteria.length > 2 && (
                        <li className="ttd-card-more">+{criteria.length - 2} ta mezon</li>
                    )}
                </ul>
            )}

            <div className="ttd-chips">
                {task.estimated_hours != null && (
                    <span className="ttd-chip" title="Taxminiy vaqt">
                        <Clock3 size={13} aria-hidden="true" /> {task.estimated_hours} soat
                    </span>
                )}
                {deadline && (
                    <span className={`ttd-chip ttd-chip--${deadline.tone}`} title="Topshirish muddati">
                        <CalendarClock size={13} aria-hidden="true" /> {deadline.text}
                    </span>
                )}
                {dependsOn.map(order => (
                    <span key={order} className="ttd-chip" title="Avval shu vazifa tugashi kerak">
                        <Link2 size={13} aria-hidden="true" /> #{order + 1} dan keyin
                    </span>
                ))}
            </div>

            {task.submission_url && (
                <a href={task.submission_url} target="_blank" rel="noreferrer" className="ttd-link ttd-card-link">
                    {task.submission_url}
                </a>
            )}
            {feedback && (
                <div className={`ttd-feedback${task.status === 'approved' ? ' ttd-feedback--ok' : ''}`}>
                    <strong>{task.ai_score != null ? `${task.ai_score}/100` : ''}</strong>
                    <p>{feedback.feedback}</p>
                </div>
            )}
            {task.lead_comment && (
                <div className="ttd-feedback">
                    <strong>O'qituvchi izohi</strong>
                    <p>{task.lead_comment}</p>
                </div>
            )}

            <footer className="ttd-card-foot">
                {reviewable && (
                    <div className="ttd-card-review">
                        <button className="ttd-btn ttd-btn--ok" onClick={() => onReview(task.id, 'approve')}>
                            <Check size={14} aria-hidden="true" /> Tasdiqlash
                        </button>
                        <button className="ttd-btn ttd-btn--warn" onClick={() => onReview(task.id, 'request_changes')}>
                            <Pencil size={14} aria-hidden="true" /> O'zgartirish so'rash
                        </button>
                    </div>
                )}
                <button className="ttd-btn ttd-btn--outline" onClick={() => setShowDetail(true)}>
                    <Info size={14} aria-hidden="true" /> Batafsil
                </button>
                <div className="ttd-menu" ref={menuRef}>
                    <button
                        className="ttd-icon-btn" aria-label="Boshqa amallar"
                        aria-haspopup="menu" aria-expanded={menuOpen}
                        onClick={() => setMenuOpen(o => !o)}
                    >
                        <Ellipsis size={18} aria-hidden="true" />
                    </button>
                    {menuOpen && (
                        <div className="ttd-menu-pop" role="menu">
                            {others.length > 0 && (
                                <div className="ttd-menu-section">
                                    <span className="ttd-menu-label">Boshqa a'zoga topshirish</span>
                                    <div className="ttd-menu-reassign">
                                        <select
                                            className="ttd-select" aria-label="A'zoni tanlang"
                                            value={reassignTo} onChange={e => setReassignTo(e.target.value)}
                                        >
                                            <option value="">A'zoni tanlang…</option>
                                            {others.map(m => (
                                                <option key={m.student_id} value={m.student_id}>{m.full_name}</option>
                                            ))}
                                        </select>
                                        <button
                                            className="ttd-btn ttd-btn--outline" disabled={!reassignTo}
                                            onClick={() => {
                                                onReassign(task.id, Number(reassignTo));
                                                setReassignTo('');
                                                setMenuOpen(false);
                                            }}
                                        >
                                            Tayinlash
                                        </button>
                                    </div>
                                </div>
                            )}
                            <button
                                className="ttd-menu-danger" role="menuitem"
                                onClick={() => { setMenuOpen(false); onDelete(task.id); }}
                            >
                                <Trash2 size={14} aria-hidden="true" /> Vazifani o'chirish
                            </button>
                        </div>
                    )}
                </div>
            </footer>

            {showDetail && (
                <TaskDetailModal task={task} allTasks={allTasks} onClose={() => setShowDetail(false)} lang={lang} />
            )}
        </article>
    );
};
