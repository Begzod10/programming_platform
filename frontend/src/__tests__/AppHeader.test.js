// Page tests render the app with AppHeader stubbed out (see setupTests.js);
// this file exercises the real one.
jest.unmock('../components/appheader/AppHeader');

const mockRequest = jest.fn();

jest.mock('../api/search/base', () => ({
    API_URL: 'http://test/api/',
    headers: () => ({}),
    resolveImageUrl: (src) => src || '',
    useHttp: () => ({ request: mockRequest }),
}));
jest.mock('../context/AuthContext', () => ({ useAuth: () => ({ logout: jest.fn() }) }));
jest.mock('lucide-react', () => new Proxy({ __esModule: true }, {
    get: (t, p) => (p in t || typeof p === 'symbol' ? t[p] : () => null),
}));

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import AppHeader from '../components/appheader/AppHeader';

describe('AppHeader', () => {
    beforeEach(() => {
        localStorage.clear();
        localStorage.setItem('lang', 'ru');
        mockRequest.mockReset();
        // Any raw fetch() would bypass the axios interceptor that refreshes an
        // expired token — it must never be used here.
        window.fetch = jest.fn(() => { throw new Error('raw fetch() must not be used'); });
    });

    afterEach(() => {
        delete window.fetch;
    });

    test('loads the unread count and the profile through useHttp, never fetch', async () => {
        mockRequest.mockImplementation((url) => {
            if (url.includes('notifications/unread-count')) return Promise.resolve({ unread_count: 3 });
            if (url.includes('student/me')) return Promise.resolve({ full_name: 'Aziz Karimov', current_level: 'Advanced' });
            return Promise.resolve(null);
        });

        render(<AppHeader />);

        expect(await screen.findByText('3')).toBeInTheDocument();       // unread badge
        await waitFor(() => {
            expect(mockRequest).toHaveBeenCalledWith(expect.stringContaining('v1/student/me'), 'GET', null, {});
        });
        expect(mockRequest).toHaveBeenCalledWith(
            expect.stringContaining('v1/notifications/unread-count'), 'GET', null, {});
        expect(window.fetch).not.toHaveBeenCalled();
    });

    test('does not fetch the profile when the page already passes it in', async () => {
        mockRequest.mockResolvedValue({ unread_count: 0 });

        render(<AppHeader me={{ full_name: 'Aziz Karimov' }} />);

        await waitFor(() => expect(mockRequest).toHaveBeenCalled());
        expect(mockRequest).not.toHaveBeenCalledWith(
            expect.stringContaining('v1/student/me'), expect.anything(), expect.anything(), expect.anything());
    });

    test('survives failing requests: no badge, no crash', async () => {
        mockRequest.mockRejectedValue(new Error('network down'));

        render(<AppHeader />);

        await waitFor(() => expect(mockRequest).toHaveBeenCalled());
        expect(screen.getByRole('button', { name: /Меню/ })).toBeInTheDocument();
        expect(window.fetch).not.toHaveBeenCalled();
    });

    test('opens the navigation launcher', async () => {
        mockRequest.mockResolvedValue(null);

        render(<AppHeader />);
        fireEvent.click(screen.getByRole('button', { name: /Меню/ }));

        expect(await screen.findByText('Курсы')).toBeInTheDocument();
    });
});
