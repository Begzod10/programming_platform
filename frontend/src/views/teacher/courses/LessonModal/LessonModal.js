import React, { useState, useRef, useEffect } from 'react';
import './LessonModal.css';
import '../Exercise additions/Lessonmodal exercise additions.css';
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
    { v: 'Easy',   label: 'Лёгкий',  color: '#00b894' },
    { v: 'Medium', label: 'Средний', color: '#e17055' },
    { v: 'Hard',   label: 'Сложный', color: '#d63031' },
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

/* ── Rich Text Editor ── */
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
                <select className="rte-select" defaultValue="Paragraph" onMouseDown={e => e.stopPropagation()}
                    onChange={e => { restore(); document.execCommand('formatBlock', false, e.target.value === 'Paragraph' ? 'p' : e.target.value.toLowerCase()); onChange(editorRef.current.innerHTML); }}>
                    {HEADINGS.map(h => <option key={h}>{h}</option>)}
                </select>
                <div className="rte-divider" />
                <select className="rte-select" defaultValue="Inter" onMouseDown={e => e.stopPropagation()}
                    onChange={e => { restore(); document.execCommand('fontName', false, e.target.value); onChange(editorRef.current.innerHTML); editorRef.current.focus(); }}>
                    {FONT_FAMILIES.map(f => <option key={f}>{f}</option>)}
                </select>
                <select className="rte-select" defaultValue="14px" onMouseDown={e => e.stopPropagation()}
                    onChange={e => { restore(); const span = document.createElement('span'); span.style.fontSize = e.target.value; if (savedRange.current && !savedRange.current.collapsed) { try { savedRange.current.surroundContents(span); onChange(editorRef.current.innerHTML); } catch { } } editorRef.current.focus(); }}>
                    {FONT_SIZES.map(s => <option key={s}>{s}</option>)}
                </select>
                <div className="rte-divider" />
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('bold')}><b>B</b></button>
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('italic')}><i>I</i></button>
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('underline')}><u>U</u></button>
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('strikeThrough')}><s>S</s></button>
                <div className="rte-divider" />
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('justifyLeft')}>⬅</button>
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('justifyCenter')}>☰</button>
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('justifyRight')}>➡</button>
                <div className="rte-divider" />
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('insertUnorderedList')}>•–</button>
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('insertOrderedList')}>1.</button>
                <div className="rte-divider" />
                <div className="rte-color-wrap" title="Цвет текста" onMouseDown={prevent} onClick={() => { save(); textColorRef.current?.click(); }}>
                    <div className="rte-color-dot" style={{ background: '#1a1a2e', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <span style={{ fontSize: 10, fontWeight: 800, color: 'white', lineHeight: 1, userSelect: 'none' }}>A</span>
                    </div>
                    <input ref={textColorRef} type="color" className="rte-color-input" defaultValue="#1a1a2e" onChange={e => applyTextColor(e.target.value)} />
                </div>
                <div className="rte-color-wrap" title="Цвет фона текста" onMouseDown={prevent} onClick={() => { save(); bgColorRef.current?.click(); }}>
                    <div className="rte-color-dot" style={{ background: '#fdcb6e', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <span style={{ fontSize: 8, fontWeight: 800, color: '#1a1a2e', lineHeight: 1, userSelect: 'none' }}>bg</span>
                    </div>
                    <input ref={bgColorRef} type="color" className="rte-color-input" defaultValue="#fdcb6e" onChange={e => applyBgColor(e.target.value)} />
                </div>
                <div className="rte-divider" />
                <button className="rte-btn" onMouseDown={prevent} onClick={() => exec('removeFormat')}>✕</button>
            </div>
            <div className="rte-editor" ref={editorRef} contentEditable suppressContentEditableWarning
                data-placeholder="Введите текст урока..."
                onFocus={save} onKeyUp={save} onMouseUp={save} onSelect={save}
                onInput={() => { onChange(editorRef.current.innerHTML); save(); }} />
        </div>
    );
};

/* ── Exercise Item ── */
const ExerciseItem = ({ ex, index, onChange, onDelete, onMoveUp, onMoveDown, isFirst, isLast }) => {
    const upd = patch => onChange({ ...ex, ...patch });
    const [optionInput, setOptionInput] = useState('');
    const [dragInput,   setDragInput]   = useState('');
    const [collapsed,   setCollapsed]   = useState(false);
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
                <div className="ex-item-head-left">
                    <span className="ex-item-num">{index + 1}</span>
                    <span className="ex-item-type-label">{currentType.icon} {currentType.label}</span>
                    {ex.title && <span className="ex-item-title-preview">{ex.title}</span>}
                </div>
                <div className="ex-item-head-actions">
                    <button className="ex-move-btn" onClick={onMoveUp}  disabled={isFirst}  title="Переместить вверх">↑</button>
                    <button className="ex-move-btn" onClick={onMoveDown} disabled={isLast}  title="Переместить вниз">↓</button>
                    <button className="ex-collapse-btn" onClick={() => setCollapsed(c => !c)}>{collapsed ? '▼ Развернуть' : '▲ Свернуть'}</button>
                    <button className="ex-delete-btn" onClick={onDelete} title="Удалить задание">✕</button>
                </div>
            </div>

            {!collapsed && <>
                <div className="ex-type-pills">
                    {EXERCISE_TYPES.map(t => (
                        <button key={t.v} className={`ex-type-pill ${ex.exercise_type === t.v ? 'active' : ''}`}
                            onClick={() => upd({ exercise_type: t.v })} title={t.desc}>
                            {t.icon} {t.label}
                        </button>
                    ))}
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
                                <input type="number" min="1" max="1000" className="ex-points-input" value={ex.points} onChange={e => upd({ points: Number(e.target.value) })} />
                                <span className="ex-points-suffix">pts</span>
                            </div>
                        </div>
                    </div>

                    <div className="lm-field">
                        <label>Название задания *</label>
                        <input placeholder="Например: Что такое переменная?" value={ex.title} onChange={e => upd({ title: e.target.value })} />
                    </div>

                    {ex.exercise_type === 'text_input' && (<>
                        <div className="lm-field"><label>Вопрос для студента *</label>
                            <textarea rows={3} placeholder="Что нужно сделать или написать?" value={ex.description} onChange={e => upd({ description: e.target.value })} /></div>
                        <div className="lm-field"><label>Ожидаемый ответ <span className="ex-label-note">(AI будет проверять по смыслу)</span></label>
                            <textarea rows={2} placeholder="Опишите правильный ответ..." value={ex.expected_answer} onChange={e => upd({ expected_answer: e.target.value })} /></div>
                    </>)}

                    {ex.exercise_type === 'multiple_choice' && (<>
                        <div className="lm-field"><label>Вопрос *</label>
                            <textarea rows={2} placeholder="Задайте вопрос..." value={ex.description} onChange={e => upd({ description: e.target.value })} /></div>
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
                                <input placeholder="Новый вариант..." value={optionInput} onChange={e => setOptionInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && addOption()} />
                                <button className="ex-add-btn" onClick={addOption}>+ Добавить</button>
                            </div>
                        </div>
                        <div className="lm-field">
                            <label>Правильный(е) ответ(ы) * <span className="ex-label-note">— напишите букву(ы): A или A,C</span></label>
                            <input placeholder={ex.is_multiple_select ? 'A,C' : 'A'} value={ex.correct_answers} onChange={e => upd({ correct_answers: e.target.value })} />
                        </div>
                        <label className="ex-checkbox-label">
                            <input type="checkbox" checked={ex.is_multiple_select} onChange={e => upd({ is_multiple_select: e.target.checked })} />
                            Разрешить выбрать несколько правильных ответов
                        </label>
                    </>)}

                    {ex.exercise_type === 'drag_and_drop' && (<>
                        <div className="lm-field"><label>Инструкция *</label>
                            <textarea rows={2} placeholder="Расставь шаги в правильном порядке..." value={ex.description} onChange={e => upd({ description: e.target.value })} /></div>
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
                                <input placeholder="Новый элемент..." value={dragInput} onChange={e => setDragInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && addDrag()} />
                                <button className="ex-add-btn" onClick={addDrag}>+ Добавить</button>
                            </div>
                        </div>
                        <div className="lm-field">
                            <label>Правильный порядок * <span className="ex-label-note">— через запятую</span></label>
                            <input placeholder="элемент1,элемент2,элемент3" value={ex.correct_order} onChange={e => upd({ correct_order: e.target.value })} />
                        </div>
                    </>)}

                    {ex.exercise_type === 'fill_in_blank' && (<>
                        <div className="lm-field">
                            <label>Текст с пропусками * <span className="ex-label-note">— используйте ___ для пропусков</span></label>
                            <textarea rows={3} placeholder="Python — это ___ язык программирования, созданный в ___" value={ex.description} onChange={e => upd({ description: e.target.value })} />
                        </div>
                        {ex.description?.includes('___') && (
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
                            <input placeholder="интерпретируемый,1991" value={ex.correct_answers} onChange={e => upd({ correct_answers: e.target.value })} />
                        </div>
                    </>)}

                    <div className="ex-hint-row">
                        <div className="lm-field">
                            <label>💡 Подсказка <span className="ex-label-note">(необязательно)</span></label>
                            <input placeholder="Студент увидит это если попросит подсказку..." value={ex.hint} onChange={e => upd({ hint: e.target.value })} />
                        </div>
                        <div className="lm-field">
                            <label>💬 Объяснение <span className="ex-label-note">(после ответа)</span></label>
                            <input placeholder="Почему ответ именно такой..." value={ex.explanation} onChange={e => upd({ explanation: e.target.value })} />
                        </div>
                    </div>
                </div>
            </>}
        </div>
    );
};

/* ── Exercise Editor ── */
const ExerciseEditor = ({ section, onUpdate }) => {
    const exercises = section.exercises || [];
    const addExercise    = () => onUpdate({ ...section, exercises: [...exercises, makeExercise()] });
    const updateExercise = (localId, data) => onUpdate({ ...section, exercises: exercises.map(e => e._localId === localId ? data : e) });
    const deleteExercise = localId => onUpdate({ ...section, exercises: exercises.filter(e => e._localId !== localId) });
    const moveExercise = (index, direction) => {
        const arr = [...exercises];
        const target = index + direction;
        if (target < 0 || target >= arr.length) return;
        [arr[index], arr[target]] = [arr[target], arr[index]];
        onUpdate({ ...section, exercises: arr });
    };

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
                            onDelete={() => deleteExercise(ex._localId)}
                            onMoveUp={() => moveExercise(i, -1)}
                            onMoveDown={() => moveExercise(i, 1)}
                            isFirst={i === 0} isLast={i === exercises.length - 1} />
                    ))}
                </div>
            )}
            <button className="ex-add-exercise-btn" onClick={addExercise}>➕ Добавить задание</button>
        </div>
    );
};

