import React, { useMemo, useState } from 'react';
import './ArithmeticActivity.css';
import './WordChartActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { starsForWrongCount, WRONG_FLASH_MS, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

const CORRECT_PULSE_MS = 700;

function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}

/** Shuffle so the word never comes out already solved (a 1-letter-different
 * scramble is fine, the identical one is not). */
function scramble(word) {
    const letters = word.split('');
    if (new Set(letters).size < 2) return letters;
    let out = shuffle(letters);
    let guard = 0;
    while (out.join('') === word && guard++ < 10) out = shuffle(letters);
    return out;
}

/** Build the word from scrambled letters. activity.content shape (mode:
 * "wordbuild"): { character: {emoji,label}, rounds_count: 5,
 * words: [{emoji, uz, ru}] } — words are authored (real vocabulary can't be
 * generated). Tap the next correct letter; a wrong tap counts a mistake.
 * Scoring reuses starsForWrongCount, styles reuse ArithmeticActivity.css. */
export default function WordBuildActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const roundsCount = content.rounds_count || 5;

    const rounds = useMemo(() => {
        const pool = (content.words || []).filter((w) => w && (w.uz || w.ru));
        return shuffle(pool).slice(0, roundsCount);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activity.id, activity.content]);

    const [roundIndex, setRoundIndex] = useState(0);
    const [placed, setPlaced] = useState(0); // letters of the current word already placed
    const [used, setUsed] = useState([]); // tile indexes already used
    const [wrongCount, setWrongCount] = useState(0);
    const [flashTile, setFlashTile] = useState(null);
    const [locked, setLocked] = useState(false);
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const entry = rounds[roundIndex];
    const word = entry ? String(lang === 'ru' && entry.ru ? entry.ru : entry.uz || entry.ru).toUpperCase() : '';
    const tiles = useMemo(() => scramble(word), [word, roundIndex]); // eslint-disable-line react-hooks/exhaustive-deps

    const tap = (idx) => {
        if (celebration !== null || submitting || locked || used.includes(idx)) return;
        if (tiles[idx] === word[placed]) {
            playSynth('chime');
            const nextUsed = [...used, idx];
            setUsed(nextUsed);
            const nextPlaced = placed + 1;
            setPlaced(nextPlaced);
            if (nextPlaced === word.length) {
                setLocked(true);
                setTimeout(() => {
                    setLocked(false);
                    setUsed([]);
                    setPlaced(0);
                    if (roundIndex + 1 < rounds.length) {
                        setRoundIndex((i) => i + 1);
                    } else {
                        playSynth('fanfare');
                        setCelebration(starsForWrongCount(wrongCount));
                    }
                }, CORRECT_PULSE_MS);
            }
        } else {
            playSynth('laser');
            setWrongCount((c) => c + 1);
            const token = Date.now();
            setFlashTile({ token, idx });
            setTimeout(() => setFlashTile((f) => (f?.token === token ? null : f)), WRONG_FLASH_MS);
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

    if (!entry) return null;

    return (
        <div className="aa-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="aa-character-header">
                <span className="aa-character-emoji">{character.emoji || '🔤'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {activity.instruction_text && <p className="aa-instruction">{activity.instruction_text}</p>}

            <div className="wc-picture">{entry.emoji}</div>

            <div className="wc-slots">
                {word.split('').map((ch, i) => (
                    <span key={i} className={`wc-slot ${i < placed ? 'is-filled' : ''}`}>{i < placed ? ch : ''}</span>
                ))}
            </div>

            <div className="wc-tiles">
                {tiles.map((ch, i) => (
                    <button
                        key={`${roundIndex}-${i}`}
                        className={`wc-tile ${used.includes(i) ? 'is-used' : ''} ${flashTile?.idx === i ? 'is-wrong' : ''}`}
                        onClick={() => tap(i)}
                        disabled={submitting || locked || used.includes(i)}
                    >
                        {ch}
                    </button>
                ))}
            </div>

            <div className="aa-progress">{roundIndex + 1} / {rounds.length}</div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
