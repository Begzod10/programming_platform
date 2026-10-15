/* Practice mode components — FlashcardMode, QuizMode, SpellingMode, ListeningMode, ClozeMode. */

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { judgeTypedAsync, Icon } from './practiceUtils';
import { useTranslation } from '../../../i18n/useTranslation';

export function FlashcardMode({ word, onAnswer }) {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const [flipped, setFlipped] = useState(false);
    const answered = useRef(false);
    useEffect(() => { setFlipped(false); answered.current = false; }, [word.id]);
    // A fast double-tap used to post the same answer twice (double lapse).
    const answer = (result) => {
        if (answered.current) return;
        answered.current = true;
        onAnswer(result);
    };

    return (
        <div className="pr-card pr-flash">
            <button
                className={`pr-flash-card ${flipped ? 'flipped' : ''}`}
                onClick={() => setFlipped(f => !f)}
                aria-label={ru ? 'Перевернуть' : 'Aylantirish'}
            >
                <div className="pr-flash-face pr-flash-front">
                    <div className="pr-flash-hint">{ru ? 'Слово' : "So'z"}</div>
                    <div className="pr-flash-word">{word.word}</div>
                    <div className="pr-flash-tap">{ru ? 'Нажмите, чтобы увидеть значение' : "Ma'nosini ko'rish uchun bosing"}</div>
                </div>
                <div className="pr-flash-face pr-flash-back">
                    <div className="pr-flash-hint">{ru ? 'Значение' : "Ma'no"}</div>
                    <div className="pr-flash-ctx">
                        {word.context || <em>{ru ? 'Контекста нет — прочитайте вслух, чтобы запомнить' : "Kontekst yo'q — ovoz chiqarib o'qib eslab qoling"}</em>}
                    </div>
                </div>
            </button>

            {flipped && (
                <div className="pr-flash-actions">
                    <button
                        className="pr-btn pr-btn--bad"
                        onClick={() => answer({ grade: 0, was_correct: false })}
                    >
                        <Icon.X /> {ru ? 'Не знаю' : 'Bilmayman'}
                    </button>
                    <button
                        className="pr-btn pr-btn--good"
                        onClick={() => answer({ grade: 2, was_correct: true })}
                    >
                        <Icon.Check /> {ru ? 'Знаю' : 'Bilaman'}
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
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const [picked, setPicked] = useState(null);
    const timer = useRef(null);
    useEffect(() => { setPicked(null); }, [word.id]);
    // Leaving mid-answer must not fire onAnswer into the next screen.
    useEffect(() => () => clearTimeout(timer.current), []);

    // Decide direction once per word. Meaning-side MCQ needs a real context
    // AND at least one extra distractor to be a fair test.
    const ctxOpts = Array.isArray(word.context_options) ? word.context_options : [];
    const meaningMode =
        Boolean((word.context || '').trim()) &&
        ctxOpts.filter(o => (o || '').trim()).length >= 2;

    const prompt = meaningMode
        ? (ru ? 'Какое значение у этого слова?' : "Bu so'zning ma'nosi qaysi?")
        : (ru ? 'Какое слово подходит к этому значению?' : "Bu ma'noga qaysi so'z mos keladi?");

    const center = meaningMode
        ? <span className="pr-quiz-word">{word.word}</span>
        : (word.context_masked || word.context || <em>{ru ? 'Контекста нет — выберите примерно' : "Kontekst yo'q — taxminan tanlang"}</em>);

    const opts = meaningMode ? ctxOpts : (word.options || []);
    // ctxOpts are already masked server-side (see practice_words.py
    // _mask_word_in_text) so the option text can't be matched by literally
    // spotting the target word inside it — compare against the masked
    // value, not the raw context, or the "correct" option would never
    // equal-match its own (masked) rendered text.
    const correctValue = meaningMode ? word.context_masked : word.word;

    const pick = (opt) => {
        if (picked !== null) return;
        const correct = opt === correctValue;
        setPicked(opt);
        timer.current = setTimeout(() => onAnswer({
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
function TypedAnswer({ word, request, onAnswer, promptLabel, showContext, header, strict = false }) {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const [value, setValue] = useState('');
    const [verdict, setVerdict] = useState(null);
    const [judging, setJudging] = useState(false);
    const inputRef = useRef(null);
    const timers = useRef([]);
    const later = (fn, ms) => { timers.current.push(setTimeout(fn, ms)); };
    useEffect(() => () => { timers.current.forEach(clearTimeout); }, []);

    useEffect(() => {
        setValue('');
        setVerdict(null);
        setJudging(false);
        later(() => inputRef.current?.focus(), 60);
    }, [word.id]); // eslint-disable-line react-hooks/exhaustive-deps

    const submit = async (e) => {
        e?.preventDefault?.();
        if (verdict || judging) return;
        setJudging(true);
        const v = await judgeTypedAsync(request, value, word.word, word.context, strict);
        setVerdict(v);
        setJudging(false);
        const grade = v.exact ? 2 : v.ok ? 1 : 0;
        later(() => onAnswer({ grade, was_correct: v.ok }), 900);
    };

    return (
        <>
            {header}
            {promptLabel && <div className="pr-typed-hint">{promptLabel}</div>}
            {showContext && (
                <div className="pr-typed-ctx">
                    {/* Masked — this is a recall prompt (guess the word from its
                        meaning), so the word itself must not appear in the text
                        the student is shown before they answer. */}
                    {word.context_masked || word.context || <em>{ru ? 'Контекста нет' : "Kontekst yo'q"}</em>}
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
                    placeholder={ru ? 'Напишите слово…' : "So'zni yozing…"}
                    className={`pr-typed-input ${verdict ? (verdict.ok ? 'ok' : 'bad') : ''}`}
                    disabled={!!verdict || judging}
                />
                <button
                    type="submit"
                    className="pr-btn pr-btn--primary"
                    disabled={!!verdict || judging || !value.trim()}
                >
                    {judging ? (ru ? 'Проверка…' : 'Tekshirilmoqda…') : (ru ? 'Проверить' : 'Tekshirish')}
                </button>
            </form>
            {verdict && (
                <div className={`pr-typed-feedback ${verdict.ok ? (verdict.exact ? 'ok' : 'close') : 'bad'}`}>
                    {verdict.ok && verdict.exact && <><Icon.Check /> {ru ? 'Верно!' : "To'g'ri!"}</>}
                    {verdict.ok && !verdict.exact && (
                        <>
                            <Icon.Warn /> {ru ? 'Близко — правильно:' : "Yaqin — to'g'risi:"} <strong>{word.word}</strong>
                            {verdict.aiUsed && <span className="pr-ai-tag"><Icon.Sparkle /> AI</span>}
                        </>
                    )}
                    {!verdict.ok && <><Icon.X /> {ru ? 'Правильно:' : "To'g'risi:"} <strong>{word.word}</strong></>}
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
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const isSpelling = qpPass === 'spelling';
    return (
        <div className="pr-card pr-quiz">
            <div className="pr-quiz-modeline pr-quiz-modeline--locked">
                <span className={`pr-sub ${!isSpelling ? 'active' : ''}`}>
                    {ru ? '1. Узнавание (MCQ)' : '1. Tanish (MCQ)'}
                </span>
                <span className={`pr-sub ${isSpelling ? 'active' : ''}`}>
                    {ru ? '2. Запоминание (Письмо)' : '2. Eslab qolish (Yozish)'}
                </span>
            </div>
            {isSpelling
                ? <TypedAnswer
                    word={word}
                    request={request}
                    onAnswer={onAnswer}
                    promptLabel={ru ? 'Напишите слово — вы видели его в первом раунде' : "So'zni yozing — birinchi raundda ko'rdingiz"}
                    showContext
                />
                : <MCQ word={word} onAnswer={onAnswer} />
            }
        </div>
    );
}


export function SpellingMode({ word, onAnswer, request }) {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    return (
        <div className="pr-card pr-typed">
            <TypedAnswer
                word={word}
                request={request}
                onAnswer={onAnswer}
                promptLabel={ru ? 'Значение:' : "Ma'no:"}
                showContext
            />
        </div>
    );
}


export function ListeningMode({ word, onAnswer, request }) {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
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
                strict
                promptLabel={ru ? 'Напишите то, что услышали' : 'Eshitganingizni yozing'}
                header={
                    <button type="button" className="pr-listen-btn" onClick={speak} title={ru ? 'Прослушать снова' : 'Qayta eshitish'}>
                        <Icon.Volume /> <span>{ru ? 'Прослушать' : 'Eshitish'}</span>
                    </button>
                }
            />
        </div>
    );
}


/* Blank every occurrence of `word` in `ctx`, including the Uzbek forms that
   carry a suffix ("JavaScript'da", "funksiyalar"). Unicode-aware: a plain \b
   is ASCII-only, so Cyrillic words and words like "C++" were never found. */
export function blankWord(ctx, word) {
    const w = (word || '').trim();
    if (!ctx || !w) return null;
    const esc = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const apos = "['’ʻʼ`]";
    const tail = w.length >= 4 ? `(?:${apos}\\p{L}*|\\p{L}*)` : `(?:${apos}\\p{L}*)?`;
    const re = new RegExp(`(^|[^\\p{L}\\p{N}_])${esc}${tail}(?![\\p{L}\\p{N}_])`, 'giu');
    if (!re.test(ctx)) return null;
    re.lastIndex = 0;
    return ctx.replace(re, '$1_____');
}


export function ClozeMode({ word, onAnswer, request }) {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const blanked = useMemo(() => blankWord(word.context, word.word), [word]);
    // Not found in the sentence: fall back to the masked definition (recall
    // prompt), which still tests the word — and only if there is no text at
    // all can the card be skipped, which records nothing.
    const fallback = !blanked && (word.context_masked || '').trim();

    if (!blanked && !fallback) {
        return (
            <div className="pr-card pr-typed">
                <div className="pr-typed-hint">
                    {ru ? 'Для этого слова нет сохранённого контекста предложения.' : "Bu so'z uchun gap kontekstida saqlanmagan."}
                </div>
                <div className="pr-typed-ctx">«{word.word}»</div>
                <button
                    className="pr-btn pr-btn--primary"
                    onClick={() => onAnswer({ skip: true, was_correct: true })}
                >
                    {ru ? 'Пропустить' : "O'tkazib yuborish"}
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
                promptLabel={blanked
                    ? (ru ? 'Заполните пропуск:' : "Bo'shliqni to'ldiring:")
                    : (ru ? 'Значение:' : "Ma'no:")}
                header={<div className="pr-cloze-ctx">{blanked || fallback}</div>}
            />
        </div>
    );
}
