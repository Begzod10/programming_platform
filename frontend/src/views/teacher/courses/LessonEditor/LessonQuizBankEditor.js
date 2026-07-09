import React, { useState, useEffect } from 'react';

// ── Lesson Quiz Question Bank ──────────────────────────────────────────────────
const QUIZ_OPTION_LABELS = ['A', 'B', 'C', 'D'];

export function LessonQuizBankEditor({ lessonId, apiBaseUrl }) {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAdd, setShowAdd] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [form, setForm] = useState({ question_text: '', options: ['', '', '', ''], correct_option: 0, time_limit: 30, points: 1000 });
    const [saving, setSaving] = useState(false);

    const token = localStorage.getItem('token');
    const authHeaders = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

    const load = () => {
        setLoading(true);
        fetch(`${apiBaseUrl}/lessons/${lessonId}/questions`, { headers: { Authorization: `Bearer ${token}` } })
            .then(r => r.json())
            .then(d => setQuestions(Array.isArray(d) ? d : []))
            .catch(() => {})
            .finally(() => setLoading(false));
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => { load(); }, [lessonId]);

    const openAdd = () => {
        setEditingId(null);
        setForm({ question_text: '', options: ['', '', '', ''], correct_option: 0, time_limit: 30, points: 1000 });
        setShowAdd(true);
    };

    const openEdit = (q) => {
        setEditingId(q.id);
        const opts = [...q.options];
        while (opts.length < 4) opts.push('');
        setForm({ question_text: q.question_text, options: opts, correct_option: q.correct_option, time_limit: q.time_limit, points: q.points });
        setShowAdd(true);
    };

    const saveQuestion = async (e) => {
        e.preventDefault();
        const filledOpts = form.options.filter(o => o.trim());
        if (filledOpts.length < 2) { alert('Минимум 2 варианта ответа'); return; }
        if (form.correct_option >= filledOpts.length) { alert('Правильный ответ выходит за пределы вариантов'); return; }
        setSaving(true);
        const payload = { ...form, options: filledOpts };
        try {
            const url = editingId
                ? `${apiBaseUrl}/lessons/${lessonId}/questions/${editingId}`
                : `${apiBaseUrl}/lessons/${lessonId}/questions`;
            const res = await fetch(url, { method: editingId ? 'PUT' : 'POST', headers: authHeaders, body: JSON.stringify(payload) });
            if (!res.ok) { alert((await res.json()).detail || 'Ошибка'); return; }
            setShowAdd(false);
            load();
        } finally { setSaving(false); }
    };

    const deleteQuestion = async (id) => {
        if (!window.confirm('Удалить вопрос?')) return;
        await fetch(`${apiBaseUrl}/lessons/${lessonId}/questions/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
        load();
    };

    const setOption = (i, val) => setForm(f => { const o = [...f.options]; o[i] = val; return { ...f, options: o }; });

    return (
        <div className="lep-quiz-bank">
            <div className="lep-quiz-bank-header">
                <div>
                    <h3>🎮 Вопросы для командных игр</h3>
                    <p>Стандартные вопросы по этому уроку — можно импортировать в любую викторину</p>
                </div>
                <button className="lep-quiz-bank-add-btn" onClick={openAdd}>+ Добавить вопрос</button>
            </div>

            {showAdd && (
                <form className="lep-quiz-bank-form" onSubmit={saveQuestion}>
                    <h4>{editingId ? 'Редактировать вопрос' : 'Новый вопрос'}</h4>
                    <textarea
                        required placeholder="Текст вопроса"
                        value={form.question_text}
                        onChange={e => setForm(f => ({ ...f, question_text: e.target.value }))}
                        rows={2}
                    />
                    <div className="lep-quiz-bank-opts">
                        {form.options.map((opt, i) => (
                            <div key={i} className={`lep-quiz-bank-opt-row${form.correct_option === i ? ' correct' : ''}`}>
                                <button type="button" className="lep-quiz-bank-letter"
                                    onClick={() => setForm(f => ({ ...f, correct_option: i }))}>
                                    {QUIZ_OPTION_LABELS[i]}
                                </button>
                                <input placeholder={`Вариант ${QUIZ_OPTION_LABELS[i]}${i >= 2 ? ' (необязательно)' : ''}`}
                                    value={opt} onChange={e => setOption(i, e.target.value)} />
                            </div>
                        ))}
                    </div>
                    <div className="lep-quiz-bank-meta">
                        <label>⏱ {form.time_limit}с
                            <input type="range" min={5} max={120} step={5} value={form.time_limit}
                                onChange={e => setForm(f => ({ ...f, time_limit: Number(e.target.value) }))} />
                        </label>
                        <label>⭐ {form.points} очков
                            <input type="range" min={100} max={5000} step={100} value={form.points}
                                onChange={e => setForm(f => ({ ...f, points: Number(e.target.value) }))} />
                        </label>
                    </div>
                    <div className="lep-quiz-bank-form-actions">
                        <button type="button" onClick={() => setShowAdd(false)}>Отмена</button>
                        <button type="submit" className="primary" disabled={saving}>{saving ? 'Сохранение...' : '💾 Сохранить'}</button>
                    </div>
                </form>
            )}

            {loading ? <p className="lep-quiz-bank-empty">Загрузка...</p> : questions.length === 0 && !showAdd ? (
                <p className="lep-quiz-bank-empty">Нет вопросов. Добавьте первый!</p>
            ) : (
                <div className="lep-quiz-bank-list">
                    {questions.map((q, idx) => (
                        <div key={q.id} className="lep-quiz-bank-item">
                            <div className="lep-quiz-bank-item-num">#{idx + 1}</div>
                            <div className="lep-quiz-bank-item-body">
                                <p className="lep-quiz-bank-q-text">{q.question_text}</p>
                                <div className="lep-quiz-bank-chips">
                                    {q.options.map((opt, i) => (
                                        <span key={i} className={`lep-quiz-bank-chip${i === q.correct_option ? ' correct' : ''}`}>
                                            {QUIZ_OPTION_LABELS[i]}: {opt}
                                        </span>
                                    ))}
                                    <span className="lep-quiz-bank-meta-chip">⏱{q.time_limit}с</span>
                                    <span className="lep-quiz-bank-meta-chip">⭐{q.points}</span>
                                </div>
                            </div>
                            <div className="lep-quiz-bank-item-actions">
                                <button onClick={() => openEdit(q)} title="Редактировать">✏️</button>
                                <button onClick={() => deleteQuestion(q.id)} title="Удалить">🗑</button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
