import React, { useEffect, useRef, useState } from 'react';
import './TraceActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { starsForCoverage } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

// Logical canvas resolution — CSS scales the element visually (see
// TraceActivity.css's .ta-canvas-wrap), pointer coordinates are converted
// back into this space via getBoundingClientRect() in toCanvasPoint, so the
// mapping stays correct at any on-screen size. No devicePixelRatio
// supersampling in this first pass — see the feature plan's known
// limitations.
const CANVAS_SIZE = 300;
// How many points along a shape's own outline count as "did the kid trace
// this part". Same total across shapes so the coverage-percent threshold
// in starsForCoverage means the same thing for a circle as a triangle.
const CHECKPOINT_COUNT = 36;
// How close (px, in canvas space) a drawn point must land to a checkpoint
// to count it as traced — forgiving on purpose, see the plan's "coverage
// only, no stay-inside-the-lines penalty" rationale.
const HIT_RADIUS = 22;
// A checkpoint only counts once a SINGLE stroke sweeps past it *and* its
// immediate neighbors in order — see creditableCheckpointsForStroke below.
// Without this, "coverage" could be earned by dabbing 36 disconnected taps
// around the outline instead of actually tracing it; this is the fix for
// that gap. MAX_JUMP tolerates normal hand jitter/backtracking between two
// checkpoints hit right after each other in the same stroke (checkpoints
// are close together — a real continuous drag naturally lands on the same
// or a neighboring one from one recorded point to the next); MIN_RUN
// is the shortest connected sweep that earns any credit at all — small
// enough that drawing one side of a square still easily qualifies (~9
// checkpoints), large enough that a single tap (a run of 1) never does.
const MAX_JUMP = 3;
const MIN_RUN_CHECKPOINTS = 3;
const INK_COLOR = '#f97316';
const GUIDE_COLOR = 'rgba(100, 116, 139, 0.5)';

function pointsOnCircle(cx, cy, r, n) {
    return Array.from({ length: n }, (_, i) => {
        const a = (i / n) * Math.PI * 2;
        return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
    });
}

/** Evenly-spaced checkpoints around a closed polygon, distributed by each
 * edge's share of the total perimeter — so a longer edge gets proportionally
 * more checkpoints than a short one, rather than a flat count-per-edge. */
function pointsOnPolygon(vertices, n) {
    const edges = vertices.map((v, i) => {
        const next = vertices[(i + 1) % vertices.length];
        return { a: v, b: next, len: Math.hypot(next.x - v.x, next.y - v.y) };
    });
    const totalLen = edges.reduce((s, e) => s + e.len, 0);
    const points = [];
    edges.forEach((e) => {
        const count = Math.max(1, Math.round((e.len / totalLen) * n));
        for (let i = 0; i < count; i++) {
            const t = i / count;
            points.push({ x: e.a.x + (e.b.x - e.a.x) * t, y: e.a.y + (e.b.y - e.a.y) * t });
        }
    });
    return points;
}

/** Which checkpoints a single stroke (one pointerdown-to-pointerup path)
 * actually earns credit for. A checkpoint is only credited when it's part
 * of a *connected* run — the stroke passed near it and near its immediate
 * neighbors in outline order, right after one another — not just touched
 * in isolation at some point during the stroke. This is what makes a
 * "sweep along the outline" score well while a series of disconnected taps
 * around the shape doesn't, without requiring the stroke to be perfectly
 * smooth or go in one fixed direction (small back-and-forth jitter within
 * MAX_JUMP is tolerated, checkpoint order is cyclic since the shape is a
 * closed loop). Multiple separate strokes are still expected and fine —
 * e.g. drawing a square's 4 sides one at a time — each stroke is scored
 * independently and their credited checkpoints are just unioned together.
 */
