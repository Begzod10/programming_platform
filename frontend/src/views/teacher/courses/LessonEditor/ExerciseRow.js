import React, { useState } from 'react';
import { EX_TYPES, DIFF_LEVELS, DIFF_POINTS } from './lessonEditorConstants';

/* ─────────────────────────────────────────────
   EXERCISE ROW
───────────────────────────────────────────── */
export const ExerciseRow = ({ ex, index, onUpdate, onDelete, onMoveUp, onMoveDown, isFirst, isLast }) => {
    const [open, setOpen] = useState(true);
    const upd = (patch) => onUpdate({ ...ex, ...patch });

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
                    <select className="lep-ex-type-sel" value={ex.exercise_type} onChange={e => upd({ exercise_type: e.target.value })}>
                        {EX_TYPES.map(t => <option key={t} value={t}>{TYPE_LABELS[t] || t}</option>)}
                    </select>
                    <select className="lep-ex-diff-sel" value={ex.difficulty_level}
                            onChange={e => { const d = e.target.value; upd({ difficulty_level: d, points: DIFF_POINTS[d] }); }}>
                        {DIFF_LEVELS.map(d => <option key={d}>{d}</option>)}
                    </select>
                    <div className="lep-ex-pts-wrap">
                        <button type="button" className="lep-ex-pts-btn" onClick={() => upd({ points: Math.max(0, ex.points - 1) })}>–</button>
                        <input className="lep-ex-pts-input" type="number" value={ex.points}
                               onChange={e => upd({ points: Number(e.target.value) })} title="Баллы"/>
                        <button type="button" className="lep-ex-pts-btn" onClick={() => upd({ points: ex.points + 1 })}>+</button>
                        <span className="lep-ex-pts-label">pts</span>
                    </div>
                </div>
                <div className="lep-ex-row-right">
                    <button className="lep-ex-ctrl" onClick={onMoveUp} disabled={isFirst} title="Вверх">↑</button>
                    <button className="lep-ex-ctrl" onClick={onMoveDown} disabled={isLast} title="Вниз">↓</button>
                    <button className="lep-ex-ctrl lep-ex-ctrl--toggle" onClick={() => setOpen(o => !o)} title={open ? 'Свернуть' : 'Развернуть'}>
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
                                   onChange={e => upd({ title: e.target.value })} placeholder="Заголовок..."/>
                        </div>
                    </div>

                    {ex.exercise_type !== 'fill_in_blank' && (
                        <div className="lep-ex-field">
                            <label>Вопрос / Описание</label>
                            <textarea className="lep-ex-textarea" value={ex.description}
                                      onChange={e => upd({ description: e.target.value })} placeholder="Опишите задание..."/>
                        </div>
                    )}

                    {ex.exercise_type === 'multiple_choice' && (<>
                        <div className="lep-ex-field">
                            <label>Варианты ответов <span className="lep-ex-hint-label">(через запятую)</span></label>
                            <input className="lep-ex-input" value={ex.options}
                                   onChange={e => upd({ options: e.target.value })} placeholder="Вариант A, Вариант B, Вариант C"/>
                        </div>
                        <div className="lep-ex-field">
                            <label>Правильный ответ(ы) <span className="lep-ex-hint-label">(A yoki B yoki to'liq matn)</span></label>
                            <input className="lep-ex-input" value={ex.correct_answers}
                                   onChange={e => upd({ correct_answers: e.target.value })} placeholder="A"/>
                        </div>
                        <label className="lep-ex-check">
                            <input type="checkbox" checked={!!ex.is_multiple_select}
                                   onChange={e => upd({ is_multiple_select: e.target.checked })}/>
                            Несколько правильных ответов
                        </label>
                    </>)}

                    {ex.exercise_type === 'drag_and_drop' && (<>
                        <div className="lep-ex-field">
                            <label>Элементы <span className="lep-ex-hint-label">(через запятую)</span></label>
                            <input className="lep-ex-input" value={ex.drag_items}
                                   onChange={e => upd({ drag_items: e.target.value })} placeholder="Элемент 1, Элемент 2, Элемент 3"/>
                        </div>
                        <div className="lep-ex-field">
                            <label>Правильный порядок <span className="lep-ex-hint-label">(через запятую)</span></label>
                            <input className="lep-ex-input" value={ex.correct_order}
                                   onChange={e => upd({ correct_order: e.target.value })} placeholder="Элемент 1, Элемент 3, Элемент 2"/>
                        </div>
                    </>)}

                    {ex.exercise_type === 'fill_in_blank' && (<>
                        <div className="lep-ex-field">
                            <label>Текст с пропусками <span className="lep-ex-hint-label">(используйте ___ для пропуска)</span></label>
                            <textarea className="lep-ex-textarea" value={ex.description}
                                      onChange={e => upd({ description: e.target.value })} placeholder="Столица России — ___, а Франции — ___."/>
                        </div>
                        <div className="lep-ex-field">
                            <label>Правильные ответы <span className="lep-ex-hint-label">(через запятую, по порядку)</span></label>
                            <input className="lep-ex-input" value={ex.correct_answers}
                                   onChange={e => upd({ correct_answers: e.target.value })} placeholder="Москва, Париж"/>
                        </div>
                    </>)}

                    {ex.exercise_type === 'text_input' && (
                        <div className="lep-ex-field">
                            <label>Ожидаемый ответ <span className="lep-ex-hint-label">(для AI-проверки)</span></label>
                            <input className="lep-ex-input" value={ex.expected_answer}
                                   onChange={e => upd({ expected_answer: e.target.value })}
                                   placeholder="Ключевые слова или суть правильного ответа"/>
                        </div>
                    )}

                    <div className="lep-ex-field">
                        <label>Подсказка <span className="lep-ex-hint-label">(необязательно)</span></label>
                        <input className="lep-ex-input" value={ex.hint} onChange={e => upd({ hint: e.target.value })}
                               placeholder="Подсказка для студента..."/>
                    </div>
                </div>
            )}
        </div>
    );
};
