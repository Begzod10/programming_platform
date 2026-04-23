import React, { useState, useRef, useEffect } from 'react';
import './LessonModal.css';
import '../Exercise additions/Lessonmodal exercise additions.css'
import ReactDOM from 'react-dom';
import { SECTION_TYPES, getYTId } from '../../../../constants/courseUtils';

const FONT_SIZES    = ['12px','14px','16px','18px','20px','24px','28px','32px'];
const FONT_FAMILIES = ['Inter','Georgia','Courier New','Arial','Trebuchet MS'];
const HEADINGS      = ['Paragraph','H1','H2','H3'];
const CODE_LANGS    = ['javascript','typescript','python','html','css','jsx','tsx','java','c','cpp','rust','go','sql','bash'];

const EXERCISE_TYPES = [
    { v: 'text_input',      icon: '✍️', label: 'Свободный ответ',     desc: 'Студент пишет ответ — AI проверяет' },
    { v: 'multiple_choice', icon: '☑️', label: 'Выбор ответа',        desc: 'A/B/C/D варианты, один или несколько правильных' },
    { v: 'drag_and_drop',   icon: '🔀', label: 'Расставь по порядку', desc: 'Перетащи элементы в правильный порядок' },
    { v: 'fill_in_blank',   icon: '✏️', label: 'Заполни пропуски',    desc: 'Впиши слова вместо ___ в тексте' },
];

const DIFFICULTY_LEVELS = [
    { v: 'Easy',   label: 'Лёгкий',   color: '#00b894' },
    { v: 'Medium', label: 'Средний',  color: '#e17055' },
    { v: 'Hard',   label: 'Сложный',  color: '#d63031' },
];

export const makeSection = (type) => ({
    id: Date.now() + Math.random(), type, label: '',
    html: '', code: '', lang: 'javascript',
    videoUrl: '', imgUrl: '', imgUrlDirect: '', imgName: '',
    fileName: '', fileSize: '',
    description: '', requirements: '', techStack: '', deadline: '',
    exercises: [],
});

const makeExercise = () => ({
    _localId: Date.now() + Math.random(),
    title: '', description: '', exercise_type: 'text_input',
    correct_answers: '', drag_items: '', correct_order: '', options: '',
    is_multiple_select: false, expected_answer: '', hint: '', explanation: '',
    difficulty_level: 'Easy', points: 10, order: 0,
});

