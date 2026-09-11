import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { RichTextEditor } from '../views/teacher/courses/LessonEditor/RichTextEditor';

// Regression tests for: the DOM-sync useEffect read `value` but had an
// empty dependency array, so it only ever applied the initial value once.
// The fix adds `value` to the deps, guarded by a `lastEmitted` ref so the
// effect can tell "value changed because the editor itself emitted it"
// (skip — the DOM is already correct, and resetting it would blow away the
// caret) apart from "value changed for an external reason, e.g. switching
// to a different lesson section" (must resync the DOM).
describe('RichTextEditor value syncing', () => {
    function ControlledEditor({ initialValue }) {
        const [value, setValue] = React.useState(initialValue);
        return <RichTextEditor value={value} onChange={setValue} />;
    }

    test('does not tear down the DOM when the value change is self-originated (typing)', async () => {
        const { container } = render(<ControlledEditor initialValue="<p>Hello</p>" />);
        const editorDiv = container.querySelector('.lep-rte-editor');
        expect(editorDiv.innerHTML).toBe('<p>Hello</p>');

        // Simulate the browser applying a keystroke to the contentEditable
        // DOM before React ever sees it (this is how contentEditable works).
        await act(async () => {
            editorDiv.innerHTML = '<p>Hello world</p>';
        });
        const paragraphAfterTyping = editorDiv.firstChild;

        // Now let React find out, via the onInput handler that echoes the
        // DOM's current HTML back through onChange -> setValue -> a new
        // `value` prop with the exact content already in the DOM.
        await act(async () => {
            fireEvent.input(editorDiv);
        });

        // Same paragraph node instance: the effect must not have reset
        // innerHTML in reaction to its own echoed value.
        expect(editorDiv.firstChild).toBe(paragraphAfterTyping);
        expect(editorDiv.innerHTML).toBe('<p>Hello world</p>');
    });

    test('resyncs the DOM when value changes externally (e.g. switching sections)', () => {
        function Wrapper() {
            const [value, setValue] = React.useState('<p>First section</p>');
            return (
                <>
                    <button type="button" onClick={() => setValue('<p>Second section</p>')}>
                        switch section
                    </button>
                    <RichTextEditor value={value} onChange={setValue} />
                </>
            );
        }

        const { container } = render(<Wrapper />);
        const editorDiv = container.querySelector('.lep-rte-editor');
        expect(editorDiv.innerHTML).toBe('<p>First section</p>');

        fireEvent.click(screen.getByText('switch section'));

        expect(editorDiv.innerHTML).toBe('<p>Second section</p>');
    });

    test('calls onChange with the live DOM content when the user types', () => {
        const onChange = jest.fn();
        const { container } = render(<RichTextEditor value="<p>Hi</p>" onChange={onChange} />);
        const editorDiv = container.querySelector('.lep-rte-editor');

        act(() => {
            editorDiv.innerHTML = '<p>Hi there</p>';
            fireEvent.input(editorDiv);
        });

        expect(onChange).toHaveBeenCalledWith('<p>Hi there</p>');
    });
});
