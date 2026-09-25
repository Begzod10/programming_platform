import React, { useMemo, useState } from 'react';
import './WordChartActivity.css';
import ActivityShell, { useActivityCompletion } from './ActivityShell';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle } from './earlyLearningUtils';

const SCENES = [
    ['☀️', '☁️', '🐦', '🌳', '🏠', '🌳', '🌱', '🐕', '🌷'],
    ['⭐', '🌙', '⭐', '🌲', '⛺', '🌲', '🔥', '🐻', '🌿'],
    ['🌈', '☁️', '☀️', '🐄', '🚜', '🐑', '🌾', '🌻', '🌾'],
    ['☁️', '✈️', '☁️', '🏔️', '🏔️', '🏔️', '🌲', '🚂', '🌲'],
];

function scrambled(target) {
    let order = shuffle(target.map((_, i) => i));
    let guard = 0;
    while (order.every((v, i) => target[v] === target[i]) && guard++ < 20) order = shuffle(order);
    return order;
}

/** Rebuild the picture: tap two tiles to swap them until the 3x3 scene matches
 * the small preview. activity.content (mode: "puzzle"): { scenes?: [[9 emoji]] }.
 * Stars by number of swaps. */
export default function PicturePuzzleActivity(props) {
    const { activity, guest, onComplete, lang } = props;
    const completion = useActivityCompletion(activity, guest, onComplete);
    const target = useMemo(() => {
        const list = (activity.content || {}).scenes || SCENES;
        return list[Math.floor(Math.random() * list.length)];
    }, [activity.id, activity.content]); // eslint-disable-line react-hooks/exhaustive-deps
    const [order, setOrder] = useState(() => scrambled(target)); // order[pos] = index into target
    const [sel, setSel] = useState(null);
    const [swaps, setSwaps] = useState(0);

    const isRight = (pos) => target[order[pos]] === target[pos];

    const tap = (pos) => {
        if (completion.celebration !== null) return;
        if (sel === null) { setSel(pos); return; }
        if (sel === pos) { setSel(null); return; }
        const next = [...order];
        [next[sel], next[pos]] = [next[pos], next[sel]];
        setOrder(next);
        setSel(null);
        setSwaps((s) => s + 1);
        playSynth('chime');
        if (next.every((v, p) => target[v] === target[p])) {
            playSynth('fanfare');
            const total = swaps + 1;
            completion.finish(total <= 8 ? 3 : total <= 14 ? 2 : 1);
        }
    };

    return (
        <ActivityShell {...props} emoji="🧩" completion={completion}>
            <div className="wc-preview">
                {target.map((e, i) => <span key={i}>{e}</span>)}
            </div>
            <div className="wc-bubble-target">{lang === 'ru' ? 'Ходов' : 'Almashtirish'}: <b>{swaps}</b></div>
            <div className="wc-puzzle">
                {order.map((idx, pos) => (
                    <button
                        key={pos}
                        className={`wc-piece ${sel === pos ? 'is-sel' : ''} ${isRight(pos) ? 'is-right' : ''}`}
                        onClick={() => tap(pos)}
                    >
                        {target[idx]}
                    </button>
                ))}
            </div>
        </ActivityShell>
    );
}
