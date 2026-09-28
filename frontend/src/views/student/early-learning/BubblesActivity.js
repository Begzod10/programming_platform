import React, { useMemo, useState } from 'react';
import './WordChartActivity.css';
import ActivityShell, { useActivityCompletion } from './ActivityShell';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount } from './earlyLearningUtils';

const rnd = (lo, hi) => Math.floor(Math.random() * (hi - lo + 1)) + lo;
const COLORS = ['#ff8787', '#ffd43b', '#69db7c', '#74c0fc', '#da77f2', '#ffa94d', '#63e6be'];
const LETTERS = 'ABDEFGHIJKLMNOPQRSTUVXYZ'.split('');

/** One round: a target and 7 bubbles, 1-2 of which match it. Every bubble has
 * its own `key` and `ok` flag so the same label appearing twice is fine. */
function makeRound(kind, max) {
    let target;
    let make;
    if (kind === 'letters') {
        target = LETTERS[rnd(0, LETTERS.length - 1)];
        make = () => LETTERS[rnd(0, LETTERS.length - 1)];
    } else if (kind === 'sums') {
        target = rnd(6, max);
        make = () => {
            const a = rnd(1, target - 1);
            return { label: `${a}+${target - a}`, ok: true };
        };
    } else {
        target = rnd(1, max);
        make = () => rnd(1, max);
    }
    const okCount = rnd(1, 2);
    const bubbles = [];
    for (let i = 0; i < okCount; i++) {
        bubbles.push(kind === 'sums' ? make() : { label: String(target), ok: true });
    }
    while (bubbles.length < 7) {
        if (kind === 'sums') {
            const a = rnd(1, max - 1);
            const b = rnd(1, max - 1);
            if (a + b !== target) bubbles.push({ label: `${a}+${b}`, ok: false });
        } else {
            const v = String(make());
            if (v !== String(target)) bubbles.push({ label: v, ok: false });
        }
    }
    return {
        target: kind === 'sums' ? `= ${target}` : String(target),
        okCount,
        bubbles: shuffle(bubbles).map((b, i) => ({
            ...b, key: i, color: COLORS[i % COLORS.length],
            left: 6 + ((i * 13 + rnd(0, 6)) % 78), delay: -rnd(0, 60) / 10, dur: 7 + rnd(0, 30) / 10,
        })),
    };
}

/** Pop the bubbles that match the target. activity.content (mode: "bubbles"):
 * { kind: "numbers"|"letters"|"sums", max?: 10, rounds_count?: 6 }. A wrong bubble
 * counts a mistake; popping every matching bubble advances the round. */
export default function BubblesActivity(props) {
    const { activity, guest, onComplete, lang } = props;
    const content = activity.content || {};
    const kind = content.kind || 'numbers';
    const roundsCount = content.rounds_count || 6;
    const completion = useActivityCompletion(activity, guest, onComplete);

    const rounds = useMemo(
        () => Array.from({ length: roundsCount }, () => makeRound(kind, content.max || 10)),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [activity.id, activity.content]
    );
    const [idx, setIdx] = useState(0);
    const [popped, setPopped] = useState([]); // bubble keys gone this round
    const [wrongCount, setWrongCount] = useState(0);
    const [shake, setShake] = useState(null);
    const round = rounds[idx];

    const pop = (b) => {
        if (completion.celebration !== null || popped.includes(b.key)) return;
        if (!b.ok) {
            playSynth('laser');
            setWrongCount((c) => c + 1);
            setShake(b.key);
            setTimeout(() => setShake(null), 400);
            return;
        }
        playSynth('coin');
        const next = [...popped, b.key];
        setPopped(next);
        const left = round.bubbles.filter((x) => x.ok && !next.includes(x.key)).length;
        if (left === 0) {
            setTimeout(() => {
                setPopped([]);
                if (idx + 1 < rounds.length) setIdx((i) => i + 1);
                else { playSynth('fanfare'); completion.finish(starsForWrongCount(wrongCount)); }
            }, 350);
        }
    };

    if (!round) return null;
    const label = lang === 'ru' ? 'Лопни' : "Yorib chiq";

    return (
        <ActivityShell {...props} emoji="🫧" completion={completion}>
            <div className="wc-bubble-target">{label}: <b>{round.target}</b></div>
            <div className="wc-sky">
                {round.bubbles.map((b) => !popped.includes(b.key) && (
                    <button
                        key={`${idx}-${b.key}`}
                        className={`wc-bubble ${shake === b.key ? 'is-wrong' : ''}`}
                        style={{ left: `${b.left}%`, background: b.color, animationDelay: `${b.delay}s`, animationDuration: `${b.dur}s` }}
                        onClick={() => pop(b)}
                    >
                        {b.label}
                    </button>
                ))}
            </div>
            <div className="aa-progress">{idx + 1} / {rounds.length}</div>
        </ActivityShell>
    );
}
