import React, { useState, useRef, useMemo } from 'react';
import { Star, Trophy } from 'lucide-react';
import { API_URL, useHttp, headers } from '../../../../api/search/base';

/* ─────────────────────────────────────────────────────────────
   Умный парсер → всегда возвращает чистый массив строк
───────────────────────────────────────────────────────────── */
export const parseListField = (val) => {
    if (!val) return [];
    if (Array.isArray(val)) return val.map(s => String(s).trim()).filter(Boolean);
    if (typeof val === "string") {
        const trimmed = val.trim();
        if (trimmed.startsWith("[")) {
            try {
                const parsed = JSON.parse(trimmed);
                if (Array.isArray(parsed)) return parsed.map(s => String(s).trim()).filter(Boolean);
            } catch {}
        }
        return trimmed.split(",").map(s => s.trim()).filter(Boolean);
    }
    return [];
};

/* ═══════════════════════════════════════════════════════════
   SINGLE EXERCISE CARD
═══════════════════════════════════════════════════════════ */
export const ExerciseCard = ({ex, courseId, lessonId, index, previousSubmission = null}) => {
    const {request} = useHttp();

    const exType = ex.exercise_type;

    // Number of blanks the CURRENT description actually renders. Must be
    // the single source of truth for both reconstructing saved answers and
    // building the submitted one — otherwise a stale extra entry (e.g. from
    // a since-fixed description that used to render 2 inputs) survives in
    // fillAnswers and gets silently joined into the answer even though only
    // 1 input is on screen.
    const fillBlankCount = useMemo(() => {
        if (exType !== 'fill_in_blank') return 0;
        const desc = ex.description || '';
        const matches = desc.match(/_{3,}/g);
        return matches ? matches.length : 1;
    }, [exType, ex.description]);

    // Reconstruct each exercise type's input state from the saved
    // student_answer string. Mirrors buildAnswer()'s encoding.
    const initialInputs = useMemo(() => {
        const blank = {textAnswer: '', selected: [], fillAnswers: [], dragDropped: [], matchedPairs: null};
        if (!previousSubmission?.student_answer) return blank;
        const ans = previousSubmission.student_answer;
        if (exType === 'multiple_choice') {
            return {...blank, selected: ans.split(',').filter(Boolean)};
        }
        if (exType === 'fill_in_blank') {
            const parts = ans.split(',');
            const trimmed = Array.from({length: fillBlankCount}, (_, i) => parts[i] || '');
            return {...blank, fillAnswers: trimmed};
        }
        if (exType === 'drag_and_drop') {
            try { return {...blank, dragDropped: JSON.parse(ans) || []}; }
            catch { return blank; }
        }
        if (exType === 'matching') {
            try {
                const parsed = JSON.parse(ans);
                return {...blank, matchedPairs: Array.isArray(parsed) ? parsed : null};
            } catch { return blank; }
        }
        return {...blank, textAnswer: ans};
    }, [previousSubmission, exType, fillBlankCount]);

    const initialResult = previousSubmission
        ? (previousSubmission.is_correct === true ? 'correct'
            : previousSubmission.is_correct === false ? 'wrong'
            : 'submitted')
        : null;

    const [textAnswer, setTextAnswer] = useState(initialInputs.textAnswer);
    const [selected, setSelected] = useState(initialInputs.selected);
    const [fillAnswers, setFillAnswers] = useState(initialInputs.fillAnswers);
    const cleanOptions = parseListField(ex.options);
    const cleanDragItems = parseListField(ex.drag_items);

    const [dragAvailable, setDragAvailable] = useState(() => {
        const dropped = new Set(initialInputs.dragDropped || []);
        const remaining = cleanDragItems.filter(it => !dropped.has(it));
        return [...remaining].sort(() => Math.random() - 0.5);
    });
    const [dragDropped, setDragDropped] = useState(initialInputs.dragDropped);

    // MATCHING — cleanDragItems doubles as the left column (terms, fixed
    // order) and cleanOptions as the right column (definitions), exactly
    // like drag_and_drop/multiple_choice reuse the same two generic
    // fields for their own shapes. matchedPairs[i] is the right column's
    // ORIGINAL (pre-shuffle) index paired with left item i, or null if
    // that term isn't matched yet — mirrors buildAnswer()'s encoding.
    // rightDisplayOrder is shuffled once per mount (same "shuffle into
    // state once via the initializer, not on every render" pattern as
    // dragAvailable above), not re-derived, so the right column's on-
    // screen order stays stable while the student is working.
    const [matchedPairs, setMatchedPairs] = useState(() => {
        const prev = initialInputs.matchedPairs;
        if (prev && prev.length === cleanDragItems.length) return prev;
        return cleanDragItems.map(() => null);
    });
    const [selectedLeftIndex, setSelectedLeftIndex] = useState(null);
    const [rightDisplayOrder, setRightDisplayOrder] = useState(() =>
        cleanOptions.map((_, i) => i).sort(() => Math.random() - 0.5)
    );

    const [result, setResult] = useState(initialResult);
    const [aiFeedback, setAiFeedback] = useState(previousSubmission?.ai_feedback || '');
    const [score, setScore] = useState(previousSubmission?.score ?? null);
    const [submitting, setSubmitting] = useState(false);
    const [showHint, setShowHint] = useState(false);
    const exerciseOpenedAtRef = useRef(Date.now());

    // True once the student has submitted at least once for this exercise —
    // either in this session or previously. Used to render the checkmark.
    // We deliberately DO NOT lock inputs: resubmitting is allowed.
    const hasPreviousSubmission = !!previousSubmission;

    const isDone = result === 'correct' || result === 'submitted';
    const isWrong = result === 'wrong';

    const buildAnswer = () => {
        if (exType === 'fill_in_blank') return fillAnswers.slice(0, fillBlankCount).join(',');
        if (exType === 'drag_and_drop') return JSON.stringify(dragDropped.map(s => s.trim()));
        if (exType === 'multiple_choice') return selected.join(',');
        if (exType === 'matching') {
            // Require every term matched before allowing submit — a
            // partial mapping has no useful "is this right so far?"
            // answer, unlike drag_and_drop where a partial order is at
            // least a well-formed (if incomplete) sequence.
            if (matchedPairs.some(v => v === null || v === undefined)) return '';
            return JSON.stringify(matchedPairs);
        }
        return textAnswer.trim();
    };

    const handleSubmit = async () => {
        const answer = buildAnswer();
        if (!answer) return;
        setSubmitting(true);
        setAiFeedback('');
        setScore(null);
        try {
            const timeSpentMs = Date.now() - exerciseOpenedAtRef.current;
            const res = await request(
                `${API_URL}v1/courses/${courseId}/lessons/${lessonId}/exercises/${ex.id}/submit`,
                'POST',
                JSON.stringify({
                    student_answer: answer,
                    time_spent_ms: timeSpentMs,
                    lang: localStorage.getItem('lang') || 'uz',
                }),
                headers()
            );
            if (res?.is_correct === true) setResult('correct');
            else if (res?.is_correct === false) setResult('wrong');
            else setResult('submitted');
            if (res?.ai_feedback) setAiFeedback(res.ai_feedback);
            if (res?.score != null) setScore(res.score);
        } catch {
            setResult('wrong');
        } finally {
            setSubmitting(false);
        }
    };

    const handleRetry = () => {
        setResult(null);
        setAiFeedback('');
        setScore(null);
        setSelected([]);
        setTextAnswer('');
        setFillAnswers([]);
        setDragDropped([]);
        setDragAvailable([...cleanDragItems].sort(() => Math.random() - 0.5));
        setMatchedPairs(cleanDragItems.map(() => null));
        setSelectedLeftIndex(null);
        setRightDisplayOrder(cleanOptions.map((_, i) => i).sort(() => Math.random() - 0.5));
    };

    // MATCHING interaction — tap a left term, then tap an available right
    // definition to pair them; tapping an already-matched left term again
    // clears that one pairing so the student can redo it (mirrors
    // drag_and_drop's tap-a-dropped-chip-to-remove-it pattern above).
    const usedRightIndices = new Set(matchedPairs.filter(v => v !== null && v !== undefined));

    const handleMatchLeftTap = (leftIdx) => {
        if (isDone) return;
        if (matchedPairs[leftIdx] !== null && matchedPairs[leftIdx] !== undefined) {
            const next = [...matchedPairs];
            next[leftIdx] = null;
            setMatchedPairs(next);
            setResult(null);
            return;
        }
        setSelectedLeftIndex(prev => prev === leftIdx ? null : leftIdx);
    };

    const handleMatchRightTap = (rightOriginalIdx) => {
        if (isDone) return;
        if (usedRightIndices.has(rightOriginalIdx)) return;
        if (selectedLeftIndex === null) return;
        const next = [...matchedPairs];
        next[selectedLeftIndex] = rightOriginalIdx;
        setMatchedPairs(next);
        setSelectedLeftIndex(null);
        setResult(null);
    };

    const DIFF_COLOR = {Easy: '#00b894', Medium: '#e17055', Hard: '#d63031'};
    const diffColor = DIFF_COLOR[ex.difficulty_level] || '#6c5ce7';

    const stateClass = result === 'correct' ? 'state-correct'
        : result === 'wrong' ? 'state-wrong'
            : result === 'submitted' ? 'state-submitted' : '';

    return (
        <div className={`slp-ex-card ${stateClass} ${hasPreviousSubmission ? 'has-previous' : ''}`}
             style={{animationDelay: `${index * 0.07}s`}}>
            <div className="slp-ex-card-head">
                <div className="slp-ex-card-meta">
                    <span className="slp-ex-num">#{index + 1}</span>
                    {ex.difficulty_level && (
                        <span className="slp-ex-diff-badge"
                              style={{color: diffColor, borderColor: diffColor + '55', background: diffColor + '15'}}>
                            {ex.difficulty_level}
                        </span>
                    )}
                    {ex.points > 0 && <span className="slp-ex-pts-badge"><Star size={12} aria-hidden="true" /> {ex.points} pts</span>}
                    {score > 0 && <span className="slp-ex-score-badge"><Trophy size={12} aria-hidden="true" /> +{score} pts</span>}
                    {hasPreviousSubmission && result === initialResult && (
                        // Hide once the student takes a fresh action this
                        // session — `result` diverges from `initialResult`
                        // either when they resubmit or after handleRetry().
                        // The card's own state-correct/state-wrong classes
                        // carry the current verdict so the badge becomes
                        // redundant once the student is back in motion.
                        <span
                            className={`slp-ex-done-badge ${
                                previousSubmission.is_correct === true ? 'ok'
                                    : previousSubmission.is_correct === false ? 'bad'
                                    : 'pending'
                            }`}
                            title="Avval javob bergan edingiz. Qayta urinish mumkin."
                        >
                            {previousSubmission.is_correct === true ? '✓ Bajarilgan'
                                : previousSubmission.is_correct === false ? "✕ Javob noto’g‘ri"
                                : '✓ Javob yuborilgan'}
                        </span>
                    )}
                    <span className="slp-ex-type-label">
                        {{
                            fill_in_blank: '✏️ Заполни пропуск',
                            multiple_choice: '🔘 Выбор ответа',
                            drag_and_drop: '↕️ Расставь порядок',
                            text_input: '📝 Свободный ответ',
                            matching: '🔗 Найди пару',
                        }[exType] || '❓ Задание'}
                    </span>
                </div>
                {ex.title && <div className="slp-ex-card-title">{ex.title}</div>}
            </div>

            <div className="slp-ex-card-body">
                {exType === 'fill_in_blank' && (() => {
                    const desc = ex.description || '';
                    // Content shape #1: description contains ___ placeholders —
                    // render inline inputs at each placeholder. Content shape
                    // #2: description is a plain question with no ___ — fall
                    // back to a single input beneath the question so the
                    // student has somewhere to type. Without this fallback
                    // the exercise renders with no input and the submit
                    // button is permanently disabled.
                    // Regex, not a literal '___' split — a longer blank like
                    // "______" must still count as ONE input, not two.
                    if (/_{3,}/.test(desc)) {
                        return (
                            <div className="slp-ex-fill-wrap">
                                <div className="slp-ex-fill-text">
                                    {desc.split(/_{3,}/).map((part, i, arr) => (
                                        <span key={i}>
                                            {part}
                                            {i < arr.length - 1 && (
                                                <input
                                                    className={`slp-ex-fill-input ${isDone ? (result === 'correct' ? 'correct' : 'wrong') : ''}`}
                                                    placeholder={`${i + 1}`}
                                                    disabled={isDone}
                                                    value={fillAnswers[i] || ''}
                                                    onChange={e => {
                                                        const copy = [...fillAnswers];
                                                        copy[i] = e.target.value;
                                                        setFillAnswers(copy);
                                                        setResult(null);
                                                    }}
                                                />
                                            )}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        );
                    }
                    return (
                        <div className="slp-ex-fill-wrap">
                            {desc && <div className="slp-ex-question">{desc}</div>}
                            <input
                                className={`slp-ex-fill-input slp-ex-fill-input-single ${isDone ? (result === 'correct' ? 'correct' : 'wrong') : ''}`}
                                placeholder="Ваш ответ..."
                                disabled={isDone}
                                value={fillAnswers[0] || ''}
                                onChange={e => {
                                    setFillAnswers([e.target.value]);
                                    setResult(null);
                                }}
                            />
                        </div>
                    );
                })()}

                {exType === 'multiple_choice' && (
                    <>
                        {ex.description && <div className="slp-ex-question">{ex.description}</div>}
                        <div className="slp-ex-options">
                            {cleanOptions.map((opt, i) => {
                                const letter = String.fromCharCode(65 + i);
                                const isSelected = selected.includes(letter);
                                return (
                                    <button
                                        key={i}
                                        className={`slp-ex-option-btn ${isSelected ? 'selected' : ''}`}
                                        disabled={isDone}
                                        onClick={() => {
                                            if (ex.is_multiple_select) {
                                                setSelected(s => isSelected ? s.filter(x => x !== letter) : [...s, letter]);
                                            } else {
                                                setSelected([letter]);
                                            }
                                            setResult(null);
                                        }}
                                    >
                                        <span className="slp-ex-opt-letter">{letter}</span>
                                        <span className="slp-ex-opt-text">{opt}</span>
                                        {isSelected && <span className="slp-ex-opt-check">✓</span>}
                                    </button>
                                );
                            })}
                            {ex.is_multiple_select && (
                                <div className="slp-ex-multi-hint">⚡ Можно выбрать несколько ответов</div>
                            )}
                        </div>
                    </>
                )}

                {exType === 'drag_and_drop' && (
                    <>
                        {ex.description && <div className="slp-ex-question">{ex.description}</div>}
                        <div className="slp-ex-drag-wrap">
                            <div className="slp-ex-dropzone-label">Правильный порядок:</div>
                            <div
                                className="slp-ex-dropzone"
                                onDragOver={e => e.preventDefault()}
                                onDrop={e => {
                                    if (isDone) return;
                                    const word = e.dataTransfer.getData('word');
                                    setDragDropped(d => [...d, word]);
                                    setDragAvailable(a => a.filter(w => w !== word));
                                    setResult(null);
                                }}
                            >
                                {dragDropped.length === 0
                                    ? <span className="slp-drop-hint">Перетащите элементы сюда по порядку</span>
                                    : dragDropped.map((w, i) => (
                                        <span key={i} className="slp-ex-dropped-chip"
                                              onClick={() => {
                                                  if (isDone) return;
                                                  setDragDropped(d => d.filter((_, j) => j !== i));
                                                  setDragAvailable(a => [...a, w]);
                                                  setResult(null);
                                              }}>
                                            <span className="slp-dropped-num">{i + 1}</span>
                                            {w}
                                            <span className="slp-dropped-del">✕</span>
                                        </span>
                                    ))
                                }
                            </div>
                            <div className="slp-ex-drag-chips-label">Доступные элементы:</div>
                            <div className="slp-ex-drag-words">
                                {dragAvailable.map((w, i) => (
                                    <span
                                        key={i}
                                        className="slp-ex-drag-chip"
                                        draggable={!isDone}
                                        onDragStart={e => e.dataTransfer.setData('word', w)}
                                    >
                                        {w}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </>
                )}

                {exType === 'matching' && (
                    <>
                        {ex.description && <div className="slp-ex-question">{ex.description}</div>}
                        <div className="slp-ex-match-wrap">
                            <div className="slp-ex-match-columns">
                                <div className="slp-ex-match-col">
                                    {cleanDragItems.map((term, i) => {
                                        const pairNum = matchedPairs[i] !== null && matchedPairs[i] !== undefined
                                            ? i + 1 : null;
                                        const isSelected = selectedLeftIndex === i;
                                        return (
                                            <button
                                                key={i}
                                                className={`slp-ex-match-item slp-ex-match-left ${isSelected ? 'selected' : ''} ${pairNum ? 'matched' : ''}`}
                                                disabled={isDone}
                                                onClick={() => handleMatchLeftTap(i)}
                                            >
                                                {pairNum && <span className="slp-ex-match-num">{pairNum}</span>}
                                                <span className="slp-ex-match-text">{term}</span>
                                            </button>
                                        );
                                    })}
                                </div>
                                <div className="slp-ex-match-col">
                                    {rightDisplayOrder.map((originalIdx) => {
                                        const leftIdx = matchedPairs.findIndex(v => v === originalIdx);
                                        const pairNum = leftIdx !== -1 ? leftIdx + 1 : null;
                                        const isUsed = usedRightIndices.has(originalIdx);
                                        return (
                                            <button
                                                key={originalIdx}
                                                className={`slp-ex-match-item slp-ex-match-right ${isUsed ? 'matched' : ''} ${selectedLeftIndex !== null && !isUsed ? 'targetable' : ''}`}
                                                disabled={isDone || isUsed}
                                                onClick={() => handleMatchRightTap(originalIdx)}
                                            >
                                                {pairNum && <span className="slp-ex-match-num">{pairNum}</span>}
                                                <span className="slp-ex-match-text">{cleanOptions[originalIdx]}</span>
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                            {selectedLeftIndex !== null && (
                                <div className="slp-ex-match-hint">👉 Теперь выберите пару справа</div>
                            )}
                        </div>
                    </>
                )}

                {exType === 'text_input' && (
                    <>
                        {ex.description && <div className="slp-ex-question">{ex.description}</div>}
                        <textarea
                            className="slp-ex-textarea"
                            placeholder="Напишите ваш ответ..."
                            disabled={isDone}
                            value={textAnswer}
                            rows={4}
                            onChange={e => { setTextAnswer(e.target.value); setResult(null); }}
                        />
                        <div className="slp-ex-ai-note">
                            <span className="slp-ai-dot"/>
                            Ответ будет проверен AI
                        </div>
                    </>
                )}

                {ex.hint && (
                    <div className="slp-ex-hint-wrap">
                        <button className="slp-ex-hint-btn" onClick={() => setShowHint(h => !h)}>
                            💡 {showHint ? 'Скрыть подсказку' : 'Показать подсказку'}
                        </button>
                        {showHint && <div className="slp-ex-hint-text">{ex.hint}</div>}
                    </div>
                )}

                {result && (
                    <div className={`slp-ex-result-banner ${result}`}>
                        <span className="slp-res-icon">
                            {result === 'correct' ? '🎉' : result === 'wrong' ? '❌' : '✅'}
                        </span>
                        <div>
                            {result === 'correct' && <><strong>Правильно!</strong> Отличная работа!</>}
                            {result === 'wrong' && <><strong>Неправильно.</strong> Попробуйте ещё раз.</>}
                            {result === 'submitted' && <><strong>Ответ отправлен!</strong> AI проверит его.</>}
                        </div>
                    </div>
                )}

                {aiFeedback && (
                    <div className="slp-ex-ai-feedback">
                        <div className="slp-ex-ai-feedback-label">
                            <span className="slp-ai-pulse-dot"/>
                            AI Feedback
                        </div>
                        <div className="slp-ex-ai-feedback-text">{aiFeedback}</div>
                    </div>
                )}

                <div className="slp-ex-actions">
                    {!isDone && (
                        <button
                            className="slp-ex-submit-btn"
                            onClick={handleSubmit}
                            disabled={submitting || !buildAnswer()}
                        >
                            {submitting
                                ? <><span className="slp-btn-spin"/>Проверяем...</>
                                : '✅ Проверить ответ'
                            }
                        </button>
                    )}
                    {isWrong && (
                        <button className="slp-ex-retry-btn" onClick={handleRetry}>
                            🔄 Попробовать снова
                        </button>
                    )}
                    {isDone && result === 'correct' && (
                        <div className="slp-ex-done-label">✓ Выполнено</div>
                    )}
                </div>
            </div>
        </div>
    );
};

/* ═══════════════════════════════════════════════════════════
   EXERCISE SECTION BLOCK
═══════════════════════════════════════════════════════════ */
export const ExerciseSection = ({section, courseId, lessonId, submissions = {}, submissionsReady = false}) => {
    const exercises = section.exercises || [];
    if (exercises.length === 0) return null;
    const totalPts = exercises.reduce((s, e) => s + (e.points || 0), 0);
    const completedCount = exercises.reduce(
        (n, e) => n + (submissions[e.id] ? 1 : 0),
        0,
    );
    // Include the "ready" flag in the card key so the card remounts ONCE the
    // async submissions fetch resolves. Without this remount, ExerciseCard's
    // useState initializers fire only at first mount (with empty submissions)
    // and the previous-answer hydration silently never happens.
    const keyTag = submissionsReady ? 'h' : 'p';
    return (
        <div className="slp-ex-section">
            <div className="slp-ex-section-bar">
                <div className="slp-ex-section-left">
                    <span className="slp-ex-section-icon">🎯</span>
                    <span className="slp-ex-section-count">{exercises.length} заданий</span>
                    {completedCount > 0 && (
                        <span className="slp-ex-section-done">
                            ✓ {completedCount}/{exercises.length}
                        </span>
                    )}
                </div>
                {totalPts > 0 && (
                    <span className="slp-ex-section-pts"><Trophy size={14} aria-hidden="true" /> {totalPts} pts всего</span>
                )}
            </div>
            <div className="slp-ex-section-list">
                {exercises
                    .slice()
                    .sort((a, b) => (a.order || 0) - (b.order || 0))
                    .map((ex, i) => (
                        <ExerciseCard
                            key={`${ex.id || i}-${keyTag}`}
                            ex={ex}
                            courseId={courseId}
                            lessonId={lessonId}
                            index={i}
                            previousSubmission={submissions[ex.id] || null}
                        />
                    ))
                }
            </div>
        </div>
    );
};
