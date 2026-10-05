import { useEffect, useRef, useState } from 'react';
import ReactDOM from 'react-dom';
import './LessonCompanion.css';

const TYPE_ICON = {
    text: '📝', code: '💻', video: '🎬', image: '🖼',
    file: '📦', exercise: '🎯', project: '🚀',
};

/**
 * Lesson companion rail — a live reading aid that fills the otherwise-empty
 * right gutter on wide screens. It gives the lesson a real sense of place:
 *  • a reading-progress ring driven by the actual scroll position,
 *  • an auto table-of-contents (scroll-spy) built from the lesson's sections,
 *    that highlights the section you're currently reading and lets you jump,
 *  • course position (lesson N / M) and a quick vocab-review shortcut.
 * The scroll container is the full-bleed `.slp-page` (position:fixed; overflow),
 * so all measurements are taken against that element rather than `window`.
 */
export default function LessonCompanion({ lesson, currentIndex, allLessons, isDone, ru }) {
    const sections = lesson?.sections || [];
    const [activeId, setActiveId] = useState(null);
    const [progress, setProgress] = useState(0);
    const rafRef = useRef(0);

    useEffect(() => {
        const scroller = document.querySelector('.slp-page');
        if (!scroller) return;

        const measure = () => {
            const max = scroller.scrollHeight - scroller.clientHeight;
            setProgress(max > 10 ? Math.min(100, Math.max(0, Math.round((scroller.scrollTop / max) * 100))) : 0);

            const blocks = Array.from(scroller.querySelectorAll('[data-section-id]'));
            const anchor = scroller.getBoundingClientRect().top + scroller.clientHeight * 0.3;
            let current = null;
            for (const b of blocks) {
                if (b.getBoundingClientRect().top <= anchor) current = b.getAttribute('data-section-id');
            }
            setActiveId(current);
        };

        const onScroll = () => {
            cancelAnimationFrame(rafRef.current);
            rafRef.current = requestAnimationFrame(measure);
        };

        measure();
        scroller.addEventListener('scroll', onScroll, { passive: true });
        window.addEventListener('resize', onScroll);
        return () => {
            cancelAnimationFrame(rafRef.current);
            scroller.removeEventListener('scroll', onScroll);
            window.removeEventListener('resize', onScroll);
        };
    }, [lesson?.id]);

    const jump = (id) => {
        const el = document.querySelector(`[data-section-id="${id}"]`);
        if (!el) return;
        // scrollIntoView works no matter which ancestor is the scroll container;
        // scroll-margin-top on .slp-block (CSS) keeps the sticky top bar clear.
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    const total = allLessons?.length || 0;

    // Rendered into <body> via a portal: the lesson's scroll container
    // (.slp-page / .slp-container) establishes a containing block that would
    // otherwise capture position:fixed and make the rail scroll away. In the
    // body it is truly viewport-fixed and stays put while the lesson scrolls.
    return ReactDOM.createPortal(
        <aside className="slp-companion" aria-label={ru ? 'Спутник урока' : 'Dars hamrohi'}>
            {/* reading progress */}
            <div className="slp-cmp-head">
                <div className="slp-cmp-ring" style={{ '--p': progress }}>
                    <span>{progress}%</span>
                </div>
                <div className="slp-cmp-head-txt">
                    <div className="slp-cmp-title">{ru ? 'Прочитано' : "O'qilgan"}</div>
                    <div className="slp-cmp-sub">
                        {ru ? 'Урок' : 'Dars'} {currentIndex + 1}{total ? ` / ${total}` : ''}
                        {isDone && <span className="slp-cmp-done">✓</span>}
                    </div>
                </div>
            </div>

            {/* auto table of contents (scroll-spy) */}
            {sections.length > 0 && (
                <nav className="slp-cmp-toc">
                    <div className="slp-cmp-toc-title">{ru ? 'Содержание' : 'Mundarija'}</div>
                    <div className="slp-cmp-toc-list">
                        {sections.map((s, i) => (
                            <button key={s.id}
                                className={`slp-cmp-item ${activeId === String(s.id) ? 'is-active' : ''}`}
                                onClick={() => jump(s.id)}>
                                <span className="slp-cmp-ico">{TYPE_ICON[s.type] || '•'}</span>
                                <span className="slp-cmp-label">
                                    {s.label || (ru ? `Раздел ${i + 1}` : `${i + 1}-bo'lim`)}
                                </span>
                            </button>
                        ))}
                    </div>
                </nav>
            )}

            <button type="button" className="slp-cmp-cta" onClick={() => { window.location.href = '/student/dictionary'; }}>
                📖 {ru ? 'Повторить слова' : "So'zlarni takrorlash"}
            </button>
        </aside>,
        document.body
    );
}
