import React from 'react';
import ReactDOM from 'react-dom';
import './StickerAlbum.css';
import StickerCard from './StickerCard';

const SHOWN = 3;

/** "You got a new sticker!" overlay, shown on the module page right after a
 * game that earned one or more. `stickers` come straight from the completion
 * reply ({key, emoji, name, name_ru, kind, rarity}). */
export default function StickerReveal({ stickers, lang, t, onClose, onOpenAlbum }) {
    const shown = stickers.slice(0, SHOWN);
    const extra = stickers.length - shown.length;
    return ReactDOM.createPortal(
        <div className="stk-reveal-overlay" onClick={onClose}>
            <div className="stk-reveal-card" role="dialog" aria-label={t('el.stickerGot')} onClick={(e) => e.stopPropagation()}>
                <div className="stk-reveal-title">{t('el.stickerGot')}</div>
                <div className="stk-reveal-row">
                    {shown.map((s) => (
                        <StickerCard
                            key={s.key}
                            size="lg"
                            sticker={{ ...s, name: lang === 'ru' && s.name_ru ? s.name_ru : s.name, owned: true, is_new: false }}
                        />
                    ))}
                    {extra > 0 && <span className="stk-reveal-more">+{extra}</span>}
                </div>
                <div className="stk-reveal-actions">
                    <button type="button" className="stk-reveal-btn stk-reveal-btn-alt" onClick={onOpenAlbum}>{t('el.stickerToAlbum')}</button>
                    <button type="button" className="stk-reveal-btn" onClick={onClose}>{t('el.continueBtn')}</button>
                </div>
            </div>
        </div>,
        document.body
    );
}
