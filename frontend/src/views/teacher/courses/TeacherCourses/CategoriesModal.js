import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { API_URL, headers } from '../../../../api/search/base';

/* CategoriesModal — real CRUD against /v1/categories.
   Each row supports inline rename + delete; the input at the bottom creates
   a new category. Category count next to the name shows current usage. */
export const CategoriesModal = ({ categories, onClose, onChanged, request }) => {
    const [items, setItems]   = useState(categories);
    const [input, setInput]   = useState('');
    const [editing, setEditing] = useState({}); // id → draft name
    const [busyId, setBusyId] = useState(null);
    const [error, setError]   = useState(null);

    useEffect(() => { setItems(categories); }, [categories]);

    useEffect(() => {
        const h = e => { if (e.key === 'Escape') onClose(); };
        document.addEventListener('keydown', h);
        return () => document.removeEventListener('keydown', h);
    }, [onClose]);

    const safe = (p) => p.catch((e) => { setError("Operatsiya bajarilmadi"); throw e; });

    const add = async () => {
        const v = input.trim();
        if (!v) return;
        if (items.some(c => c.name.toLowerCase() === v.toLowerCase())) {
            setError('Bu nom allaqachon mavjud');
            return;
        }
        setBusyId(-1);
        try {
            const created = await safe(request(
                `${API_URL}v1/categories/`, 'POST', JSON.stringify({ name: v }), headers(),
            ));
            setItems(arr => [...arr, { ...created, courses_count: 0 }].sort((a, b) => a.name.localeCompare(b.name)));
            setInput('');
            setError(null);
            onChanged?.();
        } finally { setBusyId(null); }
    };

    const rename = async (cat) => {
        const draft = (editing[cat.id] ?? '').trim();
        if (!draft || draft === cat.name) { setEditing(p => { const n = { ...p }; delete n[cat.id]; return n; }); return; }
        setBusyId(cat.id);
        try {
            const updated = await safe(request(
                `${API_URL}v1/categories/${cat.id}`, 'PUT', JSON.stringify({ name: draft }), headers(),
            ));
            setItems(arr => arr.map(c => c.id === cat.id ? { ...c, ...updated } : c).sort((a, b) => a.name.localeCompare(b.name)));
            setEditing(p => { const n = { ...p }; delete n[cat.id]; return n; });
            setError(null);
            onChanged?.();
        } finally { setBusyId(null); }
    };

    const remove = async (cat) => {
        if (!window.confirm(`"${cat.name}" kategoriyasini o'chirish? Kurslar uncategorized bo'ladi.`)) return;
        setBusyId(cat.id);
        try {
            await safe(request(
                `${API_URL}v1/categories/${cat.id}`, 'DELETE', null, headers(),
            ));
            setItems(arr => arr.filter(c => c.id !== cat.id));
            setError(null);
            onChanged?.();
        } finally { setBusyId(null); }
    };

    return ReactDOM.createPortal(
        <div className="tc-modal-overlay" onClick={onClose}>
            <div className="tc-modal" onClick={e => e.stopPropagation()}>
                <h3>📚 Kategoriyalar</h3>

                <div className="tc-chapter-list">
                    {items.length === 0 && <p className="tc-chapter-empty">Kategoriyalar yo'q</p>}
                    {items.map(cat => {
                        const isEditing = editing[cat.id] !== undefined;
                        return (
                            <div key={cat.id} className="tc-chapter-item">
                                {isEditing ? (
                                    <input
                                        autoFocus
                                        value={editing[cat.id]}
                                        onChange={e => setEditing(p => ({ ...p, [cat.id]: e.target.value }))}
                                        onKeyDown={e => {
                                            if (e.key === 'Enter') rename(cat);
                                            if (e.key === 'Escape') setEditing(p => { const n = { ...p }; delete n[cat.id]; return n; });
                                        }}
                                        onBlur={() => rename(cat)}
                                        disabled={busyId === cat.id}
                                    />
                                ) : (
                                    <span
                                        onClick={() => setEditing(p => ({ ...p, [cat.id]: cat.name }))}
                                        style={{ cursor: 'pointer' }}
                                        title="Tahrirlash uchun bosing"
                                    >
                                        📁 {cat.name}
                                        <span style={{ opacity: 0.55, fontWeight: 500, marginLeft: 8 }}>
                                            {cat.courses_count || 0} kurs
                                        </span>
                                    </span>
                                )}
                                <button
                                    className="tc-chapter-item-del"
                                    onClick={() => remove(cat)}
                                    disabled={busyId === cat.id}
                                >✕</button>
                            </div>
                        );
                    })}
                </div>

                {error && <p className="tc-chapter-empty" style={{ color: '#be123c' }}>{error}</p>}

                <div className="tc-chapter-add-row">
                    <input
                        placeholder="Yangi kategoriya nomi…"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && add()}
                        disabled={busyId === -1}
                    />
                    <button className="tc-chapter-add-btn" onClick={add} disabled={busyId === -1 || !input.trim()}>
                        + Qo'shish
                    </button>
                </div>
                <div className="tc-modal-actions">
                    <button className="tc-cancel-btn" onClick={onClose}>Yopish</button>
                </div>
            </div>
        </div>,
        document.body
    );
};
