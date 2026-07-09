import React, { useState, useRef } from 'react';
import { Trophy } from 'lucide-react';
import { SECTION_TYPES, getYTId } from '../../../../constants/courseUtils';
import ExerciseFileUpload from '../ExercsieFileUpload/ExercsieFileUpload';
import { RichTextEditor } from './RichTextEditor';
import { ExerciseRow } from './ExerciseRow';
import { makeExercise, CODE_LANGS } from './lessonEditorConstants';

/* ─────────────────────────────────────────────
   SECTION BLOCK
───────────────────────────────────────────── */
export const SectionBlock = ({ section, onUpdate, onDelete, index, total, onMoveUp, onMoveDown, dragHandleProps, lessonId, apiBaseUrl }) => {
    const [collapsed, setCollapsed] = useState(false);
    const [projectTab, setProjectTab] = useState('info'); // 'info' | 'files'
    const fileRef = useRef(null);
    const imgRef = useRef(null);
    const update = (patch) => onUpdate({ ...section, ...patch });
    const meta = SECTION_TYPES.find(t => t.type === section.type);
    const ytId = section.type === 'video' ? getYTId(section.videoUrl || '') : null;

    const addExercise = () => update({ exercises: [...(section.exercises || []), makeExercise()] });
    const updateExercise = (lid, data) => update({ exercises: (section.exercises || []).map(e => (e._localId || e.id) === lid ? data : e) });
    const deleteExercise = (lid) => update({ exercises: (section.exercises || []).filter(e => (e._localId || e.id) !== lid) });
    const moveExercise = (lid, dir) => {
        const list = [...(section.exercises || [])];
        const idx = list.findIndex(e => (e._localId || e.id) === lid);
        if (idx < 0) return;
        const t = idx + dir;
        if (t < 0 || t >= list.length) return;
        [list[idx], list[t]] = [list[t], list[idx]];
        update({ exercises: list });
    };

    const taskCount = (section.exercises || []).length;
    const projectFileCount = (section.projectFiles || []).length;

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
                        onChange={e => update({ label: e.target.value })}
                        onClick={e => e.stopPropagation()}
                    />
                </div>
                <div className="lep-section-head-right">
                    <button className="lep-section-ctrl" onClick={onMoveUp} disabled={index === 0} title="Переместить вверх">↑</button>
                    <button className="lep-section-ctrl" onClick={onMoveDown} disabled={index === total - 1} title="Переместить вниз">↓</button>
                    <button className="lep-section-ctrl lep-section-ctrl--collapse" onClick={() => setCollapsed(c => !c)} title={collapsed ? 'Развернуть' : 'Свернуть'}>
                        {collapsed ? '▼' : '▲'}
                    </button>
                    <button className="lep-section-del" onClick={onDelete} title="Удалить блок">✕</button>
                </div>
            </div>

            {/* BODY */}
            {!collapsed && (
                <div className="lep-section-body">

                    {section.type === 'text' && (
                        <RichTextEditor value={section.html} onChange={html => update({ html })}/>
                    )}

                    {section.type === 'code' && (<>
                        <div className="lep-code-bar">
                            <label>Язык:</label>
                            <select value={section.lang} onChange={e => update({ lang: e.target.value })}>
                                {CODE_LANGS.map(l => <option key={l}>{l}</option>)}
                            </select>
                        </div>
                        <textarea className="lep-code-area" placeholder="// Вставьте код сюда..." value={section.code}
                                  onChange={e => update({ code: e.target.value })}/>
                    </>)}

                    {section.type === 'video' && (<>
                        <input className="lep-input" placeholder="YouTube ссылка (https://youtu.be/...)"
                               value={section.videoUrl} onChange={e => update({ videoUrl: e.target.value })}/>
                        <div className="lep-video-preview">
                            {ytId
                                ? <iframe src={`https://www.youtube.com/embed/${ytId}`} allowFullScreen title="preview"/>
                                : <div className="lep-video-placeholder"><span>🎬</span><p>Введите YouTube ссылку для предпросмотра</p></div>
                            }
                        </div>
                    </>)}

                    {section.type === 'image' && (<>
                        <div className="lep-upload-zone" onClick={() => imgRef.current.click()}>
                            <span>🖼️</span>
                            <p>Нажмите для загрузки изображения</p>
                            <p className="lep-upload-hint">PNG, JPG, GIF, WebP</p>
                        </div>
                        <input ref={imgRef} type="file" accept="image/*" style={{ display: 'none' }}
                               onChange={e => {
                                   const f = e.target.files[0];
                                   if (f) update({ imgUrl: URL.createObjectURL(f), imgName: f.name, imgUrlDirect: '' });
                               }}/>
                        {section.imgUrl && <div className="lep-img-preview"><img src={section.imgUrl} alt={section.imgName || ''}/></div>}
                        <input className="lep-input lep-input-sm" placeholder="Или вставьте URL изображения"
                               value={section.imgUrlDirect || ''}
                               onChange={e => update({ imgUrlDirect: e.target.value, imgUrl: e.target.value })}/>
                    </>)}

                    {section.type === 'file' && (<>
                        <div className="lep-upload-zone" onClick={() => fileRef.current.click()}>
                            <span>📁</span><p>Нажмите для загрузки файла</p>
                        </div>
                        <input ref={fileRef} type="file" style={{ display: 'none' }}
                               onChange={e => {
                                   const f = e.target.files[0];
                                   if (f) update({ fileName: f.name, fileSize: (f.size / 1024).toFixed(1) + ' KB' });
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

                    {/* ══════════════════════════════════════════
                        PROJECT (Loyiha) — sub-tabs: Info | Files
                    ══════════════════════════════════════════ */}
                    {section.type === 'project' && (
                        <div className="lep-project-editor">

                            {/* ── Sub-tab bar ── */}
                            <div className="lep-ex-subtab-bar">
                                <button
                                    className={`lep-ex-subtab-btn ${projectTab === 'info' ? 'active' : ''}`}
                                    onClick={() => setProjectTab('info')}
                                >
                                    🚀 Описание
                                </button>
                                <button
                                    className={`lep-ex-subtab-btn ${projectTab === 'files' ? 'active' : ''}`}
                                    onClick={() => setProjectTab('files')}
                                >
                                    🗂️ Файлы кода
                                    {projectFileCount > 0 && (
                                        <span className="lep-ex-subtab-badge lep-ex-subtab-badge--files">
                                            {projectFileCount}
                                        </span>
                                    )}
                                </button>
                            </div>

                            {/* ── INFO tab ── */}
                            {projectTab === 'info' && (<>
                                <div className="lep-ex-field">
                                    <label>Описание проекта</label>
                                    <textarea className="lep-ex-textarea" value={section.description || ''}
                                              onChange={e => update({ description: e.target.value })}
                                              placeholder="Опишите суть проекта..."/>
                                </div>
                                <div className="lep-ex-field">
                                    <label>Требования</label>
                                    <textarea className="lep-ex-textarea" value={section.requirements || ''}
                                              onChange={e => update({ requirements: e.target.value })}
                                              placeholder="Перечислите требования к проекту..."/>
                                </div>
                                <div className="lep-ex-field-row">
                                    <div className="lep-ex-field">
                                        <label>Стек технологий <span className="lep-ex-hint-label">(через запятую)</span></label>
                                        <input className="lep-ex-input" value={section.techStack || ''}
                                               onChange={e => update({ techStack: e.target.value })}
                                               placeholder="React, Node.js, PostgreSQL"/>
                                    </div>
                                    <div className="lep-ex-field lep-ex-field--sm">
                                        <label>Дедлайн (дней)</label>
                                        <input className="lep-ex-input" type="number" value={section.deadline || ''}
                                               onChange={e => update({ deadline: e.target.value })} placeholder="7"/>
                                    </div>
                                </div>
                                {section.techStack && (
                                    <div className="lep-project-tags-preview">
                                        {section.techStack.split(',').filter(Boolean).map((t, i) => (
                                            <span key={i} className="lep-project-tag">{t.trim()}</span>
                                        ))}
                                    </div>
                                )}
                            </>)}

                            {/* ── FILES tab ── */}
                            {projectTab === 'files' && (
                                <ExerciseFileUpload
                                    lessonId={lessonId}
                                    apiBaseUrl={apiBaseUrl}
                                    files={section.projectFiles || []}
                                    onChange={(newFiles) => update({ projectFiles: newFiles })}
                                />
                            )}

                        </div>
                    )}

                    {/* ── EXERCISE ── */}
                    {section.type === 'exercise' && (
                        <div className="lep-exercise-editor">
                            <div className="lep-exercise-editor-bar">
                                <span className="lep-exercise-count">
                                    🎯 {taskCount} заданий
                                    {taskCount > 0 && (
                                        <> · <Trophy size={12} aria-hidden="true" /> {(section.exercises || []).reduce((s, e) => s + (Number(e.points) || 0), 0)} pts</>
                                    )}
                                </span>
                                <button className="lep-exercise-add-btn" onClick={addExercise}>+ Добавить задание</button>
                            </div>
                            {taskCount === 0 ? (
                                <div className="lep-exercise-empty">
                                    <span>📭</span>
                                    <p>Нет заданий. Нажмите «Добавить задание»</p>
                                </div>
                            ) : (
                                <div className="lep-exercise-list">
                                    {(section.exercises || []).map((ex, i) => {
                                        const lid = ex._localId || ex.id;
                                        return (
                                            <ExerciseRow
                                                key={lid} ex={ex} index={i}
                                                isFirst={i === 0}
                                                isLast={i === taskCount - 1}
                                                onUpdate={d => updateExercise(lid, d)}
                                                onDelete={() => deleteExercise(lid)}
                                                onMoveUp={() => moveExercise(lid, -1)}
                                                onMoveDown={() => moveExercise(lid, 1)}
                                            />
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
                                        onChange={e => update({ mashqType: e.target.value })}>
                                    <option value="textarea">Свободный ответ</option>
                                    <option value="word_sort">Сортировка слов</option>
                                </select>
                            </div>
                            <div className="lep-ex-field">
                                <label>Вопрос</label>
                                <textarea className="lep-ex-textarea" value={section.question || ''}
                                          onChange={e => update({ question: e.target.value })}
                                          placeholder="Введите вопрос..."/>
                            </div>
                            <div className="lep-ex-field">
                                <label>Правильный ответ</label>
                                <input className="lep-ex-input" value={section.answer || ''}
                                       onChange={e => update({ answer: e.target.value })} placeholder="Ответ..."/>
                            </div>
                            {section.mashqType === 'word_sort' && (
                                <div className="lep-ex-field">
                                    <label>Слова для сортировки <span className="lep-ex-hint-label">(через запятую)</span></label>
                                    <input className="lep-ex-input"
                                           value={Array.isArray(section.words) ? section.words.join(', ') : (section.words || '')}
                                           onChange={e => update({ words: e.target.value.split(',').map(w => w.trim()).filter(Boolean) })}
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
