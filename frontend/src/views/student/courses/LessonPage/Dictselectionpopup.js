/**
 * DictSelectionPopup
 * ──────────────────
 * Подключается ОДИН РАЗ в StudentLessonPage.
 * Слушает mouseup/touchend — если выделен текст внутри .slp-container,
 * показывает всплывающую кнопку "📖 Lug'atga qo'shish".
 * При нажатии сразу сохраняет слово через API и диспатчит dict:word-added.
 *
 * Props:
 *   lessonId  — number (текущий урок, пишем в lesson_id)
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { API_URL, useHttp, headers } from '../../../../api/search/base';
import './Dictselectionpopup.css';

const BASE = `${API_URL}v1/dictionary/`;

export default function DictSelectionPopup({ lessonId }) {
    const { request } = useHttp();
    const [popup,   setPopup]   = useState(null); // null | { x, y, word, context, done, saving, error }
    const btnRef                = useRef(null);

    const hide = useCallback(() => setPopup(null), []);

    useEffect(() => {
        const onSelection = () => {
            requestAnimationFrame(() => {
                const sel  = window.getSelection();
                const word = sel?.toString().trim();

                if (!word || word.length < 2 || word.length > 80) { hide(); return; }

                const anchor = sel.anchorNode?.parentElement;
                if (!anchor?.closest('.slp-container')) { hide(); return; }

                const range = sel.getRangeAt(0);
                const rect  = range.getBoundingClientRect();

                // Контекст — предложение из ближайшего блока
                let ctx = '';
                const block = anchor.closest(
                    '.slp-text-content, .slp-ex-question, .slp-ex-fill-text, .slp-project-desc'
                );
                if (block) {
                    const sentences = (block.innerText || '').split(/[.!?]/);
                    const found = sentences.find(s => s.toLowerCase().includes(word.toLowerCase()));
                    ctx = found ? found.trim().substring(0, 120) : '';
                }

                setPopup({
                    x:       rect.left + rect.width / 2 + window.scrollX,
                    y:       rect.top  + window.scrollY - 10,
                    word,
                    context: ctx,
                    done:    false,
                    saving:  false,
                    error:   false,
                });
            });
        };

        const onMouseDown = (e) => {
            if (btnRef.current && btnRef.current.contains(e.target)) return;
            hide();
        };

        document.addEventListener('mouseup',   onSelection);
        document.addEventListener('touchend',  onSelection);
        document.addEventListener('mousedown', onMouseDown);
        return () => {
            document.removeEventListener('mouseup',   onSelection);
            document.removeEventListener('touchend',  onSelection);
            document.removeEventListener('mousedown', onMouseDown);
        };
    }, [hide]);

    const handleAdd = async () => {
        if (!popup || popup.saving || popup.done) return;

        // Снимаем выделение сразу
        window.getSelection()?.removeAllRanges();

        setPopup(p => ({ ...p, saving: true, error: false }));

        try {
            await request(BASE, 'POST', JSON.stringify({
                word:      popup.word,
                context:   popup.context || '',
                lesson_id: lessonId || null,
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

    return (
        <div
            ref={btnRef}
            className={`dsp-popup ${popup.done ? 'done' : ''} ${popup.error ? 'error' : ''}`}
            style={{ left: popup.x, top: popup.y }}
        >
            {popup.done ? (
                <span className="dsp-done">✓ Qo'shildi!</span>
            ) : popup.error ? (
                <span className="dsp-err">⚠ Xatolik</span>
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
                            : '📖 Lug\'atga qo\'shish'
                        }
                    </button>
                </>
            )}
            <div className="dsp-arrow" />
        </div>
    );
}