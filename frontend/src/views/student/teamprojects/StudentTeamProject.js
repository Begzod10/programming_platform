import { useCallback, useEffect, useState } from 'react';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import './StudentTeamProject.css';

const STATUS_LABELS = {
    assigned: 'Boshlanmagan', submitted: 'Tekshirilmoqda',
    changes_requested: "O'zgartirish kerak", approved: 'Tasdiqlandi',
    blocked: 'Muddati o\'tgan', reassigned: 'Qayta tayinlandi',
};

const TaskCard = ({ task, isMine, onSubmit, submitting }) => {
    const [url, setUrl] = useState('');
    const feedback = task.ai_feedback;

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
            {!isMine && (
                <p className="stp-muted">Bajaruvchi: {task.assigned_student_name}</p>
            )}
            {isMine && task.status !== 'approved' && (
                <div className="stp-submit-row">
                    <input
                        placeholder="GitHub havolasi"
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

    const reload = useCallback(async () => {
        setLoading(true);
        try {
            const data = await request(`${API_URL}v1/team-projects/my`, 'GET', null, headers());
            setEntries(Array.isArray(data) ? data : []);
        } catch {
            setEntries([]);
        } finally {
            setLoading(false);
        }
    }, [request]);

    useEffect(() => { reload(); }, [reload]);

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
        try {
            await request(
                `${API_URL}v1/team-projects/teams/${entry.my_team.id}/tasks/${taskId}/submit`,
                'POST', JSON.stringify({ submission_url: url }), headers(),
            );
            await reload();
        } catch {} finally {
            setSubmittingId(null);
        }
    };

    const finalize = async (team) => {
        setFinalizing(true);
        try {
            await request(
                `${API_URL}v1/team-projects/teams/${team.id}/finalize`,
                'POST', JSON.stringify({}), headers(),
            );
            await reload();
        } catch {} finally {
            setFinalizing(false);
        }
    };

    const submitRatings = async (team, items) => {
        setRatingSubmitting(true);
        try {
            await request(
                `${API_URL}v1/team-projects/teams/${team.id}/peer-ratings`,
                'POST', JSON.stringify(items), headers(),
            );
            setRatingSubmitted(true);
        } catch {} finally {
            setRatingSubmitting(false);
        }
    };

    if (loading) return <div className="stp-page"><p className="stp-muted">Yuklanmoqda…</p></div>;
    if (entries.length === 0) {
        return (
            <div className="stp-page">
                <p className="stp-muted">Sizga hali jamoaviy loyiha topshirilmagan.</p>
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

            <div className="stp-members">
                {team.members.map(m => (
                    <span key={m.student_id} className={`stp-member${m.role === 'lead' ? ' stp-member--lead' : ''}`}>
                        {m.full_name}{m.role === 'lead' ? ' 👑' : ''}
                    </span>
                ))}
            </div>

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
