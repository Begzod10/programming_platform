import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import './TeacherTeamProjects.css';

const STATUS_LABELS = {
    planning: 'Rejalashtirilmoqda', forming: 'Shakillanmoqda', working: 'Ishlanmoqda',
    submitted: 'Topshirilgan', reviewed: 'Baholangan', active: 'Faol',
};
const TASK_STATUS_LABELS = {
    assigned: 'Boshlanmagan', submitted: 'Tekshirilmoqda',
    changes_requested: "O'zgartirish kerak", approved: 'Tasdiqlandi',
    blocked: "Muddati o'tgan", reassigned: 'Qayta tayinlandi',
};

const TaskRow = ({ task, members, onReassign }) => {
    const [reassignTo, setReassignTo] = useState('');
    const feedback = task.ai_feedback;

    return (
        <div className="ttd-task">
            <div className="ttd-task-head">
                <strong>{task.title}</strong>
                <span className={`ttp-status ttp-status--${task.status}`}>
                    {TASK_STATUS_LABELS[task.status] || task.status}
                </span>
            </div>
            <p className="ttd-task-desc">{task.description}</p>
            {task.acceptance_criteria?.length > 0 && (
                <ul className="ttd-criteria">
                    {task.acceptance_criteria.map((c, i) => <li key={i}>{c}</li>)}
                </ul>
            )}
            <p className="ttp-muted">Bajaruvchi: {task.assigned_student_name || '—'}</p>
            {task.submission_url && (
                <p>
                    <a href={task.submission_url} target="_blank" rel="noreferrer" className="ttd-link">
                        {task.submission_url}
                    </a>
                </p>
            )}
            {feedback && (
                <div className={`ttd-feedback${task.status === 'approved' ? ' ttd-feedback--ok' : ''}`}>
                    <strong>{task.ai_score != null ? `${task.ai_score}/100` : ''}</strong>
                    <p>{feedback.feedback}</p>
                </div>
            )}
            <div className="ttd-reassign">
                <select value={reassignTo} onChange={e => setReassignTo(e.target.value)}>
                    <option value="">Boshqa a'zoga topshirish…</option>
                    {members
                        .filter(m => m.student_id !== task.assigned_student_id)
                        .map(m => <option key={m.student_id} value={m.student_id}>{m.full_name}</option>)}
                </select>
                <button
                    className="ttp-btn ttp-btn--ghost ttp-btn--sm"
                    disabled={!reassignTo}
                    onClick={() => { onReassign(task.id, Number(reassignTo)); setReassignTo(''); }}
                >
                    Qayta tayinlash
                </button>
            </div>
        </div>
    );
};

const TeacherTeamProjectDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { request } = useHttp();
    const [tp, setTp] = useState(null);
    const [loading, setLoading] = useState(true);

    const reload = useCallback(async () => {
        setLoading(true);
        try {
            const data = await request(`${API_URL}v1/team-projects/${id}`, 'GET', null, headers());
            setTp(data);
        } catch {
            setTp(null);
        } finally {
            setLoading(false);
        }
    }, [request, id]);

    useEffect(() => { reload(); }, [reload]);

    const regenerate = async (teamId) => {
        try {
            await request(`${API_URL}v1/team-projects/teams/${teamId}/regenerate`, 'POST', null, headers());
            await reload();
        } catch {}
    };

    const reassign = async (teamId, taskId, studentId) => {
        try {
            await request(
                `${API_URL}v1/team-projects/teams/${teamId}/tasks/${taskId}/reassign`,
                'POST', JSON.stringify({ student_id: studentId }), headers(),
            );
            await reload();
        } catch {}
    };

    if (loading) return <div className="ttp-page"><p className="ttp-muted">Yuklanmoqda…</p></div>;
    if (!tp) return <div className="ttp-page"><p className="ttp-muted">Topshiriq topilmadi.</p></div>;

    return (
        <div className="ttp-page">
            <div className="ttp-page-head">
                <div className="ttd-head-left">
                    <button className="ttp-btn ttp-btn--ghost" onClick={() => navigate('/teacher/team-projects')}>
                        ← Orqaga
                    </button>
                    <h2>Topshiriq #{tp.id}</h2>
                </div>
                <span className="ttp-muted">{STATUS_LABELS[tp.status] || tp.status}</span>
            </div>

            {tp.teams.map(team => (
                <div key={team.id} className="ttd-team-section">
                    <div className="ttd-team-header">
                        <h3>{team.name}</h3>
                        <span className={`ttp-status ttp-status--${team.status}`}>
                            {STATUS_LABELS[team.status] || team.status}
                        </span>
                    </div>
                    <div className="ttp-team-badges">
                        {team.theme_label && <span className="ttp-badge">{team.theme_label}</span>}
                        {team.tech_stack_label && <span className="ttp-badge ttp-badge--tech">{team.tech_stack_label}</span>}
                    </div>
                    {team.project_title && <p className="ttp-project-title">{team.project_title}</p>}
                    {team.project_description && <p className="ttd-project-desc">{team.project_description}</p>}
                    <div className="ttp-members">
                        {team.members.map(m => (
                            <span key={m.student_id} className={`ttp-member${m.role === 'lead' ? ' ttp-member--lead' : ''}`}>
                                {m.full_name}{m.role === 'lead' ? ' 👑' : ''}
                            </span>
                        ))}
                    </div>

                    {team.generation_attempts < 3 && (
                        <button
                            className="ttp-btn ttp-btn--ghost ttp-btn--sm"
                            onClick={() => regenerate(team.id)}
                        >
                            Rejani qayta yaratish ({team.generation_attempts}/3)
                        </button>
                    )}

                    <div className="ttd-tasks-grid">
                        {team.tasks.map(task => (
                            <TaskRow
                                key={task.id} task={task} members={team.members}
                                onReassign={(taskId, studentId) => reassign(team.id, taskId, studentId)}
                            />
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default TeacherTeamProjectDetail;
