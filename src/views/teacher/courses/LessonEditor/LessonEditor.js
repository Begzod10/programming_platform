import React, {useState, useRef, useEffect} from 'react';
import './LessonEditor.css';
import {SECTION_TYPES, getYTId} from '../../../../constants/courseUtils';

/* ─── Constants ─── */
const FONT_SIZES = ['12px', '14px', '16px', '18px', '20px', '24px', '28px', '32px'];
const FONT_FAMILIES = ['Georgia', 'Courier New', 'Arial', 'Trebuchet MS', 'Verdana'];
const HEADINGS = ['Paragraph', 'H1', 'H2', 'H3'];
const CODE_LANGS = ['javascript', 'typescript', 'python', 'html', 'css', 'jsx', 'tsx', 'java', 'c', 'cpp', 'rust', 'go', 'sql', 'bash'];
const EX_TYPES = ['text_input', 'multiple_choice', 'drag_and_drop', 'fill_in_blank'];
const DIFF_LEVELS = ['Easy', 'Medium', 'Hard'];

export const makeSection = (type) => ({
    id: Date.now() + Math.random(),
    type,
    label: '',
    html: '',
    code: '',
    lang: 'javascript',
    videoUrl: '',
    imgUrl: '',
    imgUrlDirect: '',
    imgName: '',
    fileName: '',
    fileSize: '',
    description: '',
    requirements: '',
    techStack: '',
    deadline: '',
    exercises: [],
    mashqType: 'textarea',
    question: '',
    answer: '',
    words: [],
});

const makeExercise = () => ({
    _localId: Date.now() + Math.random(),
    id: null,
    title: '',
    description: '',
    exercise_type: 'text_input',
    options: '',
    correct_answers: '',
    drag_items: '',
    correct_order: '',
    is_multiple_select: false,
    expected_answer: '',
    hint: '',
    difficulty_level: 'Easy',
    points: 10,
    order: 0,
});

