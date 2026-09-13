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

const LEVELS = ['Beginner', 'Intermediate', 'Advanced'];
const LEVEL_RANK = { Beginner: 0, Intermediate: 1, Advanced: 2 };

// request() throws `Could not fetch {url}, status: {status}: {message}` —
// strip the prefix so the teacher sees just the actual reason (often a
// validate_plan error naming exactly which task/field is wrong).
const extractErrorMessage = (e) => {
    const text = e?.message || "Noma'lum xatolik";
    const idx = text.indexOf(': ', text.indexOf('status:'));
    return idx === -1 ? text : text.slice(idx + 2);
};

const emptyManualTask = () => ({
    title: '', title_ru: '', description: '', description_ru: '',
    required_level: 'Beginner', estimated_hours: 4,
    acceptance_criteria_text: '', depends_on: [],
});

// AI-disabled / /regenerate-exhausted fallback: lets the teacher author a
// plan by hand instead. One task block per member, fixed 1:1 (no
// assignee picker) — side-steps the "every member exactly once" permutation
// check entirely by construction, since a row can't be assigned to the
// wrong member or duplicated.
const ManualPlanForm = ({ team, onSubmit, onCancel, submitting, error }) => {
    const [projectTitle, setProjectTitle] = useState('');
    const [projectDescription, setProjectDescription] = useState('');
    const [tasks, setTasks] = useState(() => team.members.map(emptyManualTask));

    const updateTask = (idx, patch) =>
        setTasks(prev => prev.map((t, i) => (i === idx ? { ...t, ...patch } : t)));

    const toggleDependsOn = (idx, depIdx) =>
        setTasks(prev => prev.map((t, i) => {
            if (i !== idx) return t;
            const has = t.depends_on.includes(depIdx);
            return { ...t, depends_on: has ? t.depends_on.filter(d => d !== depIdx) : [...t.depends_on, depIdx] };
        }));

    const canSubmit = projectTitle.trim() && tasks.every(
        t => t.title.trim() && t.title_ru.trim() && t.description.trim() && t.description_ru.trim()
    );

    const submit = () => onSubmit({
        project_title: projectTitle,
        project_description: projectDescription,
        tasks: tasks.map((t, idx) => ({
            assigned_student_id: team.members[idx].student_id,
            title: t.title, title_ru: t.title_ru,
            description: t.description, description_ru: t.description_ru,
            required_level: t.required_level,
            acceptance_criteria: t.acceptance_criteria_text.split('\n').map(s => s.trim()).filter(Boolean),
            depends_on: t.depends_on,
            estimated_hours: Number(t.estimated_hours) || 4,
        })),
    });

    return (
        <div className="ttd-manual-plan">
            <h4>Qo'lda reja tuzish</h4>
            <p className="ttp-muted">
                AI yoqilmagan yoki urinishlar tugagan holatlar uchun — loyiha va har bir a'zoning
                vazifasini qo'lda kiriting.
            </p>
            <label className="ttp-field">
                <span>Loyiha nomi</span>
                <input value={projectTitle} onChange={e => setProjectTitle(e.target.value)} />
            </label>
            <label className="ttp-field">
                <span>Loyiha tavsifi</span>
                <input value={projectDescription} onChange={e => setProjectDescription(e.target.value)} />
            </label>

            {team.members.map((m, idx) => {
                const allowedLevels = LEVELS.filter(l => LEVEL_RANK[l] <= LEVEL_RANK[m.level_at_assignment]);
                const task = tasks[idx];
                return (
                    <div key={m.student_id} className="ttd-manual-task">
                        <h5>{m.full_name} <span className="ttp-muted">({m.level_at_assignment})</span></h5>
                        <label className="ttp-field">
                            <span>Vazifa nomi</span>
                            <input value={task.title} onChange={e => updateTask(idx, { title: e.target.value })} />
                        </label>
                        <label className="ttp-field">
                            <span>Vazifa nomi (ru)</span>
                            <input value={task.title_ru} onChange={e => updateTask(idx, { title_ru: e.target.value })} />
                        </label>
                        <label className="ttp-field">
                            <span>Tavsif</span>
                            <input value={task.description} onChange={e => updateTask(idx, { description: e.target.value })} />
                        </label>
                        <label className="ttp-field">
                            <span>Tavsif (ru)</span>
                            <input value={task.description_ru} onChange={e => updateTask(idx, { description_ru: e.target.value })} />
                        </label>
                        <label className="ttp-field">
                            <span>Daraja</span>
                            <select value={task.required_level} onChange={e => updateTask(idx, { required_level: e.target.value })}>
                                {allowedLevels.map(l => <option key={l} value={l}>{l}</option>)}
                            </select>
                        </label>
                        <label className="ttp-field">
                            <span>Taxminiy soat</span>
                            <input type="number" min={1} value={task.estimated_hours}
                                   onChange={e => updateTask(idx, { estimated_hours: e.target.value })} />
                        </label>
                        <label className="ttp-field">
                            <span>Qabul mezonlari (har birini yangi qatordan)</span>
                            <textarea value={task.acceptance_criteria_text}
                                      onChange={e => updateTask(idx, { acceptance_criteria_text: e.target.value })} />
                        </label>
                        {team.members.length > 1 && (
                            <div className="ttd-depends-on">
                                <span className="ttp-muted">Bog'liq bo'lgan vazifalar (avval bajarilishi kerak):</span>
                                <div className="ttd-depends-chips">
                                    {team.members.map((other, otherIdx) => otherIdx !== idx && (
                                        <label key={other.student_id} className="ttd-depends-chip">
                                            <input
                                                type="checkbox"
                                                checked={task.depends_on.includes(otherIdx)}
                                                onChange={() => toggleDependsOn(idx, otherIdx)}
                                            />
                                            {other.full_name}
                                        </label>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                );
            })}

            {error && <p className="ttp-error">{error}</p>}

            <div className="ttd-manual-actions">
                <button className="ttp-btn ttp-btn--ghost ttp-btn--sm" onClick={onCancel} disabled={submitting}>
                    Bekor qilish
                </button>
                <button className="ttp-btn ttp-btn--primary ttp-btn--sm" disabled={!canSubmit || submitting} onClick={submit}>
                    {submitting ? 'Saqlanmoqda…' : 'Rejani saqlash'}
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
    const [manualPlanTeamId, setManualPlanTeamId] = useState(null);
    const [manualPlanSubmitting, setManualPlanSubmitting] = useState(false);
    const [manualPlanError, setManualPlanError] = useState('');

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

    const submitManualPlan = async (teamId, body) => {
        setManualPlanSubmitting(true);
        setManualPlanError('');
        try {
            await request(
                `${API_URL}v1/team-projects/teams/${teamId}/manual-plan`,
                'POST', JSON.stringify(body), headers(),
            );
            setManualPlanTeamId(null);
            await reload();
        } catch (e) {
            setManualPlanError(extractErrorMessage(e));
        } finally {
            setManualPlanSubmitting(false);
        }
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

                    <div className="ttd-plan-actions">
                        {team.generation_attempts < 3 && (
                            <button
                                className="ttp-btn ttp-btn--ghost ttp-btn--sm"
                                onClick={() => regenerate(team.id)}
                            >
                                Rejani qayta yaratish ({team.generation_attempts}/3)
                            </button>
                        )}
                        {team.status === 'forming' && team.tasks.length === 0 && manualPlanTeamId !== team.id && (
                            <button
                                className="ttp-btn ttp-btn--ghost ttp-btn--sm"
                                onClick={() => { setManualPlanTeamId(team.id); setManualPlanError(''); }}
                            >
                                Qo'lda reja tuzish
                            </button>
                        )}
                    </div>

                    {manualPlanTeamId === team.id && (
                        <ManualPlanForm
                            team={team}
                            submitting={manualPlanSubmitting}
                            error={manualPlanError}
                            onCancel={() => { setManualPlanTeamId(null); setManualPlanError(''); }}
                            onSubmit={body => submitManualPlan(team.id, body)}
                        />
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
