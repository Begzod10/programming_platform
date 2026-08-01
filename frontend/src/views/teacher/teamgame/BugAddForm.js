import React, { useState } from 'react';
import { API_URL } from '../../../api/search/base';
import axiosInstance from '../../../api/axiosInstance';
import { highlight } from '../../../utils/highlight';
import './TeacherTeamGame.css';
import './BugAddForm.css';

const OPTION_LABELS = ['A', 'B', 'C', 'D', 'E', 'F'];
const LANGUAGES = ['javascript', 'python', 'html', 'css'];
const MAX_CANDIDATES = 6;

// A selected line reads as "vaguely not a real bug spot" if it's blank or
// just a closing bracket/brace/semicolon — soft warning only, never blocks
// saving (a teacher may legitimately want a blank-line distractor).
const looksTrivial = (line) => !line || /^\s*[})\];]*\s*$/.test(line);

export default function BugAddForm({ session, onClose, onSaved }) {
    const [tab, setTab] = useState('edit'); // 'edit' | 'mark'
    const [questionText, setQuestionText] = useState('');
    const [code, setCode] = useState('');
    const [language, setLanguage] = useState('javascript');
    const [candidates, setCandidates] = useState([]); // 1-based line numbers, insertion order
    const [bugLine, setBugLine] = useState(null);
    const [explanation, setExplanation] = useState('');
    const [explanationRu, setExplanationRu] = useState('');
    const [timeLimit, setTimeLimit] = useState(90);
    const [points, setPoints] = useState(1500);
    const [saving, setSaving] = useState(false);

    const lines = code.split('\n');
    const highlightedLines = highlight(code, language).split('\n');

    const toggleCandidate = (lineNum) => {
        setCandidates(prev => {
            if (prev.includes(lineNum)) {
                if (bugLine === lineNum) setBugLine(null);
                return prev.filter(n => n !== lineNum);
            }
            if (prev.length >= MAX_CANDIDATES) return prev;
            return [...prev, lineNum];
        });
    };

    const canSave = code.trim()
        && candidates.length >= 3 && candidates.length <= MAX_CANDIDATES
        && bugLine !== null
        && questionText.trim()
        && explanation.trim();

    const save = async (e) => {
        e.preventDefault();
        if (!canSave) return;
        setSaving(true);
        try {
            await axiosInstance.post(`${API_URL}v1/game-sessions/${session.id}/bug-questions`, {
                question_text: questionText.trim(),
                code_snippet: code,
                code_language: language,
                bug_line: bugLine,
                distractor_lines: candidates.filter(n => n !== bugLine),
                bug_explanation: explanation.trim(),
                bug_explanation_ru: explanationRu.trim() || null,
                time_limit: timeLimit,
                points,
            });
            onSaved();
        } catch (err) {
            alert(err.response?.data?.detail || 'Ошибка');
        } finally { setSaving(false); }
    };

    return (
        <form className="tbf-form" onSubmit={save}>
            <textarea
                required placeholder="Текст задания — например: «Найдите ошибку: почему функция возвращает неверный результат?»"
                className="tbf-question-text"
                value={questionText}
                onChange={e => setQuestionText(e.target.value)}
                rows={2}
            />

            <div className="tbf-code-toolbar">
                <select value={language} onChange={e => setLanguage(e.target.value)} className="tbf-lang-select">
                    {LANGUAGES.map(l => <option key={l} value={l}>{l}</option>)}
                </select>
                <div className="tbf-tabs">
                    <button type="button" className={`tbf-tab${tab === 'edit' ? ' tbf-tab--active' : ''}`} onClick={() => setTab('edit')}>
                        ✏️ Редактировать
                    </button>
                    <button type="button" className={`tbf-tab${tab === 'mark' ? ' tbf-tab--active' : ''}`} onClick={() => setTab('mark')} disabled={!code.trim()}>
                        🎯 Отметить
                    </button>
                </div>
            </div>

            {tab === 'edit' ? (
                <div className="tbf-editor-wrap">
                    <div className="tbf-line-nums" aria-hidden="true">
                        {lines.map((_, i) => <div key={i} className="tbf-line-num">{i + 1}</div>)}
                    </div>
                    <textarea
                        className="tbf-code-textarea"
                        value={code}
                        onChange={e => setCode(e.target.value)}
                        onKeyDown={e => {
                            if (e.key === 'Tab') {
                                e.preventDefault();
                                const ta = e.target;
                                const start = ta.selectionStart, end = ta.selectionEnd;
                                const next = code.substring(0, start) + '  ' + code.substring(end);
                                setCode(next);
                                requestAnimationFrame(() => { ta.selectionStart = ta.selectionEnd = start + 2; });
                            }
                        }}
                        spellCheck={false}
                        autoComplete="off"
                        placeholder="Вставьте код с ошибкой..."
                        rows={10}
                    />
                </div>
            ) : (
                <div className="tbf-mark-wrap">
                    {lines.map((lineText, i) => {
                        const lineNum = i + 1;
                        const isCandidate = candidates.includes(lineNum);
                        const isBug = bugLine === lineNum;
                        return (
                            <div key={i} className="tbf-mark-row">
                                <button
                                    type="button"
                                    className={`tbf-mark-gutter${isCandidate ? ' tbf-mark-gutter--selected' : ''}${isBug ? ' tbf-mark-gutter--bug' : ''}`}
                                    onClick={() => toggleCandidate(lineNum)}
                                    title={isCandidate ? 'Убрать из вариантов' : 'Добавить как вариант'}
                                >
                                    {lineNum}
                                </button>
                                <pre className="tbf-mark-code" dangerouslySetInnerHTML={{ __html: highlightedLines[i] || ' ' }} />
                            </div>
                        );
                    })}
                </div>
            )}

            {candidates.length > 0 && (
                <div className="tbf-candidates">
                    <span className="tbf-candidates-label">Кандидаты ({candidates.length}/{MAX_CANDIDATES}) — выберите, где баг:</span>
                    <div className="tbf-candidates-chips">
                        {candidates.map((lineNum, i) => (
                            <label key={lineNum} className={`tbf-chip${bugLine === lineNum ? ' tbf-chip--bug' : ''}`}>
                                <input
                                    type="radio"
                                    name="bugLine"
                                    checked={bugLine === lineNum}
                                    onChange={() => setBugLine(lineNum)}
                                />
                                <span className="tbf-chip-letter">{OPTION_LABELS[i]}</span>
                                <span className="tbf-chip-num">строка {lineNum}</span>
                                {looksTrivial(lines[lineNum - 1]) && <span className="tbf-chip-warn" title="Строка выглядит пустой/тривиальной">⚠️</span>}
                                <button type="button" className="tbf-chip-remove" onClick={() => toggleCandidate(lineNum)}>✕</button>
                            </label>
                        ))}
                    </div>
                    {candidates.length < 3 && (
                        <p className="tbf-hint">Нужно минимум 3 варианта (1 баг + 2 отвлекающих).</p>
                    )}
                </div>
            )}

            <textarea
                required placeholder="Объяснение — почему это баг и как исправить (показывается студентам после ответа)"
                className="tbf-explain-text"
                value={explanation}
                onChange={e => setExplanation(e.target.value)}
                rows={2}
            />
            <textarea
                placeholder="Объяснение на русском (необязательно)"
                className="tbf-explain-text"
                value={explanationRu}
                onChange={e => setExplanationRu(e.target.value)}
                rows={2}
            />

            <div className="tg-quiz-meta-row">
                <label>⏱ {timeLimit}с
                    <input type="range" min={5} max={120} step={5} value={timeLimit}
                        onChange={e => setTimeLimit(Number(e.target.value))} />
                </label>
                <label>⭐ {points} очков
                    <input type="range" min={100} max={5000} step={100} value={points}
                        onChange={e => setPoints(Number(e.target.value))} />
                </label>
            </div>

            <div className="tg-modal-actions">
                <button type="submit" className="tg-btn-primary" disabled={saving || !canSave}>
                    {saving ? 'Сохранение...' : '💾 Сохранить'}
                </button>
                <button type="button" className="tg-btn-secondary" onClick={onClose}>Отмена</button>
            </div>
        </form>
    );
}
