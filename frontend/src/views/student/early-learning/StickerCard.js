import React from 'react';
import './StickerAlbum.css';

/** One sticker tile. Owned: emoji + name in a rarity-coloured frame. Locked:
 * greyed emoji + how to earn it (sticker.hint). `sticker.name` is shown as
 * given — callers pick the language. */
export default function StickerCard({ sticker, newLabel, size = 'md' }) {
    const locked = !sticker.owned;
    return (
        <div className={`stk-card stk-${sticker.rarity} stk-size-${size} ${locked ? 'stk-locked' : ''}`}>
            {sticker.is_new && <span className="stk-new">{newLabel}</span>}
            <span className="stk-emoji" aria-hidden="true">{sticker.emoji}</span>
            <span className="stk-label">{locked ? sticker.hint : sticker.name}</span>
        </div>
    );
}
