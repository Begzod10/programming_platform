import React, { useMemo } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { EditorView } from '@codemirror/view';
import { Transaction } from '@codemirror/state';
import { html } from '@codemirror/lang-html';
import { css } from '@codemirror/lang-css';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { sql } from '@codemirror/lang-sql';
import { json } from '@codemirror/lang-json';

const LANGUAGES = { html, css, javascript, python, sql, json };

/** CodeMirror extensions that highlight `language`; none for plain text or an unknown language. */
export const languageExtension = (language) => (LANGUAGES[language] ? [LANGUAGES[language]()] : []);

/** Whether a user change was typed or pasted (a drop counts as pasted); anything else (deleting, autocomplete) is neither. */
export const classifyChange = (userEvent, insertedLength) => {
    if (!insertedLength || !userEvent) return null;
    if (userEvent === 'input.paste' || userEvent === 'input.drop') return 'pasted';
    if (userEvent === 'input' || userEvent.startsWith('input.type')) return 'typed';
    return null;
};

/** A code editor: highlighting, indentation, line numbers. `onInsert('typed' | 'pasted', n)` fires per user change
 *  so a page can tell the teacher how much of the code was pasted. Load it through LazyCodeEditor. */
export default function CodeEditor({ value, onChange, language = 'text', readOnly = false, minHeight = '320px', onInsert }) {
    const extensions = useMemo(() => [
        ...languageExtension(language),
        EditorView.lineWrapping,
        EditorView.updateListener.of((update) => {
            if (!onInsert || !update.docChanged) return;
            update.transactions.forEach((tr) => {
                let inserted = 0;
                tr.changes.iterChanges((fromA, toA, fromB, toB, text) => { inserted += text.length; });
                const kind = classifyChange(tr.annotation(Transaction.userEvent), inserted);
                if (kind) onInsert(kind, inserted);
            });
        }),
    ], [language, onInsert]);

    return (
        <CodeMirror
            value={value}
            onChange={(v) => onChange && onChange(v)}
            extensions={extensions}
            editable={!readOnly}
            readOnly={readOnly}
            minHeight={minHeight}
            basicSetup={{ lineNumbers: true, foldGutter: false }}
        />
    );
}
