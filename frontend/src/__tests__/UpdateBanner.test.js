import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import UpdateBanner from '../components/UpdateBanner/UpdateBanner';

describe('UpdateBanner', () => {
    beforeEach(() => {
        jest.useFakeTimers();
        Object.defineProperty(document, 'visibilityState', {
            configurable: true, get: () => 'visible',
        });
    });

    afterEach(() => {
        jest.useRealTimers();
        jest.restoreAllMocks();
    });

    it('does not show on first load (baseline capture), then shows once the manifest hash changes', async () => {
        let call = 0;
        global.fetch = jest.fn(() => {
            call += 1;
            const mainJs = call === 1 ? '/static/js/main.aaa111.js' : '/static/js/main.bbb222.js';
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ files: { 'main.js': mainJs } }),
            });
        });

        render(<UpdateBanner />);

        // First fetch (mount effect) captures the baseline — no banner yet.
        await act(async () => { await Promise.resolve(); });
        expect(screen.queryByText(/Yangi versiya/i)).not.toBeInTheDocument();
        expect(global.fetch).toHaveBeenCalledTimes(1);

        // Second poll (3 min later) sees a different main.js hash.
        await act(async () => {
            jest.advanceTimersByTime(3 * 60 * 1000);
            await Promise.resolve();
        });
        await waitFor(() => expect(screen.getByText(/Yangi versiya/i)).toBeInTheDocument());
        expect(screen.getByText('Yangilash')).toBeInTheDocument();
    });

    it('does not flag an update when consecutive polls return the same hash', async () => {
        global.fetch = jest.fn(() => Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ files: { 'main.js': '/static/js/main.same111.js' } }),
        }));

        render(<UpdateBanner />);
        await act(async () => { await Promise.resolve(); });

        await act(async () => {
            jest.advanceTimersByTime(3 * 60 * 1000);
            await Promise.resolve();
        });
        expect(screen.queryByText(/Yangi versiya/i)).not.toBeInTheDocument();
    });

    it('does not flag an update while the tab is hidden', async () => {
        Object.defineProperty(document, 'visibilityState', {
            configurable: true, get: () => 'hidden',
        });
        let call = 0;
        global.fetch = jest.fn(() => {
            call += 1;
            const mainJs = call === 1 ? '/static/js/main.aaa111.js' : '/static/js/main.bbb222.js';
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ files: { 'main.js': mainJs } }),
            });
        });

        render(<UpdateBanner />);
        await act(async () => {
            jest.advanceTimersByTime(3 * 60 * 1000);
            await Promise.resolve();
        });
        // Hidden the whole time — checkForUpdate short-circuits before fetch.
        expect(global.fetch).not.toHaveBeenCalled();
        expect(screen.queryByText(/Yangi versiya/i)).not.toBeInTheDocument();
    });
});
