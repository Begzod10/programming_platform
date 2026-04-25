import { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import './TeacherReview.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

const GRADES   = ['A', 'B', 'C', 'D'];

const gradeColor = { A: '#00b894', B: '#6c5ce7', C: '#fdcb6e', D: '#ff7675' };
const gradeTextColor = { A: '#fff', B: '#fff', C: '#1a1a2e', D: '#fff' };

const statusLabel = {
    Draft:        'Черновик',
    Submitted:    'Отправлен',
    'Under Review':'На проверке',
    Approved:     'Одобрен',
    Rejected:     'Отклонён',
};
const statusClass = {
    Draft:         'tr-s-draft',
    Submitted:     'tr-s-pending',
    'Under Review':'tr-s-pending',
    Approved:      'tr-s-approved',
    Rejected:      'tr-s-denied',
};
const diffClass = { Easy: 'tr-d-easy', Medium: 'tr-d-medium', Hard: 'tr-d-hard' };

function TeacherReview() {
    const { request } = useHttp();

    const [projects, setProjects] = useState([]);
    const [loading,  setLoading]  = useState(true);
    const [search,   setSearch]   = useState('');
    const [filter,   setFilter]   = useState('all'); // all | pending | approved | rejected
    const [detail,   setDetail]   = useState(null);
    const [saving,   setSaving]   = useState(false);
    const [msg,      setMsg]      = useState('');

    // review form
    const [feedback, setFeedback] = useState('');
    const [grade,    setGrade]    = useState('A');
    const [points,   setPoints]   = useState('');
    const [status,   setStatus]   = useState('Approved');

    useEffect(() => {
        request(`${API_URL}v1/project/`, 'GET', null, headers())
            .then(data => setProjects(Array.isArray(data) ? data : []))
            .catch(() => setProjects([]))
            .finally(() => setLoading(false));
    }, []);

    const openDetail = (p) => {
        setDetail(p);
        setFeedback(p.instructor_feedback || '');
        setGrade(p.grade || 'A');
        setPoints(p.points_earned ?? '');
        setStatus(p.status === 'Approved' || p.status === 'Rejected' ? p.status : 'Approved');
        setMsg('');
    };

    const handleReview = async () => {
        if (!feedback.trim()) { setMsg('Введите комментарий для студента'); return; }
        setSaving(true);
        setMsg('');
        try {
            const id = detail.id;

            // review сохраняет всё включая статус в одном запросе
            await request(
                `${API_URL}v1/project/${id}/review`,
                'POST',
                JSON.stringify({
                    feedback: feedback,
                    grade:    grade,
                    points:   Number(points) || 0,
                    status:   status,
                }),
                headers()
            );

            const updated = {
                ...detail,
                instructor_feedback: feedback,
                grade,
                points_earned: Number(points) || 0,
                status,
            };
            setProjects(p => p.map(pr => pr.id === id ? updated : pr));
            setDetail(updated);
            setMsg('✅ Проверка сохранена!');
            setTimeout(() => setDetail(null), 900);
        } catch {
            setMsg('❌ Ошибка при сохранении');
        } finally {
            setSaving(false);
        }
    };

    const filtered = projects.filter(p => {
        const q = search.toLowerCase();
        const matchSearch =
            (p.title || '').toLowerCase().includes(q) ||
            (p.student_name || p.student_id?.toString() || '').toLowerCase().includes(q);

        const matchFilter =
            filter === 'all'      ? true :
            filter === 'pending'  ? (p.status === 'Submitted' || p.status === 'Under Review') :
            filter === 'approved' ? p.status === 'Approved' :
            filter === 'rejected' ? p.status === 'Rejected' : true;

        return matchSearch && matchFilter;
    });

    const counts = {
        all:      projects.length,
        pending:  projects.filter(p => p.status === 'Submitted' || p.status === 'Under Review').length,
        approved: projects.filter(p => p.status === 'Approved').length,
        rejected: projects.filter(p => p.status === 'Rejected').length,
    };

    return (
        <div className="tr-container">

            {/* Header */}
            <div className="tr-top-section">
                <div className="tr-title-block">
                    <h2>Проверка работ</h2>
                    <p>Ожидают проверки: <span>{counts.pending}</span></p>
                </div>
                <div className="tr-search-box">
                    <span className="search-icon">🔍</span>
                    <input
                        type="text"
                        placeholder="Поиск по проекту или студенту..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                </div>
            </div>

            {/* Filter tabs */}
            <div className="tr-filter-tabs">
                {[
                    { key: 'all',      label: 'Все',        count: counts.all },
                    { key: 'pending',  label: 'На проверке',count: counts.pending },
                    { key: 'approved', label: 'Одобрены',   count: counts.approved },
                    { key: 'rejected', label: 'Отклонены',  count: counts.rejected },
                ].map(tab => (
                    <button
                        key={tab.key}
                        className={`tr-filter-tab ${filter === tab.key ? 'active' : ''}`}
                        onClick={() => setFilter(tab.key)}
                    >
                        {tab.label}
                        <span className="tr-tab-count">{tab.count}</span>
                    </button>
                ))}
            </div>

            {/* Table */}
            {loading ? (
                <div className="tr-loading"><div className="tr-spinner" /><p>Загрузка...</p></div>
            ) : filtered.length === 0 ? (
                <div className="tr-empty">📭 Проектов не найдено</div>
            ) : (
                <div className="tr-table-wrapper">
                    <div className="tr-table-header">
                        <span>Проект</span>
                        <span>Сложность</span>
                        <span>Статус</span>
                        <span>Оценка</span>
                        <span>Очки</span>
                        <span style={{ textAlign: 'right' }}>Действие</span>
                    </div>
                    <div className="tr-rows">
                        {filtered.map(p => (
                            <div key={p.id} className="tr-row" onClick={() => openDetail(p)}>
                                <div className="tr-col-main">
                                    <div className="tr-user-mark" />
                                    <div>
                                        <div className="tr-student-name">{p.title}</div>
                                        <div className="tr-project-name">
                                            {p.github_url
                                                ? <a href={p.github_url} target="_blank" rel="noreferrer"
                                                    className="tr-gh-link"
                                                    onClick={e => e.stopPropagation()}>GitHub →</a>
                                                : <span style={{color:'rgba(26,26,46,0.35)'}}>Нет ссылки</span>}
                                        </div>
                                    </div>
                                </div>
                                <div>
                                    <span className={`tr-diff ${diffClass[p.difficulty_level] || ''}`}>
                                        {p.difficulty_level || '—'}
                                    </span>
                                </div>
                                <div>
                                    <span className={`tr-status ${statusClass[p.status] || ''}`}>
                                        {statusLabel[p.status] || p.status}
                                    </span>
                                </div>
                                <div>
                                    {p.grade ? (
                                        <span className="tr-grade-badge"
                                            style={{
                                                background: gradeColor[p.grade] || '#6c5ce7',
                                                color: gradeTextColor[p.grade] || '#fff',
                                            }}>
                                            {p.grade}
                                        </span>
                                    ) : <span style={{color:'rgba(26,26,46,0.3)',fontSize:13}}>—</span>}
                                </div>
                                <div className="tr-col-pts">{p.points_earned ?? 0} pts</div>
                                <div className="tr-col-action">
                                    <button className="tr-action-btn" onClick={e => { e.stopPropagation(); openDetail(p); }}>
                                        Рассмотреть →
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Detail Modal via Portal */}
            {detail && ReactDOM.createPortal(
                <div className="tr-overlay" onClick={() => setDetail(null)}>
                    <div className="tr-modal" onClick={e => e.stopPropagation()}>

                        {/* Modal Header */}
                        <div className="tr-modal-header">
                            <div className="tr-modal-header-left">
                                <div className="tr-modal-icon">📋</div>
                                <div>
                                    <h3>{detail.title}</h3>
                                    <div className="tr-modal-meta">
                                        {detail.difficulty_level && (
                                            <span className={`tr-diff ${diffClass[detail.difficulty_level] || ''}`}>
                                                {detail.difficulty_level}
                                            </span>
                                        )}
                                        <span className={`tr-status ${statusClass[detail.status] || ''}`}>
                                            {statusLabel[detail.status] || detail.status}
                                        </span>
                                        {detail.grade && (
                                            <span className="tr-grade-badge"
                                                style={{
                                                    background: gradeColor[detail.grade],
                                                    color: gradeTextColor[detail.grade],
                                                }}>
                                                {detail.grade}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                            <button className="tr-close" onClick={() => setDetail(null)}>✕</button>
                        </div>

                        <div className="tr-modal-body">

                            {/* Project info */}
                            <div className="tr-info-cards">
                                {detail.description && (
                                    <div className="tr-info-card">
                                        <label>📝 Описание</label>
                                        <p>{detail.description}</p>
                                    </div>
                                )}
                                {detail.github_url && (
                                    <div className="tr-info-card">
                                        <label>🔗 GitHub</label>
                                        <a href={detail.github_url} target="_blank" rel="noreferrer" className="tr-gh-link">
                                            {detail.github_url}
                                        </a>
                                    </div>
                                )}
                                {detail.live_demo_url && (
                                    <div className="tr-info-card">
                                        <label>🌐 Live Demo</label>
                                        <a href={detail.live_demo_url} target="_blank" rel="noreferrer" className="tr-gh-link">
                                            {detail.live_demo_url}
                                        </a>
                                    </div>
                                )}
                                {(detail.technologies_used || []).length > 0 && (
                                    <div className="tr-info-card">
                                        <label>⚙️ Технологии</label>
                                        <div className="tr-techs">
                                            {detail.technologies_used.map((t, i) => (
                                                <span key={i} className="tr-tech">{t}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                {detail.instructor_feedback && (
                                    <div className="tr-info-card prev-feedback">
                                        <label>💬 Предыдущий отзыв</label>
                                        <p>{detail.instructor_feedback}</p>
                                    </div>
                                )}
                            </div>

                            <div className="tr-section-divider">
                                <span>Выставить оценку</span>
                            </div>

                            {/* Status */}
                            <div className="tr-field">
                                <label>Решение *</label>
                                <div className="tr-status-btns">
                                    <button
                                        className={`tr-sbtn tr-sbtn-approve ${status === 'Approved' ? 'active' : ''}`}
                                        onClick={() => setStatus('Approved')}>
                                        ✅ Одобрить
                                    </button>
                                    <button
                                        className={`tr-sbtn tr-sbtn-deny ${status === 'Rejected' ? 'active' : ''}`}
                                        onClick={() => setStatus('Rejected')}>
                                        ❌ Отклонить
                                    </button>
                                </div>
                            </div>

                            {/* Grade + Points */}
                            <div className="tr-row-fields">
                                <div className="tr-field">
                                    <label>Оценка *</label>
                                    <div className="tr-grade-btns">
                                        {GRADES.map(g => (
                                            <button key={g}
                                                className={`tr-gbtn ${grade === g ? 'active' : ''}`}
                                                style={grade === g ? {
                                                    background: gradeColor[g],
                                                    color: gradeTextColor[g],
                                                    borderColor: gradeColor[g],
                                                } : {}}
                                                onClick={() => setGrade(g)}>
                                                {g}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                <div className="tr-field">
                                    <label>Очки</label>
                                    <input
                                        type="number" min="0" placeholder="например, 100"
                                        value={points}
                                        onChange={e => setPoints(e.target.value)}
                                    />
                                </div>
                            </div>

                            {/* Feedback */}
                            <div className="tr-field">
                                <label>Комментарий для студента *</label>
                                <textarea
                                    rows={4}
                                    placeholder="Напишите подробный отзыв о работе студента..."
                                    value={feedback}
                                    onChange={e => setFeedback(e.target.value)}
                                />
                                <span className="tr-char-count">{feedback.length} символов</span>
                            </div>

                            {msg && (
                                <div className={`tr-msg ${msg.startsWith('✅') ? 'tr-msg-ok' : 'tr-msg-err'}`}>
                                    {msg}
                                </div>
                            )}
                        </div>

                        <div className="tr-modal-footer">
                            <button className="tr-btn-cancel" onClick={() => setDetail(null)}>Закрыть</button>
                            <button className="tr-btn-save" onClick={handleReview} disabled={saving}>
                                {saving ? '⏳ Сохранение...' : '💾 Сохранить проверку'}
                            </button>
                        </div>
                    </div>
                </div>,
                document.body
            )}
        </div>
    );
}

export default TeacherReview;