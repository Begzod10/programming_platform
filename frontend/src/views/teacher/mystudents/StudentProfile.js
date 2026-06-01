import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './StudentProfile.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

/* ─── Helpers ─── */
const LEVEL_MAP = {
  Beginner:     { color: '#00b894', bg: '#e6faf5', bar: '#00b894', icon: '🌱' },
  Elementary:   { color: '#0984e3', bg: '#e6f2fd', bar: '#0984e3', icon: '📘' },
  Intermediate: { color: '#6c5ce7', bg: '#f0edff', bar: '#6c5ce7', icon: '⚡' },
  Advanced:     { color: '#e17055', bg: '#fff2ee', bar: '#e17055', icon: '🔥' },
  Expert:       { color: '#d4ac0d', bg: '#fef9e7', bar: '#d4ac0d', icon: '👑' },
};
const getLevel  = (l) => LEVEL_MAP[l] || { color: '#888', bg: '#f5f5f5', bar: '#888', icon: '📚' };

const fmt = (n) => new Intl.NumberFormat('uz-UZ', {
  style: 'currency',
  currency: 'UZS',
  maximumFractionDigits: 0
}).format(n ?? 0);
const fmtDate   = (iso) => iso
  ? new Intl.DateTimeFormat('ru-RU', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(iso))
  : '—';
const balColor  = (b) => b < 0 ? '#e63946' : b < 100_000 ? '#e6a817' : '#00b894';

/* ─── Ring SVG ─── */
const Ring = ({ value = 0, size = 64, stroke = 5, color = '#6c5ce7' }) => {
  const r = (size - stroke * 2) / 2;
  const c = 2 * Math.PI * r;
  return (
    <svg width={size} height={size} style={{ transform: 'rotate(-90deg)', display: 'block', flexShrink: 0 }}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#f0f0f8" strokeWidth={stroke}/>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color}   strokeWidth={stroke}
        strokeDasharray={c} strokeDashoffset={c - (Math.min(value,100)/100)*c}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.16,1,0.3,1)' }}/>
    </svg>
  );
};

/* ─── Course Card ─── */
const CourseCard = ({ course, idx }) => {
  const pct = course.progress_percentage ?? 0;
  return (
    <div className="spp-course-card" style={{ animationDelay: `${idx*0.07}s` }}>
      <div className="spp-cc-top">
        <div className="spp-cc-info">
          <p className="spp-cc-title">{course.course_title}</p>
          <p className="spp-cc-diff">{course.difficulty_level}</p>
        </div>
        <div className="spp-cc-ring-wrap">
          <Ring value={pct} size={54} stroke={4.5} color="#6c5ce7"/>
          <span className="spp-cc-pct">{pct}%</span>
        </div>
      </div>
      <div className="spp-cc-bar"><div className="spp-cc-bar-fill" style={{ width:`${pct}%` }}/></div>
      <div className="spp-cc-foot">
        <span>📖 {course.completed_lessons ?? 0}/{course.total_lessons ?? 0} dars</span>
        <span>⭐ {course.earned_points ?? 0}/{course.max_points ?? 0} pts</span>
        {course.is_completed && <span className="spp-done">✅ Tugallandi</span>}
      </div>
    </div>
  );
};

/* ─── Badge Card ─── */
const BadgeCard = ({ ach, idx }) => (
  <div className="spp-badge-card" style={{ animationDelay: `${idx*0.06}s` }}>
    {ach.badge_image_url
      ? <img src={ach.badge_image_url} alt={ach.name} className="spp-badge-img"/>
      : <div className="spp-badge-ico">🏆</div>}
    <div className="spp-badge-info">
      <div className="spp-badge-top">
        <span className="spp-badge-name">{ach.name}</span>
        <span className="spp-badge-pts">+{ach.points_reward} pts</span>
      </div>
      <p className="spp-badge-desc">{ach.description}</p>
    </div>
  </div>
);

