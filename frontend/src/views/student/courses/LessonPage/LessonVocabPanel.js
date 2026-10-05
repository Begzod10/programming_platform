import { useEffect, useState, useCallback } from 'react';
import ReactDOM from 'react-dom';
import { API_URL, useHttp, headers } from '../../../../api/search/base';
import { useTranslation } from '../../../../i18n/useTranslation';
import './LessonVocabPanel.css';

/**
 * Always-open lesson vocabulary panel for the left gutter (wide screens).
 * Replaces the old floating drawer button: the words a student saved while
 * reading THIS lesson are shown right next to the content, live-updating when
 * a new word is added via the in-text selection popup (`dict:word-added`).
 * Rendered via a portal so it's viewport-fixed regardless of the lesson's
 * scroll container; hidden under 1400px where there's no gutter.
 */
export default function LessonVocabPanel({ lessonId, ru }) {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const [words, setWords] = useState([]);
    const [loaded, setLoaded] = useState(false);

    const fetchWords = useCallback(() => {
        request(`${API_URL}v1/dictionary/?lang=${lang || 'uz'}`, 'GET', null, headers())
            .then(d => setWords(Array.isArray(d) ? d : []))
            .catch(() => setWords([]))
            .finally(() => setLoaded(true));
    }, [request, lang]);

    useEffect(() => { fetchWords(); }, [fetchWords]);

    // Live refresh when a word is saved from the in-text selection popup.
    useEffect(() => {
        const onAdded = () => fetchWords();
        window.addEventListener('dict:word-added', onAdded);
        return () => window.removeEventListener('dict:word-added', onAdded);
    }, [fetchWords]);

    const lessonWords = words.filter(w => w.lesson_id === lessonId);

    return ReactDOM.createPortal(
        <aside className="lvp-panel" aria-label={ru ? 'Словарь урока' : "Dars lug'ati"}>
            <div className="lvp-head">
                <span className="lvp-head-ico">📖</span>
                <div className="lvp-head-txt">
                    <div className="lvp-title">{ru ? 'Словарь урока' : "Dars lug'ati"}</div>
                    <div className="lvp-sub">
                        {lessonWords.length} {ru ? 'слов' : "so'z"}
                    </div>
                </div>
            </div>

            <div className="lvp-body">
                {!loaded ? (
                    <div className="lvp-skel">
                        {[0, 1, 2].map(i => <div key={i} className="lvp-skel-row" />)}
                    </div>
                ) : lessonWords.length === 0 ? (
                    <div className="lvp-empty">
                        <span className="lvp-empty-ico">✍️</span>
                        <p>{ru
                            ? 'Выделите текст в уроке и нажмите «Добавить в словарь», чтобы собрать слова здесь.'
                            : "Darsdagi matnni belgilab, «Lug'atga qo'shish» tugmasini bosing — so'zlar shu yerda to'planadi."}</p>
                    </div>
                ) : (
                    <ul className="lvp-list">
                        {lessonWords.map(w => (
                            <li key={w.id} className="lvp-item">
                                <span className="lvp-word">{w.word}</span>
                                {w.context && <span className="lvp-ctx">{w.context}</span>}
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            {lessonWords.length > 0 && (
                <button type="button" className="lvp-cta" onClick={() => { window.location.href = '/student/dictionary'; }}>
                    🎯 {ru ? 'Тренировать слова' : "So'zlarni mashq qilish"}
                </button>
            )}
        </aside>,
        document.body
    );
}
