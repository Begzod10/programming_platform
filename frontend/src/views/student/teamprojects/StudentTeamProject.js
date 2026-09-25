import { useCallback, useEffect, useState } from 'react';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useSessionSocket } from '../../../hooks/useSessionSocket';
import './StudentTeamProject.css';

// Matches the two shapes api/search/base.js's request() wrapper can reject
// with (see TeacherTeamGame.js for the same pattern elsewhere in this app).
function getBackendErrorMessage(e, fallback) {
    return e?.response?.data?.error?.message || e?.response?.data?.detail || fallback;
}

const STATUS_LABELS = {
    assigned: 'Boshlanmagan', submitted: 'Tekshirilmoqda',
    changes_requested: "O'zgartirish kerak", approved: 'Tasdiqlandi',
    blocked: 'Muddati o\'tgan', reassigned: 'Qayta tayinlandi',
};

// Returns { text, warning } for a small proactive deadline chip, or null when
// the task is already resolved (approved/blocked already has its own status
// chip) or there's no deadline at all. Uses an hours-based cutoff instead of
// a raw day count for the near-term case: a "days left" figure computed with
// Math.ceil() turns anything under 24h into "1 day", which reads as "due
// tomorrow" even when the real deadline is later *today* — misleading about
// urgency, the opposite of the point of this chip. Also, once the deadline
// has actually passed but the backend hasn't flipped status to "blocked"
// yet, this still shows something rather than silently going blank in that
// window (the whole reason this chip exists is to be proactive, not just
// mirror the status chip after the fact).
function deadlineLabel(task) {
    if (task.status === 'approved' || task.status === 'blocked') return null;
    if (!task.deadline_at) return null;
    const msLeft = new Date(task.deadline_at) - new Date();
    if (msLeft <= 0) return { text: "Muddati o'tgan", warning: true };
    const hoursLeft = msLeft / (1000 * 60 * 60);
    if (hoursLeft < 24) return { text: '24 soatdan kam qoldi', warning: true };
    const daysLeft = Math.ceil(hoursLeft / 24);
    return { text: `${daysLeft} kun qoldi`, warning: daysLeft <= 2 };
}

const TaskCard = ({ task, isMine, onSubmit, submitting }) => {
    const [url, setUrl] = useState('');
    const feedback = task.ai_feedback;
    const deadline = deadlineLabel(task);

    return (
        <div className={`stp-task${isMine ? ' stp-task--mine' : ''}`}>
            <div className="stp-task-head">
                <strong>{task.title}</strong>
                <span className={`stp-chip stp-chip--${task.status}`}>
                    {STATUS_LABELS[task.status] || task.status}
                </span>
            </div>
            <p className="stp-task-desc">{task.description}</p>
            {task.acceptance_criteria?.length > 0 && (
                <ul className="stp-criteria">
                    {task.acceptance_criteria.map((c, i) => <li key={i}>{c}</li>)}
                </ul>
            )}
            {deadline && (
                <span className={`stp-deadline${deadline.warning ? ' stp-deadline--warning' : ''}`}>
                    {deadline.text}
                </span>
            )}
            {!isMine && (
                <p className="stp-muted">Bajaruvchi: {task.assigned_student_name}</p>
            )}
            {isMine && task.status !== 'approved' && (
                <div className="stp-submit-row">
                    <label className="stp-field-label" htmlFor={`stp-url-${task.id}`}>GitHub havolasi</label>
                    <input
                        id={`stp-url-${task.id}`}
                        placeholder="https://github.com/foydalanuvchi/loyiha"
                        value={url}
                        onChange={e => setUrl(e.target.value)}
                    />
                    <button
                        className="stp-btn stp-btn--primary"
                        disabled={!url || submitting}
                        onClick={() => onSubmit(task.id, url)}
                    >
                        {submitting ? 'Yuborilmoqda…' : 'Topshirish'}
                    </button>
                </div>
            )}
            {feedback && (
                <div className={`stp-feedback${task.status === 'approved' ? ' stp-feedback--ok' : ''}`}>
                    <strong>{task.ai_score != null ? `${task.ai_score}/100` : ''}</strong>
                    <p>{feedback.feedback}</p>
                </div>
            )}
        </div>
    );
};

