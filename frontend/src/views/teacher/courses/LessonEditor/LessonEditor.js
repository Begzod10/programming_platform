import React, { useState, useEffect, useMemo } from 'react';
import LessonVocabEditor from './LessonVocabEditor';
import './LessonEditor.css';
import './LessonEditor.additions.css';
import { SECTION_TYPES } from '../../../../constants/courseUtils';
import { SectionsList } from './SectionsList';
import { LessonQuizBankEditor } from './LessonQuizBankEditor';
import { makeSection } from './lessonEditorConstants';

// Re-export makeSection so existing callers keep working.
export { makeSection };

/* ─────────────────────────────────────────────
   MAIN EXPORT: LESSON EDITOR PAGE
───────────────────────────────────────────── */
const LessonEditorPage = ({ course, lesson, chapters, onSave, onClose, apiBaseUrl = '/api/v1' }) => {
    const initialForm = useMemo(() => ({
        title: lesson?.title || '',
        chapter: lesson?.chapter || '',
        image: lesson?.image || '',
        sections: lesson?.sections ? lesson.sections.map(s => ({ ...s })) : [],
    }), [lesson]);
    const [form, setForm] = useState(initialForm);
    const [saving, setSaving] = useState(false);

    // Track whether the form has been touched since open. Used to prompt the
    // teacher before discarding work via Cancel/back.
    const isDirty = useMemo(
        () => JSON.stringify(form) !== JSON.stringify(initialForm),
        [form, initialForm],
    );

    const guardedClose = () => {
        if (saving) return; // never interrupt a save in flight
        if (isDirty) {
            const ok = window.confirm(
                'У вас есть несохранённые изменения. Закрыть без сохранения?',
            );
            if (!ok) return;
        }
        onClose();
    };

    // Block browser back/refresh while there are unsaved edits.
    useEffect(() => {
        if (!isDirty) return;
        const onBeforeUnload = (e) => {
            e.preventDefault();
            e.returnValue = '';
        };
        window.addEventListener('beforeunload', onBeforeUnload);
        return () => window.removeEventListener('beforeunload', onBeforeUnload);
    }, [isDirty]);

    const setField = (key, val) => setForm(f => ({ ...f, [key]: val }));
    const addSection = (type) => setField('sections', [...form.sections, makeSection(type)]);
    const updateSection = (id, data) => setField('sections', form.sections.map(s => s.id === id ? data : s));
    const deleteSection = (id) => setField('sections', form.sections.filter(s => s.id !== id));
    const reorderSections = (list) => setField('sections', list);
    const moveSection = (i, dir) => {
        const list = [...form.sections];
        const t = i + dir;
        if (t < 0 || t >= list.length) return;
        [list[i], list[t]] = [list[t], list[i]];
        setField('sections', list);
    };

    const handleSave = async () => {
        if (!form.title.trim()) return;
        setSaving(true);
        try { await onSave(form); } finally { setSaving(false); }
    };

    return (
        <div className="lep-page">
            <div className="lep-header">
                <div className="lep-header-left">
                    <button className="lep-back-btn" onClick={guardedClose} title="Назад">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                            <path d="M11 4L6 9L11 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                    </button>
                    <div className="lep-header-meta">
                        <span className="lep-header-course">{course?.title}</span>
                        <h2 className="lep-header-title">{lesson ? 'Редактировать урок' : 'Новый урок'}</h2>
                    </div>
                </div>
                <div className="lep-header-right">
                    <button className="lep-cancel-btn" onClick={guardedClose}>Отмена</button>
                    <button className="lep-save-btn" onClick={handleSave} disabled={saving || !form.title.trim()}>
                        {saving
                            ? <><span className="lep-spinner"/>Сохранение...</>
                            : lesson ? <><span>💾</span> Сохранить</> : <><span>✅</span> Добавить урок</>
                        }
                    </button>
                </div>
            </div>

            <div className="lep-body">
                <aside className="lep-sidebar">
                    <div className="lep-sidebar-card">
                        <h3 className="lep-sidebar-title">Основное</h3>
                        <div className="lep-field">
                            <label>Название урока <span className="lep-required">*</span></label>
                            <input className={`lep-field-input${!form.title.trim() ? ' lep-field-input--error' : ''}`}
                                   placeholder="Введите название..." value={form.title}
                                   onChange={e => setField('title', e.target.value)}/>
                            {!form.title.trim() && <span className="lep-field-hint">Обязательное поле</span>}
                        </div>
                        <div className="lep-field">
                            <label>Раздел / Глава</label>
                            <select className="lep-field-select" value={form.chapter}
                                    onChange={e => setField('chapter', e.target.value)}>
                                <option value="">— Без раздела —</option>
                                {chapters.map(ch => <option key={ch} value={ch}>{ch}</option>)}
                            </select>
                        </div>
                        <div className="lep-field">
                            <label>URL обложки</label>
                            <input className="lep-field-input" placeholder="https://..." value={form.image}
                                   onChange={e => setField('image', e.target.value)}/>
                            {form.image && (
                                <div className="lep-cover-preview">
                                    <img src={form.image} alt="cover" onError={e => e.target.style.display = 'none'}/>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="lep-sidebar-card">
                        <h3 className="lep-sidebar-title">Добавить блок</h3>
                        <div className="lep-type-grid">
                            {SECTION_TYPES.map(t => (
                                <button key={t.type} className="lep-type-btn" onClick={() => addSection(t.type)}>
                                    <span className="lep-type-icon">{t.icon}</span>
                                    <span className="lep-type-label">{t.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {form.sections.length > 0 && (
                        <div className="lep-sidebar-card lep-stats-card">
                            <div className="lep-stat-row"><span>📦 Блоков</span><strong>{form.sections.length}</strong></div>
                            {[
                                { type: 'text', icon: '📝', label: 'Текст' },
                                { type: 'video', icon: '🎬', label: 'Видео' },
                                { type: 'code', icon: '💻', label: 'Код' },
                                { type: 'exercise', icon: '🎯', label: 'Упражнения' },
                                { type: 'project', icon: '🚀', label: 'Проект' },
                                { type: 'mashq', icon: '✏️', label: 'Mashq' },
                            ].map(({ type, icon, label }) => {
                                const cnt = form.sections.filter(s => s.type === type).length;
                                return cnt > 0 ? (
                                    <div key={type} className="lep-stat-row">
                                        <span>{icon} {label}</span><strong>{cnt}</strong>
                                    </div>
                                ) : null;
                            })}
                            {(() => {
                                const totalFiles = form.sections
                                    .filter(s => s.type === 'project')
                                    .reduce((sum, s) => sum + (s.projectFiles || []).length, 0);
                                return totalFiles > 0 ? (
                                    <div className="lep-stat-row">
                                        <span>🗂️ Файлов кода</span><strong>{totalFiles}</strong>
                                    </div>
                                ) : null;
                            })()}
                        </div>
                    )}
                </aside>

                <main className="lep-main">
                    {form.sections.length === 0 ? (
                        <div className="lep-empty">
                            <div className="lep-empty-icon">✦</div>
                            <h3>Урок пустой</h3>
                            <p>Добавьте блоки контента с помощью панели слева</p>
                            <div className="lep-empty-types">
                                {SECTION_TYPES.slice(0, 5).map(t => (
                                    <button key={t.type} className="lep-empty-type-btn" onClick={() => addSection(t.type)}>
                                        {t.icon} {t.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <SectionsList
                            sections={form.sections}
                            onReorder={reorderSections}
                            onUpdate={updateSection}
                            onDelete={deleteSection}
                            onMoveUp={i => moveSection(i, -1)}
                            onMoveDown={i => moveSection(i, 1)}
                            lessonId={lesson?.id}
                            apiBaseUrl={apiBaseUrl}
                        />
                    )}
                </main>
            </div>
            {lesson?.id && (
                <LessonVocabEditor
                    courseId={course?.id}
                    lessonId={lesson.id}
                    apiBaseUrl={apiBaseUrl}
                />
            )}
            {lesson?.id && (
                <LessonQuizBankEditor lessonId={lesson.id} apiBaseUrl={apiBaseUrl} />
            )}
        </div>
    );
};

export default LessonEditorPage;
