import React, { useEffect, useMemo, useState } from 'react';
import './WordChartActivity.css';
import ActivityShell, { useActivityCompletion } from './ActivityShell';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount } from './earlyLearningUtils';

const MAX_LIVES = 6;
const UZ_KEYS = 'ABDEFGHIJKLMNOPQRSTUVXYZ'.split('');
const RU_KEYS = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'.split('');

/** Guess the word letter by letter. activity.content (mode: "hangman"):
 * { rounds_count?: 4, words: [{emoji, uz, ru}] }. The emoji is the hint. Six
 * wrong letters lose the word (it's revealed and the game moves on); stars
 * come from the total of wrong letters across the game. */
export default function HangmanActivity(props) {
    const { activity, guest, onComplete, lang } = props;
    const content = activity.content || {};
    const completion = useActivityCompletion(activity, guest, onComplete);

    const words = useMemo(
        () => shuffle((content.words || []).filter((w) => w && (w.uz || w.ru))).slice(0, content.rounds_count || 4),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [activity.id, activity.content]
    );

    const [idx, setIdx] = useState(0);
    const [guessed, setGuessed] = useState([]);
    const [wrongLetters, setWrongLetters] = useState(0); // this word
    const [totalWrong, setTotalWrong] = useState(0);
    const [revealed, setRevealed] = useState(false);

    const entry = words[idx];
    const word = entry ? String((lang === 'ru' && entry.ru ? entry.ru : entry.uz || entry.ru)).toUpperCase() : '';
    const keys = /[А-ЯЁ]/.test(word) ? RU_KEYS : UZ_KEYS;
    const solved = word && word.split('').every((ch) => guessed.includes(ch));
    const lost = wrongLetters >= MAX_LIVES;

    const next = () => {
        setGuessed([]);
        setWrongLetters(0);
        setRevealed(false);
        if (idx + 1 < words.length) setIdx((i) => i + 1);
        else { playSynth('fanfare'); completion.finish(starsForWrongCount(Math.floor(totalWrong / 2))); }
    };

    const guess = (ch) => {
        if (completion.celebration !== null || solved || lost || guessed.includes(ch)) return;
        const nextGuessed = [...guessed, ch];
        setGuessed(nextGuessed);
        if (word.includes(ch)) {
            playSynth('chime');
            if (word.split('').every((c) => nextGuessed.includes(c))) setTimeout(next, 900);
        } else {
            playSynth('laser');
            setTotalWrong((n) => n + 1);
            const w = wrongLetters + 1;
            setWrongLetters(w);
            if (w >= MAX_LIVES) {
                setRevealed(true);
                setTimeout(next, 1800);
            }
        }
    };

    // Physical keyboard: typing a letter is the same as tapping its key.
    useEffect(() => {
        const onKey = (e) => {
            if (e.ctrlKey || e.metaKey || e.altKey || e.key.length !== 1) return;
            const ch = e.key.toUpperCase();
            if (keys.includes(ch)) guess(ch);
        };
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    });

    if (!entry) return null;

    return (
        <ActivityShell {...props} emoji="🔤" completion={completion}>
            <div className="wc-picture">{entry.emoji}</div>
            <div className="wc-lives">{'❤️'.repeat(MAX_LIVES - wrongLetters)}{'🖤'.repeat(wrongLetters)}</div>
            <div className="wc-slots">
                {word.split('').map((ch, i) => {
                    const shown = guessed.includes(ch) || revealed;
                    return (
                        <span key={i} className={`wc-slot ${shown ? 'is-filled' : ''} ${revealed && !guessed.includes(ch) ? 'is-missed' : ''}`}>
                            {shown ? ch : ''}
                        </span>
                    );
                })}
            </div>
            <div className="wc-keys">
                {keys.map((ch) => {
                    const used = guessed.includes(ch);
                    const hit = used && word.includes(ch);
                    return (
                        <button
                            key={ch}
                            className={`wc-key ${used ? (hit ? 'is-hit' : 'is-miss') : ''}`}
                            disabled={used || solved || lost || completion.submitting}
                            onClick={() => guess(ch)}
                        >
                            {ch}
                        </button>
                    );
                })}
            </div>
            <div className="aa-progress">{idx + 1} / {words.length}</div>
        </ActivityShell>
    );
}