/* ─────────────────────────────────────────────
   RICH TEXT EDITOR
───────────────────────────────────────────── */
const RichTextEditor = ({value, onChange}) => {
    const editorRef = useRef(null);
    const savedRange = useRef(null);

    useEffect(() => {
        if (editorRef.current && editorRef.current.innerHTML !== (value || ''))
            editorRef.current.innerHTML = value || '';
    }, []);

    const saveSelection = () => {
        const sel = window.getSelection();
        if (sel && sel.rangeCount > 0) savedRange.current = sel.getRangeAt(0).cloneRange();
    };
    const restoreSelection = () => {
        if (!savedRange.current) return;
        const sel = window.getSelection();
        if (sel) {
            sel.removeAllRanges();
            sel.addRange(savedRange.current);
        }
    };
    const preventBlur = (e) => e.preventDefault();
    const exec = (cmd, val = null) => {
        restoreSelection();
        document.execCommand(cmd, false, val);
        onChange(editorRef.current.innerHTML);
        saveSelection();
    };
    const setBlock = (e) => {
        restoreSelection();
        document.execCommand('formatBlock', false, e.target.value === 'Paragraph' ? 'p' : e.target.value.toLowerCase());
        onChange(editorRef.current.innerHTML);
        editorRef.current.focus();
    };
    const applyFontFamily = (e) => {
        restoreSelection();
        document.execCommand('fontName', false, e.target.value);
        onChange(editorRef.current.innerHTML);
        editorRef.current.focus();
    };
    const applyFontSize = (e) => {
        const size = e.target.value;
        restoreSelection();
        if (savedRange.current && !savedRange.current.collapsed) {
            const span = document.createElement('span');
            span.style.fontSize = size;
            try {
                savedRange.current.surroundContents(span);
                onChange(editorRef.current.innerHTML);
            } catch {
            }
        } else {
            document.execCommand('fontSize', false, '3');
            const fonts = editorRef.current.querySelectorAll('font[size]');
            if (fonts.length) {
                const last = fonts[fonts.length - 1];
                last.removeAttribute('size');
                last.style.fontSize = size;
            }
            onChange(editorRef.current.innerHTML);
        }
        editorRef.current.focus();
    };
    const applyColor = (e, cmd) => {
        restoreSelection();
        document.execCommand(cmd, false, e.target.value);
        onChange(editorRef.current.innerHTML);
        editorRef.current.focus();
    };

    return (
        <div className="lep-rte-wrap">
            <div className="lep-rte-toolbar" onMouseDown={preventBlur}>
                <select className="lep-rte-select" defaultValue="Paragraph" onMouseDown={e => e.stopPropagation()}
                        onChange={setBlock}>
                    {HEADINGS.map(h => <option key={h}>{h}</option>)}
                </select>
                <div className="lep-rte-sep"/>
                <select className="lep-rte-select" defaultValue="Georgia" onMouseDown={e => e.stopPropagation()}
                        onChange={applyFontFamily}>
                    {FONT_FAMILIES.map(f => <option key={f}>{f}</option>)}
                </select>
                <select className="lep-rte-select" defaultValue="14px" onMouseDown={e => e.stopPropagation()}
                        onChange={applyFontSize}>
                    {FONT_SIZES.map(s => <option key={s}>{s}</option>)}
                </select>
                <div className="lep-rte-sep"/>
                <button className="lep-rte-btn" title="Жирный" onMouseDown={preventBlur} onClick={() => exec('bold')}>
                    <b>B</b></button>
                <button className="lep-rte-btn" title="Курсив" onMouseDown={preventBlur} onClick={() => exec('italic')}>
                    <i>I</i></button>
                <button className="lep-rte-btn" title="Подчёркнутый" onMouseDown={preventBlur}
                        onClick={() => exec('underline')}><u>U</u></button>
                <button className="lep-rte-btn" title="Зачёркнутый" onMouseDown={preventBlur}
                        onClick={() => exec('strikeThrough')}><s>S</s></button>
                <div className="lep-rte-sep"/>
                <button className="lep-rte-btn" onMouseDown={preventBlur} onClick={() => exec('justifyLeft')}>⬅</button>
                <button className="lep-rte-btn" onMouseDown={preventBlur} onClick={() => exec('justifyCenter')}>☰
                </button>
                <button className="lep-rte-btn" onMouseDown={preventBlur} onClick={() => exec('justifyRight')}>➡
                </button>
                <div className="lep-rte-sep"/>
                <button className="lep-rte-btn" onMouseDown={preventBlur} onClick={() => exec('insertUnorderedList')}>•
                    –
                </button>
                <button className="lep-rte-btn" onMouseDown={preventBlur} onClick={() => exec('insertOrderedList')}>1.
                </button>
                <div className="lep-rte-sep"/>
                <div className="lep-rte-color" title="Цвет текста">
                    <div className="lep-rte-dot" style={{background: '#1a1a2e'}}/>
                    <input type="color" className="lep-rte-color-input" defaultValue="#1a1a2e"
                           onMouseDown={e => e.stopPropagation()} onChange={e => applyColor(e, 'foreColor')}/>
                </div>
                <div className="lep-rte-color" title="Фон текста">
                    <div className="lep-rte-dot" style={{background: '#a29bfe'}}/>
                    <input type="color" className="lep-rte-color-input" defaultValue="#a29bfe"
                           onMouseDown={e => e.stopPropagation()} onChange={e => applyColor(e, 'hiliteColor')}/>
                </div>
                <div className="lep-rte-sep"/>
                <button className="lep-rte-btn" title="Очистить" onMouseDown={preventBlur}
                        onClick={() => exec('removeFormat')}>✕
                </button>
            </div>
            <div className="lep-rte-editor" ref={editorRef} contentEditable suppressContentEditableWarning
                 data-placeholder="Введите текст урока..."
                 onFocus={saveSelection} onKeyUp={saveSelection} onMouseUp={saveSelection} onSelect={saveSelection}
                 onInput={() => {
                     onChange(editorRef.current.innerHTML);
                     saveSelection();
                 }}/>
        </div>
    );
};

