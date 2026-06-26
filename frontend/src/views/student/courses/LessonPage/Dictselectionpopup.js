/**
 * DictSelectionPopup
 * ──────────────────
 * Подключается ОДИН РАЗ в StudentLessonPage.
 * Слушает mouseup/touchend — если выделен текст внутри .slp-container,
 * показывает всплывающую кнопку с иконкой книги + "Lug'atga qo'shish".
 * При нажатии сразу сохраняет слово через API и диспатчит dict:word-added.
 *
 * Props:
 *   lessonId  — number (текущий урок, пишем в lesson_id)
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { API_URL, useHttp, headers } from '../../../../api/search/base';
import './Dictselectionpopup.css';

// Inline SVG icons — emojis render as missing-glyph boxes on some
// Linux/Windows systems without a color emoji font installed.
const BookIcon = (props) => (
    <svg viewBox="0 0 24 24" width="14" height="14" fill="none"
         stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
    </svg>
);
const CheckIcon = (props) => (
    <svg viewBox="0 0 24 24" width="14" height="14" fill="none"
         stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <polyline points="20 6 9 17 4 12" />
    </svg>
);
const WarnIcon = (props) => (
    <svg viewBox="0 0 24 24" width="14" height="14" fill="none"
         stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
        <line x1="12" y1="9" x2="12" y2="13" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
);

const BASE = `${API_URL}v1/dictionary/`;

export default function DictSelectionPopup({ lessonId }) {
    const { request } = useHttp();
    const [popup,   setPopup]   = useState(null); // null | { x, y, word, context, done, saving, error }
    const btnRef                = useRef(null);

    const hide = useCallback(() => setPopup(null), []);

    useEffect(() => {
        // Walk up from a text/element node to the nearest Element so .closest()
        // can run. anchorNode is usually a Text node; older browsers may also
        // hand back null inside shadow / iframe boundaries.
        const elementFor = (node) => {
            if (!node) return null;
            return node.nodeType === 1 ? node : node.parentElement;
        };

        const evaluate = () => {
            const sel = window.getSelection();
            if (!sel || sel.rangeCount === 0 || sel.isCollapsed) {
                // Don't tear down the popup on a transient collapse — the user
                // may have just clicked the button itself. The mousedown handler
                // owns hide() for the click-outside case.
                return;
            }

            // Strip outer whitespace + trailing punctuation that mouse cursors
            // commonly pick up at sentence edges.
            const raw  = sel.toString().trim();
            const word = raw.replace(/^[.,!?;:•·«»"'()\[\]{}—–-]+|[.,!?;:•·«»"'()\[\]{}—–-]+$/g, '').trim();

            if (!word || word.length < 2) { hide(); return; }

            // Dictionary entries are meant to be a word or a short phrase,
            // not a whole sentence. Limits mirror the backend exactly
            // (DictionaryCreate.word: max 80 chars + 6 words).
            const tooLong  = word.length > 80;
            const tooManyWords = word.split(/\s+/).length > 6;

            const anchor = elementFor(sel.anchorNode);
            const focus  = elementFor(sel.focusNode);
            // Either endpoint inside the lesson container is enough — selections
            // that start in a code block and end in body text shouldn't be lost.
            const inLesson =
                anchor?.closest('.slp-container') ||
                focus?.closest('.slp-container');
            if (!inLesson) { hide(); return; }

            const range = sel.getRangeAt(0);
            const rect  = range.getBoundingClientRect();
            // Browsers occasionally return a 0×0 rect for collapsed/intra-token
            // selections in styled <pre> blocks; bail rather than render a
            // floating popup at (0, 0).
            if (rect.width === 0 && rect.height === 0) { hide(); return; }

            // Context — pull the sentence around the selected word from the
            // nearest narrative block. Code blocks intentionally don't match;
            // their text is rarely useful as a dictionary gloss.
            let ctx = '';
            const block = (anchor || focus)?.closest(
                '.slp-text-content, .slp-ex-question, .slp-ex-fill-text, .slp-project-desc'
            );
            if (block) {
                const sentences = (block.innerText || '').split(/[.!?]/);
                const found = sentences.find(s => s.toLowerCase().includes(word.toLowerCase()));
                ctx = found ? found.trim().substring(0, 120) : '';
            }

            // Viewport coordinates — paired with `position: fixed` on the
            // popup. Avoids picking up offsets from positioned ancestors
            // (the lesson wrapper, modal overlays, transformed parents).
            setPopup({
                x:       rect.left + rect.width / 2,
                y:       rect.top  - 10,
                word,
                context: ctx,
                done:    false,
                saving:  false,
                error:   false,
                invalid: tooLong || tooManyWords,
                invalidReason: tooLong
                    ? "Juda uzun (80 belgigacha)"
                    : tooManyWords
                        ? "Faqat 1-6 ta so'z"
                        : null,
            });
        };

        // `selectionchange` is the authoritative signal — it fires whenever the
        // selection actually updates, regardless of how (mouseup, dblclick word
        // selection, keyboard shift-arrow, touch handles). Debounced by RAF so
        // we don't thrash during drag-extend.
        let raf = 0;
        const onSelectionChange = () => {
            if (raf) cancelAnimationFrame(raf);
            raf = requestAnimationFrame(() => { raf = 0; evaluate(); });
        };

        const onMouseDown = (e) => {
            if (btnRef.current && btnRef.current.contains(e.target)) return;
            hide();
        };

        // With `position: fixed`, scrolling would leave the popup floating
        // over the wrong content. Re-anchor by re-evaluating from the live
        // selection rect (rather than hiding outright, so the user can
        // still scroll a tiny bit without losing the popup).
        const onScroll = () => onSelectionChange();

        document.addEventListener('selectionchange', onSelectionChange);
        document.addEventListener('mousedown',       onMouseDown);
        window.addEventListener('scroll', onScroll, { passive: true, capture: true });
        return () => {
            if (raf) cancelAnimationFrame(raf);
            document.removeEventListener('selectionchange', onSelectionChange);
            document.removeEventListener('mousedown',       onMouseDown);
            window.removeEventListener('scroll', onScroll, { capture: true });
        };
    }, [hide]);

    const handleAdd = async () => {
        if (!popup || popup.saving || popup.done || popup.invalid) return;

        // Снимаем выделение сразу
        window.getSelection()?.removeAllRanges();

        setPopup(p => ({ ...p, saving: true, error: false }));

        try {
            await request(BASE, 'POST', JSON.stringify({
                word:      popup.word,
                context:   popup.context || '',
                lesson_id: lessonId || null,
                lang:      localStorage.getItem('lang') || 'uz',
            }), headers());

            // Уведомляем Dictionary чтобы перезагрузил список
            window.dispatchEvent(new CustomEvent('dict:word-added'));

            setPopup(p => p ? { ...p, done: true, saving: false } : null);
            setTimeout(hide, 1400);
        } catch {
            setPopup(p => p ? { ...p, saving: false, error: true } : null);
            setTimeout(() => setPopup(p => p ? { ...p, error: false } : null), 2000);
        }
    };

    if (!popup) return null;

    // Render into document.body so `position: fixed` is anchored to the
    // viewport, NOT to any positioned/transformed ancestor of where this
    // component happens to be mounted. CSS spec: a `transform`, `filter`,
    // `perspective`, or `will-change: transform` on an ancestor turns that
    // ancestor into the containing block for fixed-positioned descendants
    // — so the popup would drift to the corner of that ancestor instead
    // of sitting next to the selection. Lesson pages have mermaid SVGs and
    // card-entry animations that trigger this; portaling sidesteps all of
    // it.
    const node = (
        <div
            ref={btnRef}
            className={`dsp-popup ${popup.done ? 'done' : ''} ${popup.error ? 'error' : ''} ${popup.invalid ? 'invalid' : ''}`}
            style={{ left: popup.x, top: popup.y }}
        >
            {popup.done ? (
                <span className="dsp-done"><CheckIcon /> Qo'shildi!</span>
            ) : popup.error ? (
                <span className="dsp-err"><WarnIcon /> Xatolik</span>
            ) : popup.invalid ? (
                <span className="dsp-invalid">
                    <WarnIcon /> {popup.invalidReason}
                </span>
            ) : (
                <>
                    <span className="dsp-word">«{popup.word}»</span>
                    <button
                        className="dsp-btn"
                        onClick={handleAdd}
                        disabled={popup.saving}
                    >
                        {popup.saving
                            ? <span className="dsp-spin" />
                            : <><BookIcon /> Lug'atga qo'shish</>
                        }
                    </button>
                </>
            )}
            <div className="dsp-arrow" />
        </div>
    );

    return createPortal(node, document.body);
}