import { useCallback, useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import './TeacherTeamProjects.css';

const CreateModal = ({ onClose, onCreated }) => {
    const { request } = useHttp();
    const [groups, setGroups] = useState([]);
    const [groupId, setGroupId] = useState('');
    const [teamSize, setTeamSize] = useState(4);
    const [deadlineDays, setDeadlineDays] = useState(14);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        request(`${API_URL}v1/groups/`, 'GET', null, headers())
            .then(data => setGroups(Array.isArray(data) ? data : []))
            .catch(() => {});
    }, [request]);

    const submit = async () => {
        if (!groupId) { setError("Guruhni tanlang"); return; }
        setBusy(true);
        setError(null);
        try {
            await request(`${API_URL}v1/team-projects`, 'POST', JSON.stringify({
                group_id: Number(groupId),
                team_size: Number(teamSize),
                deadline_days: Number(deadlineDays),
            }), headers());
            onCreated();
            onClose();
        } catch (e) {
            setError(e?.message || "Topshiriq yaratib bo'lmadi");
        } finally {
            setBusy(false);
        }
    };

    return ReactDOM.createPortal(
        <div className="ttp-overlay" onClick={onClose}>
            <div className="ttp-modal" onClick={e => e.stopPropagation()}>
                <header className="ttp-modal-head">
                    <h3>Jamoaviy loyiha topshirig'i</h3>
                    <button className="ttp-close" onClick={onClose}>✕</button>
                </header>
                <div className="ttp-modal-body">
                    <label className="ttp-field">
                        <span>Guruh</span>
                        <select value={groupId} onChange={e => setGroupId(e.target.value)}>
                            <option value="">— tanlang —</option>
                            {groups.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
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

const TeamCard = ({ team, onRegenerate }) => (
    <div className="ttp-team-card">
        <div className="ttp-team-head">
            <strong>{team.name}</strong>
            <span className={`ttp-status ttp-status--${team.status}`}>
                {STATUS_LABELS[team.status] || team.status}
            </span>
        </div>
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
            <button className="ttp-btn ttp-btn--ghost ttp-btn--sm" onClick={() => onRegenerate(team.id)}>
                Rejani qayta yaratish ({team.generation_attempts}/3)
            </button>
        )}
    </div>
);

const TeacherTeamProjects = () => {
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

            {assignments.map(tp => (
                <div key={tp.id} className="ttp-assignment">
                    <div className="ttp-assignment-head">
                        <span>#{tp.id} · {STATUS_LABELS[tp.status] || tp.status}</span>
                        <span className="ttp-muted">{tp.teams.length} ta jamoa</span>
                    </div>
                    <div className="ttp-team-grid">
                        {tp.teams.map(team => (
                            <TeamCard key={team.id} team={team} onRegenerate={regenerate} />
                        ))}
                    </div>
                </div>
            ))}

            {showCreate && (
                <CreateModal onClose={() => setShowCreate(false)} onCreated={reload} />
            )}
        </div>
    );
};

export default TeacherTeamProjects;
