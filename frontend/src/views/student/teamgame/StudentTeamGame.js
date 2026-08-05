import React, { useEffect, useState, useCallback, useRef } from 'react';
import { API_URL, headers, getCurrentUser } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import { useSessionSocket } from '../../../hooks/useSessionSocket';
import { BugSnippet, BugExplanation } from './BugHuntArena';
import './StudentTeamGame.css';
import { Trophy, Timer, Star, Check, X, CircleCheckBig, XCircle } from 'lucide-react';

export const OPTION_LABELS = ['A', 'B', 'C', 'D', 'E', 'F'];
// Bug-hunt explanations are the whole pedagogical payload — hold the reveal
// long enough to actually read one, vs. a quick correct/incorrect flash for quiz.
const QUIZ_REVEAL_MS = 2500;
const BUG_REVEAL_MS = 5000;

// Rough heuristic for detecting code-flavored answer options (e.g. "<body>",
// "<head>") so they render in the monospace font per the design spec —
// question content stays free-form/author-supplied, this is presentation-only.
function looksLikeCode(text) {
    if (typeof text !== 'string') return false;
    const trimmed = text.trim();
    return /^<\/?[a-zA-Z][\w-]*\/?>$/.test(trimmed)
        || /[{};]/.test(trimmed)
        || /^(function|const|let|var|import|class|def|print|SELECT|INSERT)\b/i.test(trimmed);
}

// Pure helper shared by QuizOverlay and AutoQuizFlow to derive each answer
// option's visual state — 'neutral' | 'chosen' | 'correct' | 'wrongPick' | 'faded'.
// Kept outside the components since it has no dependency on component state
// beyond its arguments (DRY — both quiz arenas need identical reveal rules).
export function getAnswerState(i, { chosen, showResult, correctOption }) {
    if (showResult) {
        if (i === correctOption) return 'correct';
        if (i === chosen && i !== correctOption) return 'wrongPick';
        return 'faded';
    }
    if (chosen === i) return 'chosen';
    if (chosen !== null) return 'faded';
    return 'neutral';
}

// ── Shared language toggle for QUESTION CONTENT (not UI chrome) ───────────────
// This is a legitimate separate concept from the app's UI language: it flips
// which authored translation of the question/options is shown, independent of
// useTranslation()'s chrome language. Reads as a labeled content-language chip.
function useLang() {
    const [lang, setLangState] = useState(() => localStorage.getItem('game_lang') || 'uz');
    const toggle = () => {
        const next = lang === 'uz' ? 'ru' : 'uz';
        localStorage.setItem('game_lang', next);
        setLangState(next);
    };
    return [lang, toggle];
}

// ── Shared presentational pieces for the quiz arena ───────────────────────────

function LangChip({ lang, onToggle, label }) {
    return (
        <button type="button" className="stg-lang-chip" onClick={onToggle} aria-label={label}>
            {lang === 'uz' ? "🇺🇿 O'z" : '🇷🇺 Рус'}
        </button>
    );
}

function TimerPill({ seconds, low, label }) {
    return (
        <div className={`stg-timer-pill${low ? ' stg-timer-pill--low' : ''}`} role="timer" aria-label={label}>
            <Timer size={15} className="stg-timer-pill-icon" aria-hidden="true" />
            <span className="stg-timer-pill-num">{seconds}</span>
        </div>
    );
}

function PointsChip({ children }) {
    return (
        <div className="stg-points-chip">
            <Star size={13} aria-hidden="true" />
            <span>{children}</span>
        </div>
    );
}

function AnswerOption({ index, text, state, chosen, isCode, onClick, disabled }) {
    const stateClass = state !== 'neutral' ? ` stg-answer-card--${state}` : '';
    const letterClass = state === 'correct' ? ' stg-answer-letter--correct'
        : state === 'wrongPick' ? ' stg-answer-letter--wrong' : '';
    return (
        <button
            type="button"
            className={`stg-answer-card${stateClass}`}
            onClick={onClick}
            disabled={disabled}
            aria-pressed={chosen === index}
        >
            <span className={`stg-answer-letter${letterClass}`}>{OPTION_LABELS[index]}</span>
            <span className={`stg-answer-text${isCode ? ' stg-answer-text--code' : ''}`}>{text}</span>
            {state === 'correct' && <Check size={16} className="stg-answer-icon" aria-hidden="true" />}
            {state === 'wrongPick' && <X size={16} className="stg-answer-icon" aria-hidden="true" />}
        </button>
    );
}

function FeedbackBanner({ variant, children }) {
    const Icon = variant === 'success' ? CircleCheckBig : XCircle;
    return (
        <div className={`stg-feedback-banner stg-feedback-banner--${variant}`} aria-live="polite">
            <Icon size={20} aria-hidden="true" />
            <span className="stg-feedback-text">{children}</span>
        </div>
    );
}