const PeerRatings = ({ team, meId, onSubmit, submitting, submitted }) => {
    const teammates = team.members.filter(m => m.student_id !== meId);
    const [ratings, setRatings] = useState(
        () => Object.fromEntries(teammates.map(m => [m.student_id, { score: 0, comment: '' }]))
    );

    if (teammates.length === 0) return null;

    const allScored = teammates.every(m => ratings[m.student_id]?.score > 0);
    const setScore = (studentId, score) =>
        setRatings(prev => ({ ...prev, [studentId]: { ...prev[studentId], score } }));
    const setComment = (studentId, comment) =>
        setRatings(prev => ({ ...prev, [studentId]: { ...prev[studentId], comment } }));

    if (submitted) {
        return (
            <div className="stp-peer-ratings">
                <h3>Jamoadoshlarni baholash</h3>
                <p className="stp-muted">Rahmat! Baholaringiz qabul qilindi.</p>
            </div>
        );
    }

    return (
        <div className="stp-peer-ratings">
            <h3>Jamoadoshlarni baholash</h3>
            <p className="stp-muted">
                Jamoadoshlaringiz loyihaga qanchalik hissa qo'shganini 1–5 baho bilan belgilang.
            </p>
            {teammates.map(m => (
                <div key={m.student_id} className="stp-peer-row">
                    <span className="stp-peer-name">{m.full_name}</span>
                    <div className="stp-peer-stars">
                        {[1, 2, 3, 4, 5].map(n => (
                            <button
                                key={n}
                                type="button"
                                className={`stp-star${(ratings[m.student_id]?.score || 0) >= n ? ' stp-star--on' : ''}`}
                                onClick={() => setScore(m.student_id, n)}
                                aria-label={`${n} ball`}
                            >★</button>
                        ))}
                    </div>
                    <input
                        className="stp-peer-comment"
                        placeholder="Izoh (ixtiyoriy)"
                        value={ratings[m.student_id]?.comment || ''}
                        onChange={e => setComment(m.student_id, e.target.value)}
                    />
                </div>
            ))}
            <button
                className="stp-btn stp-btn--primary"
                disabled={!allScored || submitting}
                onClick={() => onSubmit(
                    teammates.map(m => ({
                        rated_student_id: m.student_id,
                        score: ratings[m.student_id].score,
                        comment: ratings[m.student_id].comment || null,
                    }))
                )}
            >
                {submitting ? 'Yuborilmoqda…' : 'Baholarni yuborish'}
            </button>
            {!allScored && <p className="stp-muted">Yuborishdan oldin har bir a'zoga baho qo'ying.</p>}
        </div>
    );
};

