import React, { useEffect } from 'react';
import ReactDOM from 'react-dom';

export const ConfirmModal = ({ title, text, onConfirm, onClose }) => {
    useEffect(() => {
        const h = e => { if (e.key === 'Escape') onClose(); };
        document.addEventListener('keydown', h);
        return () => document.removeEventListener('keydown', h);
    }, [onClose]);
    return ReactDOM.createPortal(
        <div className="tc-modal-overlay" onClick={onClose}>
            <div className="tc-confirm" onClick={e => e.stopPropagation()}>
                <span className="tc-confirm-icon">🗑️</span>
                <h4>{title}</h4>
                {text && <p>{text}</p>}
                <div className="tc-confirm-actions">
                    <button className="tc-cancel-btn" onClick={onClose}>Отмена</button>
                    <button className="tc-delete-btn" onClick={onConfirm}>🗑️ Удалить</button>
                </div>
            </div>
        </div>,
        document.body
    );
};