// revealData: question_end payload from teacher — when set, show result then close
function QuizOverlay({ question, sessionId, revealData, onDone }) {
    const { t } = useTranslation();
    const [chosen, setChosen] = useState(null);
    const [pendingResult, setPendingResult] = useState(null);  // API response stored until reveal
    const [timeLeft, setTimeLeft] = useState(question.time_limit);
    const [submitting, setSubmitting] = useState(false);
    const [lang, toggleLang] = useLang();
    const [clickable, setClickable] = useState(false);

    // Lock body scroll while overlay is shown
    useEffect(() => {
        const prev = document.body.style.overflow;
        document.body.style.overflow = 'hidden';
        return () => { document.body.style.overflow = prev; };
    }, []);

    // Ignore clicks/taps for the first 350ms after mount to prevent
    // touch-event passthrough from the previous interaction
    useEffect(() => {
        const t = setTimeout(() => setClickable(true), 350);
        return () => clearTimeout(t);
    }, []);

    // Countdown
    useEffect(() => {
        const start = question.activated_at ? new Date(question.activated_at) : new Date();
        const tick = () => {
            const elapsed = (Date.now() - start.getTime()) / 1000;
            setTimeLeft(Math.max(0, Math.ceil(question.time_limit - elapsed)));
        };
        tick();
        const t = setInterval(tick, 250);
        return () => clearInterval(t);
    }, [question]);

    // When teacher reveals: show result, then close (longer hold for
    // bug-hunt so there's time to read the explanation)
    useEffect(() => {
        if (!revealData) return;
        const ms = question.question_kind === 'bug_hunt' ? BUG_REVEAL_MS : QUIZ_REVEAL_MS;
        const t = setTimeout(() => onDone(), ms);
        return () => clearTimeout(t);
    }, [revealData, onDone, question.question_kind]);

    const submit = async (idx) => {
        if (!clickable || chosen !== null || submitting) return;
        setChosen(idx);
        setSubmitting(true);
        try {
            const res = await fetch(`${API_URL}v1/game-sessions/${sessionId}/questions/${question.id}/answer`, {
                method: 'POST',
                headers: { ...headers(), 'Content-Type': 'application/json' },
                body: JSON.stringify({ chosen_option: idx }),
            });
            if (res.ok) {
                const data = await res.json();
                setPendingResult(data);
            } else {
                setPendingResult('late');
            }
        } catch {
            // Network/offline failure — the answer was never recorded server-side,
            // so this must NOT fall through to the "incorrect" branch below.
            setPendingResult('error');
        } finally { setSubmitting(false); }
    };

    // After reveal: determine result to display
    const revealedCorrectOpt = revealData?.correct_option;
    const showResult = revealData !== null && revealData !== undefined;
    const resultIsCorrect = pendingResult && pendingResult !== 'late' && pendingResult !== 'error' && pendingResult.is_correct;
    const resultPts = pendingResult && pendingResult !== 'late' && pendingResult !== 'error' ? pendingResult.points_earned : 0;
    const didNotAnswer = chosen === null;
    const wasLate = pendingResult === 'late';
    const wasError = pendingResult === 'error';

    const options = lang === 'ru' && question.options_ru ? question.options_ru : question.options;

    return (
        <div className="stg-quiz-overlay">
            <div className="stg-top-bar-row">
                <div className="stg-top-bar-spacer" />
                {/* bug_hunt questions never have question_text_ru (the code/question
                    itself isn't translated) but bug_explanation_ru still is, so the
                    toggle must stay available to pick which language that reveal uses. */}
                {(question.question_text_ru || question.question_kind === 'bug_hunt') && (
                    <LangChip lang={lang} onToggle={toggleLang} label={t('game.questionLangTitle')} />
                )}
                <TimerPill
                    seconds={`${timeLeft}${t('game.secondsSuffix')}`}
                    low={timeLeft <= 5}
                    label={`${timeLeft} ${t('game.secondsSuffix')}`}
                />
            </div>

            <div className="stg-quiz-question">
                <PointsChip>{t('game.pointsUpTo').replace('{points}', question.points)}</PointsChip>
                <h2>{lang === 'ru' && question.question_text_ru ? question.question_text_ru : question.question_text}</h2>
            </div>

            {question.question_kind === 'bug_hunt' ? (
                <BugSnippet
                    code={question.code_snippet}
                    language={question.code_language}
                    options={options}
                    chosen={chosen}
                    showResult={showResult}
                    correctOption={revealedCorrectOpt}
                    onPick={submit}
                    disabled={chosen !== null || showResult}
                />
            ) : (
                <div className="stg-quiz-options">
                    {options.map((opt, i) => {
                        const state = getAnswerState(i, { chosen, showResult, correctOption: revealedCorrectOpt });
                        return (
                            <AnswerOption
                                key={i}
                                index={i}
                                text={opt}
                                state={state}
                                chosen={chosen}
                                isCode={looksLikeCode(opt)}
                                onClick={() => submit(i)}
                                disabled={chosen !== null || showResult}
                            />
                        );
                    })}
                </div>
            )}

            {/* Before reveal: show waiting state */}
            {!showResult && chosen !== null && (
                <p className="stg-quiz-waiting-teacher">{t('game.waitingReveal')}</p>
            )}
            {!showResult && timeLeft === 0 && chosen === null && (
                <FeedbackBanner variant="danger">{t('game.timeUp')}</FeedbackBanner>
            )}

            {/* After reveal: show personal result */}
            {showResult && (
                <FeedbackBanner variant={(didNotAnswer || wasLate || wasError) ? 'danger' : resultIsCorrect ? 'success' : 'danger'}>
                    {didNotAnswer
                        ? t('game.notAnswered')
                        : wasLate
                            ? t('game.tooLate')
                            : wasError
                                ? t('game.submitError')
                                : resultIsCorrect
                                    ? <>{t('game.correctExclaim')} <span className="stg-feedback-pts">+{resultPts} {t('game.pointsSuffix')}</span></>
                                    : t('game.incorrectExclaim')
                    }
                </FeedbackBanner>
            )}

            {showResult && question.question_kind === 'bug_hunt' && (
                <BugExplanation
                    lang={lang}
                    text={revealData?.bug_explanation}
                    textRu={revealData?.bug_explanation_ru}
                    correctLine={revealData?.bug_line}
                />
            )}
        </div>
    );
}


