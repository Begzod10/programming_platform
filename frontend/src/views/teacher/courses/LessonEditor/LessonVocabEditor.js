import React, { useEffect, useState } from 'react';
import './LessonVocabEditor.css';

export default function LessonVocabEditor({ courseId, lessonId, apiBaseUrl = '/api/v1' }) {
    const [words, setWords] = useState([]);
    const [loading, setLoading] = useState(true);
    const [newWord, setNewWord] = useState('');
    const [newDef, setNewDef] = useState('');
    const [saving, setSaving] = useState(false);
    const [editId, setEditId] = useState(null);
    const [editWord, setEditWord] = useState('');
    const [editDef, setEditDef] = useState('');

    const token = localStorage.getItem('token') || sessionStorage.getItem('token') || '';
    const authHeaders = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
    const base = `${apiBaseUrl}/courses/${courseId}/lessons/${lessonId}/vocabulary`;

    const load = () => {
        setLoading(true);
        fetch(base, { headers: authHeaders })
            .then(r => r.ok ? r.json() : [])
            .then(data => { setWords(data); setLoading(false); })
            .catch(() => setLoading(false));
    };

    useEffect(() => { load(); }, [lessonId]);

    const handleAdd = async () => {
        if (!newWord.trim() || !newDef.trim()) return;
        setSaving(true);
        try {
            const r = await fetch(base, {
                method: 'POST',
                headers: authHeaders,
                body: JSON.stringify({ word: newWord.trim(), definition: newDef.trim(), order: words.length }),
            });
            if (r.ok) {
                const created = await r.json();
                setWords(prev => [...prev, created]);
                setNewWord('');
                setNewDef('');
            }
        } finally { setSaving(false); }
    };

    const handleDelete = async (id) => {
        await fetch(`${base}/${id}`, { method: 'DELETE', headers: authHeaders });
        setWords(prev => prev.filter(w => w.id !== id));
    };

    const startEdit = (w) => {
        setEditId(w.id);
        setEditWord(w.word);
        setEditDef(w.definition);
    };

    const handleSaveEdit = async () => {
        if (!editWord.trim() || !editDef.trim()) return;
        setSaving(true);
        try {
            const r = await fetch(`${base}/${editId}`, {
                method: 'PUT',
                headers: authHeaders,
                body: JSON.stringify({ word: editWord.trim(), definition: editDef.trim(), order: 0 }),
            });
            if (r.ok) {
                const updated = await r.json();
                setWords(prev => prev.map(w => w.id === editId ? updated : w));
                setEditId(null);
            }
        } finally { setSaving(false); }
    };

    return (
        <div className="lve-panel">
            <div className="lve-header">
                <span className="lve-icon">📚</span>
                <span className="lve-title">Dars atamalari (Tayyorgarlik ro'yxati)</span>
                <span className="lve-count">{words.length} ta</span>
            </div>

            <div className="lve-add-row">
                <input
                    className="lve-input"
                    placeholder="Atama (so'z)"
                    value={newWord}
                    onChange={e => setNewWord(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && document.getElementById('lve-def-input')?.focus()}
                />
                <input
                    id="lve-def-input"
                    className="lve-input lve-input--def"
                    placeholder="Ta'rifi (o'zbek tilida)"
                    value={newDef}
                    onChange={e => setNewDef(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleAdd()}
                />
                <button
                    className="lve-btn-add"
                    onClick={handleAdd}
                    disabled={saving || !newWord.trim() || !newDef.trim()}
                >
                    {saving ? '...' : '+ Qo\'sh'}
                </button>
            </div>

            {loading ? (
                <div className="lve-empty">Yuklanmoqda...</div>
            ) : words.length === 0 ? (
                <div className="lve-empty">Hali atamalar qo'shilmagan</div>
            ) : (
                <div className="lve-list">
                    {words.map(w => (
                        <div key={w.id} className="lve-item">
                            {editId === w.id ? (
                                <div className="lve-edit-row">
                                    <input className="lve-input" value={editWord} onChange={e => setEditWord(e.target.value)} />
                                    <input className="lve-input lve-input--def" value={editDef} onChange={e => setEditDef(e.target.value)} />
                                    <button className="lve-btn-save" onClick={handleSaveEdit} disabled={saving}>Saqlash</button>
                                    <button className="lve-btn-cancel" onClick={() => setEditId(null)}>✕</button>
                                </div>
                            ) : (
                                <>
                                    <div className="lve-item-word">{w.word}</div>
                                    <div className="lve-item-def">{w.definition}</div>
                                    <div className="lve-item-actions">
                                        <button className="lve-btn-edit" onClick={() => startEdit(w)}>✎</button>
                                        <button className="lve-btn-del" onClick={() => handleDelete(w.id)}>✕</button>
                                    </div>
                                </>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
