// Mock external dependencies so Jest can load the module without real imports.
// jest.mock() calls are hoisted by babel-jest before any imports are resolved.
jest.mock('lucide-react', () => ({
    Trophy: () => null,
    Crown: () => null,
    Medal: () => null,
    Infinity: () => null,
    CalendarDays: () => null,
    Calendar: () => null,
    Sun: () => null,
}));
jest.mock('../context/AuthContext', () => ({
    useAuth: () => ({ user: { id: 1, username: 'me' } }),
}));
jest.mock('../api/search/base', () => ({
    API_URL: 'http://test/',
    headers: () => ({}),
    useHttp: jest.fn(),
}));

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Leaderboard from '../views/student/rankings/LeaderBoard';
import { useHttp } from '../api/search/base';

// jsdom doesn't implement Element.scrollTo; LeaderBoard calls it on mount
// for scroll-to-top behavior, which is irrelevant to this test.
if (!window.HTMLElement.prototype.scrollTo) {
    window.HTMLElement.prototype.scrollTo = () => {};
}

// Real translations — default language is 'uz' unless localStorage says
// otherwise, so pin it explicitly for deterministic assertions.
const ERROR_TEXT = "Reytingni yuklab bo'lmadi";
const RETRY_TEXT = 'Qayta urinish';

// Regression test for: fetchMyRank swallowed its error silently
// (`.catch(() => {})`), so a failed "my rank" request left `myRank` null
// forever with zero feedback — the "Mening o'rnim" card just never
// appeared, with nothing telling the student (or a developer) why.
describe('Leaderboard my-rank error handling', () => {
    beforeEach(() => {
        localStorage.setItem('lang', 'uz');
    });

    afterEach(() => {
        jest.clearAllMocks();
        localStorage.clear();
    });

    test('shows an inline error with retry when fetchMyRank fails, and retry re-fetches', async () => {
        const request = jest.fn((url) => {
            if (url.includes('rankings/leaderboard')) return Promise.resolve([]);
            if (url.includes('rankings/me')) return Promise.reject(new Error('network down'));
            return Promise.resolve([]);
        });
        useHttp.mockReturnValue({ request });

        render(<Leaderboard />);

        // Error surfaces near where the rank card would render, with a
        // retry affordance — matching the existing .lb-state--error /
        // .lb-retry pattern already used for the main leaderboard fetch.
        const errorNode = await screen.findByText(ERROR_TEXT, { selector: '.lb-myrank-error-text' });
        expect(errorNode).toBeInTheDocument();

        const retryBtn = errorNode.closest('.lb-myrank--error').querySelector('.lb-retry');
        expect(retryBtn).toHaveTextContent(RETRY_TEXT);

        // Retry re-triggers fetchMyRank; once it succeeds, the error band
        // goes away and the real my-rank card renders instead.
        request.mockImplementation((url) => {
            if (url.includes('rankings/leaderboard')) return Promise.resolve([]);
            if (url.includes('rankings/me')) {
                return Promise.resolve({ global_rank: 5, total_points: 120 });
            }
            return Promise.resolve([]);
        });
        fireEvent.click(retryBtn);

        await waitFor(() => {
            expect(screen.queryByText(ERROR_TEXT, { selector: '.lb-myrank-error-text' })).not.toBeInTheDocument();
        });
        expect(document.querySelector('.lb-myrank:not(.lb-myrank--error)')).toBeInTheDocument();
    });

    test('does not show the my-rank error band when the fetch succeeds', async () => {
        const request = jest.fn((url) => {
            if (url.includes('rankings/leaderboard')) return Promise.resolve([]);
            if (url.includes('rankings/me')) {
                return Promise.resolve({ global_rank: 3, total_points: 200 });
            }
            return Promise.resolve([]);
        });
        useHttp.mockReturnValue({ request });

        render(<Leaderboard />);

        await waitFor(() => {
            expect(document.querySelector('.lb-myrank:not(.lb-myrank--error)')).toBeInTheDocument();
        });
        expect(screen.queryByText(ERROR_TEXT, { selector: '.lb-myrank-error-text' })).not.toBeInTheDocument();
    });
});
