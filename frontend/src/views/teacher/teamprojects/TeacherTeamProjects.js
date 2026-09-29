import { useCallback, useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { isStuckWithNoManualPlan } from './isStuckWithNoManualPlan';
import './TeacherTeamProjects.css';

// Deterministic pastel-on-dark avatar color, picked from the name so the
// same student always gets the same color across renders/reloads rather
// than a random one that would flicker on every re-render.
const AVATAR_PALETTE = [
    ['#ede9fe', '#6d28d9'], ['#fef3c7', '#b45309'], ['#dbeafe', '#1d4ed8'],
    ['#dcfce7', '#15803d'], ['#fce7f3', '#be185d'], ['#e0f2fe', '#0369a1'],
];
const avatarColors = (name) => {
    let hash = 0;
    for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) >>> 0;
    return AVATAR_PALETTE[hash % AVATAR_PALETTE.length];
};
const initials = (name) => (name || '?').trim().split(/\s+/).slice(0, 2).map(w => w[0]).join('').toUpperCase();

const CreateModal = ({ onClose, onCreated }) => {
    const { request } = useHttp();
    const [groups, setGroups] = useState([]);
    // groupId is a FILTER/quick-select convenience only — picking one just
    // bulk-checks its students, it is NOT required to submit and does not
    // have to match who ends up selected. The actual group_id sent to the
    // backend (still a required FK there — see create_team_project) is
    // derived from the selection itself at submit time (whichever group
    // most of the picked students belong to), never from this dropdown.
    const [groupId, setGroupId] = useState('');
    const [teamSize, setTeamSize] = useState(4);
    const [deadlineDays, setDeadlineDays] = useState(14);
    const [selected, setSelected] = useState({});
    const [search, setSearch] = useState('');
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        request(`${API_URL}v1/groups/`, 'GET', null, headers())
            .then(data => setGroups(Array.isArray(data) ? data : []))
            .catch(() => {});
    }, [request]);

    // Quick-select: bulk-check a group's students. Leaves any other
    // group's checkboxes (from a previous pick) exactly as they were.
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

    const setGroupAll = (group, value) => {
        setSelected(prev => {
            const next = { ...prev };
            for (const s of group.students || []) next[s.id] = value;
            return next;
        });
    };

    const selectedIds = Object.keys(selected).filter(id => selected[id]).map(Number);
    const selectedCount = selectedIds.length;
    const query = search.trim().toLowerCase();
    const matches = (s) => !query || (s.full_name || s.username || '').toLowerCase().includes(query);

    // The backend still needs ONE group_id (its FK, and the "one active
    // assignment per group" collision check) — but the teacher is picking
    // people, not a group, so derive it instead of asking for it: whichever
    // of the teacher's groups has the most students in common with the
    // current selection wins. Ties go to whichever group comes first in
    // `groups` (stable, not random) — with real rosters a tie across two
    // full groups is vanishingly rare, and this only decides bookkeeping,
    // never who's on the team.
    const inferGroupId = () => {
        let bestId = null;
        let bestCount = -1;
        for (const g of groups) {
            const count = (g.students || []).filter(s => selected[s.id]).length;
            if (count > bestCount) { bestCount = count; bestId = g.id; }
        }
        return bestId;
    };

    const submit = async () => {
        if (selectedCount < 2) { setError("Kamida 2 ta o'quvchi tanlang"); return; }
        // Always derived fresh from the final selection — the dropdown is
        // just a filter to bulk-check a group, so a teacher who quick-picked
        // one group and then hand-edited the selection afterward should not
        // have that first click silently win over what they actually chose.
        const derivedGroupId = inferGroupId();
        if (!derivedGroupId) { setError("Kamida bitta o'quvchi biror guruhga tegishli bo'lishi kerak"); return; }
        setBusy(true);
        setError(null);
        try {
            await request(`${API_URL}v1/team-projects`, 'POST', JSON.stringify({
                group_id: Number(derivedGroupId),
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
            <div className="ttp-modal ttp-modal--wide ttp-modal--create" onClick={e => e.stopPropagation()}>
                <header className="ttp-modal-head ttp-modal-head--accent">
                    <div>
                        <h3>Jamoaviy loyiha topshirig'i</h3>
                        <p className="ttp-modal-subtitle">Pastda ishtirokchilarni o'zingiz belgilang</p>
                    </div>
                    <button className="ttp-close" onClick={onClose}>✕</button>
                </header>
                <div className="ttp-modal-body">
                    <div className="ttp-form-row">
                        <label className="ttp-field">
                            <span>Guruh bo'yicha tezkor tanlash (ixtiyoriy)</span>
                            <select value={groupId} onChange={e => chooseGroup(e.target.value)}>
                                <option value="">— guruh tanlab, hammasini belgilash —</option>
                                {groups.map(g => (
                                    <option key={g.id} value={g.id}>
                                        {g.name} ({g.students?.length ?? 0} ta o'quvchi)
                                    </option>
                                ))}
                            </select>
                        </label>
                        <label className="ttp-field ttp-field--sm">
                            <span>Jamoa hajmi</span>
                            <input type="number" min={2} max={10} value={teamSize}
                                   onChange={e => setTeamSize(e.target.value)} />
                        </label>
                        <label className="ttp-field ttp-field--sm">
                            <span>Muddat (kun)</span>
                            <input type="number" min={1} max={90} value={deadlineDays}
                                   onChange={e => setDeadlineDays(e.target.value)} />
                        </label>
                    </div>

                    {groups.length > 0 && (
                        <div className="ttp-field">
                            <div className="ttp-picker-label-row">
                                <span>O'quvchilarni tanlang</span>
                                <span className={`ttp-selected-pill${selectedCount < 2 ? ' ttp-selected-pill--warn' : ''}`}>
                                    {selectedCount} ta tanlandi
                                </span>
                            </div>
                            <p className="ttp-picker-hint">
                                Ishtirok etmaydiganlarni belgidan chiqaring, kerak bo'lsa boshqa guruhdan ham qo'shing.
                            </p>
                            <input
                                className="ttp-search"
                                placeholder="🔍 Ism bo'yicha qidirish…"
                                value={search}
                                onChange={e => setSearch(e.target.value)}
                            />
                            <div className="ttp-student-picker">
                                {groups.map(g => {
                                    const visible = (g.students || []).filter(matches);
                                    if (query && visible.length === 0) return null;
                                    const allChecked = (g.students || []).length > 0
                                        && (g.students || []).every(s => selected[s.id]);
                                    return (
                                        <div key={g.id} className="ttp-student-picker-group">
                                            <div className="ttp-student-picker-group-head">
                                                <span className="ttp-student-picker-group-name">{g.name}</span>
                                                {(g.students || []).length > 0 && (
                                                    <button
                                                        type="button"
                                                        className="ttp-select-all-btn"
                                                        onClick={() => setGroupAll(g, !allChecked)}
                                                    >
                                                        {allChecked ? 'Hammasini bekor qilish' : 'Hammasini tanlash'}
                                                    </button>
                                                )}
                                            </div>
                                            {(g.students || []).length === 0 && (
                                                <p className="ttp-muted">O'quvchilar yo'q</p>
                                            )}
                                            <div className="ttp-student-grid">
                                                {visible.map(s => {
                                                    const name = s.full_name || s.username;
                                                    const [bg, fg] = avatarColors(name);
                                                    const checked = !!selected[s.id];
                                                    return (
                                                        <label
                                                            key={s.id}
                                                            className={`ttp-student-chip${checked ? ' ttp-student-chip--on' : ''}`}
                                                        >
                                                            <input
                                                                type="checkbox"
                                                                checked={checked}
                                                                onChange={() => toggleStudent(s.id)}
                                                            />
                                                            <span
                                                                className="ttp-student-avatar"
                                                                style={{ background: bg, color: fg }}
                                                            >
                                                                {initials(name)}
                                                            </span>
                                                            <span className="ttp-student-chip-name">{name}</span>
                                                            <span className="ttp-student-chip-check" aria-hidden="true">✓</span>
                                                        </label>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    );
                                })}
                                {query && groups.every(g => (g.students || []).filter(matches).length === 0) && (
                                    <p className="ttp-muted ttp-no-results">
                                        "{search}" bo'yicha hech kim topilmadi
                                    </p>
                                )}
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
