/* Practice mode components — FlashcardMode, QuizMode, SpellingMode, ListeningMode, ClozeMode. */

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { judgeTypedAsync, Icon } from './practiceUtils';

export function FlashcardMode({ word, onAnswer }) {
    const [flipped, setFlipped] = useState(false);
    useEffect(() => { setFlipped(false); }, [word.id]);

    return (
        <div className="pr-card pr-flash">
            <button
                className={`pr-flash-card ${flipped ? 'flipped' : ''}`}
                onClick={() => setFlipped(f => !f)}
                aria-label="Aylantirish"
            >
                <div className="pr-flash-face pr-flash-front">
                    <div className="pr-flash-hint">So'z</div>
                    <div className="pr-flash-word">{word.word}</div>
                    <div className="pr-flash-tap">Ma'nosini ko'rish uchun bosing</div>
                </div>
                <div className="pr-flash-face pr-flash-back">
                    <div className="pr-flash-hint">Ma'no</div>
                    <div className="pr-flash-ctx">
                        {word.context || <em>Konteskt yo'q — ezma o'qib eslab qoling</em>}
                    </div>
                </div>
            </button>

            {flipped && (
                <div className="pr-flash-actions">
                    <button
                        className="pr-btn pr-btn--bad"
                        onClick={() => onAnswer({ grade: 0, was_correct: false })}
                    >
                        <Icon.X /> Bilmayman
                    </button>
                    <button
                        className="pr-btn pr-btn--good"
                        onClick={() => onAnswer({ grade: 2, was_correct: true })}
                    >
                        <Icon.Check /> Bilaman
                    </button>
                </div>
            )}
        </div>
    );
}


/* MCQ — show the word, ask the student to pick its meaning. This is the
   natural flashcard direction. For entries with no saved context we fall
   back to the old "context → pick word" direction so the card is still
   usable. */