/* ─────────────────────────────────────────────
   EXERCISE ROW
───────────────────────────────────────────── */
const ExerciseRow = ({ex, index, onUpdate, onDelete, onMoveUp, onMoveDown, isFirst, isLast}) => {
    const [open, setOpen] = useState(true);
    const upd = (patch) => onUpdate({...ex, ...patch});

    const TYPE_LABELS = {
        text_input: '✍️ Свободный ответ',
        multiple_choice: '☑️ Выбор ответа',
        drag_and_drop: '🔀 Drag & Drop',
        fill_in_blank: '✏️ Заполни пропуск',
    };

    return (
        <div className="lep-ex-row">
            <div className="lep-ex-row-head">
                <div className="lep-ex-row-left">
                    <span className="lep-ex-row-num">{index + 1}</span>
                    <select className="lep-ex-type-sel" value={ex.exercise_type}
                            onChange={e => upd({exercise_type: e.target.value})}>
                        {EX_TYPES.map(t => <option key={t} value={t}>{TYPE_LABELS[t] || t}</option>)}
                    </select>
                    <select className="lep-ex-diff-sel" value={ex.difficulty_level}
                            onChange={e => upd({difficulty_level: e.target.value})}>
                        {DIFF_LEVELS.map(d => <option key={d}>{d}</option>)}
                    </select>
                    <div className="lep-ex-pts-wrap">
                        <input className="lep-ex-pts-input" type="number" value={ex.points}
                               onChange={e => upd({points: Number(e.target.value)})} title="Баллы"/>
                        <span className="lep-ex-pts-label">pts</span>
                    </div>
                </div>
                <div className="lep-ex-row-right">
                    <button className="lep-ex-ctrl" onClick={onMoveUp} disabled={isFirst} title="Вверх">↑</button>
                    <button className="lep-ex-ctrl" onClick={onMoveDown} disabled={isLast} title="Вниз">↓</button>
                    <button className="lep-ex-ctrl lep-ex-ctrl--toggle" onClick={() => setOpen(o => !o)}
                            title={open ? 'Свернуть' : 'Развернуть'}>
                        {open ? '▲' : '▼'}
                    </button>
                    <button className="lep-ex-ctrl lep-ex-ctrl--del" onClick={onDelete} title="Удалить">✕</button>
                </div>
            </div>

            {open && (
                <div className="lep-ex-row-body">
                    <div className="lep-ex-field-row">
                        <div className="lep-ex-field">
                            <label>Заголовок задания</label>
                            <input className="lep-ex-input" value={ex.title}
                                   onChange={e => upd({title: e.target.value})} placeholder="Заголовок..."/>
                        </div>
                    </div>

                    {ex.exercise_type !== 'fill_in_blank' && (
                        <div className="lep-ex-field">
                            <label>Вопрос / Описание</label>
                            <textarea className="lep-ex-textarea" value={ex.description}
                                      onChange={e => upd({description: e.target.value})}
                                      placeholder="Опишите задание..."/>
                        </div>
                    )}

                    {ex.exercise_type === 'multiple_choice' && (<>
                        <div className="lep-ex-field">
                            <label>Варианты ответов <span className="lep-ex-hint-label">(через запятую)</span></label>
                            <input className="lep-ex-input" value={ex.options}
                                   onChange={e => upd({options: e.target.value})}
                                   placeholder="Вариант A, Вариант B, Вариант C"/>
                        </div>
                        <div className="lep-ex-field">
                            <label>Правильный ответ(ы) <span
                                className="lep-ex-hint-label">(через запятую)</span></label>
                            <input className="lep-ex-input" value={ex.correct_answers}
                                   onChange={e => upd({correct_answers: e.target.value})} placeholder="Вариант A"/>
                        </div>
                        <label className="lep-ex-check">
                            <input type="checkbox" checked={!!ex.is_multiple_select}
                                   onChange={e => upd({is_multiple_select: e.target.checked})}/>
                            Несколько правильных ответов
                        </label>
                    </>)}

                    {ex.exercise_type === 'drag_and_drop' && (<>
                        <div className="lep-ex-field">
                            <label>Элементы <span className="lep-ex-hint-label">(через запятую)</span></label>
                            <input className="lep-ex-input" value={ex.drag_items}
                                   onChange={e => upd({drag_items: e.target.value})}
                                   placeholder="Элемент 1, Элемент 2, Элемент 3"/>
                        </div>
                        <div className="lep-ex-field">
                            <label>Правильный порядок <span className="lep-ex-hint-label">(через запятую)</span></label>
                            <input className="lep-ex-input" value={ex.correct_order}
                                   onChange={e => upd({correct_order: e.target.value})}
                                   placeholder="Элемент 1, Элемент 3, Элемент 2"/>
                        </div>
                    </>)}

                    {ex.exercise_type === 'fill_in_blank' && (<>
                        <div className="lep-ex-field">
                            <label>Текст с пропусками <span
                                className="lep-ex-hint-label">(используйте ___ для пропуска)</span></label>
                            <textarea className="lep-ex-textarea" value={ex.description}
                                      onChange={e => upd({description: e.target.value})}
                                      placeholder="Столица России — ___, а Франции — ___."/>
                        </div>
                        <div className="lep-ex-field">
                            <label>Правильные ответы <span
                                className="lep-ex-hint-label">(через запятую, по порядку)</span></label>
                            <input className="lep-ex-input" value={ex.correct_answers}
                                   onChange={e => upd({correct_answers: e.target.value})} placeholder="Москва, Париж"/>
                        </div>
                    </>)}

                    {ex.exercise_type === 'text_input' && (
                        <div className="lep-ex-field">
                            <label>Ожидаемый ответ <span className="lep-ex-hint-label">(для AI-проверки)</span></label>
                            <input className="lep-ex-input" value={ex.expected_answer}
                                   onChange={e => upd({expected_answer: e.target.value})}
                                   placeholder="Ключевые слова или суть правильного ответа"/>
                        </div>
                    )}

                    <div className="lep-ex-field">
                        <label>Подсказка <span className="lep-ex-hint-label">(необязательно)</span></label>
                        <input className="lep-ex-input" value={ex.hint} onChange={e => upd({hint: e.target.value})}
                               placeholder="Подсказка для студента..."/>
                    </div>
                </div>
            )}
        </div>
    );
};