// ── Live ranking shown right after each answer in auto mode ────────────────────
// Tracks the student's position across questions via sessionStorage (this
// component unmounts/remounts every question since it's only rendered while
// showResult is true), so movement direction and the top-1 streak survive
// that remount cycle without needing a ref that would reset each time.
function LiveRanking({ rankings, myId, sessionId }) {
    const { t } = useTranslation();
    // Scoped by student id too, not just session id — on a shared classroom
    // computer, a second student reusing the same browser tab must not
    // inherit the first student's rank history / top-1 streak.
    const uid = getCurrentUser()?.id ?? 'anon';
    const posKey = `auto_prevpos_${sessionId}_${uid}`;
    const top1Key = `auto_top1_${sessionId}_${uid}`;

    const myIdx = rankings ? rankings.findIndex(r => r.id === myId) : -1;
    const [movement, setMovement] = useState(null); // 'up' | 'down' | null
    const [top1Count, setTop1Count] = useState(() => parseInt(sessionStorage.getItem(top1Key) || '0', 10));

    useEffect(() => {
        if (myIdx === -1) return;
        const prevRaw = sessionStorage.getItem(posKey);
        const prev = prevRaw !== null ? parseInt(prevRaw, 10) : null;

        setMovement(prev !== null && prev !== myIdx ? (myIdx < prev ? 'up' : 'down') : null);

        if (myIdx === 0 && prev !== 0) {
            const nextCount = parseInt(sessionStorage.getItem(top1Key) || '0', 10) + 1;
            sessionStorage.setItem(top1Key, String(nextCount));
            setTop1Count(nextCount);
        }
        sessionStorage.setItem(posKey, String(myIdx));
    }, [myIdx, posKey, top1Key]);

    if (!rankings || rankings.length === 0) return null;

    const rival = myIdx >= 0 && myIdx < rankings.length - 1 ? rankings[myIdx + 1] : null;
    const gap = rival ? rankings[myIdx].score - rival.score : null;
    const isUrgent = gap !== null && gap <= 2;

    return (
        <div className={`stg-rating-panel${movement ? ` stg-rating-panel--${movement}` : ''}`}>
            <div className="stg-rating-header">
                <Trophy size={13} className="stg-rating-header-icon" aria-hidden="true" />
                <span>{t('quiz.teamsRating')}</span>
                {top1Count > 0 && (
                    <span className="stg-top1-badge" title={t('game.top1Title')}>🥇 ×{top1Count}</span>
                )}
            </div>

            {movement === 'up' && <div className="stg-rank-mood stg-rank-mood--up">🚀 {t('game.risingLabel')}</div>}
            {movement === 'down' && <div className="stg-rank-mood stg-rank-mood--down">😢 {t('game.fallingLabel')}</div>}

            <div className="stg-rating-rows">
                {rankings.map((r, i) => (
                    <div
                        key={r.id}
                        className={`stg-rating-row${r.id === myId ? ' stg-rating-row--mine' : ''}`}
                    >
                        <span className="stg-rating-pos">{i + 1}</span>
                        <span className="stg-rating-dot" style={{ background: r.color }} />
                        <span className="stg-rating-name">{r.name}</span>
                        <span className="stg-rating-score">{r.score}</span>
                    </div>
                ))}
            </div>

            {/* Legend: explains each color dot used in the rows above. Built from
                the actual live team roster (name + real color) rather than a fixed
                blue/red/green scheme — sessions can have 2-10 teams with palette
                colors assigned at random, so a hardcoded 3-color legend would
                mislabel real teams. See judgment-call note in the task report. */}
            <div className="stg-rating-legend">
                {rankings.map(r => (
                    <span key={r.id} className="stg-rating-legend-item">
                        <span className="stg-rating-dot" style={{ background: r.color }} />
                        {r.name}
                    </span>
                ))}
            </div>

            {myIdx === 0 && !rival && (
                <div className="stg-rank-chase stg-rank-chase--leading">👑 {t('game.youAreLeading')}</div>
            )}
            {rival && (
                <div className={`stg-rank-chase${isUrgent ? ' stg-rank-chase--urgent' : ''}`}>
                    {(isUrgent ? t('game.catchingUpUrgent') : t('game.catchingUp'))
                        .replace('{name}', rival.name).replace('{gap}', gap)}
                </div>
            )}
        </div>
    );
}


