import React, { useState, useEffect, useCallback } from 'react';
import './MyStudents.css';
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
const StudentRow = ({ student }) => {
  const bc = balanceColor(student.balance);
  const initials = `${(student.name || '?')[0]}${(student.surname || '')[0] || ''}`.toUpperCase();

  return (
    <div className="ms-student-row">
      <div className="ms-sr-avatar">{initials}</div>
      <div className="ms-sr-info">
        <span className="ms-sr-name">{student.name} {student.surname}</span>
        <span className="ms-sr-phone">📱 {student.phone}</span>
      </div>
      <div className={`ms-sr-balance ${bc}`}>{fmt(student.balance)}</div>
    </div>
  );
};

/* ─── GroupCard ─── */
const GroupCard = ({ group }) => {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');

  const students = group.students || [];
  const filtered = students.filter(s => {
    const q = search.toLowerCase();
    return (
      (s.name    || '').toLowerCase().includes(q) ||
      (s.surname || '').toLowerCase().includes(q) ||
      (s.phone   || '').includes(q)
    );
  });

  const totalBalance = students.reduce((sum, s) => sum + (s.balance || 0), 0);

  return (
    <div className={`ms-group-card ${open ? 'expanded' : ''}`}>
      <div className="ms-group-header" onClick={() => setOpen(o => !o)}>
        <div className="ms-group-left">
          <div className="ms-group-icon">🏫</div>
          <div className="ms-group-meta">
            <span className="ms-group-name">{group.name}</span>
            <span className="ms-group-sub">
              👥 {students.length} talaba · 💰 {fmt(group.price)}
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
                <StudentRow key={s.id} student={s} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/* ─── Main ─── */
const MyStudents = () => {
  const { request } = useHttp();

  const [groups,  setGroups]  = useState([]);
  const [loading, setLoading] = useState(true);
  const [search,  setSearch]  = useState('');
  const [syncing, setSyncing] = useState(false);

  const loadData = useCallback(() => {
    setLoading(true);
    request(`${API_URL}v1/groups/`, 'GET', null, headers())
      .then(data => setGroups(Array.isArray(data) ? data : []))
      .catch(() => setGroups([]))
      .finally(() => setLoading(false));
  }, [request]);

  useEffect(() => {
    loadData();
  }, [loadData]);


  const filteredGroups = groups.filter(g =>
    (g.name || '').toLowerCase().includes(search.toLowerCase())
  );

  const totalStudents = groups.reduce((s, g) => s + (g.students?.length || 0), 0);

  return (
    <div className="ms-container">
      <div className="ms-header">
        <div>
          <h2>Mening talabalarim</h2>
          <p className="ms-subtitle">Gennis'dagi guruhlar va talabalar</p>
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
        <div className="ms-stat-chip">👥 Talabalar: {totalStudents}</div>
      </div>

      {loading && !syncing ? (
        <div className="ms-loading">
          <div className="ms-spinner" />
          <span>Ma'lumotlar yuklanmoqda...</span>
        </div>
      ) : filteredGroups.length === 0 ? (
        <div className="ms-empty-row">Guruhlar topilmadi</div>
      ) : (
        <div className="ms-groups-list">
          {filteredGroups.map(g => (
            <GroupCard key={g.id} group={g} />
          ))}
        </div>
      )}
    </div>
  );
};

export default MyStudents;