/* ─────────────────────────────────────────
   Rich Text Editor — с кнопками цвета текста и фона
───────────────────────────────────────── */
const RichTextEditor = ({ value, onChange }) => {
    const editorRef    = useRef(null);
    const savedRange   = useRef(null);
    const textColorRef = useRef(null);
    const bgColorRef   = useRef(null);

    useEffect(() => {
        if (editorRef.current && editorRef.current.innerHTML !== (value || ''))
            editorRef.current.innerHTML = value || '';
    }, []);

    const save    = () => { const s = window.getSelection(); if (s && s.rangeCount > 0) savedRange.current = s.getRangeAt(0).cloneRange(); };
    const restore = () => { if (!savedRange.current) return; const s = window.getSelection(); if (s) { s.removeAllRanges(); s.addRange(savedRange.current); } };
    const prevent = e => e.preventDefault();
    const exec    = (cmd, v = null) => { restore(); document.execCommand(cmd, false, v); onChange(editorRef.current.innerHTML); save(); };

    const applyTextColor = (color) => { restore(); document.execCommand('foreColor', false, color); onChange(editorRef.current.innerHTML); save(); };
    const applyBgColor   = (color) => { restore(); document.execCommand('hiliteColor', false, color); onChange(editorRef.current.innerHTML); save(); };

    return (
        <div>
            <div className="rte-toolbar" onMouseDown={prevent}>
                {/* Heading */}
                <select className="rte-select" defaultValue="Paragraph" onMouseDown={e => e.stopPropagation()}
                    onChange={e => { restore(); document.execCommand('formatBlock', false, e.target.value === 'Paragraph' ? 'p' : e.target.value.toLowerCase()); onChange(editorRef.current.innerHTML); }}>
                    {HEADINGS.map(h => <option key={h}>{h}</option>)}
                </select>
                <div className="rte-divider" />
                {/* Font family */}
                <select className="rte-select" defaultValue="Inter" onMouseDown={e => e.stopPropagation()}
                    onChange={e => { restore(); document.execCommand('fontName', false, e.target.value); onChange(editorRef.current.innerHTML); editorRef.current.focus(); }}>
                    {FONT_FAMILIES.map(f => <option key={f}>{f}</option>)}
                </select>
                {/* Font size */}
                <select className="rte-select" defaultValue="14px" onMouseDown={e => e.stopPropagation()}
                    onChange={e => { restore(); const span = document.createElement('span'); span.style.fontSize = e.target.value; if (savedRange.current && !savedRange.current.collapsed) { try { savedRange.current.surroundContents(span); onChange(editorRef.current.innerHTML); } catch { } } editorRef.current.focus(); }}>
                    {FONT_SIZES.map(s => <option key={s}>{s}</option>)}
                </select>
                <div className="rte-divider" />
                {/* Format */}
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('bold')}><b>B</b></button>
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('italic')}><i>I</i></button>
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('underline')}><u>U</u></button>
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('strikeThrough')}><s>S</s></button>
                <div className="rte-divider" />
                {/* Align */}
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('justifyLeft')}>⬅</button>
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('justifyCenter')}>☰</button>
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('justifyRight')}>➡</button>
                <div className="rte-divider" />
                {/* Lists */}
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('insertUnorderedList')}>• –</button>
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('insertOrderedList')}>1.</button>
                <div className="rte-divider" />
                {/* Цвет текста */}
                <div className="rte-color-wrap" title="Цвет текста" onMouseDown={prevent}
                    onClick={() => { save(); textColorRef.current?.click(); }}>
                    <div className="rte-color-dot" style={{ background: '#1a1a2e', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <span style={{ fontSize: 11, fontWeight: 800, color: 'white', lineHeight: 1, userSelect: 'none' }}>A</span>
                    </div>
                    <input ref={textColorRef} type="color" className="rte-color-input" defaultValue="#1a1a2e"
                        onChange={e => applyTextColor(e.target.value)} />
                </div>
                {/* Цвет фона */}
                <div className="rte-color-wrap" title="Цвет фона текста" onMouseDown={prevent}
                    onClick={() => { save(); bgColorRef.current?.click(); }}>
                    <div className="rte-color-dot" style={{ background: '#fdcb6e', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <span style={{ fontSize: 9, fontWeight: 800, color: '#1a1a2e', lineHeight: 1, userSelect: 'none' }}>bg</span>
                    </div>
                    <input ref={bgColorRef} type="color" className="rte-color-input" defaultValue="#fdcb6e"
                        onChange={e => applyBgColor(e.target.value)} />
                </div>
                <div className="rte-divider" />
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('removeFormat')}>✕</button>
            </div>
            <div className="rte-editor" ref={editorRef} contentEditable suppressContentEditableWarning
                data-placeholder="Введите текст урока..."
                onFocus={save} onKeyUp={save} onMouseUp={save} onSelect={save}
                onInput={() => { onChange(editorRef.current.innerHTML); save(); }}
            />
        </div>
    );
};

/* ─────────────────────────────────────────
   Single Exercise Item
───────────────────────────────────────── */
const ExerciseItem = ({ ex, index, onChange, onDelete }) => {
    const upd = patch => onChange({ ...ex, ...patch });
    const [optionInput, setOptionInput] = useState('');
    const [dragInput,   setDragInput]   = useState('');

    const currentType = EXERCISE_TYPES.find(t => t.v === ex.exercise_type) || EXERCISE_TYPES[0];

    const optionsList = ex.options ? ex.options.split(',').map(o => o.trim()).filter(Boolean) : [];
    const addOption    = () => { const v = optionInput.trim(); if (!v) return; upd({ options: [...optionsList, v].join(',') }); setOptionInput(''); };
    const removeOption = i  => upd({ options: optionsList.filter((_, j) => j !== i).join(',') });

    const dragList  = ex.drag_items ? ex.drag_items.split(',').map(d => d.trim()).filter(Boolean) : [];
    const addDrag    = () => { const v = dragInput.trim(); if (!v) return; upd({ drag_items: [...dragList, v].join(',') }); setDragInput(''); };
    const removeDrag = i  => upd({ drag_items: dragList.filter((_, j) => j !== i).join(',') });

    return (
        <div className="ex-item">
            <div className="ex-item-head">
                <span className="ex-item-num">{index + 1}</span>
                <div className="ex-type-pills">
                    {EXERCISE_TYPES.map(t => (
                        <button key={t.v} className={`ex-type-pill ${ex.exercise_type === t.v ? 'active' : ''}`}
                            onClick={() => upd({ exercise_type: t.v })} title={t.desc}>
                            {t.icon} {t.label}
                        </button>
                    ))}
                </div>
                <button className="ex-delete-btn" onClick={onDelete} title="Удалить задание">✕</button>
            </div>

            <div className="ex-type-desc">{currentType.icon} {currentType.desc}</div>

            <div className="ex-item-body">
                <div className="ex-meta-row">
                    <div className="ex-meta-group">
                        <label>Сложность</label>
                        <div className="ex-diff-pills">
                            {DIFFICULTY_LEVELS.map(d => (
                                <button key={d.v} className={`ex-diff-pill ${ex.difficulty_level === d.v ? 'active' : ''}`}
                                    style={ex.difficulty_level === d.v ? { background: d.color, color: '#fff', borderColor: d.color } : {}}
                                    onClick={() => upd({ difficulty_level: d.v })}>{d.label}</button>
                            ))}
                        </div>
                    </div>
                    <div className="ex-meta-group">
                        <label>Баллы</label>
                        <div className="ex-points-wrap">
                            <input type="number" min="1" max="1000" className="ex-points-input"
                                value={ex.points} onChange={e => upd({ points: Number(e.target.value) })} />
                            <span className="ex-points-suffix">pts</span>
                        </div>
                    </div>
                </div>

                <div className="lm-field">
                    <label>Название задания *</label>
                    <input placeholder="Например: Что такое переменная?"
                        value={ex.title} onChange={e => upd({ title: e.target.value })} />
                </div>

                {ex.exercise_type === 'text_input' && (<>
                    <div className="lm-field"><label>Вопрос для студента *</label>
                        <textarea rows={3} placeholder="Что нужно сделать или написать?"
                            value={ex.description} onChange={e => upd({ description: e.target.value })} /></div>
                    <div className="lm-field">
                        <label>Ожидаемый ответ <span className="ex-label-note">(AI будет проверять по смыслу)</span></label>
                        <textarea rows={2} placeholder="Опишите правильный ответ..."
                            value={ex.expected_answer} onChange={e => upd({ expected_answer: e.target.value })} /></div>
                </>)}

                {ex.exercise_type === 'multiple_choice' && (<>
                    <div className="lm-field"><label>Вопрос *</label>
                        <textarea rows={2} placeholder="Задайте вопрос..."
                            value={ex.description} onChange={e => upd({ description: e.target.value })} /></div>
                    <div className="lm-field">
                        <label>Варианты ответов *</label>
                        <div className="ex-options-list">
                            {optionsList.map((opt, i) => (
                                <div key={i} className="ex-option-row">
                                    <span className="ex-option-letter">{String.fromCharCode(65 + i)}</span>
                                    <span className="ex-option-text">{opt}</span>
                                    <button className="ex-option-del" onClick={() => removeOption(i)}>✕</button>
                                </div>
                            ))}
                            {optionsList.length === 0 && <div className="ex-options-empty">Добавьте хотя бы 2 варианта</div>}
                        </div>
                        <div className="ex-input-row">
                            <input placeholder="Новый вариант..." value={optionInput}
                                onChange={e => setOptionInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && addOption()} />
                            <button className="ex-add-btn" onClick={addOption}>+ Добавить</button>
                        </div>
                    </div>
                    <div className="lm-field">
                        <label>Правильный(е) ответ(ы) * <span className="ex-label-note">— напишите букву(ы): A или A,C</span></label>
                        <input placeholder={ex.is_multiple_select ? 'A,C' : 'A'}
                            value={ex.correct_answers} onChange={e => upd({ correct_answers: e.target.value })} />
                    </div>
                    <label className="ex-checkbox-label">
                        <input type="checkbox" checked={ex.is_multiple_select}
                            onChange={e => upd({ is_multiple_select: e.target.checked })} />
                        Разрешить выбрать несколько правильных ответов
                    </label>
                </>)}

                {ex.exercise_type === 'drag_and_drop' && (<>
                    <div className="lm-field"><label>Инструкция *</label>
                        <textarea rows={2} placeholder="Расставь шаги в правильном порядке..."
                            value={ex.description} onChange={e => upd({ description: e.target.value })} /></div>
                    <div className="lm-field">
                        <label>Элементы для перетаскивания *</label>
                        <div className="ex-drag-list">
                            {dragList.map((item, i) => (
                                <div key={i} className="ex-drag-row">
                                    <span className="ex-drag-handle">⠿</span>
                                    <span className="ex-drag-text">{item}</span>
                                    <button className="ex-option-del" onClick={() => removeDrag(i)}>✕</button>
                                </div>
                            ))}
                            {dragList.length === 0 && <div className="ex-options-empty">Добавьте элементы которые студент будет перетаскивать</div>}
                        </div>
                        <div className="ex-input-row">
                            <input placeholder="Новый элемент..." value={dragInput}
                                onChange={e => setDragInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && addDrag()} />
                            <button className="ex-add-btn" onClick={addDrag}>+ Добавить</button>
                        </div>
                    </div>
                    <div className="lm-field">
                        <label>Правильный порядок * <span className="ex-label-note">— через запятую</span></label>
                        <input placeholder="элемент1,элемент2,элемент3"
                            value={ex.correct_order} onChange={e => upd({ correct_order: e.target.value })} />
                        <span className="lm-field-hint">Напишите элементы в правильной последовательности</span>
                    </div>
                </>)}

                {ex.exercise_type === 'fill_in_blank' && (<>
                    <div className="lm-field">
                        <label>Текст с пропусками * <span className="ex-label-note">— используйте ___ для пропусков</span></label>
                        <textarea rows={3} placeholder="Python — это ___ язык программирования, созданный в ___"
                            value={ex.description} onChange={e => upd({ description: e.target.value })} />
                    </div>
                    {ex.description && ex.description.includes('___') && (
                        <div className="ex-blank-preview">
                            <div className="ex-blank-preview-label">👁 Как видит студент:</div>
                            <div className="ex-blank-preview-text">
                                {ex.description.split('___').map((part, i, arr) => (
                                    <span key={i}>{part}{i < arr.length - 1 && <span className="ex-blank-input-mock" />}</span>
                                ))}
                            </div>
                        </div>
                    )}
                    <div className="lm-field">
                        <label>Правильные ответы * <span className="ex-label-note">— через запятую, по порядку пропусков</span></label>
                        <input placeholder="интерпретируемый,1991"
                            value={ex.correct_answers} onChange={e => upd({ correct_answers: e.target.value })} />
                    </div>
                </>)}

                <div className="ex-hint-row">
                    <div className="lm-field">
                        <label>💡 Подсказка <span className="ex-label-note">(необязательно)</span></label>
                        <input placeholder="Студент увидит это если попросит подсказку..."
                            value={ex.hint} onChange={e => upd({ hint: e.target.value })} />
                    </div>
                    <div className="lm-field">
                        <label>💬 Объяснение <span className="ex-label-note">(после ответа)</span></label>
                        <input placeholder="Почему ответ именно такой..."
                            value={ex.explanation} onChange={e => upd({ explanation: e.target.value })} />
                    </div>
                </div>
            </div>
        </div>
    );
};

/* ─────────────────────────────────────────
   Exercise Editor
───────────────────────────────────────── */
const ExerciseEditor = ({ section, onUpdate }) => {
    const exercises = section.exercises || [];
    const addExercise    = () => onUpdate({ ...section, exercises: [...exercises, makeExercise()] });
    const updateExercise = (localId, data) => onUpdate({ ...section, exercises: exercises.map(e => e._localId === localId ? data : e) });
    const deleteExercise = localId => onUpdate({ ...section, exercises: exercises.filter(e => e._localId !== localId) });
    return (
        <div className="ex-editor">
            {exercises.length === 0 ? (
                <div className="ex-empty-state">
                    <div className="ex-empty-icon">🎯</div>
                    <div className="ex-empty-title">Нет заданий</div>
                    <div className="ex-empty-sub">Добавьте задания для практики студентов</div>
                </div>
            ) : (
                <div className="ex-list">
                    {exercises.map((ex, i) => (
                        <ExerciseItem key={ex._localId} ex={ex} index={i}
                            onChange={data => updateExercise(ex._localId, data)}
                            onDelete={() => deleteExercise(ex._localId)} />
                    ))}
                </div>
            )}
            <button className="ex-add-exercise-btn" onClick={addExercise}>➕ Добавить задание</button>
        </div>
    );
};

/* ─────────────────────────────────────────
   Section Block
───────────────────────────────────────── */
const SectionBlock = ({ section, onUpdate, onDelete }) => {
    const fileRef = useRef(null);
    const imgRef  = useRef(null);
    const update  = patch => onUpdate({ ...section, ...patch });
    const meta    = SECTION_TYPES.find(t => t.type === section.type);
    const ytId    = section.type === 'video' ? getYTId(section.videoUrl || '') : null;
    return (
        <div className="lm-section">
            <div className="lm-section-head">
                <div className="lm-section-head-left">
                    <span>{meta?.icon}</span>
                    <span className="lm-section-badge">{meta?.label}</span>
                    <input className="lm-section-label-input" placeholder="Заголовок блока..."
                        value={section.label} onChange={e => update({ label: e.target.value })} />
                </div>
                <button className="lm-section-del" onClick={onDelete}>✕</button>
            </div>
            <div className="lm-section-body">
                {section.type === 'text'     && <RichTextEditor value={section.html} onChange={html => update({ html })} />}
                {section.type === 'code'     && (<>
                    <div className="lm-code-lang"><label>Язык:</label>
                        <select value={section.lang} onChange={e => update({ lang: e.target.value })}>
                            {CODE_LANGS.map(l => <option key={l}>{l}</option>)}
                        </select>
                    </div>
                    <textarea className="lm-code-area" placeholder="// Код сюда..."
                        value={section.code} onChange={e => update({ code: e.target.value })} />
                </>)}
                {section.type === 'video'    && (<>
                    <input className="lm-video-input" placeholder="YouTube ссылка..."
                        value={section.videoUrl} onChange={e => update({ videoUrl: e.target.value })} />
                    <div className="lm-video-preview">
                        {ytId ? <iframe src={`https://www.youtube.com/embed/${ytId}`} allowFullScreen title="preview" />
                              : <div className="lm-video-placeholder"><div className="lm-video-placeholder-icon">🎬</div><p>Введите YouTube ссылку</p></div>}
                    </div>
                </>)}
                {section.type === 'image'    && (<>
                    <div className="lm-img-upload" onClick={() => imgRef.current.click()}>
                        <div className="lm-img-upload-icon">🖼️</div>
                        <p>Нажмите для загрузки</p><p className="hint">PNG, JPG, WebP</p>
                    </div>
                    <input ref={imgRef} type="file" accept="image/*" style={{ display: 'none' }}
                        onChange={e => { const f = e.target.files[0]; if (f) update({ imgUrl: URL.createObjectURL(f), imgName: f.name, imgUrlDirect: '' }); }} />
                    {section.imgUrl && <div className="lm-img-preview"><img src={section.imgUrl} alt={section.imgName || ''} /></div>}
                    <input className="lm-img-url-input" placeholder="Или URL изображения"
                        value={section.imgUrlDirect} onChange={e => update({ imgUrlDirect: e.target.value, imgUrl: e.target.value })} />
                </>)}
                {section.type === 'file'     && (<>
                    <div className="lm-file-drop" onClick={() => fileRef.current.click()}>
                        <div className="lm-file-drop-icon">📁</div><p>Нажмите для загрузки файла</p>
                    </div>
                    <input ref={fileRef} type="file" style={{ display: 'none' }}
                        onChange={e => { const f = e.target.files[0]; if (f) update({ fileName: f.name, fileSize: (f.size / 1024).toFixed(1) + ' KB' }); }} />
                    {section.fileName && (
                        <div className="lm-file-info">
                            <span className="lm-file-info-icon">📦</span>
                            <div><div className="lm-file-name">{section.fileName}</div><div className="lm-file-size">{section.fileSize}</div></div>
                        </div>
                    )}
                </>)}
                {section.type === 'exercise' && <ExerciseEditor section={section} onUpdate={onUpdate} />}
                {section.type === 'project'  && (
                    <div className="lm-project-fields">
                        <div className="lm-project-info-banner">🚀 Задание для студента</div>
                        <div className="lm-field"><label>Описание *</label>
                            <textarea className="lm-project-textarea" rows={3} placeholder="Что нужно сделать?"
                                value={section.description} onChange={e => update({ description: e.target.value })} /></div>
                        <div className="lm-field"><label>Требования</label>
                            <textarea className="lm-project-textarea" rows={4} placeholder="1. ...\n2. ..."
                                value={section.requirements} onChange={e => update({ requirements: e.target.value })} /></div>
                        <div className="lm-field"><label>Стек технологий</label>
                            <input placeholder="React, FastAPI..." value={section.techStack}
                                onChange={e => update({ techStack: e.target.value })} />
                            <span className="lm-field-hint">Через запятую</span></div>
                        <div className="lm-field"><label>Дедлайн (дней)</label>
                            <input type="number" min="1" placeholder="7" value={section.deadline}
                                onChange={e => update({ deadline: e.target.value })} /></div>
                    </div>
                )}
            </div>
        </div>
    );
};

/* ─────────────────────────────────────────
   Main LessonModal
───────────────────────────────────────── */
const LessonModal = ({ course, lesson, chapters, onSave, onClose }) => {
    const [form, setForm] = useState({
        title:    lesson?.title   || '',
        chapter:  lesson?.chapter || '',
        image:    lesson?.image   || '',
        order:    lesson?.order   || '',
        sections: lesson?.sections ? lesson.sections.map(s => ({ ...s })) : [],
    });

    useEffect(() => {
        const p = document.querySelector('.page-container');
        if (p) p.classList.add('stop-scrolling');
        return () => { if (p) p.classList.remove('stop-scrolling'); };
    }, []);

    const setField      = (k, v) => setForm(f => ({ ...f, [k]: v }));
    const addSection    = type  => setField('sections', [...form.sections, makeSection(type)]);
    const updateSection = (id, data) => setField('sections', form.sections.map(s => s.id === id ? data : s));
    const deleteSection = id   => setField('sections', form.sections.filter(s => s.id !== id));
    const handleSave    = ()   => { if (form.title.trim()) onSave(form); };

    return ReactDOM.createPortal(
        <div className="lm-overlay" onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
            <div className="lm-panel">
                <div className="lm-header">
                    <div className="lm-header-left">
                        <button className="lm-back-btn" onClick={onClose}>←</button>
                        <div className="lm-header-title">
                            <span className="lm-header-course">{course?.title}</span>
                            <h3>{lesson ? 'Редактировать урок' : 'Новый урок'}</h3>
                        </div>
                    </div>
                    <button className="lm-save-btn" onClick={handleSave}>
                        {lesson ? '💾 Сохранить' : '✅ Добавить урок'}
                    </button>
                </div>
                <div className="lm-body">
                    <div className="lm-row">
                        <div className="lm-field"><label>Название урока *</label>
                            <input placeholder="Введение в компоненты" value={form.title}
                                onChange={e => setField('title', e.target.value)} /></div>
                        <div className="lm-field"><label>Раздел</label>
                            <select value={form.chapter} onChange={e => setField('chapter', e.target.value)}>
                                <option value="">— Без раздела —</option>
                                {chapters.map(ch => <option key={ch} value={ch}>{ch}</option>)}
                            </select></div>
                    </div>
                    <div className="lm-row">
                        <div className="lm-field"><label>URL обложки</label>
                            <input placeholder="https://..." value={form.image}
                                onChange={e => setField('image', e.target.value)} /></div>
                        <div className="lm-field lm-field-order"><label>Порядок</label>
                            <input type="number" min="1" placeholder="1" value={form.order}
                                onChange={e => setField('order', e.target.value)} />
                            <span className="lm-field-hint">Чем меньше — тем раньше</span></div>
                    </div>
                    <div className="lm-section-toolbar">
                        <span className="lm-section-toolbar-label">Добавить блок контента</span>
                        <div className="lm-type-btns">
                            {SECTION_TYPES.map(t => (
                                <button key={t.type} className="lm-type-btn" onClick={() => addSection(t.type)}>
                                    {t.icon} {t.label}
                                </button>
                            ))}
                        </div>
                    </div>
                    {form.sections.length > 0 ? (
                        <div className="lm-sections-list">
                            {form.sections.map(s => (
                                <SectionBlock key={s.id} section={s}
                                    onUpdate={data => updateSection(s.id, data)}
                                    onDelete={() => deleteSection(s.id)} />
                            ))}
                        </div>
                    ) : (
                        <div className="lm-sections-empty">
                            <div className="lm-sections-empty-icon">📄</div>
                            <p>Добавьте блоки урока с помощью кнопок выше</p>
                        </div>
                    )}
                </div>
            </div>
        </div>,
        document.body
    );
};

export default LessonModal;