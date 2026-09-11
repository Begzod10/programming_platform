import React, { useEffect, useRef, useState } from 'react';
import './TypingActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

const CORRECT_PULSE_MS = 500;

const DEFAULT_WORDS = ['salom', 'olma', 'kitob', 'uy', 'mushuk', 'it', 'gul', 'osmon'];

/** MonkeyType-style "type the word" round. activity.content shape (mode:
 * "typing"): { character: {emoji,label}, words: ["olma","kitob",...] } —
 * words are shuffled once per play, one word = one round. Each keystroke is
 * compared live against the target: the word above the input colors green
 * per correctly-typed letter and red at the first mismatch, same instant
 * feedback as monkeytype.com. A wrong letter counts once per round (fixing
 * a typo via backspace doesn't add more), scored with the same
 * starsForWrongCount every sibling activity uses. */
export default function TypingActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const words = content.words?.length ? content.words : DEFAULT_WORDS;

    const roundsRef = useRef(shuffle(words));
    const rounds = roundsRef.current;

    const [roundIndex, setRoundIndex] = useState(0);
    const [typed, setTyped] = useState('');
    const [mistakeThisRound, setMistakeThisRound] = useState(false);
    const [wrongCount, setWrongCount] = useState(0);
    const [locked, setLocked] = useState(false);
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const inputRef = useRef(null);

    const target = (rounds[roundIndex] || '').toLowerCase();

    useEffect(() => {
        setTyped('');
        setMistakeThisRound(false);
        inputRef.current?.focus();
    }, [roundIndex]);

    const handleChange = (e) => {
        if (locked || celebration !== null || submitting) return;
        const v = e.target.value.toLowerCase();
        if (v.length > target.length) return; // target reached, ignore overtyping
        setTyped(v);

        const lastIdx = v.length - 1;
        if (lastIdx >= 0 && v[lastIdx] !== target[lastIdx] && !mistakeThisRound) {
            setMistakeThisRound(true);
            setWrongCount((c) => c + 1);
            playSynth('laser');
        }

        if (v === target) {
            playSynth('chime');
            setLocked(true);
            setTimeout(() => {
                setLocked(false);
                if (roundIndex + 1 < rounds.length) {
                    setRoundIndex((i) => i + 1);
                } else {
                    playSynth('fanfare');
                    setCelebration(starsForWrongCount(wrongCount));
                }
            }, CORRECT_PULSE_MS);
        }
    };

    const handleCelebrationDone = () => {
        const stars = celebration;
        if (guest) {
            onComplete(recordGuestCompletion(activity.id, stars));
            return;
        }
        setSubmitting(true);
        request(`${API_URL}v1/early-learning/activities/${activity.id}/complete`, 'POST', { stars }, headers())
            .then((result) => onComplete(result))
            .catch((err) => {
                console.error(err);
                onComplete({ stars_earned: stars, attempts: 1 });
            })
            .finally(() => setSubmitting(false));
    };

    if (!target) return null;

    return (
        <div className="ty-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="ty-character-header">
                <span className="ty-character-emoji">{character.emoji || '⌨️'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {activity.instruction_text && <p className="ty-instruction">{activity.instruction_text}</p>}

            <div className={`ty-word ${mistakeThisRound ? 'ty-word-has-mistake' : ''}`}>
                {target.split('').map((ch, i) => {
                    let cls = 'ty-char-pending';
                    if (i < typed.length) {
                        cls = typed[i] === ch ? 'ty-char-correct' : 'ty-char-wrong';
                    } else if (i === typed.length) {
                        cls = 'ty-char-caret';
                    }
                    return <span key={i} className={cls}>{ch}</span>;
                })}
            </div>

            <input
                ref={inputRef}
                className="ty-input"
                type="text"
                value={typed}
                onChange={handleChange}
                disabled={submitting || locked}
                autoComplete="off"
                autoCorrect="off"
                autoCapitalize="off"
                spellCheck={false}
                placeholder={t('el.type_here') || 'Yozing...'}
            />

            <div className="ty-progress">{roundIndex + 1} / {rounds.length}</div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