const StudentTeamProject = () => {
    const { request } = useHttp();
    const [entries, setEntries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [submittingId, setSubmittingId] = useState(null);
    const [finalizing, setFinalizing] = useState(false);
    const [meId, setMeId] = useState(null);
    const [ratingSubmitting, setRatingSubmitting] = useState(false);
    const [ratingSubmitted, setRatingSubmitted] = useState(false);
    const [error, setError] = useState(null);

    const reload = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await request(`${API_URL}v1/team-projects/my`, 'GET', null, headers());
            setEntries(Array.isArray(data) ? data : []);
        } catch (e) {
            setEntries([]);
            setError(getBackendErrorMessage(e, "Ma'lumotlarni yuklab bo'lmadi. Sahifani yangilang."));
        } finally {
            setLoading(false);
        }
    }, [request]);

    useEffect(() => { reload(); }, [reload]);

    // Realtime: a teammate submitting/getting reassigned, or the team's own
    // status advancing, used to only show up after a manual reload. Merges
    // the pushed team into state rather than re-running reload() (a REST
    // round-trip) — safe to do unconditionally since child components
    // (TaskCard's typed-but-unsubmitted URL, PeerRatings' picked stars)
    // keep their own local useState across a prop update; only a
    // remount would lose it, and nothing here causes one.
    const myTeamId = entries[0]?.my_team?.id;
    const handleTeamWsMessage = useCallback((msg) => {
        if (msg.type !== 'team_update') return;
        setEntries(prev => {
            if (!prev[0]) return prev;
            return [{ ...prev[0], my_team: msg.data }, ...prev.slice(1)];
        });
    }, []);
    useSessionSocket(myTeamId, null, null, handleTeamWsMessage, 'team-projects/teams');

    useEffect(() => {
        try {
            const user = JSON.parse(localStorage.getItem('user') || sessionStorage.getItem('user') || '{}');
            setMeId(user.id ?? null);
        } catch { setMeId(null); }
    }, []);

    const submitTask = async (taskId, url) => {
        const entry = entries[0];
        if (!entry) return;
        setSubmittingId(taskId);
        setError(null);
        try {
            await request(
                `${API_URL}v1/team-projects/teams/${entry.my_team.id}/tasks/${taskId}/submit`,
                'POST', JSON.stringify({ submission_url: url }), headers(),
            );
            await reload();
        } catch (e) {
            setError(getBackendErrorMessage(e, "Vazifani topshirib bo'lmadi"));
        } finally {
            setSubmittingId(null);
        }
    };

    const finalize = async (team) => {
        setFinalizing(true);
        setError(null);
        try {
            await request(
                `${API_URL}v1/team-projects/teams/${team.id}/finalize`,
                'POST', JSON.stringify({}), headers(),
            );
            await reload();
        } catch (e) {
            setError(getBackendErrorMessage(e, "Loyihani yakunlab bo'lmadi"));
        } finally {
            setFinalizing(false);
        }
    };

    const submitRatings = async (team, items) => {
        setRatingSubmitting(true);
        setError(null);
        try {
            await request(
                `${API_URL}v1/team-projects/teams/${team.id}/peer-ratings`,
                'POST', JSON.stringify(items), headers(),
            );
            setRatingSubmitted(true);
        } catch (e) {
            setError(getBackendErrorMessage(e, "Baholarni yuborib bo'lmadi"));
        } finally {
            setRatingSubmitting(false);
        }
    };

    if (loading) return <div className="stp-page"><p className="stp-muted">Yuklanmoqda…</p></div>;
    if (entries.length === 0) {
        // A failed reload() also lands here (its catch sets entries to []) —
        // without checking `error` first, the very first load failing (the
        // single most common failure path, including the automatic
        // mount-time reload) would show the same friendly "no project yet"
        // placeholder as a genuinely empty account, silently hiding the
        // real problem instead of surfacing it via the error banner below.
        return (
            <div className="stp-page">
                {error
                    ? <div className="stp-error-banner" role="alert">{error}</div>
                    : <p className="stp-muted">Sizga hali jamoaviy loyiha topshirilmagan.</p>}
            </div>
        );
    }

    const { my_team: team, my_role: role } = entries[0];
    const allApproved = team.tasks.length > 0 && team.tasks.every(t => t.status === 'approved');

    return (
        <div className="stp-page">
            <div className="stp-header">
                <h2>{team.name}</h2>
                <div className="stp-badges">
                    {team.theme_label && <span className="stp-badge">{team.theme_label}</span>}
                    {team.tech_stack_label && <span className="stp-badge stp-badge--tech">{team.tech_stack_label}</span>}
                </div>
                {team.project_title && <p className="stp-project-title">{team.project_title}</p>}
                {team.project_description && <p className="stp-project-desc">{team.project_description}</p>}
            </div>

            {error && <div className="stp-error-banner" role="alert">{error}</div>}

            <div className="stp-members">
                {team.members.map(m => (
                    <span key={m.student_id} className={`stp-member${m.role === 'lead' ? ' stp-member--lead' : ''}`}>
                        {m.full_name}
                        {m.role === 'lead' && (
                            <>
                                <span aria-hidden="true"> 👑</span>
                                <span className="stp-sr-only"> (jamoa boshlig'i)</span>
                            </>
                        )}
                    </span>
                ))}
            </div>

            {team.tasks.length > 0 && (() => {
                const total = team.tasks.length;
                const approvedCount = team.tasks.filter(t => t.status === 'approved').length;
                const pct = Math.round((approvedCount / total) * 100);
                return (
                    <div className="stp-progress">
                        <div
                            className="stp-progress-bar"
                            role="progressbar"
                            aria-valuenow={approvedCount}
                            aria-valuemin={0}
                            aria-valuemax={total}
                            aria-label="Vazifalar bajarilishi"
                        >
                            <div className="stp-progress-fill" style={{ width: `${pct}%` }} />
                        </div>
                        <span className="stp-progress-label">{approvedCount}/{total} vazifa tasdiqlandi</span>
                    </div>
                );
            })()}

            {team.tasks.length === 0 && (
                <p className="stp-muted">Loyiha rejasi tayyorlanmoqda, biroz kuting…</p>
            )}

            <div className="stp-tasks-grid">
                {team.tasks.map(task => (
                    <TaskCard
                        key={task.id}
                        task={task}
                        isMine={task.assigned_student_id === meId}
                        submitting={submittingId === task.id}
                        onSubmit={submitTask}
                    />
                ))}
            </div>

            {role === 'lead' && (
                <div className="stp-finalize">
                    <button
                        className="stp-btn stp-btn--primary"
                        disabled={!allApproved || finalizing}
                        onClick={() => finalize(team)}
                    >
                        {finalizing ? 'Yuborilmoqda…' : "Yakuniy loyihani topshirish"}
                    </button>
                    {!allApproved && <p className="stp-muted">Barcha vazifalar tasdiqlangach yakunlashingiz mumkin.</p>}
                </div>
            )}

            {(team.status === 'submitted' || team.status === 'reviewed') && (
                <PeerRatings
                    team={team}
                    meId={meId}
                    submitting={ratingSubmitting}
                    submitted={ratingSubmitted}
                    onSubmit={items => submitRatings(team, items)}
                />
            )}
        </div>
    );
};

export default StudentTeamProject;
