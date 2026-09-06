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

const SQUARE_VERTICES = [{ x: 70, y: 70 }, { x: 230, y: 70 }, { x: 230, y: 230 }, { x: 70, y: 230 }];
const TRIANGLE_VERTICES = [{ x: 150, y: 55 }, { x: 235, y: 225 }, { x: 65, y: 225 }];

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
};

/** One "trace each shape's outline" round. activity.content shape (mode:
 * "trace"): { character: {emoji,label}, targets: [{id,shape,label,label_ru}] }.
 * Third sibling of MatchingActivity.js/BuildActivity.js — same completion
 * flow, different input: freehand pointer drawing on a canvas, scored by
 * how much of the guide outline's own checkpoints got traced near enough
 * (see HIT_RADIUS), not pixel-perfect path matching.
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
    // (updated once per stroke, on pointerup) does.
    const pointsRef = useRef([]);
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
        pointsRef.current = [];
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

    const recomputeCoverage = () => {
        const pts = pointsRef.current;
        const flags = hitFlagsRef.current;
        checkpointsRef.current.forEach((cp, i) => {
            if (flags[i]) return;
            for (const p of pts) {
                if (Math.hypot(p.x - cp.x, p.y - cp.y) <= HIT_RADIUS) {
                    flags[i] = true;
                    break;
                }
            }
        });
        const hitCount = flags.filter(Boolean).length;
        const pct = flags.length ? hitCount / flags.length : 0;
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
        pointsRef.current.push(p);
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
        pointsRef.current.push(p);
        const ctx = inkCanvasRef.current.getContext('2d');
        ctx.lineTo(p.x, p.y);
        ctx.stroke();
    };

    const handlePointerUp = (e) => {
        if (!drawingRef.current) return;
        drawingRef.current = false;
        try { inkCanvasRef.current.releasePointerCapture(e.pointerId); } catch { /* already released */ }
        recomputeCoverage();
    };

    const handleClear = () => {
        inkCanvasRef.current.getContext('2d').clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
        pointsRef.current = [];
        hitFlagsRef.current = checkpointsRef.current.map(() => false);
        setCoveragePct(0);
    };

    const handleDone = () => {
        const finalPct = recomputeCoverage();
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
