/* Pre-drill UI panels — BucketsBar, LeechAlert, HistoryStrip, QueuePreview, ScopePicker. */

import { MODES, Icon } from './practiceUtils';

export function BucketsBar({ buckets }) {
    const total = Object.values(buckets).reduce((a, b) => a + b, 0);
    if (total === 0) return null;
    const cfg = [
        { key: 'fragile',  label: 'Qiyin',     color: '#f43f5e' },
        { key: 'learning', label: "O'rganish", color: '#6c5ce7' },
        { key: 'solid',    label: 'Mustahkam', color: '#10b981' },
        { key: 'mastered', label: 'O\'zlashtirilgan', color: '#0d9488' },
    ];
    return (
        <div className="pr-buckets">
            <div className="pr-buckets-bar">
                {cfg.map((b) => {
                    const n = buckets[b.key] || 0;
                    if (n === 0) return null;
                    const pct = (n / total) * 100;
                    return (
                        <div
                            key={b.key}
                            className="pr-buckets-seg"
                            style={{ width: `${pct}%`, background: b.color }}
                            title={`${b.label}: ${n}`}
                        />
                    );
                })}
            </div>
            <div className="pr-buckets-legend">
                {cfg.map((b) => (
                    <div key={b.key} className="pr-buckets-lg">
                        <span className="pr-buckets-dot" style={{ background: b.color }} />
                        <span>{b.label}</span>
                        <strong>{buckets[b.key] || 0}</strong>
                    </div>
                ))}
            </div>
        </div>
    );
}

export function LeechAlert({ leeches }) {
    if (!leeches.length) return null;
    return (
        <div className="pr-leech">
            <div className="pr-leech-head">
                <Icon.Skull />
                <span>Ko'p marta unutgan so'zlar ({leeches.length})</span>
            </div>
            <div className="pr-leech-list">
                {leeches.slice(0, 5).map((w) => (
                    <div key={w.id} className="pr-leech-row">
                        <strong>{w.word}</strong>
                        <span className="pr-leech-meta">
                            {w.lapses}× unutilgan
                        </span>
                    </div>
                ))}
            </div>
            <p className="pr-leech-hint">
                Bu so'zlarni qayta yozib chiqing yoki tushuntirishni o'zgartiring — eski yondashuv ishlamayapti.
            </p>
        </div>
    );
}

export function HistoryStrip({ history }) {
    if (!history.length) return null;
    return (
        <div className="pr-history">
            <div className="pr-history-label">So'nggi mashqlar</div>
            <div className="pr-history-rows">
                {history.slice(0, 5).map((s) => {
                    const pct = s.total_words > 0
                        ? Math.round((s.correct / s.total_words) * 100)
                        : 0;
                    return (
                        <div key={s.id} className="pr-history-row">
                            <div className="pr-history-mode">
                                {MODES.find(m => m.key === s.mode)?.icon}
                                {' '}
                                {MODES.find(m => m.key === s.mode)?.label || s.mode}
                            </div>
                            <div className="pr-history-score">
                                {s.correct}/{s.total_words}
                            </div>
                            <div
                                className={`pr-history-pct ${pct >= 80 ? 'ok' : pct >= 50 ? 'mid' : 'bad'}`}
                            >{pct}%</div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export function QueuePreview({ words }) {
    if (!words.length) return null;
    return (
        <div className="pr-queue">
            <div className="pr-queue-label">Navbatdagi so'zlar (birinchi 5 ta)</div>
            <div className="pr-queue-list">
                {words.slice(0, 5).map((w) => {
                    let tag = 'Yangi';
                    let tagCls = 'new';
                    if ((w.review_count || 0) > 0) {
                        if ((w.lapses || 0) >= 2 || (w.ease_factor || 2.5) < 2.0) {
                            tag = 'Qiyin'; tagCls = 'weak';
                        } else if ((w.interval_days || 0) > 21) {
                            tag = "O'zlashtirilgan"; tagCls = 'master';
                        } else if ((w.interval_days || 0) > 7) {
                            tag = 'Mustahkam'; tagCls = 'solid';
                        } else {
                            tag = "O'rganish"; tagCls = 'learn';
                        }
                    }
                    return (
                        <div key={w.id} className="pr-queue-row">
                            <strong className="pr-queue-word">{w.word}</strong>
                            <span className={`pr-queue-tag pr-queue-tag--${tagCls}`}>{tag}</span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}


/* ═══════════════════════════════════════════════════════════════════════
   SCOPE PICKER — category/course/lesson narrowing
   Mirrors life_tracker's folder/module ScopePicker using the
   category → course → lesson chain that already lives on the words.
   ═══════════════════════════════════════════════════════════════════════ */

export function ScopePicker({ tree, scope, onChange }) {
    if (!tree.length) return null;

    // Flatten the tree into select options for the two dropdowns. A more
    // elaborate tree-control would be overkill for the 1-3 courses most
    // students have words in.
    const allCourses = tree.flatMap((cat) => cat.courses);
    const activeCourse = allCourses.find((c) => c.id === scope.course_id);

    return (
        <section className="pr-section">
            <h3 className="pr-section-title">Doira (ixtiyoriy)</h3>
            <div className="pr-scope">
                <label className="pr-scope-field">
                    <span className="pr-scope-lbl">Kurs</span>
                    <select
                        className="pr-scope-select"
                        value={scope.course_id || ''}
                        onChange={(e) => {
                            const v = e.target.value;
                            onChange({
                                category_id: null,
                                course_id: v ? Number(v) : null,
                                lesson_id: null,
                            });
                        }}
                    >
                        <option value="">Barchasi</option>
                        {allCourses.map((c) => (
                            <option key={c.id} value={c.id}>{c.title}</option>
                        ))}
                    </select>
                </label>
                <label className="pr-scope-field">
                    <span className="pr-scope-lbl">Dars</span>
                    <select
                        className="pr-scope-select"
                        value={scope.lesson_id || ''}
                        onChange={(e) => {
                            const v = e.target.value;
                            onChange({
                                ...scope,
                                lesson_id: v ? Number(v) : null,
                            });
                        }}
                        disabled={!activeCourse}
                    >
                        <option value="">
                            {activeCourse ? 'Barcha darslar' : 'Avval kursni tanlang'}
                        </option>
                        {(activeCourse?.lessons || []).map((l) => (
                            <option key={l.id} value={l.id}>{l.title}</option>
                        ))}
                    </select>
                </label>
                {(scope.course_id || scope.lesson_id) && (
                    <button
                        type="button"
                        className="pr-scope-clear"
                        onClick={() => onChange({ category_id: null, course_id: null, lesson_id: null })}
                    >Tozalash</button>
                )}
            </div>
        </section>
    );
}
