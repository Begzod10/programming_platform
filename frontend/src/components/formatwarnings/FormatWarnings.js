import React from 'react';
import './FormatWarnings.css';

/** Files whose content does not match their extension (Python saved as .html ...), reported by the upload endpoints.
 *  Only a warning: the upload went through, nothing is blocked. */
export default function FormatWarnings({ warnings, ru }) {
    if (!Array.isArray(warnings) || warnings.length === 0) return null;
    return (
        <div className="fw-box" role="status">
            <strong className="fw-title">{ru ? '⚠️ Формат файлов' : '⚠️ Fayl formati'}</strong>
            <ul className="fw-list">
                {warnings.map((w) => <li key={w.file}>{ru && w.message_ru ? w.message_ru : w.message}</li>)}
            </ul>
            <p className="fw-note">
                {ru
                    ? 'Проект принят. Исправьте имена файлов и загрузите архив заново, если хотите.'
                    : "Loyiha qabul qilindi. Xohlasangiz, fayl nomlarini tuzatib, ZIP'ni qayta yuklang."}
            </p>
        </div>
    );
}
