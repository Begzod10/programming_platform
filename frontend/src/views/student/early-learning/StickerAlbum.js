import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './EarlyLearning.css';
import './StickerAlbum.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import LangToggle from './LangToggle';
import Sky from './Sky';
import StickerCard from './StickerCard';
import { ArrowLeft } from 'lucide-react';

const SECTIONS = [
    ['star', 'el.stickerKindStar'],
    ['daily', 'el.stickerKindDaily'],
    ['streak', 'el.stickerKindStreak'],
    ['module', 'el.stickerKindModule'],
];

/** "Kolleksiyam" — every sticker a kid can earn in the games, owned ones in
 * colour, the rest greyed with how to get them. Opening the page is what
 * clears the "new" marks (POST stickers/seen); the tags stay visible for
 * this visit so the kid can spot what just arrived. */
export default function StickerAlbum() {
    const navigate = useNavigate();
    const { request } = useHttp();
    const { t, lang, toggleLang } = useTranslation();
    const [album, setAlbum] = useState(null);
    const [failed, setFailed] = useState(false);
    const seenSent = useRef(false);

    useEffect(() => {
        let alive = true;
        setFailed(false);
        request(`${API_URL}v1/early-learning/stickers?lang=${lang}`, 'GET', null, headers())
            .then((data) => {
                if (!alive) return;
                setAlbum(data);
                if (!seenSent.current && data.stickers.some((s) => s.is_new)) {
                    seenSent.current = true;
                    request(`${API_URL}v1/early-learning/stickers/seen`, 'POST', null, headers()).catch(() => {});
                }
            })
            .catch(() => { if (alive) setFailed(true); });
        return () => { alive = false; };
    }, [request, lang]);

    const back = () => navigate('/student/early-learning');

    return (
        <div className="el-shell">
            <Sky />
            <div className="el-page">
                <div className="el-page-topbar">
                    <button className="el-back-btn" onClick={back}>
                        <ArrowLeft size={18} /> {t('el.back')}
                    </button>
                    <LangToggle lang={lang} toggleLang={toggleLang} />
                </div>
                <div className="el-hero">
                    <h1>📒 {t('el.stickerAlbum')}</h1>
                    {album && <p className="stk-count">{album.owned_count} / {album.total}</p>}
                </div>
                {failed && !album && <div className="el-empty">{t('el.stickerError')}</div>}
                {!failed && !album && <div className="el-loading">{t('loading')}</div>}
                {album && SECTIONS.map(([kind, titleKey]) => {
                    const list = album.stickers.filter((s) => s.kind === kind);
                    if (!list.length) return null;
                    return (
                        <section key={kind} className="stk-section">
                            <h2>{t(titleKey)} <span>{list.filter((s) => s.owned).length} / {list.length}</span></h2>
                            <div className="stk-grid">
                                {list.map((s) => <StickerCard key={s.key} sticker={s} newLabel={t('el.stickerNew')} />)}
                            </div>
                        </section>
                    );
                })}
            </div>
        </div>
    );
}