// ── Auto Quiz Flow (auto mode — each student gets personalized random order) ──
function AutoQuizFlow({ session, sessionId }) {
    const { t } = useTranslation();
    // Scoped by student id too — see LiveRanking's storage keys for why a
    // shared classroom computer makes session-id-only keys unsafe.
    const uid = getCurrentUser()?.id ?? 'anon';
    const storageKey = `auto_qidx_${sessionId}_${uid}`;
    // Persists when the CURRENT question's countdown actually started, so a
    // page refresh resumes the clock instead of granting a fresh full
    // time_limit — see the countdown effect below for how it's read back.
    const timeStorageKey = `auto_qstart_${sessionId}_${uid}`;
    const [questions, setQuestions] = useState(null);
    const [qIdx, setQIdx] = useState(() => {
        const saved = sessionStorage.getItem(storageKey);
        return saved ? parseInt(saved, 10) : 0;
    });
    const [timeLeft, setTimeLeft] = useState(null);
    const [chosen, setChosen] = useState(null);
    const [result, setResult] = useState(null);
    const [done, setDone] = useState(false);
    const [clickable, setClickable] = useState(false);
    const [lang, toggleLang] = useLang();
    const advanceRef = useRef(null);  // timeout for auto-advancing to next question
    const timerRef = useRef(null);    // interval for countdown

    useEffect(() => {
        fetch(`${API_URL}v1/game-sessions/${sessionId}/my-questions`, {
            headers: { ...headers() }
        })
            .then(r => r.json())
            .then(d => {
                const qs = Array.isArray(d) ? d : [];
                setQuestions(qs);
                // Clamp saved index in case question list changed
                setQIdx(i => Math.min(i, Math.max(0, qs.length - 1)));
            })
            .catch(() => setQuestions([]));
    }, [sessionId]);

    // Persist current question index across refreshes
    useEffect(() => {
        sessionStorage.setItem(storageKey, String(qIdx));
    }, [qIdx, storageKey]);

    const currentQ = questions?.[qIdx];

    // Advance to next question
    const advance = useCallback(async () => {
        clearTimeout(advanceRef.current);
        advanceRef.current = null;
        clearInterval(timerRef.current);
        setChosen(null);
        setResult(null);
        setClickable(false);
        setTimeLeft(null);
        if (qIdx + 1 >= (questions?.length ?? 0)) {
            // Before declaring done, re-check with the server — the teacher may
            // have added more questions mid-game, and /my-questions syncs those
            // in for us, so a longer list here means there's more to do.
            try {
                const res = await fetch(`${API_URL}v1/game-sessions/${sessionId}/my-questions`, {
                    headers: { ...headers() }
                });
                if (res.ok) {
                    const fresh = await res.json();
                    if (Array.isArray(fresh) && fresh.length > (questions?.length ?? 0)) {
                        setQuestions(fresh);
                        setQIdx(i => i + 1);
                        return;
                    }
                }
            } catch {}
            sessionStorage.removeItem(storageKey);
            sessionStorage.removeItem(timeStorageKey);
            setDone(true);
        } else {
            setQIdx(i => i + 1);
        }
    }, [qIdx, questions, storageKey, timeStorageKey, sessionId]);

    // Reset click guard on each new question
    useEffect(() => {
        if (!currentQ) return;
        const t = setTimeout(() => setClickable(true), 350);
        return () => clearTimeout(t);
    }, [currentQ?.id]);

    // Countdown timer — only runs when no result yet
    useEffect(() => {
        if (!currentQ || result !== null) return;

        // Resume the existing countdown across a refresh instead of granting
        // a fresh full time_limit: reuse the saved start timestamp if it's
        // for this same question, otherwise this is a genuinely new question
        // and we stamp a fresh start.
        let start;
        try {
            const saved = JSON.parse(sessionStorage.getItem(timeStorageKey) || 'null');
            start = saved && saved.id === currentQ.id ? saved.ts : null;
        } catch {
            start = null;
        }
        if (start === null) {
            start = Date.now();
            sessionStorage.setItem(timeStorageKey, JSON.stringify({ id: currentQ.id, ts: start }));
        }

        const tick = () => {
            const elapsed = (Date.now() - start) / 1000;
            const remaining = Math.max(0, Math.ceil(currentQ.time_limit - elapsed));
            setTimeLeft(remaining);
            if (remaining === 0) {
                clearInterval(timerRef.current);
                // Only schedule advance if not already scheduled by submit()
                if (!advanceRef.current) {
                    advanceRef.current = setTimeout(advance, 1500);
                }
            }
        };
        tick();
        timerRef.current = setInterval(tick, 250);
        // Only clear the interval on cleanup — never cancel advanceRef here
        return () => clearInterval(timerRef.current);
    }, [currentQ?.id, result, advance, timeStorageKey]);

    const submit = async (idx) => {
        if (!clickable || chosen !== null || result !== null || timeLeft === 0) return;
        clearInterval(timerRef.current);
        setChosen(idx);
        try {
            const res = await fetch(
                `${API_URL}v1/game-sessions/${sessionId}/questions/${currentQ.id}/answer-auto`,
                {
                    method: 'POST',
                    headers: { ...headers(), 'Content-Type': 'application/json' },
                    body: JSON.stringify({ chosen_option: idx }),
                }
            );
            if (res.ok) {
                const data = await res.json();
                setResult(data);
                const revealMs = currentQ.question_kind === 'bug_hunt' ? BUG_REVEAL_MS : QUIZ_REVEAL_MS;
                advanceRef.current = setTimeout(advance, revealMs);
            } else {
                // Unexpected error — don't strand the student on this question forever.
                advanceRef.current = setTimeout(advance, 1500);
            }
        } catch {
            advanceRef.current = setTimeout(advance, 1500);
        }
    };

    // Cleanup on unmount
    useEffect(() => () => {
        clearTimeout(advanceRef.current);
        clearInterval(timerRef.current);
    }, []);

    if (!questions) {
        return <div className="stg-auto-loading">{t('game.loadingQuestions')}</div>;
    }
    if (questions.length === 0) {
        return <div className="stg-auto-empty">{t('game.noQuestionsYet')}</div>;
    }
    if (done) {
        return (
            <div className="stg-auto-done">
                <div className="stg-auto-done-icon">🎉</div>
                <h3>{t('game.allQuestionsDone')}</h3>
                <p>{t('game.waitingFinalResults')}</p>
            </div>
        );
    }

    const showResult = result !== null;
    const options = lang === 'ru' && currentQ.options_ru ? currentQ.options_ru : currentQ.options;
    const progressPct = questions.length > 0 ? ((qIdx + 1) / questions.length) * 100 : 0;

    return (
        <div className="stg-quiz-overlay">
            <div className="stg-top-bar-row">
                <span className="stg-question-counter">
                    <span className="stg-question-counter-current">{qIdx + 1}</span>
                    <span className="stg-question-counter-sep"> / </span>
                    <span className="stg-question-counter-total">{questions.length}</span>
                </span>
                <div className="stg-progress-track">
                    <div className="stg-progress-fill" style={{ width: `${progressPct}%` }} />
                </div>
                {/* bug_hunt questions never have question_text_ru (the code/question
                    itself isn't translated) but bug_explanation_ru still is, so the
                    toggle must stay available to pick which language that reveal uses. */}
                {(currentQ.question_text_ru || currentQ.question_kind === 'bug_hunt') && (
                    <LangChip lang={lang} onToggle={toggleLang} label={t('game.questionLangTitle')} />
                )}
                <TimerPill
                    seconds={`${timeLeft ?? 0}${t('game.secondsSuffix')}`}
                    low={timeLeft !== null && timeLeft <= 5}
                    label={`${timeLeft ?? 0} ${t('game.secondsSuffix')}`}
                />
            </div>

            <div className="stg-quiz-question">
                <PointsChip>{currentQ.points} {t('game.pointsSuffix')}</PointsChip>
                <h2>
                    {lang === 'ru' && currentQ.question_text_ru
                        ? currentQ.question_text_ru
                        : currentQ.question_text}
                </h2>
            </div>

            {currentQ.question_kind === 'bug_hunt' ? (
                <BugSnippet
                    code={currentQ.code_snippet}
                    language={currentQ.code_language}
                    options={options}
                    chosen={chosen}
                    showResult={showResult}
                    correctOption={result?.correct_option}
                    onPick={submit}
                    disabled={chosen !== null || showResult || timeLeft === 0}
                />
            ) : (
                <div className="stg-quiz-options">
                    {options.map((opt, i) => {
                        const state = getAnswerState(i, { chosen, showResult, correctOption: result?.correct_option });
                        return (
                            <AnswerOption
                                key={i}
                                index={i}
                                text={opt}
                                state={state}
                                chosen={chosen}
                                isCode={looksLikeCode(opt)}
                                onClick={() => submit(i)}
                                disabled={chosen !== null || showResult || timeLeft === 0}
                            />
                        );
                    })}
                </div>
            )}

            {!showResult && timeLeft === 0 && chosen === null && (
                <FeedbackBanner variant="danger">{t('game.timeUp')}</FeedbackBanner>
            )}

            {showResult && (
                <>
                    <FeedbackBanner variant={result.is_correct ? 'success' : 'danger'}>
                        {result.is_correct
                            ? <>{t('game.correctExclaim')} <span className="stg-feedback-pts">+{result.points_earned} {t('game.pointsSuffix')}</span></>
                            : t('game.incorrectExclaim')
                        }
                    </FeedbackBanner>
                    {currentQ.question_kind === 'bug_hunt' && (
                        <>
                            <BugExplanation
                                lang={lang}
                                text={result.bug_explanation}
                                textRu={result.bug_explanation_ru}
                                correctLine={result.bug_line}
                            />
                            <button type="button" className="stg-bug-next-btn" onClick={advance}>
                                {t('game.bug.nextBtn')}
                            </button>
                        </>
                    )}
                    <LiveRanking rankings={result.rankings} myId={result.my_team_id} sessionId={sessionId} />
                </>
            )}
        </div>
    );
}


