// import React, { useState, useEffect, useCallback } from 'react';
// import ReactDOM from 'react-dom';
// import './MyStudents.css';
// import { API_URL, useHttp, headers } from '../../../api/search/base';
//
// const AVATARS = ['👤','👩‍💻','👨‍💻','👩‍🎓','👨‍🎓','🧑‍💻','👩‍🔬','👨‍🔬'];
// const EMPTY   = { name:'', username:'', email:'', password:'', avatar:'👤' };
//
// /* ─── helpers ─── */
// const balanceColor = (b) => {
//   if (b < 0)       return 'neg';
//   if (b < 100000)  return 'warn';
//   return 'pos';
// };
// const fmt = (n) =>
//   new Intl.NumberFormat('ru-RU').format(n) + ' сум';
//
// /* ─── StudentModal ─── */
// const StudentModal = ({ student, onSave, onClose, saving, error }) => {
//   const isEdit = !!student;
//   const [form, setForm] = useState(
//     isEdit
//       ? { name: student.full_name || '', username: student.username || '',
//           email: student.email || '', password: '', avatar: student.avatar_url || '👤' }
//       : { ...EMPTY }
//   );
//   const [errors, setErrors] = useState({});
//
//   useEffect(() => {
//     const h = (e) => { if (e.key === 'Escape') onClose(); };
//     document.addEventListener('keydown', h);
//     return () => document.removeEventListener('keydown', h);
//   }, [onClose]);
//
//   useEffect(() => {
//     document.body.style.overflow = 'hidden';
//     return () => { document.body.style.overflow = ''; };
//   }, []);
//
//   const set = (k, v) => setForm(f => ({ ...f, [k]: v }));
//
//   const validate = () => {
//     const e = {};
//     if (!form.username.trim()) e.username = 'Введите логин';
//     if (!form.email.trim())    e.email    = 'Введите email';
//     else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Неверный email';
//     if (!isEdit && !form.password.trim()) e.password = 'Введите пароль';
//     setErrors(e);
//     return !Object.keys(e).length;
//   };
//
//   return ReactDOM.createPortal(
//     <div className="ms-overlay" onClick={onClose}>
//       <div className="ms-modal" onClick={e => e.stopPropagation()}>
//         <div className="ms-modal-header">
//           <h3>{isEdit ? '✏️ Редактировать студента' : '➕ Новый студент'}</h3>
//           <button className="ms-modal-close" onClick={onClose}>✕</button>
//         </div>
//         <div className="ms-modal-body">
//           {error && <div className="ms-modal-error">{error}</div>}
//           <div className="ms-field">
//             <label>Аватар</label>
//             <div className="ms-avatar-picker">
//               {AVATARS.map(a => (
//                 <button key={a}
//                   className={`ms-avatar-opt ${form.avatar === a ? 'selected' : ''}`}
//                   onClick={() => set('avatar', a)}>{a}</button>
//               ))}
//             </div>
//           </div>
//           <div className="ms-row">
//             <div className="ms-field">
//               <label>Полное имя</label>
//               <input placeholder="Алия Сейткали" value={form.name}
//                 onChange={e => set('name', e.target.value)} />
//             </div>
//             <div className="ms-field">
//               <label>Логин *</label>
//               <input placeholder="aliya123" value={form.username}
//                 onChange={e => set('username', e.target.value)}
//                 className={errors.username ? 'error' : ''} />
//               {errors.username && <span className="ms-error">{errors.username}</span>}
//             </div>
//           </div>
//           <div className="ms-row">
//             <div className="ms-field">
//               <label>Email *</label>
//               <input placeholder="student@email.com" value={form.email}
//                 onChange={e => set('email', e.target.value)}
//                 className={errors.email ? 'error' : ''} />
//               {errors.email && <span className="ms-error">{errors.email}</span>}
//             </div>
//             <div className="ms-field">
//               <label>{isEdit ? 'Новый пароль' : 'Пароль *'}</label>
//               <input type="password" placeholder="••••••••" value={form.password}
//                 onChange={e => set('password', e.target.value)}
//                 className={errors.password ? 'error' : ''} />
//               {errors.password && <span className="ms-error">{errors.password}</span>}
//             </div>
//           </div>
//         </div>
//         <div className="ms-modal-footer">
//           <button className="ms-btn-cancel" onClick={onClose}>Отмена</button>
//           <button className="ms-btn-save" onClick={() => { if (validate()) onSave(form); }}
//             disabled={saving}>
//             {saving ? '⏳...' : isEdit ? '💾 Сохранить' : '✅ Добавить'}
//           </button>
//         </div>
//       </div>
//     </div>,
//     document.body
//   );
// };
//
// /* ─── StudentRow ─── */
// const StudentRow = ({ student, onEdit, onDelete }) => {
//   const bc = balanceColor(student.balance);
//   const initials = `${(student.name || '?')[0]}${(student.surname || '')[0] || ''}`.toUpperCase();
//
//   return (
//     <div className="ms-student-row">
//       <div className="ms-sr-avatar">{initials}</div>
//       <div className="ms-sr-info">
//         <span className="ms-sr-name">{student.name} {student.surname}</span>
//         <span className="ms-sr-phone">📱 {student.phone}</span>
//       </div>
//       <div className={`ms-sr-balance ${bc}`}>{fmt(student.balance)}</div>
//       <div className="ms-sr-actions">
//         <button className="ms-action-btn edit" onClick={() => onEdit(student)}
//           title="Редактировать">✏️</button>
//         <button className="ms-action-btn del" onClick={() => onDelete(student.id)}
//           title="Удалить">🗑️</button>
//       </div>
//     </div>
//   );
// };
//
// /* ─── GroupCard ─── */
// const GroupCard = ({ group, onAddStudent, onEditStudent, onDeleteStudent }) => {
//   const [open, setOpen] = useState(false);
//   const [search, setSearch] = useState('');
//
//   const students = group.students || [];
//   const filtered = students.filter(s => {
//     const q = search.toLowerCase();
//     return (
//       (s.name    || '').toLowerCase().includes(q) ||
//       (s.surname || '').toLowerCase().includes(q) ||
//       (s.phone   || '').includes(q)
//     );
//   });
//
//   const totalBalance = students.reduce((sum, s) => sum + (s.balance || 0), 0);
//
//   return (
//     <div className={`ms-group-card ${open ? 'expanded' : ''}`}>
//       {/* Group header */}
//       <div className="ms-group-header" onClick={() => setOpen(o => !o)}>
//         <div className="ms-group-left">
//           <div className="ms-group-icon">🏫</div>
//           <div className="ms-group-meta">
//             <span className="ms-group-name">{group.name}</span>
//             <span className="ms-group-sub">
//               👥 {students.length} студентов · 💰 {fmt(group.price)}
//             </span>
//           </div>
//         </div>
//         <div className="ms-group-right">
//           <span className={`ms-total-balance ${balanceColor(totalBalance)}`}>
//             {fmt(totalBalance)}
//           </span>
//           <button
//             className="ms-add-student-btn"
//             onClick={e => { e.stopPropagation(); onAddStudent(group); }}
//             title="Добавить студента">
//             ➕
//           </button>
//           <span className={`ms-chevron ${open ? 'open' : ''}`}>▾</span>
//         </div>
//       </div>
//
//       {/* Students list */}
//       {open && (
//         <div className="ms-group-body">
//           {students.length > 4 && (
//             <div className="ms-group-search-wrap">
//               <span className="ms-search-icon">🔍</span>
//               <input
//                 className="ms-group-search"
//                 placeholder="Поиск студента..."
//                 value={search}
//                 onChange={e => setSearch(e.target.value)}
//                 onClick={e => e.stopPropagation()}
//               />
//               {search && (
//                 <button className="ms-search-clear" onClick={() => setSearch('')}>✕</button>
//               )}
//             </div>
//           )}
//
//           {filtered.length === 0 ? (
//             <div className="ms-no-students">Студенты не найдены</div>
//           ) : (
//             <div className="ms-students-list">
//               {filtered.map(s => (
//                 <StudentRow
//                   key={s.id}
//                   student={s}
//                   onEdit={onEditStudent}
//                   onDelete={onDeleteStudent}
//                 />
//               ))}
//             </div>
//           )}
//         </div>
//       )}
//     </div>
//   );
// };
//
// /* ─── Main ─── */
// const MyStudents = () => {
//   const { request } = useHttp();
//
//   const [groups,     setGroups]     = useState([]);
//   const [loading,    setLoading]    = useState(true);
//   const [search,     setSearch]     = useState('');
//   const [modal,      setModal]      = useState(null);
//   const [addGroup,   setAddGroup]   = useState(null);
//   const [confirmId,  setConfirmId]  = useState(null);
//   const [saving,     setSaving]     = useState(false);
//   const [modalError, setModalError] = useState('');
//
//   /* load groups */
//   useEffect(() => {
//     request(`${API_URL}v1/classroom/groups`, 'GET', null, headers())
//       .then(data => setGroups(Array.isArray(data) ? data : []))
//       .catch(() => setGroups([]))
//       .finally(() => setLoading(false));
//   }, []);
//
//   const filteredGroups = groups.filter(g =>
//     (g.name || '').toLowerCase().includes(search.toLowerCase())
//   );
//
//   const totalStudents = groups.reduce((s, g) => s + (g.students?.length || 0), 0);
//
//   /* ── Add / Edit student ── */
//   const handleSave = (form) => {
//     setSaving(true);
//     setModalError('');
//
//     if (modal === 'add') {
//       request(`${API_URL}v1/auth/register`, 'POST', JSON.stringify({
//         full_name: form.name,
//         username:  form.username,
//         email:     form.email,
//         password:  form.password,
//       }))
//         .then(created => {
//           const newStudent = created.user || created;
//           // Добавляем студента в нужную группу локально
//           if (addGroup) {
//             setGroups(gs => gs.map(g =>
//               g.id === addGroup.id
//                 ? { ...g, students: [...(g.students || []), newStudent] }
//                 : g
//             ));
//           }
//           setModal(null);
//           setAddGroup(null);
//         })
//         .catch(() => setModalError('Ошибка. Возможно такой логин или email уже существует.'))
//         .finally(() => setSaving(false));
//     } else {
//       // Edit
//       request(`${API_URL}v1/student/${modal.id}`, 'PUT', JSON.stringify({
//         full_name:  form.name,
//         bio:        modal.bio || '',
//         avatar_url: form.avatar.startsWith('http') ? form.avatar : '',
//         email:      form.email,
//         username:   form.username,
//       }), headers())
//         .then(updated => {
//           setGroups(gs => gs.map(g => ({
//             ...g,
//             students: (g.students || []).map(s =>
//               s.id === modal.id ? { ...s, ...updated } : s
//             )
//           })));
//           setModal(null);
//         })
//         .catch(() => setModalError('Ошибка при сохранении'))
//         .finally(() => setSaving(false));
//     }
//   };
//
//   /* ── Delete ── */
//   const handleDelete = (id) => {
//     fetch(`${API_URL}v1/student/${id}`, { method: 'DELETE', mode: 'cors', headers: headers() })
//       .then(() => {
//         setGroups(gs => gs.map(g => ({
//           ...g,
//           students: (g.students || []).filter(s => s.id !== id)
//         })));
//         setConfirmId(null);
//       })
//       .catch(() => setConfirmId(null));
//   };
//
//   const openAdd = (group) => {
//     setAddGroup(group);
//     setModal('add');
//     setModalError('');
//   };
//   const openEdit = (s) => {
//     setModal(s);
//     setModalError('');
//   };
//
//   return (
//     <div className="ms-container">
//
//       {/* Header */}
//       <div className="ms-header">
//         <div>
//           <h2>Мои Студенты</h2>
//           <p className="ms-subtitle">Группы и студенты из Classroom</p>
//         </div>
//       </div>
//
//       {/* Search groups */}
//       <div className="ms-filters">
//         <div className="ms-search-wrap">
//           <span className="ms-search-icon">🔍</span>
//           <input
//             className="ms-search"
//             placeholder="Поиск по названию группы..."
//             value={search}
//             onChange={e => setSearch(e.target.value)}
//           />
//           {search && (
//             <button className="ms-search-clear" onClick={() => setSearch('')}>✕</button>
//           )}
//         </div>
//       </div>
//
//       {/* Stats */}
//       <div className="ms-stats-row">
//         <div className="ms-stat-chip">🏫 Групп: {groups.length}</div>
//         <div className="ms-stat-chip">👥 Студентов: {totalStudents}</div>
//         <div className="ms-stat-chip">🔍 Найдено групп: {filteredGroups.length}</div>
//       </div>
//
//       {/* Groups */}
//       {loading ? (
//         <div className="ms-loading">
//           <div className="ms-spinner" />
//           <span>Загружаем группы...</span>
//         </div>
//       ) : filteredGroups.length === 0 ? (
//         <div className="ms-empty-row">Группы не найдены</div>
//       ) : (
//         <div className="ms-groups-list">
//           {filteredGroups.map(g => (
//             <GroupCard
//               key={g.id}
//               group={g}
//               onAddStudent={openAdd}
//               onEditStudent={openEdit}
//               onDeleteStudent={(id) => setConfirmId(id)}
//             />
//           ))}
//         </div>
//       )}
//
//       {/* Modal */}
//       {modal && (
//         <StudentModal
//           student={modal === 'add' ? null : modal}
//           onSave={handleSave}
//           onClose={() => { setModal(null); setAddGroup(null); }}
//           saving={saving}
//           error={modalError}
//         />
//       )}
//
//       {/* Confirm delete */}
//       {confirmId && ReactDOM.createPortal(
//         <div className="ms-overlay" onClick={() => setConfirmId(null)}>
//           <div className="ms-confirm" onClick={e => e.stopPropagation()}>
//             <span className="ms-confirm-icon">🗑️</span>
//             <h4>Удалить студента?</h4>
//             <p>Это действие нельзя отменить</p>
//             <div className="ms-confirm-actions">
//               <button className="ms-btn-cancel" onClick={() => setConfirmId(null)}>Отмена</button>
//               <button className="ms-btn-delete" onClick={() => handleDelete(confirmId)}>Удалить</button>
//             </div>
//           </div>
//         </div>,
//         document.body
//       )}
//     </div>
//   );
// };
//
// export default MyStudents;