/* ─────────────────────────────────────────────
   SECTION BLOCK  — collapse + move + drag handle
───────────────────────────────────────────── */
const SectionBlock = ({section, onUpdate, onDelete, index, total, onMoveUp, onMoveDown, dragHandleProps}) => {
    const [collapsed, setCollapsed] = useState(false);
    const fileRef = useRef(null);
    const imgRef = useRef(null);
    const update = (patch) => onUpdate({...section, ...patch});
    const meta = SECTION_TYPES.find(t => t.type === section.type);
    const ytId = section.type === 'video' ? getYTId(section.videoUrl || '') : null;

    const addExercise = () => update({exercises: [...(section.exercises || []), makeExercise()]});
    const updateExercise = (lid, data) => update({exercises: (section.exercises || []).map(e => (e._localId || e.id) === lid ? data : e)});
    const deleteExercise = (lid) => update({exercises: (section.exercises || []).filter(e => (e._localId || e.id) !== lid)});
    const moveExercise = (lid, dir) => {
        const list = [...(section.exercises || [])];
        const idx = list.findIndex(e => (e._localId || e.id) === lid);
        if (idx < 0) return;
        const t = idx + dir;
        if (t < 0 || t >= list.length) return;
        [list[idx], list[t]] = [list[t], list[idx]];
        update({exercises: list});
    };

    return (
        <div className={`lep-section${collapsed ? ' lep-section--collapsed' : ''}`} {...dragHandleProps}>
            {/* HEAD */}
            <div className="lep-section-head">
                <div className="lep-section-head-left">
                    <span className="lep-drag-handle" title="Перетащить для сортировки">⠿</span>
                    <div className="lep-section-num">{index + 1}</div>
                    <span className="lep-section-icon">{meta?.icon}</span>
                    <span className="lep-section-badge">{meta?.label}</span>
                    <input
                        className="lep-section-label-input"
                        placeholder="Заголовок блока..."
                        value={section.label}
                        onChange={e => update({label: e.target.value})}
                        onClick={e => e.stopPropagation()}
                    />
                </div>
                <div className="lep-section-head-right">
                    <button className="lep-section-ctrl" onClick={onMoveUp} disabled={index === 0}
                            title="Переместить вверх">↑
                    </button>
                    <button className="lep-section-ctrl" onClick={onMoveDown} disabled={index === total - 1}
                            title="Переместить вниз">↓
                    </button>
                    <button className="lep-section-ctrl lep-section-ctrl--collapse"
                            onClick={() => setCollapsed(c => !c)} title={collapsed ? 'Развернуть' : 'Свернуть'}>
                        {collapsed ? '▼' : '▲'}
                    </button>
                    <button className="lep-section-del" onClick={onDelete} title="Удалить блок">✕</button>
                </div>
            </div>

            {/* BODY */}
            {!collapsed && (
                <div className="lep-section-body">

                    {section.type === 'text' && (
                        <RichTextEditor value={section.html} onChange={html => update({html})}/>
                    )}

                    {section.type === 'code' && (<>
                        <div className="lep-code-bar">
                            <label>Язык:</label>
                            <select value={section.lang} onChange={e => update({lang: e.target.value})}>
                                {CODE_LANGS.map(l => <option key={l}>{l}</option>)}
                            </select>
                        </div>
                        <textarea className="lep-code-area" placeholder="// Вставьте код сюда..." value={section.code}
                                  onChange={e => update({code: e.target.value})}/>
                    </>)}

                    {section.type === 'video' && (<>
                        <input className="lep-input" placeholder="YouTube ссылка (https://youtu.be/...)"
                               value={section.videoUrl} onChange={e => update({videoUrl: e.target.value})}/>
                        <div className="lep-video-preview">
                            {ytId
                                ?
                                <iframe src={`https://www.youtube.com/embed/${ytId}`} allowFullScreen title="preview"/>
                                : <div className="lep-video-placeholder"><span>🎬</span><p>Введите YouTube ссылку для
                                    предпросмотра</p></div>
                            }
                        </div>
                    </>)}

                    {section.type === 'image' && (<>
                        <div className="lep-upload-zone" onClick={() => imgRef.current.click()}>
                            <span>🖼️</span>
                            <p>Нажмите для загрузки изображения</p>
                            <p className="lep-upload-hint">PNG, JPG, GIF, WebP</p>
                        </div>
                        <input ref={imgRef} type="file" accept="image/*" style={{display: 'none'}}
                               onChange={e => {
                                   const f = e.target.files[0];
                                   if (f) update({imgUrl: URL.createObjectURL(f), imgName: f.name, imgUrlDirect: ''});
                               }}/>
                        {section.imgUrl &&
                            <div className="lep-img-preview"><img src={section.imgUrl} alt={section.imgName || ''}/>
                            </div>}
                        <input className="lep-input lep-input-sm" placeholder="Или вставьте URL изображения"
                               value={section.imgUrlDirect || ''}
                               onChange={e => update({imgUrlDirect: e.target.value, imgUrl: e.target.value})}/>
                    </>)}

                    {section.type === 'file' && (<>
                        <div className="lep-upload-zone" onClick={() => fileRef.current.click()}>
                            <span>📁</span><p>Нажмите для загрузки файла</p>
                        </div>
                        <input ref={fileRef} type="file" style={{display: 'none'}}
                               onChange={e => {
                                   const f = e.target.files[0];
                                   if (f) update({fileName: f.name, fileSize: (f.size / 1024).toFixed(1) + ' KB'});
                               }}/>
                        {section.fileName && (
                            <div className="lep-file-info">
                                <span>📦</span>
                                <div>
                                    <div className="lep-file-name">{section.fileName}</div>
                                    <div className="lep-file-size">{section.fileSize}</div>
                                </div>
                            </div>
                        )}
                    </>)}

                    {/* ── PROJECT (Loyiha) ── */}
                    {section.type === 'project' && (
                        <div className="lep-project-editor">
                            <div className="lep-ex-field">
                                <label>Описание проекта</label>
                                <textarea className="lep-ex-textarea" value={section.description || ''}
                                          onChange={e => update({description: e.target.value})}
                                          placeholder="Опишите суть проекта..."/>
                            </div>
                            <div className="lep-ex-field">
                                <label>Требования</label>
                                <textarea className="lep-ex-textarea" value={section.requirements || ''}
                                          onChange={e => update({requirements: e.target.value})}
                                          placeholder="Перечислите требования к проекту..."/>
                            </div>
                            <div className="lep-ex-field-row">
                                <div className="lep-ex-field">
                                    <label>Стек технологий <span
                                        className="lep-ex-hint-label">(через запятую)</span></label>
                                    <input className="lep-ex-input" value={section.techStack || ''}
                                           onChange={e => update({techStack: e.target.value})}
                                           placeholder="React, Node.js, PostgreSQL"/>
                                </div>
                                <div className="lep-ex-field lep-ex-field--sm">
                                    <label>Дедлайн (дней)</label>
                                    <input className="lep-ex-input" type="number" value={section.deadline || ''}
                                           onChange={e => update({deadline: e.target.value})} placeholder="7"/>
                                </div>
                            </div>
                            {section.techStack && (
                                <div className="lep-project-tags-preview">
                                    {section.techStack.split(',').filter(Boolean).map((t, i) => (
                                        <span key={i} className="lep-project-tag">{t.trim()}</span>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* ── EXERCISE ── */}
                    {section.type === 'exercise' && (
                        <div className="lep-exercise-editor">
                            <div className="lep-exercise-editor-bar">
                                <span className="lep-exercise-count">
                                    🎯 {(section.exercises || []).length} заданий
                                    {(section.exercises || []).length > 0 && (
                                        <> ·
                                            🏆 {(section.exercises || []).reduce((s, e) => s + (Number(e.points) || 0), 0)} pts</>
                                    )}
                                </span>
                                <button className="lep-exercise-add-btn" onClick={addExercise}>+ Добавить задание
                                </button>
                            </div>
                            {(section.exercises || []).length === 0 ? (
                                <div className="lep-exercise-empty">
                                    <span>📭</span>
                                    <p>Нет заданий. Нажмите «Добавить задание»</p>
                                </div>
                            ) : (
                                <div className="lep-exercise-list">
                                    {(section.exercises || []).map((ex, i) => {
                                        const lid = ex._localId || ex.id;
                                        return (
                                            <ExerciseRow key={lid} ex={ex} index={i}
                                                         isFirst={i === 0}
                                                         isLast={i === (section.exercises || []).length - 1}
                                                         onUpdate={d => updateExercise(lid, d)}
                                                         onDelete={() => deleteExercise(lid)}
                                                         onMoveUp={() => moveExercise(lid, -1)}
                                                         onMoveDown={() => moveExercise(lid, 1)}/>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}

                    {/* ── MASHQ ── */}
                    {section.type === 'mashq' && (
                        <div className="lep-project-editor">
                            <div className="lep-ex-field">
                                <label>Тип задания</label>
                                <select className="lep-ex-input" value={section.mashqType || 'textarea'}
                                        onChange={e => update({mashqType: e.target.value})}>
                                    <option value="textarea">Свободный ответ</option>
                                    <option value="word_sort">Сортировка слов</option>
                                </select>
                            </div>
                            <div className="lep-ex-field">
                                <label>Вопрос</label>
                                <textarea className="lep-ex-textarea" value={section.question || ''}
                                          onChange={e => update({question: e.target.value})}
                                          placeholder="Введите вопрос..."/>
                            </div>
                            <div className="lep-ex-field">
                                <label>Правильный ответ</label>
                                <input className="lep-ex-input" value={section.answer || ''}
                                       onChange={e => update({answer: e.target.value})} placeholder="Ответ..."/>
                            </div>
                            {section.mashqType === 'word_sort' && (
                                <div className="lep-ex-field">
                                    <label>Слова для сортировки <span
                                        className="lep-ex-hint-label">(через запятую)</span></label>
                                    <input className="lep-ex-input"
                                           value={Array.isArray(section.words) ? section.words.join(', ') : (section.words || '')}
                                           onChange={e => update({words: e.target.value.split(',').map(w => w.trim()).filter(Boolean)})}
                                           placeholder="слово1, слово2, слово3"/>
                                </div>
                            )}
                        </div>
                    )}

                </div>
            )}
        </div>
    );
};

/* ─────────────────────────────────────────────
   DRAG-AND-DROP SORTABLE SECTIONS LIST
───────────────────────────────────────────── */
const SectionsList = ({sections, onReorder, onUpdate, onDelete, onMoveUp, onMoveDown}) => {
    const dragIdx = useRef(null);
    const [dragOver, setDragOver] = useState(null);

    const handleDragStart = (i) => {
        dragIdx.current = i;
    };
    const handleDragOver = (e, i) => {
        e.preventDefault();
        setDragOver(i);
    };
    const handleDrop = (e, i) => {
        e.preventDefault();
        if (dragIdx.current === null || dragIdx.current === i) {
            setDragOver(null);
            return;
        }
        const list = [...sections];
        const [moved] = list.splice(dragIdx.current, 1);
        list.splice(i, 0, moved);
        onReorder(list);
        dragIdx.current = null;
        setDragOver(null);
    };
    const handleDragEnd = () => {
        dragIdx.current = null;
        setDragOver(null);
    };

    return (
        <div className="lep-sections-list">
            {sections.map((s, i) => (
                <div key={s.id}
                     className={`lep-section-wrapper${dragOver === i ? ' lep-section-wrapper--over' : ''}`}
                     onDragOver={e => handleDragOver(e, i)}
                     onDrop={e => handleDrop(e, i)}>
                    <SectionBlock
                        section={s} index={i} total={sections.length}
                        onUpdate={data => onUpdate(s.id, data)}
                        onDelete={() => onDelete(s.id)}
                        onMoveUp={() => onMoveUp(i)}
                        onMoveDown={() => onMoveDown(i)}
                        dragHandleProps={{
                            draggable: true,
                            onDragStart: () => handleDragStart(i),
                            onDragEnd: handleDragEnd,
                        }}
                    />
                </div>
            ))}
        </div>
    );
};

/* ─────────────────────────────────────────────
   MAIN EXPORT: LESSON EDITOR PAGE
───────────────────────────────────────────── */
const LessonEditorPage = ({course, lesson, chapters, onSave, onClose}) => {
    const [form, setForm] = useState({
        title: lesson?.title || '',
        chapter: lesson?.chapter || '',
        image: lesson?.image || '',
        sections: lesson?.sections
            ? [...lesson.sections]
                .sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
                .map(s => ({...s}))
            : [],
    });
    const [saving, setSaving] = useState(false);

    const setField = (key, val) => setForm(f => ({...f, [key]: val}));
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
        try {
            const dataToSave = {
                ...form,
                sections: form.sections.map((s, i) => ({...s, order: i}))
            };
            await onSave(dataToSave);
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="lep-page">
            {/* Header */}
            <div className="lep-header">
                <div className="lep-header-left">
                    <button className="lep-back-btn" onClick={onClose} title="Назад">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                            <path d="M11 4L6 9L11 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"
                                  strokeLinejoin="round"/>
                        </svg>
                    </button>
                    <div className="lep-header-meta">
                        <span className="lep-header-course">{course?.title}</span>
                        <h2 className="lep-header-title">{lesson ? 'Редактировать урок' : 'Новый урок'}</h2>
                    </div>
                </div>
                <div className="lep-header-right">
                    <button className="lep-cancel-btn" onClick={onClose}>Отмена</button>
                    <button className="lep-save-btn" onClick={handleSave} disabled={saving || !form.title.trim()}>
                        {saving
                            ? <><span className="lep-spinner"/>Сохранение...</>
                            : lesson ? <><span>💾</span> Сохранить</> : <><span>✅</span> Добавить урок</>
                        }
                    </button>
                </div>
            </div>

            {/* Body */}
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
                            <div className="lep-stat-row"><span>📦 Блоков</span><strong>{form.sections.length}</strong>
                            </div>
                            {[
                                {type: 'text', icon: '📝', label: 'Текст'},
                                {type: 'video', icon: '🎬', label: 'Видео'},
                                {type: 'code', icon: '💻', label: 'Код'},
                                {type: 'exercise', icon: '🎯', label: 'Упражнения'},
                                {type: 'project', icon: '🚀', label: 'Проект'},
                                {type: 'mashq', icon: '✏️', label: 'Mashq'},
                            ].map(({type, icon, label}) => {
                                const cnt = form.sections.filter(s => s.type === type).length;
                                return cnt > 0 ? <div key={type} className="lep-stat-row">
                                    <span>{icon} {label}</span><strong>{cnt}</strong></div> : null;
                            })}
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
                                    <button key={t.type} className="lep-empty-type-btn"
                                            onClick={() => addSection(t.type)}>
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
                        />
                    )}
                </main>
            </div>
        </div>
    );
};

export default LessonEditorPage;