/* ── Section Block ── */
const SectionBlock = ({ section, onUpdate, onDelete, onMoveUp, onMoveDown, isFirst, isLast }) => {
    const fileRef = useRef(null);
    const imgRef  = useRef(null);
    const update  = patch => onUpdate({ ...section, ...patch });
    const meta    = SECTION_TYPES.find(t => t.type === section.type);
    const ytId    = section.type === 'video' ? getYTId(section.videoUrl || '') : null;
    const [collapsed, setCollapsed] = useState(false);

    return (
        <div className={`lm-section ${collapsed ? 'collapsed' : ''}`}>
            <div className="lm-section-head">
                <div className="lm-section-head-left">
                    <span className="lm-drag-handle" title="Перетащить блок">⠿⠿</span>
                    <span>{meta?.icon}</span>
                    <span className="lm-section-badge">{meta?.label}</span>
                    <input className="lm-section-label-input" placeholder="Заголовок блока..."
                        value={section.label} onChange={e => update({ label: e.target.value })} />
                </div>
                <div className="lm-section-head-right">
                    <button className="lm-move-btn" onClick={onMoveUp}  disabled={isFirst}  title="Вверх">↑</button>
                    <button className="lm-move-btn" onClick={onMoveDown} disabled={isLast}  title="Вниз">↓</button>
                    <button className="lm-collapse-btn" onClick={() => setCollapsed(c => !c)}>{collapsed ? '▼' : '▲'}</button>
                    <button className="lm-section-del" onClick={onDelete}>✕</button>
                </div>
            </div>

            {!collapsed && (
                <div className="lm-section-body">
                    {section.type === 'text'     && <RichTextEditor value={section.html} onChange={html => update({ html })} />}
                    {section.type === 'code'     && (<>
                        <div className="lm-code-lang"><label>Язык:</label>
                            <select value={section.lang} onChange={e => update({ lang: e.target.value })}>
                                {CODE_LANGS.map(l => <option key={l}>{l}</option>)}
                            </select>
                        </div>
                        <textarea className="lm-code-area" placeholder="// Код сюда..." value={section.code} onChange={e => update({ code: e.target.value })} />
                    </>)}
                    {section.type === 'video'    && (<>
                        <input className="lm-video-input" placeholder="YouTube ссылка..." value={section.videoUrl} onChange={e => update({ videoUrl: e.target.value })} />
                        <div className="lm-video-preview">
                            {ytId ? <iframe src={`https://www.youtube.com/embed/${ytId}`} allowFullScreen title="preview" />
                                  : <div className="lm-video-placeholder"><div className="lm-video-placeholder-icon">🎬</div><p>Введите YouTube ссылку</p></div>}
                        </div>
                    </>)}
                    {section.type === 'image'    && (<>
                        <div className="lm-img-upload" onClick={() => imgRef.current.click()}>
                            <div className="lm-img-upload-icon">🖼️</div><p>Нажмите для загрузки</p><p className="hint">PNG, JPG, WebP</p>
                        </div>
                        <input ref={imgRef} type="file" accept="image/*" style={{ display: 'none' }}
                            onChange={e => { const f = e.target.files[0]; if (f) update({ imgUrl: URL.createObjectURL(f), imgName: f.name, imgUrlDirect: '' }); }} />
                        {section.imgUrl && <div className="lm-img-preview"><img src={section.imgUrl} alt={section.imgName || ''} /></div>}
                        <input className="lm-img-url-input" placeholder="Или URL изображения" value={section.imgUrlDirect}
                            onChange={e => update({ imgUrlDirect: e.target.value, imgUrl: e.target.value })} />
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
                                <textarea className="lm-project-textarea" rows={3} placeholder="Что нужно сделать?" value={section.description} onChange={e => update({ description: e.target.value })} /></div>
                            <div className="lm-field"><label>Требования</label>
                                <textarea className="lm-project-textarea" rows={4} placeholder="1. ...\n2. ..." value={section.requirements} onChange={e => update({ requirements: e.target.value })} /></div>
                            <div className="lm-field"><label>Стек технологий</label>
                                <input placeholder="React, FastAPI..." value={section.techStack} onChange={e => update({ techStack: e.target.value })} />
                                <span className="lm-field-hint">Через запятую</span></div>
                            <div className="lm-field"><label>Дедлайн (дней)</label>
                                <input type="number" min="1" placeholder="7" value={section.deadline} onChange={e => update({ deadline: e.target.value })} /></div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

/* ═══════════════════════════════════════════
   Main LessonModal
═══════════════════════════════════════════ */
const LessonModal = ({ course, lesson, chapters, onSave, onClose }) => {
    const [form, setForm] = useState({
        title:    lesson?.title   || '',
        chapter:  lesson?.chapter || '',
        image:    lesson?.image   || '',
        order:    lesson?.order   || '',
        sections: lesson?.sections ? lesson.sections.map(s => ({ ...s })) : [],
    });

    // ── Mobile sidebar state ──
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const sidebarRef = useRef(null);

    // Close sidebar on overlay tap
    const handleOverlayClick = () => setSidebarOpen(false);

    // Close sidebar when a block type is added (mobile UX)
    const addSectionMobile = (type) => {
        addSection(type);
        setSidebarOpen(false);
    };

    // ── Drag-and-drop ──
    const dragIdx     = useRef(null);
    const dragOverIdx = useRef(null);

    const setField      = (k, v) => setForm(f => ({ ...f, [k]: v }));
    const addSection    = type  => setField('sections', [...form.sections, makeSection(type)]);
    const updateSection = (id, data) => setField('sections', form.sections.map(s => s.id === id ? data : s));
    const deleteSection = id   => setField('sections', form.sections.filter(s => s.id !== id));

    const moveSection = (index, direction) => {
        const arr = [...form.sections];
        const target = index + direction;
        if (target < 0 || target >= arr.length) return;
        [arr[index], arr[target]] = [arr[target], arr[index]];
        setField('sections', arr);
    };

    const handleDragStart = (e, index) => { dragIdx.current = index; e.dataTransfer.effectAllowed = 'move'; };
    const handleDragOver  = (e, index) => { e.preventDefault(); dragOverIdx.current = index; };
    const handleDrop = (e) => {
        e.preventDefault();
        if (dragIdx.current === null || dragOverIdx.current === null || dragIdx.current === dragOverIdx.current) return;
        const arr = [...form.sections];
        const [moved] = arr.splice(dragIdx.current, 1);
        arr.splice(dragOverIdx.current, 0, moved);
        setField('sections', arr);
        dragIdx.current = null;
        dragOverIdx.current = null;
    };

    // ── Save — show error if title empty ──
    const [titleError, setTitleError] = useState(false);
    const handleSave = () => {
        if (!form.title.trim()) {
            setTitleError(true);
            // Open sidebar on mobile so user sees the error
            setSidebarOpen(true);
            // Scroll to title field
            setTimeout(() => {
                const el = sidebarRef.current?.querySelector('input[placeholder="Введение в компоненты"]');
                el?.focus();
                el?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
            return;
        }
        setTitleError(false);
        onSave(form);
    };

    // Lock body scroll
    useEffect(() => {
        document.body.style.overflow = 'hidden';
        return () => { document.body.style.overflow = ''; };
    }, []);

    // Sidebar content (shared between desktop and mobile bottom sheet)
    const SidebarContent = () => (
        <>
            <div className="lm-sidebar-section">
                <h4 className="lm-sidebar-title">📋 Основное</h4>
                <div className="lm-field">
                    <label>Название урока *</label>
                    <input
                        placeholder="Введение в компоненты"
                        value={form.title}
                        onChange={e => { setField('title', e.target.value); setTitleError(false); }}
                        style={titleError ? { borderColor: '#ff7675', boxShadow: '0 0 0 3px rgba(255,118,117,0.15)' } : {}}
                    />
                    {titleError && (
                        <span style={{ fontSize: 11, color: '#ff7675', fontWeight: 600 }}>
                            ⚠ Введите название урока
                        </span>
                    )}
                </div>
                <div className="lm-field">
                    <label>Раздел</label>
                    <select value={form.chapter} onChange={e => setField('chapter', e.target.value)}>
                        <option value="">— Без раздела —</option>
                        {chapters.map(ch => <option key={ch} value={ch}>{ch}</option>)}
                    </select>
                </div>
                <div className="lm-field">
                    <label>URL обложки</label>
                    <input placeholder="https://..." value={form.image} onChange={e => setField('image', e.target.value)} />
                    {form.image && <img src={form.image} alt="preview" className="lm-cover-preview" />}
                </div>
                <div className="lm-field">
                    <label>Порядок</label>
                    <input type="number" min="1" placeholder="1" value={form.order} onChange={e => setField('order', e.target.value)} />
                    <span className="lm-field-hint">Чем меньше — тем раньше</span>
                </div>
            </div>

            <div className="lm-sidebar-section">
                <h4 className="lm-sidebar-title">➕ Добавить блок</h4>
                <div className="lm-type-grid">
                    {SECTION_TYPES.map(t => (
                        <button key={t.type} className="lm-type-card" onClick={() => addSectionMobile(t.type)}>
                            <span className="lm-type-card-icon">{t.icon}</span>
                            <span className="lm-type-card-label">{t.label}</span>
                        </button>
                    ))}
                </div>
            </div>

            {form.sections.length > 0 && (
                <div className="lm-sidebar-section">
                    <h4 className="lm-sidebar-title">🗂 Блоки урока</h4>
                    <div className="lm-blocks-nav">
                        {form.sections.map((s, i) => {
                            const meta = SECTION_TYPES.find(t => t.type === s.type);
                            return (
                                <div key={s.id} className="lm-block-nav-item"
                                    onClick={() => {
                                        setSidebarOpen(false);
                                        setTimeout(() => {
                                            document.getElementById(`block-${s.id}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                        }, 300);
                                    }}>
                                    <span>{meta?.icon}</span>
                                    <span>{s.label || meta?.label}</span>
                                    <span className="lm-block-nav-num">{i + 1}</span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </>
    );

    return (
        <div className="lm-page">
            {/* Header */}
            <div className="lm-page-header">
                <div className="lm-header-left">
                    <button className="lm-back-btn" onClick={onClose}>
                        ← <span>Назад</span>
                    </button>
                    <div className="lm-header-title">
                        <span className="lm-header-course">{course?.title}</span>
                        <h3>{lesson ? 'Редактировать урок' : 'Новый урок'}</h3>
                    </div>
                </div>
                <div className="lm-header-right">
                    <span className="lm-blocks-count">{form.sections.length} блоков</span>
                    <button className="lm-save-btn" onClick={handleSave}>
                        {lesson ? '💾 Сохранить' : '✅ Добавить урок'}
                    </button>
                </div>
            </div>

            <div className="lm-page-body">
                {/* Mobile overlay */}
                <div
                    className={`lm-sidebar-overlay ${sidebarOpen ? 'open' : ''}`}
                    onClick={handleOverlayClick}
                />

                {/* Sidebar (desktop: fixed left | mobile: bottom sheet) */}
                <div
                    ref={sidebarRef}
                    className={`lm-page-sidebar ${sidebarOpen ? 'mobile-open' : ''}`}
                >
                    <SidebarContent />
                </div>

                {/* Content area */}
                <div className="lm-page-content">
                    {form.sections.length === 0 ? (
                        <div className="lm-sections-empty">
                            <div className="lm-sections-empty-icon">📄</div>
                            <p>Добавьте блоки урока из панели</p>
                            <p className="lm-sections-empty-hint">Нажмите кнопку ✚ внизу экрана</p>
                        </div>
                    ) : (
                        <div className="lm-sections-list">
                            {form.sections.map((s, i) => (
                                <div
                                    key={s.id}
                                    id={`block-${s.id}`}
                                    draggable
                                    onDragStart={e => handleDragStart(e, i)}
                                    onDragOver={e => handleDragOver(e, i)}
                                    onDrop={handleDrop}
                                    className="lm-section-drag-wrapper"
                                >
                                    <SectionBlock
                                        section={s}
                                        onUpdate={data => updateSection(s.id, data)}
                                        onDelete={() => deleteSection(s.id)}
                                        onMoveUp={() => moveSection(i, -1)}
                                        onMoveDown={() => moveSection(i, 1)}
                                        isFirst={i === 0}
                                        isLast={i === form.sections.length - 1}
                                    />
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* FAB button — mobile only */}
            <button
                className="lm-sidebar-toggle"
                onClick={() => setSidebarOpen(o => !o)}
                title="Меню"
            >
                {sidebarOpen ? '✕' : '✚'}
            </button>
        </div>
    );
};

export default LessonModal;