import React, { useState, useEffect, useCallback } from 'react';
import ReactDOM from 'react-dom';
import './MyStudents.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

const AVATARS = ['👤','👩‍💻','👨‍💻','👩‍🎓','👨‍🎓','🧑‍💻','👩‍🔬','👨‍🔬'];
const EMPTY   = { name:'', username:'', email:'', password:'', avatar:'👤' };

/* ─── helpers ─── */
const balanceColor = (b) => {
  if (b < 0)       return 'neg';
  if (b < 100000)  return 'warn';
  return 'pos';
};
const fmt = (n) =>
  new Intl.NumberFormat('ru-RU').format(n) + ' сум';

/* ─── StudentModal ─── */
const StudentModal = ({ student, onSave, onClose, saving, error }) => {
  const isEdit = !!student;
  const [form, setForm] = useState(
    isEdit
      ? { name: student.full_name || '', username: student.username || '',
          email: student.email || '', password: '', avatar: student.avatar_url || '👤' }
      : { ...EMPTY }
  );
  const [errors, setErrors] = useState({});

  useEffect(() => {
    const h = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', h);
    return () => document.removeEventListener('keydown', h);
  }, [onClose]);

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const validate = () => {
    const e = {};
    if (!form.username.trim()) e.username = 'Введите логин';
    if (!form.email.trim())    e.email    = 'Введите email';
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Неверный email';
    if (!isEdit && !form.password.trim()) e.password = 'Введите пароль';
    setErrors(e);
    return !Object.keys(e).length;
  };

  return ReactDOM.createPortal(
    <div className="ms-overlay" onClick={onClose}>
      <div className="ms-modal" onClick={e => e.stopPropagation()}>
        <div className="ms-modal-header">
          <h3>{isEdit ? '✏️ Редактировать студента' : '➕ Новый студент'}</h3>
          <button className="ms-modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="ms-modal-body">
          {error && <div className="ms-modal-error">{error}</div>}
          <div className="ms-field">
            <label>Аватар</label>
            <div className="ms-avatar-picker">
              {AVATARS.map(a => (
                <button key={a}
                  className={`ms-avatar-opt ${form.avatar === a ? 'selected' : ''}`}
                  onClick={() => set('avatar', a)}>{a}</button>
              ))}
            </div>
          </div>
          <div className="ms-row">
            <div className="ms-field">
              <label>Полное имя</label>
              <input placeholder="Алия Сейткали" value={form.name}
                onChange={e => set('name', e.target.value)} />
            </div>
            <div className="ms-field">
              <label>Логин *</label>
              <input placeholder="aliya123" value={form.username}
                onChange={e => set('username', e.target.value)}
                className={errors.username ? 'error' : ''} />
              {errors.username && <span className="ms-error">{errors.username}</span>}
            </div>
          </div>
          <div className="ms-row">
            <div className="ms-field">
              <label>Email *</label>
              <input placeholder="student@email.com" value={form.email}
                onChange={e => set('email', e.target.value)}
                className={errors.email ? 'error' : ''} />
              {errors.email && <span className="ms-error">{errors.email}</span>}
            </div>
            <div className="ms-field">
              <label>{isEdit ? 'Новый пароль' : 'Пароль *'}</label>
              <input type="password" placeholder="••••••••" value={form.password}
                onChange={e => set('password', e.target.value)}
                className={errors.password ? 'error' : ''} />
              {errors.password && <span className="ms-error">{errors.password}</span>}
            </div>
          </div>
        </div>
        <div className="ms-modal-footer">
          <button className="ms-btn-cancel" onClick={onClose}>Отмена</button>
          <button className="ms-btn-save" onClick={() => { if (validate()) onSave(form); }}
            disabled={saving}>
            {saving ? '⏳...' : isEdit ? '💾 Сохранить' : '✅ Добавить'}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};

/* ─── StudentRow ─── */
const StudentRow = ({ student, onEdit, onDelete }) => {
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
      <div className="ms-sr-actions">
        <button className="ms-action-btn edit" onClick={() => onEdit(student)}
          title="Редактировать">✏️</button>
        <button className="ms-action-btn del" onClick={() => onDelete(student.id)}
          title="Удалить">🗑️</button>
      </div>
    </div>
  );
};

