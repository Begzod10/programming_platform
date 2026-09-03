import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import '../mystudents/MyStudents.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

/* ─── helpers ─── */
const balanceColor = (b) => {
  if (b < 0)       return 'neg';
  if (b < 100000)  return 'warn';
  return 'pos';
};
const fmt = (n) =>
  new Intl.NumberFormat('uz-UZ').format(n) + ' so\'m';

/* ─── StudentRow ─── */
const StudentRow = ({ student, onOpen }) => {
  const bc = balanceColor(student.balance);
  const displayName = student.full_name || student.username || '—';
  const words = displayName.trim().split(/\s+/);
  const initials = words.slice(0, 2).map(w => w[0]).join('').toUpperCase();

  return (
    <div className="ms-student-row" onClick={() => onOpen(student.id)} style={{ cursor: 'pointer' }}>
      <div className="ms-sr-avatar">{initials}</div>
      <div className="ms-sr-info">
        <span className="ms-sr-name">{displayName}</span>
        <span className="ms-sr-phone">📱 {student.phone}</span>
      </div>
      <div className={`ms-sr-balance ${bc}`}>{fmt(student.balance)}</div>
    </div>
  );
};

/* ─── GroupCard ───
 * Also used for Flow — turon's second, independent student container (see
 * backend/app/models/flow.py). A Flow has no price, so `group.price` is
 * simply undefined for one and the 💰 segment is omitted. */
const GroupCard = ({ group, onOpenStudent, icon = '🏫' }) => {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');

  const students = group.students || [];
  const filtered = students.filter(s => {
    const q = search.toLowerCase();
    return (
      (s.full_name || s.username || '').toLowerCase().includes(q) ||
      (s.phone   || '').includes(q)
    );
  });

  const totalBalance = students.reduce((sum, s) => sum + (s.balance || 0), 0);
  const hasPrice = group.price !== undefined && group.price !== null;

  return (
    <div className={`ms-group-card ${open ? 'expanded' : ''}`}>
      <div className="ms-group-header" onClick={() => setOpen(o => !o)}>
        <div className="ms-group-left">
          <div className="ms-group-icon">{icon}</div>
          <div className="ms-group-meta">
            <span className="ms-group-name">{group.name}</span>
            <span className="ms-group-sub">
              👥 {students.length} talaba{hasPrice ? ` · 💰 ${fmt(group.price)}` : ''}
            </span>
          </div>
        </div>
        <div className="ms-group-right">
          <span className={`ms-total-balance ${balanceColor(totalBalance)}`}>
            {fmt(totalBalance)}
          </span>
          <span className={`ms-chevron ${open ? 'open' : ''}`}>▾</span>
        </div>
      </div>

      {open && (
        <div className="ms-group-body">
          {students.length > 4 && (
            <div className="ms-group-search-wrap">
              <span className="ms-search-icon">🔍</span>
              <input
                className="ms-group-search"
                placeholder="Talabani qidirish..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                onClick={e => e.stopPropagation()}
              />
              {search && (
                <button className="ms-search-clear" onClick={() => setSearch('')}>✕</button>
              )}
            </div>
          )}

          {filtered.length === 0 ? (
            <div className="ms-no-students">Talabalar topilmadi</div>
          ) : (
            <div className="ms-students-list">
              {filtered.map(s => (
                <StudentRow key={s.id} student={s} onOpen={onOpenStudent} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/* ─── Main ───
 * The group-cards view that used to live at /teacher/students — split out
 * to its own page (Мои Группы) once /teacher/students became the flat,
 * filterable student list. Fetches the exact same teacher-scoped
 * groups/flows the old page did; nothing changed backend-side. */
const MyGroups = () => {
  const { request } = useHttp();
  const navigate = useNavigate();

  const [groups,  setGroups]  = useState([]);
  // Turon-only — a subject teacher reachable ONLY through a Flow (never set
  // as a group's own teacher) still needs to show up here. Always [] for a
  // gennis-only account. See backend/app/models/flow.py.
  const [flows,   setFlows]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [search,  setSearch]  = useState('');

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.all([
      request(`${API_URL}v1/groups/`, 'GET', null, headers()).catch(() => []),
      request(`${API_URL}v1/flows/`, 'GET', null, headers()).catch(() => []),
    ])
      .then(([groupsData, flowsData]) => {
        setGroups(Array.isArray(groupsData) ? groupsData : []);
        setFlows(Array.isArray(flowsData) ? flowsData : []);
      })
      .finally(() => setLoading(false));
  }, [request]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleOpenStudent = (studentId) => {
    navigate(`/teacher/students/${studentId}`);
  };

  const filteredGroups = groups.filter(g =>
    (g.name || '').toLowerCase().includes(search.toLowerCase())
  );
  const filteredFlows = flows.filter(f =>
    (f.name || '').toLowerCase().includes(search.toLowerCase())
  );

  const totalStudents =
    groups.reduce((s, g) => s + (g.students?.length || 0), 0) +
    flows.reduce((s, f) => s + (f.students?.length || 0), 0);

  return (
    <div className="ms-container">
      <div className="ms-header">
        <div>
          <h2>Мои группы</h2>
          <p className="ms-subtitle">Группы и Flow'ы, закреплённые за вами в Gennis</p>
        </div>
      </div>

      <div className="ms-filters">
        <div className="ms-search-wrap">
          <span className="ms-search-icon">🔍</span>
          <input
            className="ms-search"
            placeholder="Guruh nomi bo'yicha qidirish..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          {search && (
            <button className="ms-search-clear" onClick={() => setSearch('')}>✕</button>
          )}
        </div>
      </div>

      <div className="ms-stats-row">
        <div className="ms-stat-chip">🏫 Guruhlar: {groups.length}</div>
        {flows.length > 0 && (
          <div className="ms-stat-chip">🧩 Flow'lar: {flows.length}</div>
        )}
        <div className="ms-stat-chip">👥 Talabalar: {totalStudents}</div>
      </div>

      {loading ? (
        <div className="ms-loading">
          <div className="ms-spinner" />
          <span>Ma'lumotlar yuklanmoqda...</span>
        </div>
      ) : filteredGroups.length === 0 && filteredFlows.length === 0 ? (
        <div className="ms-empty-row">Guruhlar topilmadi</div>
      ) : (
        <div className="ms-groups-list">
          {filteredGroups.map(g => (
            <GroupCard
              key={`group-${g.id}`}
              group={g}
              onOpenStudent={handleOpenStudent}
            />
          ))}
          {filteredFlows.map(f => (
            <GroupCard
              key={`flow-${f.id}`}
              group={f}
              onOpenStudent={handleOpenStudent}
              icon="🧩"
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default MyGroups;