/* ════════════════════════════════════
   MAIN PAGE
════════════════════════════════════ */
const StudentProfilePage = () => {
  const { studentId } = useParams();
  const navigate = useNavigate();
  const { request } = useHttp();

  const [profile,  setProfile]  = useState(null);
  const [progress, setProgress] = useState(null);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState(null);
  const [tab,      setTab]      = useState('overview');

  const load = useCallback(() => {
    if (!studentId) return;
    
    let isMounted = true;
    setLoading(true); 
    setError(null); 

    Promise.all([
      request(`${API_URL}v1/student/${studentId}`,                   'GET', null, headers()),
      request(`${API_URL}v1/teacher/students/${studentId}/progress`, 'GET', null, headers()),
    ])
      .then(([prof, prog]) => {
        if (isMounted) {
          setProfile(prof);
          setProgress(prog);
        }
      })
      .catch(() => isMounted && setError("Ma'lumotlarni yuklashda xatolik yuz berdi"))
      .finally(() => isMounted && setLoading(false));

    return () => { isMounted = false; };
  }, [studentId, request]);

  useEffect(() => {
    load();
  }, [load]);

  const d            = profile;
  const p            = progress;
  const lvl          = getLevel(d?.current_level);
  const courses      = p?.courses     || [];
  const groups       = p?.group_names  || [];
  const achievements = d?.achievements || [];
  const avgProgress  = p?.average_progress ?? 0;
  const globalRank   = p?.global_rank     ?? '—';
  const initials = useMemo(() => {
    if (!d) return '??';
    const first = (d.full_name || d.username || '?')[0];
    const last = (d.surname || '')[0] || '';
    return `${first}${last}`.toUpperCase();
  }, [d]);

  /* ── LOADING ── */
  if (loading) return (
    <div className="spp-root">
      <div className="spp-state-screen">
        <div className="spp-spinner"/>
        <p>Profil yuklanmoqda…</p>
      </div>
    </div>
  );

  /* ── ERROR ── */
  if (error) return (
    <div className="spp-root">
      <div className="spp-state-screen">
        <span style={{ fontSize:52 }}>⚠️</span>
        <p>{error}</p>
        <button className="spp-btn-purple" onClick={load}>Qayta urinish</button>
        <button className="spp-btn-ghost"  onClick={() => navigate(-1)}>← Orqaga</button>
      </div>
    </div>
  );

  if (!d) return null;

  return (
    <div className="spp-root">

      {/* ════ TOPBAR ════ */}
      <div className="spp-topbar">
        <button className="spp-back" onClick={() => navigate(-1)}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 3L5 8L10 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Talabalar ro'yxati
        </button>
        <div className="spp-breadcrumb">
          <span>Talabalar</span>
          <span className="spp-bc-sep">/</span>
          <span className="spp-bc-current">{d.full_name}{d.surname ? ' '+d.surname : ''}</span>
        </div>
      </div>

      {/* ════ HERO BANNER ════ */}
      <div className="spp-hero">
        <div className="spp-hero-bg"/>
        <div className="spp-hero-content">
          {/* Avatar */}
          <div className="spp-hero-avatar-wrap">
            {d.avatar_url
              ? <img src={d.avatar_url} alt="" className="spp-hero-avatar-img"/>
              : <div className="spp-hero-avatar-ini">{initials}</div>}
            <span className={`spp-hero-dot ${d.is_active ? 'on' : ''}`}/>
          </div>

          {/* Name + tags */}
          <div className="spp-hero-info">
            <div className="spp-hero-name-row">
              <h1 className="spp-hero-name">{d.full_name}{d.surname ? ' '+d.surname : ''}</h1>
              <span className={`spp-hero-status ${d.is_active ? 'on' : 'off'}`}>
                {d.is_active ? 'Faol' : 'Nofaol'}
              </span>
            </div>
            <p className="spp-hero-uname">@{d.username}</p>
            <div className="spp-hero-tags">
              <span className="spp-tag-level" style={{ background: lvl.bg, color: lvl.color }}>
                {lvl.icon} {d.current_level}
              </span>
              {groups.map((g,i) => (
                <span key={i} className="spp-tag-group">🏫 {g}</span>
              ))}
            </div>
          </div>

          {/* Big ring */}
          <div className="spp-hero-ring-block">
            <div className="spp-hero-ring-wrap">
              <Ring value={avgProgress} size={96} stroke={7} color="#6c5ce7"/>
              <div className="spp-hero-ring-label">
                <span className="spp-hero-ring-val">{avgProgress}%</span>
                <span className="spp-hero-ring-sub">progress</span>
              </div>
            </div>
            <p className="spp-hero-ring-caption">O'rtacha o'zlashtirish</p>
          </div>
        </div>
      </div>

      {/* ════ STATS ROW ════ */}
      <div className="spp-stats-row">
        {[
          { icon:'⚡', val: d.total_points ?? p?.total_points ?? 0, lbl:'Umumiy ball',  color:'#6c5ce7' },
          { icon:'💰', val: fmt(d.balance),                          lbl:'Balans',       color: balColor(d.balance) },
          { icon:'📚', val: courses.length,                          lbl:'Kurslar',      color:'#0984e3' },
          { icon:'🏆', val: achievements.length,                     lbl:'Yutuqlar',     color:'#e17055' },
          { icon:'🌍', val: `#${globalRank}`,                        lbl:'Global rank',  color:'#00b894' },
          { icon:'📈', val: `${avgProgress}%`,                       lbl:'Progress',     color:'#fd79a8' },
        ].map(({ icon, val, lbl, color }, i) => (
          <div key={i} className="spp-stat-card" style={{ animationDelay:`${i*0.05}s` }}>
            <span className="spp-stat-icon">{icon}</span>
            <span className="spp-stat-val" style={{ color }}>{val}</span>
            <span className="spp-stat-lbl">{lbl}</span>
          </div>
        ))}
      </div>

      {/* ════ BODY: sidebar + main ════ */}
      <div className="spp-body">

        {/* ── LEFT SIDEBAR ── */}
        <aside className="spp-sidebar">

          {/* Contact block */}
          <div className="spp-side-card">
            <p className="spp-side-title">📋 Ma'lumotlar</p>
            <div className="spp-info-list">
              {d.email && (
                <a href={`mailto:${d.email}`} className="spp-info-row link">
                  <span className="spp-info-icon">✉️</span>
                  <span className="spp-info-val">{d.email}</span>
                </a>
              )}
              {d.phone && (
                <a href={`tel:${d.phone}`} className="spp-info-row link">
                  <span className="spp-info-icon">📱</span>
                  <span className="spp-info-val">{d.phone}</span>
                </a>
              )}
              {d.birth_date && (
                <div className="spp-info-row">
                  <span className="spp-info-icon">🎂</span>
                  <span className="spp-info-val">{fmtDate(d.birth_date)}</span>
                </div>
              )}
              {d.age !== undefined && d.age !== null && (
                <div className="spp-info-row">
                  <span className="spp-info-icon">👤</span>
                  <span className="spp-info-val">{d.age} yosh</span>
                </div>
              )}
              {d.address && (
                <div className="spp-info-row">
                  <span className="spp-info-icon">📍</span>
                  <span className="spp-info-val">{d.address}</span>
                </div>
              )}
              {d.parent_phone && (
                <div className="spp-info-row">
                  <span className="spp-info-icon">👨‍👩‍👦</span>
                  <span className="spp-info-val">{d.parent_phone}</span>
                </div>
              )}
              {p?.enrollment_date && (
                <div className="spp-info-row">
                  <span className="spp-info-icon">🎓</span>
                  <span className="spp-info-val">Qabul: {fmtDate(p.enrollment_date)}</span>
                </div>
              )}
              {d.created_at && (
                <div className="spp-info-row">
                  <span className="spp-info-icon">📅</span>
                  <span className="spp-info-val">Ro'yxat: {fmtDate(d.created_at)}</span>
                </div>
              )}
            </div>
          </div>

          {/* Groups block */}
          {groups.length > 0 && (
            <div className="spp-side-card">
              <p className="spp-side-title">🏫 Guruhlar</p>
              <div className="spp-groups-list">
                {groups.map((g,i) => (
                  <div key={i} className="spp-group-item">
                    <div className="spp-group-dot"/>
                    <span>{g}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Bio block */}
          {d.bio && (
            <div className="spp-side-card">
              <p className="spp-side-title">💬 Bio</p>
              <p className="spp-bio-text">{d.bio}</p>
            </div>
          )}

          {/* Balance block */}
          <div className="spp-side-card spp-balance-card">
            <div className="spp-balance-row">
              <div>
                <p className="spp-balance-label">Balans</p>
                <p className="spp-balance-val" style={{ color: balColor(d.balance) }}>{fmt(d.balance)}</p>
              </div>
              <span className="spp-balance-icon">💰</span>
            </div>
            {d.total_score !== undefined && (
              <div className="spp-balance-row" style={{ marginTop:12, paddingTop:12, borderTop:'1.5px solid #f3f3f8' }}>
                <div>
                  <p className="spp-balance-label">Umumiy hisob</p>
                  <p className="spp-balance-val" style={{ color: balColor(d.total_score ?? 0) }}>{fmt(d.total_score)}</p>
                </div>
                <span className="spp-balance-icon">📊</span>
              </div>
            )}
          </div>

        </aside>

        {/* ── MAIN CONTENT ── */}
        <main className="spp-main">

          {/* Tabs */}
          <div className="spp-tabs-wrap">
            {[
              { id:'overview',     label:'Umumiy',   icon:'📊', count: null },
              { id:'courses',      label:'Kurslar',  icon:'📚', count: courses.length },
              { id:'achievements', label:'Yutuqlar', icon:'🏆', count: achievements.length },
            ].map(({ id, label, icon, count }) => (
              <button key={id}
                className={`spp-tab ${tab === id ? 'active' : ''}`}
                onClick={() => setTab(id)}
              >
                <span>{icon}</span> {label}
                {count !== null && count > 0 && <span className="spp-tab-cnt">{count}</span>}
              </button>
            ))}
          </div>

          {/* ── Overview ── */}
          {tab === 'overview' && (
            <div className="spp-tab-body">
              {groups.length > 0 && (
                <div className="spp-section">
                  <p className="spp-section-lbl">🏫 Guruhlar</p>
                  <div className="spp-groups-grid">
                    {groups.map((g,i) => (
                      <div key={i} className="spp-group-card-big">
                        <span className="spp-gcb-ico">🏫</span>
                        <span className="spp-gcb-name">{g}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {courses.length > 0 && (
                <div className="spp-section">
                  <p className="spp-section-lbl">📈 Kurslar bo'yicha progress</p>
                  <div className="spp-mini-prog-list">
                    {courses.map((c) => (
                      <div key={c.course_id} className="spp-mini-prog-row">
                        <span className="spp-mpr-name">{c.course_title}</span>
                        <div className="spp-mpr-track">
                          <div className="spp-mpr-fill" style={{ width:`${c.progress_percentage ?? 0}%` }}/>
                        </div>
                        <span className="spp-mpr-pct">{c.progress_percentage ?? 0}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {courses.length === 0 && groups.length === 0 && !d.bio && (
                <div className="spp-empty">
                  <span>📭</span>
                  <p>Ma'lumot mavjud emas</p>
                </div>
              )}
            </div>
          )}

          {/* ── Courses ── */}
          {tab === 'courses' && (
            <div className="spp-tab-body">
              {courses.length === 0
                ? <div className="spp-empty"><span>📚</span><p>Hech qanday kurs yo'q</p></div>
                : <div className="spp-courses-grid">
                    {courses.map((c,i) => <CourseCard key={c.course_id} course={c} idx={i}/>)}
                  </div>
              }
            </div>
          )}

          {/* ── Achievements ── */}
          {tab === 'achievements' && (
            <div className="spp-tab-body">
              {achievements.length === 0
                ? <div className="spp-empty"><span>🏅</span><p>Hech qanday yutuq yo'q</p></div>
                : <div className="spp-badges-list">
                    {achievements.map((a,i) => <BadgeCard key={a.id} ach={a} idx={i}/>)}
                  </div>
              }
            </div>
          )}

        </main>
      </div>
    </div>
  );
};

export default StudentProfilePage;