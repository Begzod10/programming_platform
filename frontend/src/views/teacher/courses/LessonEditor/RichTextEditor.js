import React, { useRef, useEffect } from 'react';
import { FONT_SIZES, FONT_FAMILIES, HEADINGS } from './lessonEditorConstants';

/* ─────────────────────────────────────────────
   RICH TEXT EDITOR
───────────────────────────────────────────── */
export const RichTextEditor = ({ value, onChange }) => {
    const editorRef = useRef(null);
    const savedRange = useRef(null);

    useEffect(() => {
        if (editorRef.current && editorRef.current.innerHTML !== (value || ''))
            editorRef.current.innerHTML = value || '';
    }, []);

    const saveSelection = () => {
        const sel = window.getSelection();
        if (sel && sel.rangeCount > 0) savedRange.current = sel.getRangeAt(0).cloneRange();
    };
    const restoreSelection = () => {
        if (!savedRange.current) return;
        const sel = window.getSelection();
        if (sel) { sel.removeAllRanges(); sel.addRange(savedRange.current); }
    };
    const preventBlur = (e) => e.preventDefault();
    const exec = (cmd, val = null) => {
        restoreSelection();
        document.execCommand(cmd, false, val);
        onChange(editorRef.current.innerHTML);
        saveSelection();
    };
    const setBlock = (e) => {
        restoreSelection();
        document.execCommand('formatBlock', false, e.target.value === 'Paragraph' ? 'p' : e.target.value.toLowerCase());
        onChange(editorRef.current.innerHTML);
        editorRef.current.focus();
    };
    const applyFontFamily = (e) => {
        restoreSelection();
        document.execCommand('fontName', false, e.target.value);
        onChange(editorRef.current.innerHTML);
        editorRef.current.focus();
    };
    const applyFontSize = (e) => {
        const size = e.target.value;
        restoreSelection();
        if (savedRange.current && !savedRange.current.collapsed) {
            const span = document.createElement('span');
            span.style.fontSize = size;
            try { savedRange.current.surroundContents(span); onChange(editorRef.current.innerHTML); } catch {}
        } else {
            document.execCommand('fontSize', false, '3');
            const fonts = editorRef.current.querySelectorAll('font[size]');
            if (fonts.length) {
                const last = fonts[fonts.length - 1];
                last.removeAttribute('size');
                last.style.fontSize = size;
            }
            onChange(editorRef.current.innerHTML);
        }
        editorRef.current.focus();
    };
    const applyColor = (e, cmd) => {
        restoreSelection();
        document.execCommand(cmd, false, e.target.value);
        onChange(editorRef.current.innerHTML);
        editorRef.current.focus();
    };

    return (
        <div className="lep-rte-wrap">
            <div className="lep-rte-toolbar" onMouseDown={preventBlur}>
                <select className="lep-rte-select" defaultValue="Paragraph" onMouseDown={e => e.stopPropagation()} onChange={setBlock}>
                    {HEADINGS.map(h => <option key={h}>{h}</option>)}
                </select>
                <div className="lep-rte-sep"/>
                <select className="lep-rte-select" defaultValue="Georgia" onMouseDown={e => e.stopPropagation()} onChange={applyFontFamily}>
                    {FONT_FAMILIES.map(f => <option key={f}>{f}</option>)}
                </select>
                <select className="lep-rte-select" defaultValue="14px" onMouseDown={e => e.stopPropagation()} onChange={applyFontSize}>
                    {FONT_SIZES.map(s => <option key={s}>{s}</option>)}
                </select>
                <div className="lep-rte-sep"/>
                <button className="lep-rte-btn" title="Жирный" onMouseDown={preventBlur} onClick={() => exec('bold')}><b>B</b></button>
                <button className="lep-rte-btn" title="Курсив" onMouseDown={preventBlur} onClick={() => exec('italic')}><i>I</i></button>
                <button className="lep-rte-btn" title="Подчёркнутый" onMouseDown={preventBlur} onClick={() => exec('underline')}><u>U</u></button>
                <button className="lep-rte-btn" title="Зачёркнутый" onMouseDown={preventBlur} onClick={() => exec('strikeThrough')}><s>S</s></button>
                <div className="lep-rte-sep"/>
                <button className="lep-rte-btn" onMouseDown={preventBlur} onClick={() => exec('justifyLeft')}>⬅</button>
                <button className="lep-rte-btn" onMouseDown={preventBlur} onClick={() => exec('justifyCenter')}>☰</button>
                <button className="lep-rte-btn" onMouseDown={preventBlur} onClick={() => exec('justifyRight')}>➡</button>
                <div className="lep-rte-sep"/>
                <button className="lep-rte-btn" onMouseDown={preventBlur} onClick={() => exec('insertUnorderedList')}>• –</button>
                <button className="lep-rte-btn" onMouseDown={preventBlur} onClick={() => exec('insertOrderedList')}>1.</button>
                <div className="lep-rte-sep"/>
                <div className="lep-rte-color" title="Цвет текста">
                    <div className="lep-rte-dot" style={{background: '#1a1a2e'}}/>
                    <input type="color" className="lep-rte-color-input" defaultValue="#1a1a2e"
                           onMouseDown={e => e.stopPropagation()} onChange={e => applyColor(e, 'foreColor')}/>
                </div>
                <div className="lep-rte-color" title="Фон текста">
                    <div className="lep-rte-dot" style={{background: '#a29bfe'}}/>
                    <input type="color" className="lep-rte-color-input" defaultValue="#a29bfe"
                           onMouseDown={e => e.stopPropagation()} onChange={e => applyColor(e, 'hiliteColor')}/>
                </div>
                <div className="lep-rte-sep"/>
                <button className="lep-rte-btn" title="Очистить" onMouseDown={preventBlur} onClick={() => exec('removeFormat')}>✕</button>
            </div>
            <div className="lep-rte-editor" ref={editorRef} contentEditable suppressContentEditableWarning
                 data-placeholder="Введите текст урока..."
                 onFocus={saveSelection} onKeyUp={saveSelection} onMouseUp={saveSelection} onSelect={saveSelection}
                 onInput={() => { onChange(editorRef.current.innerHTML); saveSelection(); }}/>
        </div>
    );
};