function creditableCheckpointsForStroke(strokePoints, checkpoints) {
    const n = checkpoints.length;
    if (n === 0) return [];

    // Nearest checkpoint (within HIT_RADIUS) for each recorded point, in
    // temporal order; -1 where the point isn't near any checkpoint.
    const touched = strokePoints.map((p) => {
        let best = -1;
        let bestDist = HIT_RADIUS;
        checkpoints.forEach((cp, i) => {
            const d = Math.hypot(p.x - cp.x, p.y - cp.y);
            if (d <= bestDist) { bestDist = d; best = i; }
        });
        return best;
    });

    // Collapse to the sequence of checkpoints actually visited, dropping
    // misses and consecutive repeats of the same checkpoint.
    const seq = [];
    for (const idx of touched) {
        if (idx === -1) continue;
        if (seq.length === 0 || seq[seq.length - 1] !== idx) seq.push(idx);
    }
    if (seq.length === 0) return [];

    const cyclicDist = (a, b) => { const d = Math.abs(a - b); return Math.min(d, n - d); };

    // Split into runs wherever consecutive visited checkpoints are too far
    // apart to be "the same continuous sweep" (a lift-and-reposition, or a
    // jump across the shape rather than along it).
    const runs = [[seq[0]]];
    for (let i = 1; i < seq.length; i++) {
        const run = runs[runs.length - 1];
        if (cyclicDist(run[run.length - 1], seq[i]) <= MAX_JUMP) {
            run.push(seq[i]);
        } else {
            runs.push([seq[i]]);
        }
    }

    return runs
        .filter((run) => new Set(run).size >= MIN_RUN_CHECKPOINTS)
        .flat();
}

const SQUARE_VERTICES = [{ x: 70, y: 70 }, { x: 230, y: 70 }, { x: 230, y: 230 }, { x: 70, y: 230 }];
const TRIANGLE_VERTICES = [{ x: 150, y: 55 }, { x: 235, y: 225 }, { x: 65, y: 225 }];
// Wider than tall (190x100) — visually distinct from the square, same
// footprint scale as the other shapes.
const RECTANGLE_VERTICES = [{ x: 55, y: 100 }, { x: 245, y: 100 }, { x: 245, y: 200 }, { x: 55, y: 200 }];
// 5-pointed star, 10 vertices alternating outer radius 100 / inner radius 45
// around (150,150), starting at the top and stepping every 36°.
const STAR_VERTICES = [
    { x: 150, y: 50 }, { x: 176, y: 114 }, { x: 245, y: 119 }, { x: 193, y: 164 }, { x: 209, y: 231 },
    { x: 150, y: 195 }, { x: 91, y: 231 }, { x: 107, y: 164 }, { x: 55, y: 119 }, { x: 124, y: 114 },
];

/** `shape` → {draw, checkpoints}. content only ever names a shape id
 * ("circle"/"square"/"triangle") — no hand-authored path data — the
 * geometry lives here, same "small registry keyed by a content string"
 * pattern as BuildActivity.js's SCENES. */
const SHAPES = {
    circle: {
        draw: (ctx) => { ctx.beginPath(); ctx.arc(150, 150, 100, 0, Math.PI * 2); ctx.stroke(); },
        checkpoints: () => pointsOnCircle(150, 150, 100, CHECKPOINT_COUNT),
    },
    square: {
        draw: (ctx) => { ctx.beginPath(); ctx.rect(70, 70, 160, 160); ctx.stroke(); },
        checkpoints: () => pointsOnPolygon(SQUARE_VERTICES, CHECKPOINT_COUNT),
    },
    triangle: {
        draw: (ctx) => {
            ctx.beginPath();
            ctx.moveTo(TRIANGLE_VERTICES[0].x, TRIANGLE_VERTICES[0].y);
            ctx.lineTo(TRIANGLE_VERTICES[1].x, TRIANGLE_VERTICES[1].y);
            ctx.lineTo(TRIANGLE_VERTICES[2].x, TRIANGLE_VERTICES[2].y);
            ctx.closePath();
            ctx.stroke();
        },
        checkpoints: () => pointsOnPolygon(TRIANGLE_VERTICES, CHECKPOINT_COUNT),
    },
    star: {
        draw: (ctx) => {
            ctx.beginPath();
            STAR_VERTICES.forEach((v, i) => {
                if (i === 0) ctx.moveTo(v.x, v.y); else ctx.lineTo(v.x, v.y);
            });
            ctx.closePath();
            ctx.stroke();
        },
        checkpoints: () => pointsOnPolygon(STAR_VERTICES, CHECKPOINT_COUNT),
    },
    rectangle: {
        draw: (ctx) => { ctx.beginPath(); ctx.rect(55, 100, 190, 100); ctx.stroke(); },
        checkpoints: () => pointsOnPolygon(RECTANGLE_VERTICES, CHECKPOINT_COUNT),
    },
};

