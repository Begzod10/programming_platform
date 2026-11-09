import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// CodeMirror ships ES modules that CRA's Jest does not transform, so everything it provides is replaced here.
let mockLastProps = null;
jest.mock('@uiw/react-codemirror', () => ({
    __esModule: true,
    default: (props) => {
        mockLastProps = props;
        return <textarea data-testid="cm" value={props.value} readOnly={props.readOnly}
                         onChange={(e) => props.onChange(e.target.value)} />;
    },
}));
jest.mock('@codemirror/view', () => ({
    EditorView: { lineWrapping: 'wrap', updateListener: { of: (fn) => ({ listener: fn }) } },
}));
jest.mock('@codemirror/state', () => ({ Transaction: { userEvent: 'userEvent' } }));
jest.mock('@codemirror/lang-html', () => ({ html: () => 'html-ext' }));
jest.mock('@codemirror/lang-css', () => ({ css: () => 'css-ext' }));
jest.mock('@codemirror/lang-javascript', () => ({ javascript: () => 'javascript-ext' }));
jest.mock('@codemirror/lang-python', () => ({ python: () => 'python-ext' }));
jest.mock('@codemirror/lang-sql', () => ({ sql: () => 'sql-ext' }));
jest.mock('@codemirror/lang-json', () => ({ json: () => 'json-ext' }));

import CodeEditor, { languageExtension, classifyChange } from '../components/CodeEditor/CodeEditor';

test('languageExtension gives a highlighter for known languages and nothing for text or unknown ones', () => {
    expect(languageExtension('python').length).toBeGreaterThan(0);
    ['html', 'css', 'javascript', 'sql', 'json'].forEach((l) => expect(languageExtension(l).length).toBe(1));
    expect(languageExtension('text')).toEqual([]);
    expect(languageExtension('nope')).toEqual([]);
});

test('classifyChange tells typing from pasting and ignores everything else', () => {
    expect(classifyChange('input.paste', 40)).toBe('pasted');
    expect(classifyChange('input.drop', 5)).toBe('pasted');
    expect(classifyChange('input.type', 1)).toBe('typed');
    expect(classifyChange('input', 1)).toBe('typed');
    expect(classifyChange('delete.backward', 1)).toBeNull();
    expect(classifyChange('input.paste', 0)).toBeNull();
    expect(classifyChange(undefined, 3)).toBeNull();
});

test('shows the value, reports edits, and is read-only on request', () => {
    const onChange = jest.fn();
    const { rerender } = render(<CodeEditor value="print(1)" onChange={onChange} language="python" />);
    expect(screen.getByTestId('cm')).toHaveValue('print(1)');
    fireEvent.change(screen.getByTestId('cm'), { target: { value: 'print(2)' } });
    expect(onChange).toHaveBeenCalledWith('print(2)');
    expect(screen.getByTestId('cm')).not.toHaveAttribute('readonly');
    rerender(<CodeEditor value="print(1)" onChange={onChange} language="python" readOnly />);
    expect(screen.getByTestId('cm')).toHaveAttribute('readonly');
});

test('reports inserted characters per user change through onInsert', () => {
    const onInsert = jest.fn();
    render(<CodeEditor value="" onChange={() => {}} language="text" onInsert={onInsert} />);
    const { listener } = mockLastProps.extensions.find((e) => e && e.listener);
    const tx = (event, n) => ({ annotation: () => event, changes: { iterChanges: (cb) => cb(0, 0, 0, n, { length: n }) } });
    listener({ docChanged: true, transactions: [tx('input.paste', 40), tx('input.type', 1)] });
    expect(onInsert).toHaveBeenNthCalledWith(1, 'pasted', 40);
    expect(onInsert).toHaveBeenNthCalledWith(2, 'typed', 1);
    onInsert.mockClear();
    listener({ docChanged: false, transactions: [tx('input.paste', 9)] });
    expect(onInsert).not.toHaveBeenCalled();
});