function MyTeamBanner({ session }) {
    const { t } = useTranslation();
    const team = session.teams?.find(t => t.id === session.my_team_id);
    if (!team) return null;
    return (
        <div className="stg-my-banner" style={{ borderColor: team.color }}>
            <span className="stg-my-label">{session.game_type === 'individual' ? t('game.yourResult') : t('game.yourTeam')}</span>
            <span className="stg-my-name" style={{ color: team.color }}>{team.name}</span>
            <span className="stg-my-score">{team.score} {t('game.pointsSuffix')}</span>
        </div>
    );
}

function ScoreBoard({ teams }) {
    const sorted = [...teams].sort((a, b) => b.score - a.score);
    const top = sorted[0]?.score || 0;
    return (
        <div className="stg-scoreboard">
            {sorted.map((team, idx) => (
                <div key={team.id} className="stg-sb-row">
                    <span className="stg-sb-rank">{idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx + 1}`}</span>
                    <span className="stg-sb-dot" style={{ background: team.color }} />
                    <span className="stg-sb-name">{team.name}</span>
                    <span className="stg-sb-score">{team.score}</span>
                    <div className="stg-sb-bar-wrap">
                        <div className="stg-sb-bar" style={{
                            background: team.color,
                            width: top > 0 ? `${(team.score / top) * 100}%` : '0%',
                        }} />
                    </div>
                </div>
            ))}
        </div>
    );
}

function AlreadyCompletedNotice() {
    const { t } = useTranslation();
    return (
        <div className="stg-quiz-overlay stg-already-completed">
            <div className="stg-auto-done">
                <div className="stg-auto-done-icon">✅</div>
                <h3>{t('game.alreadyCompletedTitle')}</h3>
                <p>{t('game.alreadyCompletedDesc')}</p>
            </div>
        </div>
    );
}

function SessionDetail({ initialSession, onBack }) {
    const { t } = useTranslation();
    const [session, setSession] = useState(initialSession);
    const [gone, setGone] = useState(false);
    const [activeQuestion, setActiveQuestion] = useState(null);  // question_start payload
    const [revealData, setRevealData] = useState(null);          // question_end payload while overlay still open
    const [lastResult, setLastResult] = useState(null);          // shown in post-question banner
    const [lang, toggleLang] = useLang();
    const [view, setView] = useState('scores'); // 'scores' | 'teams'

    const handleUpdate = useCallback((data) => setSession(data), []);
    const handleDeleted = useCallback(() => setGone(true), []);
    const handleMessage = useCallback((msg) => {
        if (msg.type === 'question_start') {
            setActiveQuestion(msg.data);
            setRevealData(null);
            setLastResult(null);
        }
        if (msg.type === 'question_end') {
            setRevealData(msg.data);
            setLastResult(msg.data);
            if (msg.data?.team_scores) {
                setSession(prev => ({
                    ...prev,
                    teams: (prev.teams || []).map(t => {
                        const ts = msg.data.team_scores.find(s => s.team_id === t.id);
                        return ts ? { ...t, score: ts.score } : t;
                    }),
                }));
            }
        }
        if (msg.type === 'auto_score_update' && msg.data?.team_scores) {
            setSession(prev => ({
                ...prev,
                teams: (prev.teams || []).map(t => {
                    const ts = msg.data.team_scores.find(s => s.team_id === t.id);
                    return ts ? { ...t, score: ts.score } : t;
                }),
            }));
        }
    }, []);
    useSessionSocket(session.id, handleUpdate, handleDeleted, handleMessage);

    if (gone) {
        return (
            <div className="stg-detail">
                <button className="stg-back-btn" onClick={onBack}>{t('game.back')}</button>
                <div className="stg-empty">
                    <div className="stg-empty-icon">🚫</div>
                    <h3>{t('game.deletedTitle')}</h3>
                    <p>{t('game.deletedDesc')}</p>
                </div>
            </div>
        );
    }

    const sortedTeams = [...(session.teams || [])].sort((a, b) => b.score - a.score);

    return (
        <div className="stg-detail">
            {/* Auto mode: each student works independently through their shuffled question list.
                If they've already answered every question, show a notice instead of
                letting them restart from question 1 on re-entry. */}
            {session.auto_mode && session.status === 'active' && (
                session.my_auto_completed
                    ? <AlreadyCompletedNotice />
                    : <AutoQuizFlow session={session} sessionId={session.id} />
            )}

            {/* Manual mode: teacher activates questions one by one for all students */}
            {!session.auto_mode && activeQuestion && (
                <QuizOverlay
                    key={activeQuestion.id}
                    question={activeQuestion}
                    sessionId={session.id}
                    revealData={revealData}
                    onDone={() => { setActiveQuestion(null); setRevealData(null); }}
                />
            )}

            <div className="stg-top-bar">
                <button className="stg-back-btn" onClick={onBack}>{t('game.back')}</button>
                <button className="stg-lang-toggle" onClick={toggleLang} title={t('game.questionLangTitle')}>
                    {lang === 'uz' ? "🇺🇿 O'z" : '🇷🇺 Рус'}
                </button>
            </div>
            <div className="stg-detail-header">
                <h2>{session.title}</h2>
                <span className={`stg-badge stg-badge--${session.status}`}>{t(`game.status.${session.status}`)}</span>
                <span className="stg-badge stg-badge--type">{t(`game.type.${session.game_type}`)}</span>
                <span className="stg-live-dot" title={t('game.liveTitle')} />
            </div>
            {session.description && <p className="stg-description">{session.description}</p>}

            <MyTeamBanner session={session} />

            {/* Show last question result between questions (manual mode only) */}
            {!session.auto_mode && lastResult && !activeQuestion && (
                <div className="stg-quiz-end-banner">
                    <h3>{t('game.questionResultsTitle')}</h3>
                    <div className="stg-quiz-end-opts">
                        {session.teams && session.teams[0]?.members.length > 0 && lastResult.answers && (
                            <p className="stg-quiz-end-stat">
                                {t('game.correctAnsweredLabel')} {lastResult.answers.filter(a => a.is_correct).length} / {lastResult.answers.length}
                            </p>
                        )}
                    </div>
                    <p className="stg-quiz-end-hint">{t('game.waitingNextQuestion')}</p>
                </div>
            )}

            {session.status === 'pending' && (
                <div className="stg-pending-notice">
                    <span>⏳</span>
                    <p>{t('game.pendingNotice')}</p>
                </div>
            )}

            {sortedTeams.length > 0 && session.status !== 'pending' && (
                <>
                    {session.game_type === 'team' && (
                        <div className="stg-view-tabs">
                            <button
                                className={`stg-view-tab${view === 'scores' ? ' stg-view-tab--active' : ''}`}
                                onClick={() => setView('scores')}
                            >{t('game.tabResults')}</button>
                            <button
                                className={`stg-view-tab${view === 'teams' ? ' stg-view-tab--active' : ''}`}
                                onClick={() => setView('teams')}
                            >{t('game.tabTeams')}</button>
                        </div>
                    )}

                    {(session.game_type === 'individual' || view === 'scores') && <ScoreBoard teams={sortedTeams} />}

                    {view === 'teams' && session.game_type === 'team' && (
                        <div className="stg-teams-grid">
                            {sortedTeams.map(team => (
                                <div key={team.id}
                                    className={`stg-team-card${team.id === session.my_team_id ? ' stg-team-card--mine' : ''}`}
                                    style={{ borderColor: team.id === session.my_team_id ? team.color : undefined }}>
                                    <div className="stg-team-title" style={{ color: team.color }}>
                                        {team.name}
                                        {team.id === session.my_team_id && <span className="stg-you-badge">{t('game.youAreHere')}</span>}
                                    </div>
                                    <div className="stg-team-score-big">{team.score} <span>{t('game.pointsSuffix')}</span></div>
                                    <div className="stg-member-list">
                                        {team.members.length === 0
                                            ? <span className="stg-no-members">{t('game.awaitingMembers')}</span>
                                            : team.members.map(m => (
                                                <div key={m.id} className="stg-member">
                                                    <span className="stg-avatar">{(m.full_name || m.username || '?')[0].toUpperCase()}</span>
                                                    <span>{m.full_name || m.username}</span>
                                                </div>
                                            ))
                                        }
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </>
            )}

            {session.status === 'completed' && (
                <div className="stg-completed-banner">
                    <Trophy size={16} aria-hidden="true" /> {t('game.completedBanner')} {sortedTeams[0] && `${t('game.winnerLabel')} ${sortedTeams[0].name} (${sortedTeams[0].score} ${t('game.pointsSuffix')})`}
                </div>
            )}
        </div>
    );
}

export default function StudentTeamGame() {
    const { t } = useTranslation();
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selected, setSelected] = useState(null);

    const load = useCallback((silent = false) => {
        if (!silent) setLoading(true);
        fetch(`${API_URL}v1/game-sessions`, { headers: headers() })
            .then(r => r.json())
            .then(d => setSessions(Array.isArray(d) ? d : []))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        load();
        const interval = setInterval(() => load(true), 10000);
        return () => clearInterval(interval);
    }, [load]);

    const openSession = useCallback(async (id) => {
        try {
            const res = await fetch(`${API_URL}v1/game-sessions/${id}`, { headers: headers() });
            if (!res.ok) return;
            const data = await res.json();
            setSelected(data);
            window.history.pushState({ sessionId: id }, '', `?session=${id}`);
        } catch {}
    }, []);

    const goBack = useCallback(() => {
        setSelected(null);
        window.history.pushState({}, '', window.location.pathname);
        load();
    }, [load]);

    // On mount: restore session from URL param; on browser back: clear selected
    useEffect(() => {
        const sessionId = new URLSearchParams(window.location.search).get('session');
        if (sessionId) openSession(Number(sessionId));

        const onPop = () => {
            const id = new URLSearchParams(window.location.search).get('session');
            if (!id) setSelected(null);
            else openSession(Number(id));
        };
        window.addEventListener('popstate', onPop);
        return () => window.removeEventListener('popstate', onPop);
    }, [openSession]);

    if (selected) {
        return <SessionDetail initialSession={selected} onBack={goBack} />;
    }

    return (
        <div className="stg-page">
            <div className="stg-page-header">
                <h1>{t('team_game')}</h1>
                <p className="stg-subtitle">{t('game.pageSubtitle')}</p>
            </div>

            {loading ? (
                <div className="stg-loading">{t('loading')}</div>
            ) : sessions.length === 0 ? (
                <div className="stg-empty">
                    <div className="stg-empty-icon">🎮</div>
                    <h3>{t('game.emptyTitle')}</h3>
                    <p>{t('game.emptyDesc')}</p>
                    <button className="stg-refresh-btn" onClick={() => load()}>{t('game.refresh')}</button>
                </div>
            ) : (
                <div className="stg-list">
                    {sessions.map(s => {
                        const myTeam = s.teams?.find(team => team.id === s.my_team_id);
                        return (
                            <div key={s.id} className={`stg-card stg-card--${s.status}`} onClick={() => openSession(s.id)}>
                                <div className="stg-card-top">
                                    <div>
                                        <h3>{s.title}</h3>
                                        {s.description && <p>{s.description}</p>}
                                    </div>
                                    <div className="stg-badges">
                                        <span className={`stg-badge stg-badge--${s.status}`}>{t(`game.status.${s.status}`)}</span>
                                        <span className="stg-badge stg-badge--type">{t(`game.type.${s.game_type}`)}</span>
                                    </div>
                                </div>
                                <div className="stg-card-bottom">
                                    <div className="stg-card-meta">
                                        <span>👥 {s.team_count} {t('game.teamsCountSuffix')}</span>
                                        {s.course_title && <span>📚 {s.course_title}</span>}
                                        {myTeam && (
                                            <span className="stg-my-team-pill" style={{ borderColor: myTeam.color, color: myTeam.color }}>
                                                {t('game.youPrefix')} {myTeam.name}
                                            </span>
                                        )}
                                    </div>
                                    {s.status === 'active' && (
                                        <button className="stg-join-btn" onClick={e => { e.stopPropagation(); openSession(s.id); }}>
                                            {t('game.joinBtn')}
                                        </button>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
