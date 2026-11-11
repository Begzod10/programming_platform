import React from 'react';
import './StickerAlbum.css';

const fill = (text, values) => Object.entries(values).reduce((s, [k, v]) => s.replace(`{${k}}`, v), text);

/** Home-page bar summarising the sticker collection: how many are owned,
 * how far the next star sticker is, whether today's sticker is earned yet,
 * and the play streak. The whole bar opens the album. */
export default function StickerStrip({ album, t, onOpen }) {
    const { next_star: nextStar, today } = album;
    const remaining = nextStar ? Math.max(0, nextStar.at - nextStar.have) : 0;
    const pct = nextStar ? Math.round((Math.max(0, 10 - remaining) / 10) * 100) : 0;
    const hasNew = album.stickers.some((s) => s.is_new);
    return (
        <button type="button" className="stk-strip" onClick={onOpen}>
            <span className="stk-strip-title">
                📒 {t('el.stickerAlbum')} {album.owned_count}/{album.total}
                {hasNew && <span className="stk-dot" role="img" aria-label={t('el.stickerNew')} />}
            </span>
            {nextStar && (
                <span className="stk-strip-next">
                    <span className="stk-bar" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={pct}>
                        <span className="stk-bar-fill" style={{ width: `${pct}%` }} />
                    </span>
                    <span className="stk-strip-text">{fill(t('el.stickerNextStar'), { n: remaining })}</span>
                </span>
            )}
            <span className={`stk-chip ${today.earned ? 'stk-chip-done' : ''}`}>
                {today.earned
                    ? t('el.stickerTodayDone')
                    : fill(t('el.stickerTodayPlays'), { a: Math.min(today.played, today.needed), b: today.needed })}
            </span>
            {album.streak > 0 && <span className="stk-chip stk-chip-streak">🔥 {album.streak}</span>}
        </button>
    );
}
