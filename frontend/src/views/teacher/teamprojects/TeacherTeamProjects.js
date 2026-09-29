import { useCallback, useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { isStuckWithNoManualPlan } from './isStuckWithNoManualPlan';
import './TeacherTeamProjects.css';

const CreateModal = ({ onClose, onCreated }) => {
    const { request } = useHttp();
    const [groups, setGroups] = useState([]);
    const [groupId, setGroupId] = useState('');
    const [teamSize, setTeamSize] = useState(4);
    const [deadlineDays, setDeadlineDays] = useState(14);
    // Explicit per-student opt-in, keyed by student_id — NOT derived from
    // groupId at submit time. A teacher picks a primary group (still
    // required: group_id is the FK team_project rows hang off, and the
    // "one active assignment per group" check uses it), then can uncheck
    // anyone who won't be participating this round, or check students in
    // from one of their OTHER groups too — see backend/create_team_project's
    // docstring on why student_ids no longer has to equal group.students.
    const [selected, setSelected] = useState({});
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        request(`${API_URL}v1/groups/`, 'GET', null, headers())
            .then(data => setGroups(Array.isArray(data) ? data : []))
            .catch(() => {});
    }, [request]);

    // Picking a primary group is a convenience default, not a constraint:
    // check every one of its students, but leave any other group's
    // checkboxes (from a previous pick) exactly as the teacher left them.
    const chooseGroup = (id) => {
        setGroupId(id);
        const group = groups.find(g => String(g.id) === String(id));
        if (!group) return;
        setSelected(prev => {
            const next = { ...prev };
            for (const s of group.students || []) next[s.id] = true;
            return next;
        });
    };

    const toggleStudent = (studentId) => {
        setSelected(prev => ({ ...prev, [studentId]: !prev[studentId] }));
    };

    const selectedIds = Object.keys(selected).filter(id => selected[id]).map(Number);
    const selectedCount = selectedIds.length;

    const submit = async () => {
        if (!groupId) { setError("Guruhni tanlang"); return; }
        if (selectedCount < 2) { setError("Kamida 2 ta o'quvchi tanlang"); return; }
        setBusy(true);
        setError(null);
        try {
            await request(`${API_URL}v1/team-projects`, 'POST', JSON.stringify({
                group_id: Number(groupId),
                team_size: Number(teamSize),
                deadline_days: Number(deadlineDays),
                student_ids: selectedIds,
            }), headers());
            onCreated();
            onClose();
        } catch (e) {
            // Prefer the clean backend message over useHttp's verbose
            // "Could not fetch <url>, status: N: ..." wrapper — a teacher
            // shouldn't see a URL and status code in a form error banner.
            const backendMessage = e?.response?.data?.error?.message || e?.response?.data?.detail;
            setError(backendMessage || "Topshiriq yaratib bo'lmadi");
        } finally {
            setBusy(false);
        }
    };

    return ReactDOM.createPortal(
        <div className="ttp-overlay" onClick={onClose}>
            <div className="ttp-modal ttp-modal--wide" onClick={e => e.stopPropagation()}>
                <header className="ttp-modal-head">
                    <h3>Jamoaviy loyiha topshirig'i</h3>
                    <button className="ttp-close" onClick={onClose}>✕</button>
                </header>
                <div className="ttp-modal-body">
                    <label className="ttp-field">
                        <span>Asosiy guruh</span>
                        <select value={groupId} onChange={e => chooseGroup(e.target.value)}>
                            <option value="">— tanlang —</option>
                            {groups.map(g => (
                                <option key={g.id} value={g.id}>
                                    {g.name} ({g.students?.length ?? 0} ta o'quvchi)
                                </option>
                            ))}
                        </select>
                    </label>
                    <label className="ttp-field">
                        <span>Jamoa hajmi</span>
                        <input type="number" min={2} max={10} value={teamSize}
                               onChange={e => setTeamSize(e.target.value)} />
                    </label>
                    <label className="ttp-field">
                        <span>Muddat (kun)</span>
                        <input type="number" min={1} max={90} value={deadlineDays}
                               onChange={e => setDeadlineDays(e.target.value)} />
                    </label>

                    {groups.length > 0 && (
                        <div className="ttp-field">
                            <span>
                                O'quvchilarni tanlang ({selectedCount} ta tanlandi) — ishtirok
                                etmaydiganlarni belgidan chiqaring, kerak bo'lsa boshqa
                                guruhdan ham qo'shing
                            </span>
                            <div className="ttp-student-picker">
                                {groups.map(g => (
                                    <div key={g.id} className="ttp-student-picker-group">
                                        <div className="ttp-student-picker-group-name">{g.name}</div>
                                        {(g.students || []).length === 0 && (
                                            <p className="ttp-muted">O'quvchilar yo'q</p>
                                        )}
                                        {(g.students || []).map(s => (
                                            <label key={s.id} className="ttp-student-checkbox">
                                                <input
                                                    type="checkbox"
                                                    checked={!!selected[s.id]}
                                                    onChange={() => toggleStudent(s.id)}
                                                />
                                                {s.full_name || s.username}
                                            </label>
                                        ))}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {error && <div className="ttp-error">{error}</div>}
                </div>
                <footer className="ttp-modal-foot">
                    <button className="ttp-btn ttp-btn--ghost" onClick={onClose} disabled={busy}>Bekor qilish</button>
                    <button className="ttp-btn ttp-btn--primary" onClick={submit} disabled={busy}>
                        {busy ? 'Yaratilmoqda…' : 'Yaratish'}
                    </button>
                </footer>
            </div>
        </div>,
        document.body,
    );
};

const STATUS_LABELS = {
    planning: 'Rejalashtirilmoqda', forming: 'Shakillanmoqda', working: 'Ishlanmoqda',
    submitted: 'Topshirilgan', reviewed: 'Baholangan', active: 'Faol',
};

const TeamCard = ({ team, onRegenerate, onOpen, showName = true }) => (
    <div className="ttp-team-card" onClick={() => onOpen()}>
        <div className="ttp-team-head">
            {/* A project with only one team has nothing to distinguish it
                from — "Team 1" repeated on every single-team card's the
                only label read as noise, not information. Multi-team
                projects still need the number. */}
            {showName && <strong>{team.name}</strong>}
            <span className={`ttp-status ttp-status--${team.status}`}>
                {STATUS_LABELS[team.status] || team.status}
            </span>
        </div>
        {isStuckWithNoManualPlan(team) && (
            <div className="ttp-stuck-banner">
                <span aria-hidden="true">⚠️</span> Reja yaratilmadi — qo'lda reja tuzish kerak
            </div>
        )}
        <div className="ttp-team-badges">
            {team.theme_label && <span className="ttp-badge">{team.theme_label}</span>}
            {team.tech_stack_label && <span className="ttp-badge ttp-badge--tech">{team.tech_stack_label}</span>}
        </div>
        {team.project_title && <p className="ttp-project-title">{team.project_title}</p>}
        <div className="ttp-members">
            {team.members.map(m => (
                <span key={m.student_id} className={`ttp-member${m.role === 'lead' ? ' ttp-member--lead' : ''}`}>
                    {m.full_name}{m.role === 'lead' ? ' 👑' : ''}
                </span>
            ))}
        </div>
        {team.tasks.length > 0 && (
            <ul className="ttp-tasks">
                {team.tasks.map(t => (
                    <li key={t.id}>
                        <span className={`ttp-task-dot ttp-task-dot--${t.status}`} />
                        {t.title} — <em>{t.assigned_student_name}</em>
                    </li>
                ))}
            </ul>
        )}
        {team.generation_attempts < 3 && (
            <button
                className="ttp-btn ttp-btn--ghost ttp-btn--sm"
                onClick={e => { e.stopPropagation(); onRegenerate(team.id); }}
            >
                Rejani qayta yaratish ({team.generation_attempts}/3)
            </button>
        )}
    </div>
);

const TeacherTeamProjects = () => {
    const navigate = useNavigate();
    const { request } = useHttp();
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);

    const reload = useCallback(async () => {
        setLoading(true);
        try {
            const data = await request(`${API_URL}v1/team-projects`, 'GET', null, headers());
            setAssignments(Array.isArray(data) ? data : []);
        } catch {
            setAssignments([]);
        } finally {
            setLoading(false);
        }
    }, [request]);

    useEffect(() => { reload(); }, [reload]);

    const regenerate = async (teamId) => {
        try {
            await request(`${API_URL}v1/team-projects/teams/${teamId}/regenerate`, 'POST', null, headers());
            await reload();
        } catch {}
    };

    return (
        <div className="ttp-page">
            <div className="ttp-page-head">
                <h2>Jamoaviy loyihalar</h2>
                <button className="ttp-btn ttp-btn--primary" onClick={() => setShowCreate(true)}>
                    + Yangi topshiriq
                </button>
            </div>

            {loading && <p className="ttp-muted">Yuklanmoqda…</p>}
            {!loading && assignments.length === 0 && (
                <p className="ttp-muted">Hali topshiriq yaratilmagan.</p>
            )}

            <div className="ttp-assignments-row">
                {assignments.map(tp => (
                    <div key={tp.id} className="ttp-assignment">
                        <div className="ttp-assignment-head">
                            <span>#{tp.id} · {STATUS_LABELS[tp.status] || tp.status}</span>
                            <span className="ttp-muted">{tp.teams.length} ta jamoa</span>
                        </div>
                        <div className="ttp-team-grid">
                            {tp.teams.map(team => (
                                <TeamCard
                                    key={team.id} team={team} onRegenerate={regenerate}
                                    onOpen={() => navigate(`/teacher/team-projects/${tp.id}`)}
                                    showName={tp.teams.length > 1}
                                />
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {showCreate && (
                <CreateModal onClose={() => setShowCreate(false)} onCreated={reload} />
            )}
        </div>
    );
};

export default TeacherTeamProjects;
