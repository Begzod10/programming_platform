import React, { useState, useEffect } from 'react';

/* CategoryPicker — click-to-open combobox.
   `<datalist>` only shows suggestions while typing; a teacher who wants to
   see "what categories exist" gets no affordance from it. This is a real
   dropdown: the field opens on focus/click, filters as you type, and offers
   "+ Create new" as the last option when the typed name doesn't match. */
export const CategoryPicker = ({ categories, value, onChange, placeholder }) => {
    const [open, setOpen] = useState(false);
    const wrapRef = React.useRef(null);
    const inputRef = React.useRef(null);

    // Close on outside click / Escape so it behaves like a proper popup
    useEffect(() => {
        if (!open) return;
        const onDocClick = (e) => {
            if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false);
        };
        const onKey = (e) => { if (e.key === 'Escape') setOpen(false); };
        document.addEventListener('mousedown', onDocClick);
        document.addEventListener('keydown', onKey);
        return () => {
            document.removeEventListener('mousedown', onDocClick);
            document.removeEventListener('keydown', onKey);
        };
    }, [open]);

    const query = (value || '').trim().toLowerCase();
    const filtered = query
        ? categories.filter(c => c.name.toLowerCase().includes(query))
        : categories;
    const exactMatch = categories.some(c => c.name.toLowerCase() === query);
    const showCreate = query.length > 0 && !exactMatch;

    const pick = (name) => {
        onChange(name);
        setOpen(false);
        inputRef.current?.focus();
    };
    const clear = (e) => {
        e.stopPropagation();
        onChange('');
        inputRef.current?.focus();
    };

    return (
        <div className="tc-cat-picker" ref={wrapRef}>
            <div className="tc-cat-input-wrap">
                <input
                    ref={inputRef}
                    type="text"
                    placeholder={placeholder}
                    value={value || ''}
                    onChange={e => { onChange(e.target.value); if (!open) setOpen(true); }}
                    onFocus={() => setOpen(true)}
                    onClick={() => setOpen(true)}
                />
                {value && (
                    <button
                        type="button"
                        className="tc-cat-clear"
                        onClick={clear}
                        aria-label="Очистить"
                    >✕</button>
                )}
                <button
                    type="button"
                    className={`tc-cat-caret${open ? ' tc-cat-caret--open' : ''}`}
                    onClick={() => { setOpen(o => !o); inputRef.current?.focus(); }}
                    aria-label="Открыть список"
                    tabIndex={-1}
                >▾</button>
            </div>
            {open && (
                <div className="tc-cat-menu" role="listbox">
                    {filtered.length === 0 && !showCreate && (
                        <div className="tc-cat-empty">Категорий пока нет</div>
                    )}
                    {filtered.map(cat => (
                        <button
                            key={cat.id}
                            type="button"
                            className={`tc-cat-option${value === cat.name ? ' tc-cat-option--active' : ''}`}
                            onClick={() => pick(cat.name)}
                            role="option"
                            aria-selected={value === cat.name}
                        >
                            <span>📁 {cat.name}</span>
                            {cat.courses_count > 0 && (
                                <span className="tc-cat-count">{cat.courses_count}</span>
                            )}
                        </button>
                    ))}
                    {showCreate && (
                        <button
                            type="button"
                            className="tc-cat-option tc-cat-option--create"
                            onClick={() => pick(value.trim())}
                        >
                            ➕ Создать: <strong>{value.trim()}</strong>
                        </button>
                    )}
                </div>
            )}
        </div>
    );
};