/* ─── GroupCard ─── */
const GroupCard = ({ group, onAddStudent, onEditStudent, onDeleteStudent }) => {
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
              👥 {students.length} студентов · 💰 {fmt(group.price)}
            </span>
          </div>
        </div>
        <div className="ms-group-right">
          <span className={`ms-total-balance ${balanceColor(totalBalance)}`}>
            {fmt(totalBalance)}
          </span>
          <button
            className="ms-add-student-btn"
            onClick={e => { e.stopPropagation(); onAddStudent(group); }}
            title="Добавить студента">
            ➕
          </button>
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
                placeholder="Поиск студента..."
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
            <div className="ms-no-students">Студенты не найдены</div>
          ) : (
            <div className="ms-students-list">
              {filtered.map(s => (
                <StudentRow
                  key={s.id}
                  student={s}
                  onEdit={onEditStudent}
                  onDelete={onDeleteStudent}
                />
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

  const [groups,     setGroups]     = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [search,     setSearch]     = useState('');
  const [modal,      setModal]      = useState(null);
  const [addGroup,   setAddGroup]   = useState(null);
  const [confirmId,  setConfirmId]  = useState(null);
  const [saving,     setSaving]     = useState(false);
  const [syncing,    setSyncing]    = useState(false);
  const [modalError, setModalError] = useState('');

  // Загрузка групп. Оставил массив зависимостей пустым, чтобы избежать бесконечного цикла.
  const loadData = useCallback(() => {
    setLoading(true);
    request(`${API_URL}v1/classroom/groups`, 'GET', null, headers())
      .then(data => setGroups(Array.isArray(data) ? data : []))
      .catch(() => setGroups([]))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Обработка синхронизации
  const handleSync = () => {
    if (syncing) return;
    setSyncing(true);
    // POST запрос на эндпоинт синхронизации
    request(`${API_URL}v1/classroom/sync`, 'POST', JSON.stringify({}), headers())
      .then(() => {
        loadData(); // Перезагружаем список после успешного обновления в базе
      })
      .catch((err) => {
        console.error('Sync error:', err);
        alert('Ошибка при синхронизации');
      })
      .finally(() => setSyncing(false));
  };

  const filteredGroups = groups.filter(g =>
    (g.name || '').toLowerCase().includes(search.toLowerCase())
  );

  const totalStudents = groups.reduce((s, g) => s + (g.students?.length || 0), 0);

  const handleSave = (form) => {
    setSaving(true);
    setModalError('');

    if (modal === 'add') {
      request(`${API_URL}v1/auth/register`, 'POST', JSON.stringify({
        full_name: form.name,
        username:  form.username,
        email:      form.email,
        password:  form.password,
      }))
        .then(created => {
          const newStudent = created.user || created;
          if (addGroup) {
            setGroups(gs => gs.map(g =>
              g.id === addGroup.id
                ? { ...g, students: [...(g.students || []), newStudent] }
                : g
            ));
          }
          setModal(null);
          setAddGroup(null);
        })
        .catch(() => setModalError('Ошибка. Возможно такой логин или email уже существует.'))
        .finally(() => setSaving(false));
    } else {
      request(`${API_URL}v1/student/${modal.id}`, 'PUT', JSON.stringify({
        full_name:  form.name,
        bio:         modal.bio || '',
        avatar_url: form.avatar.startsWith('http') ? form.avatar : '',
        email:      form.email,
        username:   form.username,
      }), headers())
        .then(updated => {
          setGroups(gs => gs.map(g => ({
            ...g,
            students: (g.students || []).map(s =>
              s.id === modal.id ? { ...s, ...updated } : s
            )
          })));
          setModal(null);
        })
        .catch(() => setModalError('Ошибка при сохранении'))
        .finally(() => setSaving(false));
    }
  };

  const handleDelete = (id) => {
    fetch(`${API_URL}v1/student/${id}`, { method: 'DELETE', mode: 'cors', headers: headers() })
      .then(() => {
        setGroups(gs => gs.map(g => ({
          ...g,
          students: (g.students || []).filter(s => s.id !== id)
        })));
        setConfirmId(null);
      })
      .catch(() => setConfirmId(null));
  };

  return (
    <div className="ms-container">
      <div className="ms-header">
        <div>
          <h2>Мои Студенты</h2>
          <p className="ms-subtitle">Группы и студенты из Classroom</p>
        </div>
        <button
          className={`ms-sync-btn ${syncing ? 'loading' : ''}`}
          onClick={handleSync}
          disabled={syncing || loading}
          style={{ padding: '8px 16px', borderRadius: '8px', cursor: 'pointer' }}
        >
          {syncing ? '🔄 Синхронизация...' : '🔄 Синхронизировать с Classroom'}
        </button>
      </div>

      <div className="ms-filters">
        <div className="ms-search-wrap">
          <span className="ms-search-icon">🔍</span>
          <input
            className="ms-search"
            placeholder="Поиск по названию группы..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          {search && (
            <button className="ms-search-clear" onClick={() => setSearch('')}>✕</button>
          )}
        </div>
      </div>

      <div className="ms-stats-row">
        <div className="ms-stat-chip">🏫 Групп: {groups.length}</div>
        <div className="ms-stat-chip">👥 Студентов: {totalStudents}</div>
      </div>

      {loading && !syncing ? (
        <div className="ms-loading">
          <div className="ms-spinner" />
          <span>Загрузка данных...</span>
        </div>
      ) : filteredGroups.length === 0 ? (
        <div className="ms-empty-row">Группы не найдены</div>
      ) : (
        <div className="ms-groups-list">
          {filteredGroups.map(g => (
            <GroupCard
              key={g.id}
              group={g}
              onAddStudent={(group) => { setAddGroup(group); setModal('add'); setModalError(''); }}
              onEditStudent={(s) => { setModal(s); setModalError(''); }}
              onDeleteStudent={(id) => setConfirmId(id)}
            />
          ))}
        </div>
      )}

      {modal && (
        <StudentModal
          student={modal === 'add' ? null : modal}
          onSave={handleSave}
          onClose={() => { setModal(null); setAddGroup(null); }}
          saving={saving}
          error={modalError}
        />
      )}

      {confirmId && ReactDOM.createPortal(
        <div className="ms-overlay" onClick={() => setConfirmId(null)}>
          <div className="ms-confirm" onClick={e => e.stopPropagation()}>
            <span className="ms-confirm-icon">🗑️</span>
            <h4>Удалить студента?</h4>
            <p>Это действие нельзя отменить</p>
            <div className="ms-confirm-actions">
              <button className="ms-btn-cancel" onClick={() => setConfirmId(null)}>Отмена</button>
              <button className="ms-btn-delete" onClick={() => handleDelete(confirmId)}>Удалить</button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};

export default MyStudents;