function MCQ({ word, onAnswer }) {
    const [picked, setPicked] = useState(null);
    useEffect(() => { setPicked(null); }, [word.id]);

    // Decide direction once per word. Meaning-side MCQ needs a real context
    // AND at least one extra distractor to be a fair test.
    const ctxOpts = Array.isArray(word.context_options) ? word.context_options : [];
    const meaningMode =
        Boolean((word.context || '').trim()) &&
        ctxOpts.filter(o => (o || '').trim()).length >= 2;

    const prompt = meaningMode
        ? "Bu so'zning ma'nosi qaysi?"
        : "Bu ma'noga qaysi so'z mos keladi?";

    const center = meaningMode
        ? <span className="pr-quiz-word">{word.word}</span>
        : (word.context || <em>Konteskt yo'q — taxminan tanlang</em>);

    const opts = meaningMode ? ctxOpts : (word.options || []);
    const correctValue = meaningMode ? word.context : word.word;

    const pick = (opt) => {
        if (picked !== null) return;
        const correct = opt === correctValue;
        setPicked(opt);
        setTimeout(() => onAnswer({
            grade: correct ? 2 : 0,
            was_correct: correct,
        }), 650);
    };

    return (
        <>
            <div className="pr-quiz-prompt">{prompt}</div>
            <div className={`pr-quiz-ctx ${meaningMode ? 'pr-quiz-ctx--word' : ''}`}>
                {center}
            </div>
            <div className={`pr-quiz-opts ${meaningMode ? 'pr-quiz-opts--meanings' : ''}`}>
                {opts.map((opt, idx) => {
                    const isCorrect = opt === correctValue;
                    const isPicked = opt === picked;
                    const cls = picked === null
                        ? ''
                        : isCorrect
                            ? 'pr-opt--ok'
                            : isPicked
                                ? 'pr-opt--bad'
                                : 'pr-opt--dim';
                    return (
                        <button
                            key={`${idx}-${opt}`}
                            className={`pr-opt ${cls}`}
                            onClick={() => pick(opt)}
                            disabled={picked !== null}
                        >
                            <span>{opt}</span>
                            {picked !== null && isCorrect && <Icon.Check />}
                            {picked !== null && isPicked && !isCorrect && <Icon.X />}
                        </button>
                    );
                })}
            </div>
        </>
    );
}


/* TypedAnswer — shared by Spelling, Listening, Cloze, and Quiz+ spelling
   sub-mode. Local Levenshtein first; AI judge runs as a tiebreaker for
   non-exact rejections so paraphrases / missing function words can pass. */
function TypedAnswer({ word, request, onAnswer, promptLabel, showContext, header }) {
    const [value, setValue] = useState('');
    const [verdict, setVerdict] = useState(null);
    const [judging, setJudging] = useState(false);
    const inputRef = useRef(null);

    useEffect(() => {
        setValue('');
        setVerdict(null);
        setJudging(false);
        setTimeout(() => inputRef.current?.focus(), 60);
    }, [word.id]);

    const submit = async (e) => {
        e?.preventDefault?.();
        if (verdict || judging) return;
        setJudging(true);
        const v = await judgeTypedAsync(request, value, word.word, word.context);
        setVerdict(v);
        setJudging(false);
        const grade = v.exact ? 2 : v.ok ? 1 : 0;
        setTimeout(() => onAnswer({ grade, was_correct: v.ok }), 900);
    };

    return (
        <>
            {header}
            {promptLabel && <div className="pr-typed-hint">{promptLabel}</div>}
            {showContext && (
                <div className="pr-typed-ctx">
                    {word.context || <em>Konteskt yo'q</em>}
                </div>
            )}
            <form className="pr-typed-form" onSubmit={submit}>
                <input
                    ref={inputRef}
                    type="text"
                    autoComplete="off"
                    autoCorrect="off"
                    spellCheck={false}
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    placeholder="So'zni yozing…"
                    className={`pr-typed-input ${verdict ? (verdict.ok ? 'ok' : 'bad') : ''}`}
                    disabled={!!verdict || judging}
                />
                <button
                    type="submit"
                    className="pr-btn pr-btn--primary"
                    disabled={!!verdict || judging || !value.trim()}
                >
                    {judging ? 'Tekshirilmoqda…' : 'Tekshirish'}
                </button>
            </form>
            {verdict && (
                <div className={`pr-typed-feedback ${verdict.ok ? (verdict.exact ? 'ok' : 'close') : 'bad'}`}>
                    {verdict.ok && verdict.exact && <><Icon.Check /> To'g'ri!</>}
                    {verdict.ok && !verdict.exact && (
                        <>
                            <Icon.Warn /> Yaqin — to'g'risi: <strong>{word.word}</strong>
                            {verdict.aiUsed && <span className="pr-ai-tag"><Icon.Sparkle /> AI</span>}
                        </>
                    )}
                    {!verdict.ok && <><Icon.X /> To'g'risi: <strong>{word.word}</strong></>}
                </div>
            )}
        </>
    );
}


/* Quiz+ — life_tracker's two-pass design: recognition pass (MCQ over the
   whole queue) followed by a recall pass (typed Spelling over the same
   queue). A word only counts as "correct" if it passed BOTH passes.
   The orchestrator drives which pass via the `qpPass` prop; the user
   doesn't toggle. */
export function QuizMode({ word, qpPass, onAnswer, request }) {
    const isSpelling = qpPass === 'spelling';
    return (
        <div className="pr-card pr-quiz">
            <div className="pr-quiz-modeline pr-quiz-modeline--locked">
                <span className={`pr-sub ${!isSpelling ? 'active' : ''}`}>
                    1. Tanish (MCQ)
                </span>
                <span className={`pr-sub ${isSpelling ? 'active' : ''}`}>
                    2. Eslab qolish (Yozish)
                </span>
            </div>
            {isSpelling
                ? <TypedAnswer
                    word={word}
                    request={request}
                    onAnswer={onAnswer}
                    promptLabel="So'zni yozing — birinchi raundda ko'rdingiz"
                    showContext
                />
                : <MCQ word={word} onAnswer={onAnswer} />
            }
        </div>
    );
}


export function SpellingMode({ word, onAnswer, request }) {
    return (
        <div className="pr-card pr-typed">
            <TypedAnswer
                word={word}
                request={request}
                onAnswer={onAnswer}
                promptLabel="Ma'no:"
                showContext
            />
        </div>
    );
}


export function ListeningMode({ word, onAnswer, request }) {
    const speak = useCallback(() => {
        if (typeof window === 'undefined' || !window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(word.word);
        u.rate = 0.85;
        u.lang = 'en-US';
        window.speechSynthesis.speak(u);
    }, [word.word]);
    useEffect(() => { speak(); }, [speak]);

    return (
        <div className="pr-card pr-typed">
            <TypedAnswer
                word={word}
                request={request}
                onAnswer={onAnswer}
                promptLabel="Eshitganingizni yozing"
                header={
                    <button type="button" className="pr-listen-btn" onClick={speak} title="Qayta eshitish">
                        <Icon.Volume /> <span>Eshitish</span>
                    </button>
                }
            />
        </div>
    );
}


export function ClozeMode({ word, onAnswer, request }) {
    const blanked = useMemo(() => {
        const ctx = word.context || '';
        if (!ctx) return null;
        const re = new RegExp(`\\b${word.word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
        if (!re.test(ctx)) return null;
        return ctx.replace(re, '_____');
    }, [word]);

    if (!blanked) {
        return (
            <div className="pr-card pr-typed">
                <div className="pr-typed-hint">
                    Bu so'z uchun gap kontekstida saqlanmagan.
                </div>
                <div className="pr-typed-ctx">«{word.word}»</div>
                <button
                    className="pr-btn pr-btn--primary"
                    onClick={() => onAnswer({ grade: 1, was_correct: true })}
                >
                    O'tkazib yuborish
                </button>
            </div>
        );
    }

    return (
        <div className="pr-card pr-typed">
            <TypedAnswer
                word={word}
                request={request}
                onAnswer={onAnswer}
                promptLabel="Bo'shliqni to'ldiring:"
                header={<div className="pr-cloze-ctx">{blanked}</div>}
            />
        </div>
    );
}