/** One "trace each shape's outline" round. activity.content shape (mode:
 * "trace"): { character: {emoji,label}, targets: [{id,shape,label,label_ru}] }.
 * Third sibling of MatchingActivity.js/BuildActivity.js — same completion
 * flow, different input: freehand pointer drawing on a canvas, scored by
 * how much of the guide outline actually got swept by a continuous stroke
 * (see creditableCheckpointsForStroke) — forgiving on precision (HIT_RADIUS
 * is generous, no pixel-perfect path matching) but not on requiring real
 * tracing: a checkpoint only counts as part of a connected run within one
 * stroke, so dabbing disconnected taps around the outline instead of
 * actually drawing it doesn't score.
 */
export default function TraceActivity({ activity, onBack, onComplete, lang, toggleLang, t }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const targets = content.targets || [];

    const [targetIndex, setTargetIndex] = useState(0);
    const [coveragePct, setCoveragePct] = useState(0);
    const [coverageResults, setCoverageResults] = useState([]);
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const guideCanvasRef = useRef(null);
    const inkCanvasRef = useRef(null);
    // Drawn points and checkpoint-hit flags live in refs, not state — a
    // stroke can generate dozens of pointermove events per second, and
    // none of that needs to trigger a React re-render; only coveragePct
    // (updated once per stroke, on pointerup) does. strokePointsRef holds
    // only the CURRENT in-progress stroke (reset on every pointerdown) —
    // past strokes' results are already folded into hitFlagsRef by then,
    // see creditableCheckpointsForStroke's docstring for why scoring works
    // per-stroke rather than against the full accumulated point history.
    const strokePointsRef = useRef([]);
    const checkpointsRef = useRef([]);
    const hitFlagsRef = useRef([]);
    const drawingRef = useRef(false);

    const target = targets[targetIndex];
    const shapeDef = target && SHAPES[target.shape];

    // (Re)draw the dashed guide and reset drawing state for the current
    // target. Only depends on which target we're on — activity.id changing
    // means a whole new mount anyway (EarlyLearning.js unmounts this
    // component between separate play sessions).
    useEffect(() => {
        if (!shapeDef) return;
        const guide = guideCanvasRef.current;
        const ink = inkCanvasRef.current;
        if (!guide || !ink) return;

        const gctx = guide.getContext('2d');
        gctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
        gctx.setLineDash([10, 8]);
        gctx.lineWidth = 10;
        gctx.lineCap = 'round';
        gctx.lineJoin = 'round';
        gctx.strokeStyle = GUIDE_COLOR;
        shapeDef.draw(gctx);

        ink.getContext('2d').clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

        checkpointsRef.current = shapeDef.checkpoints();
        hitFlagsRef.current = checkpointsRef.current.map(() => false);
        strokePointsRef.current = [];
        setCoveragePct(0);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [targetIndex]);

    const toCanvasPoint = (e) => {
        const rect = inkCanvasRef.current.getBoundingClientRect();
        return {
            x: ((e.clientX - rect.left) / rect.width) * CANVAS_SIZE,
            y: ((e.clientY - rect.top) / rect.height) * CANVAS_SIZE,
        };
    };

    const coveragePctFromFlags = () => {
        const flags = hitFlagsRef.current;
        const hitCount = flags.filter(Boolean).length;
        return flags.length ? hitCount / flags.length : 0;
    };

    // Scores the just-finished stroke on its own (see
    // creditableCheckpointsForStroke) and folds any newly-earned
    // checkpoints into the running total.
    const creditFinishedStroke = () => {
        const earned = creditableCheckpointsForStroke(strokePointsRef.current, checkpointsRef.current);
        for (const i of earned) hitFlagsRef.current[i] = true;
        const pct = coveragePctFromFlags();
        setCoveragePct(pct);
        return pct;
    };

    const handlePointerDown = (e) => {
        if (celebration !== null || submitting) return;
        e.preventDefault();
        const canvas = inkCanvasRef.current;
        // Best-effort — a rare input/browser combo could reject capture
        // (no active pointer session for this id); the drag just wouldn't
        // survive straying off-canvas in that case, but drawing still
        // works, which matters more than crashing the whole interaction.
        try { canvas.setPointerCapture(e.pointerId); } catch { /* not capturable */ }
        drawingRef.current = true;
        const p = toCanvasPoint(e);
        strokePointsRef.current = [p];
        const ctx = canvas.getContext('2d');
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.lineWidth = 14;
        ctx.strokeStyle = INK_COLOR;
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
    };

    const handlePointerMove = (e) => {
        if (!drawingRef.current) return;
        const p = toCanvasPoint(e);
        strokePointsRef.current.push(p);
        const ctx = inkCanvasRef.current.getContext('2d');
        ctx.lineTo(p.x, p.y);
        ctx.stroke();
    };

    const handlePointerUp = (e) => {
        if (!drawingRef.current) return;
        drawingRef.current = false;
        try { inkCanvasRef.current.releasePointerCapture(e.pointerId); } catch { /* already released */ }
        creditFinishedStroke();
    };

    const handleClear = () => {
        inkCanvasRef.current.getContext('2d').clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
        strokePointsRef.current = [];
        hitFlagsRef.current = checkpointsRef.current.map(() => false);
        setCoveragePct(0);
    };

    const handleDone = () => {
        const finalPct = coveragePctFromFlags();
        playSynth(finalPct >= 0.55 ? 'chime' : 'laser');
        const results = [...coverageResults, finalPct];
        if (targetIndex + 1 < targets.length) {
            setCoverageResults(results);
            setTargetIndex((i) => i + 1);
        } else {
            playSynth('fanfare');
            const avg = results.reduce((s, v) => s + v, 0) / results.length;
            setCoverageResults(results);
            setCelebration(starsForCoverage(avg));
        }
    };

    const handleCelebrationDone = () => {
        const stars = celebration;
        setSubmitting(true);
        request(`${API_URL}v1/early-learning/activities/${activity.id}/complete`, 'POST', { stars }, headers())
            .then((result) => onComplete(result))
            .catch((err) => {
                console.error(err);
                // Still let the child close the round locally — losing the
                // star-save on a flaky request shouldn't trap the kid here.
                onComplete({ stars_earned: stars, attempts: 1 });
            })
            .finally(() => setSubmitting(false));
    };

    if (!target) return null;

    return (
        <div className="ta-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="ta-character">
                <span className="ta-character-emoji">{character.emoji || '✏️'}</span>
                <h2>{character.label || activity.title}</h2>
                <span className="ta-progress-badge">{targetIndex + 1} / {targets.length}</span>
            </div>

            {activity.instruction_text && <p className="ta-instruction">{activity.instruction_text}</p>}
            <div className="ta-target-label">{target.label}</div>

            <div className="ta-canvas-wrap">
                <canvas ref={guideCanvasRef} className="ta-canvas ta-canvas-guide" width={CANVAS_SIZE} height={CANVAS_SIZE} />
                <canvas
                    ref={inkCanvasRef}
                    className="ta-canvas ta-canvas-ink"
                    width={CANVAS_SIZE}
                    height={CANVAS_SIZE}
                    onPointerDown={handlePointerDown}
                    onPointerMove={handlePointerMove}
                    onPointerUp={handlePointerUp}
                />
            </div>

            <div className="ta-coverage-row">
                <div className="ta-coverage-bar">
                    <div className="ta-coverage-fill" style={{ width: `${Math.round(coveragePct * 100)}%` }} />
                </div>
                <span className="ta-coverage-pct">{Math.round(coveragePct * 100)}%</span>
            </div>

            <div className="ta-controls">
                <button className="ta-btn ta-btn-clear" onClick={handleClear} disabled={submitting}>{t('el.traceClear')}</button>
                <button className="ta-btn ta-btn-done" onClick={handleDone} disabled={submitting}>{t('el.traceDone')}</button>
            </div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
