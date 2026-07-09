import React, { useState, useEffect } from 'react';
import { API_URL, useHttp, headers } from '../../../../api/search/base';
import { useTranslation } from '../../../../i18n/useTranslation';

/* ═══════════════════════════════════════════════════════════
   LESSON FEEDBACK — 1-5 star rating + optional comment
═══════════════════════════════════════════════════════════ */
export const LessonFeedbackWidget = ({lessonId}) => {
    const {request} = useHttp();
    const { lang } = useTranslation();
    const [rating, setRating] = useState(0);
    const [hover, setHover] = useState(0);
    const [comment, setComment] = useState('');
    const [saving, setSaving] = useState(false);
    const [savedAt, setSavedAt] = useState(null);
    const [error, setError] = useState('');
    const [loaded, setLoaded] = useState(false);

    // Prefill from any previous submission so the student sees their last score.
    useEffect(() => {
        if (!lessonId) return;
        let cancelled = false;
        (async () => {
            try {
                const res = await request(
                    `${API_URL}v1/lessons/${lessonId}/feedback/my`,
                    'GET',
                    null,
                    headers(),
                );
                if (cancelled) return;
                if (res && typeof res.rating === 'number') {
                    setRating(res.rating);
                    setComment(res.comment || '');
                    if (res.updated_at) setSavedAt(res.updated_at);
                }
            } catch {
                // 401 / network — silently skip; widget still usable.
            } finally {
                if (!cancelled) setLoaded(true);
            }
        })();
        return () => { cancelled = true; };
    }, [lessonId, request]);

    // Reset state when navigating between lessons so we don't reuse stale UI.
    useEffect(() => {
        setRating(0);
        setHover(0);
        setComment('');
        setSavedAt(null);
        setError('');
        setLoaded(false);
    }, [lessonId]);

    const display = hover || rating;
    const isRu = lang === 'ru';
    const labels = isRu
        ? ['', 'Нужно улучшить', 'Слабо', 'Средне', 'Хорошо', 'Отлично']
        : ['', 'Yaxshilash kerak', 'Sust', 'O\'rtacha', 'Yaxshi', 'Ajoyib'];

    const handleSubmit = async () => {
        if (!rating) {
            setError(isRu ? 'Выберите оценку (1-5 звёзд)' : 'Bahoni tanlang (1-5 yulduz)');
            return;
        }
        setSaving(true);
        setError('');
        try {
            const res = await request(
                `${API_URL}v1/lessons/${lessonId}/feedback`,
                'POST',
                JSON.stringify({rating, comment: comment.trim() || null}),
                headers(),
            );
            setSavedAt(res?.updated_at || new Date().toISOString());
        } catch (e) {
            setError(isRu ? 'Не удалось отправить. Попробуйте позже.' : 'Yuborib bo\'lmadi. Birozdan keyin urinib ko\'ring.');
        } finally {
            setSaving(false);
        }
    };

    // Once the student has submitted feedback for this lesson, lock the widget
    // into a read-only "thank you" state. We capture the first rating only —
    // re-rating would dilute the teacher's analytics signal.
    if (savedAt) {
        return (
            <div className="slp-feedback slp-feedback--done">
                <div className="slp-feedback-head">
                    <div className="slp-feedback-icon" aria-hidden="true">✅</div>
                    <div>
                        <h3 className="slp-feedback-title">{isRu ? 'Спасибо — ваша оценка принята!' : 'Rahmat — bahoyingiz qabul qilindi!'}</h3>
                        <p className="slp-feedback-sub">
                            {isRu ? 'Ваш отзыв помогает улучшать уроки.' : 'Sizning fikr-mulohazangiz darslarni yaxshilashga yordam beradi.'}
                        </p>
                    </div>
                </div>

                <div className="slp-feedback-stars slp-feedback-stars--readonly" aria-label={`Sizning bahoyingiz: ${rating} yulduz`}>
                    {[1, 2, 3, 4, 5].map(n => (
                        <span key={n} className={`slp-feedback-star is-static ${n <= rating ? 'is-on' : ''}`} aria-hidden="true">★</span>
                    ))}
                    <span className="slp-feedback-star-label">{labels[rating]}</span>
                </div>

                {comment && (
                    <div className="slp-feedback-saved-comment">
                        <span className="slp-feedback-quote" aria-hidden="true">"</span>
                        {comment}
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="slp-feedback">
            <div className="slp-feedback-head">
                <div className="slp-feedback-icon" aria-hidden="true">💬</div>
                <div>
                    <h3 className="slp-feedback-title">{isRu ? 'Насколько полезен этот урок?' : 'Bu dars qanchalik foydali bo\'ldi?'}</h3>
                    <p className="slp-feedback-sub">
                        {isRu ? 'Ваша оценка и комментарий помогут улучшить следующие уроки.' : 'Bahoyingiz va izohingiz keyingi darslarni yaxshilashga yordam beradi.'}
                    </p>
                </div>
            </div>

            <div className="slp-feedback-stars" role="radiogroup" aria-label="Dars bahosi">
                {[1, 2, 3, 4, 5].map(n => (
                    <button
                        key={n}
                        type="button"
                        role="radio"
                        aria-checked={rating === n}
                        aria-label={`${n} yulduz`}
                        className={`slp-feedback-star ${n <= display ? 'is-on' : ''}`}
                        onMouseEnter={() => setHover(n)}
                        onMouseLeave={() => setHover(0)}
                        onFocus={() => setHover(n)}
                        onBlur={() => setHover(0)}
                        onClick={() => { setRating(n); setError(''); }}
                        disabled={!loaded || saving}
                    >
                        ★
                    </button>
                ))}
                <span className="slp-feedback-star-label">
                    {display ? labels[display] : (isRu ? 'Выберите оценку' : 'Yulduz tanlang')}
                </span>
            </div>

            <textarea
                className="slp-feedback-comment"
                placeholder={isRu ? 'Необязательно: что понравилось, что было сложно, что добавить?' : 'Ixtiyoriy: nima yoqdi, nima qiyin bo\'ldi, nimani qo\'shish kerak?'}
                value={comment}
                onChange={e => setComment(e.target.value)}
                maxLength={2000}
                rows={3}
                disabled={!loaded || saving}
            />

            <div className="slp-feedback-actions">
                <button
                    type="button"
                    className="slp-feedback-submit"
                    onClick={handleSubmit}
                    disabled={!loaded || saving || !rating}
                >
                    {saving ? (isRu ? 'Отправка...' : 'Yuborilmoqda...') : (isRu ? 'Отправить' : 'Yuborish')}
                </button>
                {error && <span className="slp-feedback-error">{error}</span>}
            </div>
        </div>
    );
};
