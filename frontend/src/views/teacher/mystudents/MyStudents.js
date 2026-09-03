import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import './MyStudents.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

/* Namespaced like AssignStudentsModal's `key={`group-${g.id}`}` — group and
 * flow ids are separate tables and can collide numerically, so the filter
 * value has to carry which container it means. */
const optionValue = (kind, id) => `${kind}-${id}`;

/* Class names are "0 blu" / "1-blue" / "10-green" — sorting them as plain
 * strings puts "10-blue" right after "1-blue" and before "2-blue". Pull the
 * leading number out instead so the order matches how the classes are
 * actually numbered. A name with no leading digits sorts to the end rather
 * than colliding at 0. */
const classNumber = (name) => {
  const m = /^\D*(\d+)/.exec(name || '');
  return m ? Number(m[1]) : Infinity;
};

/* ─── Main ───
 * Flat, filterable roster — one row per student, not per group. Reuses the
 * exact same teacher-scoped /groups/ and /flows/ endpoints the group-cards
 * view (now at /teacher/groups, see MyGroups.js) already fetches; both
 * already nest each container's own students, so no new backend endpoint
 * was needed to build this list or its group filter. */
const MyStudents = () => {
  const { request } = useHttp();
  const navigate = useNavigate();

  const [groups,  setGroups]  = useState([]);
  const [flows,   setFlows]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [search,  setSearch]  = useState('');
  const [classFilter, setClassFilter] = useState('all');
  const [sortDir, setSortDir] = useState('asc');

  useEffect(() => {
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

  const classOptions = useMemo(() => [
    ...groups.map(g => ({ value: optionValue('group', g.id), label: g.name, icon: '🏫' })),
    ...flows.map(f => ({ value: optionValue('flow', f.id), label: f.name, icon: '🧩' })),
  ], [groups, flows]);

  /* One row per unique student — a student in more than one group/flow
   * (e.g. a homeroom group plus an IT-subject flow) gets every class name
   * it belongs to joined in the Class column, matching how
   * AssignStudentsModal already renders multi-group membership, rather
   * than duplicating that student into several rows. minClassNumber is the
   * lowest of those (a student in "1-blue" and "10-blue" sorts under 1). */
  const allStudents = useMemo(() => {
    const byId = new Map();
    const addFrom = (container, kind, icon) => {
      const optValue = optionValue(kind, container.id);
      const num = classNumber(container.name);
      (container.students || []).forEach(s => {
        let row = byId.get(s.id);
        if (!row) {
          row = { ...s, classNames: [], classValues: new Set(), minClassNumber: Infinity };
          byId.set(s.id, row);
        }
        row.classNames.push(`${icon} ${container.name}`);
        row.classValues.add(optValue);
        row.minClassNumber = Math.min(row.minClassNumber, num);
      });
    };
    groups.forEach(g => addFrom(g, 'group', '🏫'));
    flows.forEach(f => addFrom(f, 'flow', '🧩'));
    return [...byId.values()];
  }, [groups, flows]);

  const filteredStudents = useMemo(() => {
    const q = search.trim().toLowerCase();
    const rows = allStudents.filter(s => {
      if (classFilter !== 'all' && !s.classValues.has(classFilter)) return false;
      if (!q) return true;
      return (
        (s.full_name || '').toLowerCase().includes(q) ||
        (s.surname   || '').toLowerCase().includes(q) ||
        (s.username  || '').toLowerCase().includes(q)
      );
    });
    const sign = sortDir === 'asc' ? 1 : -1;
    return rows.sort((a, b) => sign * (a.minClassNumber - b.minClassNumber));
  }, [allStudents, search, classFilter, sortDir]);

  const handleOpenStudent = (studentId) => {
    navigate(`/teacher/students/${studentId}`);
  };

  return (
    <div className="ms-container">
      <div className="ms-header">
        <div>
          <h2>Мои студенты</h2>
          <p className="ms-subtitle">Все ваши студенты в Gennis</p>
        </div>
      </div>

      <div className="ms-filters">
        <div className="ms-search-wrap">
          <span className="ms-search-icon">🔍</span>
          <input
            className="ms-search"
            placeholder="Ism / familiya / username bo'yicha qidirish..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          {search && (
            <button className="ms-search-clear" onClick={() => setSearch('')}>✕</button>
          )}
        </div>

        <select
          className="ms-class-filter"
          value={classFilter}
          onChange={e => setClassFilter(e.target.value)}
        >
          <option value="all">Barcha guruhlar</option>
          {classOptions.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.icon} {opt.label}</option>
          ))}
        </select>
      </div>

      <div className="ms-stats-row">
        <div className="ms-stat-chip">👥 Talabalar: {filteredStudents.length}</div>
      </div>

      {loading ? (
        <div className="ms-loading">
          <div className="ms-spinner" />
          <span>Ma'lumotlar yuklanmoqda...</span>
        </div>
      ) : filteredStudents.length === 0 ? (
        <div className="ms-empty-row">Talabalar topilmadi</div>
      ) : (
        <div className="ms-student-table">
          <div className="ms-student-table-head">
            <span>Ism</span>
            <span>Familiya</span>
            <span>Username</span>
            <button
              type="button"
              className="ms-sort-btn"
              onClick={() => setSortDir(d => (d === 'asc' ? 'desc' : 'asc'))}
              title="Sinf raqami bo'yicha tartibni almashtirish"
            >
              Sinf <span className={`ms-sort-arrow ${sortDir}`}>▲</span>
            </button>
          </div>
          <div className="ms-student-table-body">
            {filteredStudents.map(s => (
              <div
                key={s.id}
                className="ms-student-table-row"
                onClick={() => handleOpenStudent(s.id)}
              >
                <span className="ms-std-name">{s.full_name || s.username || '—'}</span>
                <span>{s.surname || '—'}</span>
                <span className="ms-std-username">@{s.username}</span>
                <span className="ms-std-class">{s.classNames.join(', ')}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MyStudents;
