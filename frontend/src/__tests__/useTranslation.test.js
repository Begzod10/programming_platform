import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { useTranslation } from '../i18n/useTranslation';

// Regression test for: useTranslation only listened for the custom
// `languageChange` event (dispatched by toggleLang in the same tab) and
// never for the native `storage` event, which is what fires in OTHER open
// tabs when `localStorage.lang` changes. Without a `storage` listener,
// changing the language in one tab never updates other open tabs.
function LangProbe() {
    const { lang } = useTranslation();
    return <span data-testid="lang">{lang}</span>;
}

describe('useTranslation multi-tab sync', () => {
    beforeEach(() => {
        localStorage.setItem('lang', 'uz');
    });

    afterEach(() => {
        localStorage.clear();
    });

    test('updates lang when a `storage` event reports a change from another tab', () => {
        render(<LangProbe />);
        expect(screen.getByTestId('lang')).toHaveTextContent('uz');

        act(() => {
            // Simulate another tab changing localStorage — this is what the
            // browser dispatches to *other* tabs, never the tab that wrote it.
            window.dispatchEvent(new StorageEvent('storage', {
                key: 'lang',
                newValue: 'ru',
                oldValue: 'uz',
            }));
        });

        expect(screen.getByTestId('lang')).toHaveTextContent('ru');
    });

    test('ignores storage events for unrelated keys', () => {
        render(<LangProbe />);

        act(() => {
            window.dispatchEvent(new StorageEvent('storage', {
                key: 'someOtherKey',
                newValue: 'ru',
                oldValue: null,
            }));
        });

        expect(screen.getByTestId('lang')).toHaveTextContent('uz');
    });

    test('still responds to the same-tab languageChange custom event', () => {
        render(<LangProbe />);

        act(() => {
            window.dispatchEvent(new CustomEvent('languageChange', { detail: 'ru' }));
        });

        expect(screen.getByTestId('lang')).toHaveTextContent('ru');
    });

    test('removes both listeners on unmount', () => {
        const addSpy = jest.spyOn(window, 'addEventListener');
        const removeSpy = jest.spyOn(window, 'removeEventListener');

        const { unmount } = render(<LangProbe />);
        const addedEvents = addSpy.mock.calls.map(([type]) => type);
        expect(addedEvents).toEqual(expect.arrayContaining(['languageChange', 'storage']));

        unmount();
        const removedEvents = removeSpy.mock.calls.map(([type]) => type);
        expect(removedEvents).toEqual(expect.arrayContaining(['languageChange', 'storage']));

        addSpy.mockRestore();
        removeSpy.mockRestore();
    });
});
