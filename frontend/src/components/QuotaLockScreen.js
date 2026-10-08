// Shown on the gated leisure pages (1-vs-1 duel, early-learning) when today's
// learning quota isn't met yet. Never a dead end — the primary CTA sends the
// student back to their lessons.
import { useNavigate } from 'react-router-dom';
import { Lock, ArrowRight, BookOpen } from 'lucide-react';
import { useTranslation } from '../i18n/useTranslation';
import './QuotaLockScreen.css';

export default function QuotaLockScreen({ completed = 0, baseRequired = 2, remaining }) {
    const navigate = useNavigate();
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const left = remaining != null ? remaining : Math.max(0, baseRequired - completed);
    const pct = Math.min(100, Math.round((completed / Math.max(1, baseRequired)) * 100));

    return (
        <div className="qls-wrap">
            <div className="qls-card">
                <div className="qls-ico"><Lock size={30} /></div>
                <h2 className="qls-title">{ru ? 'Игры пока закрыты' : "O'yinlar hozircha yopiq"}</h2>
                <p className="qls-sub">
                    {ru
                        ? 'Сначала выполни сегодняшнюю учебную норму, потом играй 🎮'
                        : "Avval bugungi o'quv normani bajar, keyin o'yna 🎮"}
                </p>

                <div className="qls-progress">
                    <div className="qls-bar"><span style={{ width: `${pct}%` }} /></div>
                    <div className="qls-count">
                        <b>{completed}</b> / {baseRequired} {ru ? 'уроков' : 'dars'}
                    </div>
                </div>

                <div className="qls-remaining">
                    {left > 0
                        ? (ru
                            ? <>Осталось <b>{left}</b> {left === 1 ? 'урок' : 'урока'} до разблокировки</>
                            : <>Ochilishiga yana <b>{left}</b> ta dars qoldi</>)
                        : (ru ? 'Почти готово!' : 'Deyarli tayyor!')}
                </div>

                <button className="qls-cta" onClick={() => navigate('/student/courses')}>
                    <BookOpen size={18} />
                    {ru ? 'Продолжить обучение' : "Darslarni davom ettirish"}
                    <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
}
