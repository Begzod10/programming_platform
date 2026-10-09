jest.mock('lucide-react', () => new Proxy({ __esModule: true }, {
    get: (t, p) => (p in t || typeof p === 'symbol' ? t[p] : () => null),
}));

const mockRequest = jest.fn();
jest.mock('../api/search/base', () => ({
    API_URL: 'http://test/api/',
    headers: () => ({}),
    headersImg: () => ({}),
    resolveImageUrl: (s) => s || '',
    useHttp: () => ({ request: mockRequest }),
}));

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Profile, { apiErrorMessage } from '../views/student/profile/Profile';

const ME = {
    id: 1, username: 'afruz_web', email: 'afruz_web@gennis.uz', full_name: 'Afruzbek Abdujjaborov',
    phone: '993154318', identity_managed: true, total_points: 100, balance: 0, achievements: [], current_level: 'Advanced',
};

beforeEach(() => {
    localStorage.setItem('lang', 'uz');
    mockRequest.mockReset();
    mockRequest.mockImplementation((url, method) =>
        Promise.resolve(url.includes('student/me') && method === 'GET' ? ME : {}));
});

describe('apiErrorMessage', () => {
    test('reads the app-wrapped error, FastAPI detail and ignores the rest', () => {
        expect(apiErrorMessage({ response: { data: { error: { message: 'Bu xato' } } } })).toBe('Bu xato');
        expect(apiErrorMessage({ response: { data: { detail: 'Detail' } } })).toBe('Detail');
        expect(apiErrorMessage({ response: { data: { error: { message: { code: 'x' } } } } })).toBe('');
        expect(apiErrorMessage(new Error('boom'))).toBe('');
        expect(apiErrorMessage(null)).toBe('');
    });
});

describe('Profile personal info', () => {
    test('shows the username (read-only) where the email used to be', async () => {
        render(<Profile user={ME} onLogout={jest.fn()} />);
        const username = await screen.findByDisplayValue('afruz_web');
        expect(username).toHaveAttribute('readonly');
        expect(screen.queryByDisplayValue('afruz_web@gennis.uz')).not.toBeInTheDocument();
        expect(screen.queryByText(/Email manzil/)).not.toBeInTheDocument();
    });

    test('saves only the phone for a linked student, and shows the server message when it is refused', async () => {
        render(<Profile user={ME} onLogout={jest.fn()} />);
        const phone = await screen.findByDisplayValue('993154318');
        mockRequest.mockImplementation((url, method) => method === 'PUT'
            ? Promise.reject({ response: { data: { error: { message: "Ma'lumotlar asosiy tizimga saqlanmadi." } } } })
            : Promise.resolve(ME));
        fireEvent.change(phone, { target: { value: '911111111' } });
        fireEvent.click(screen.getByRole('button', { name: /O'zgarishlarni saqlash/ }));

        expect(await screen.findByText("Ma'lumotlar asosiy tizimga saqlanmadi.")).toBeInTheDocument();
        const put = mockRequest.mock.calls.find(([, method]) => method === 'PUT');
        expect(JSON.parse(put[2])).toEqual({ phone: '911111111' });
    });

    test('name and photo are read-only for a gennis/turon student', async () => {
        render(<Profile user={ME} onLogout={jest.fn()} />);
        expect(await screen.findByDisplayValue('Afruzbek Abdujjaborov')).toHaveAttribute('readonly');
        expect(screen.getByText(/Gennis\/Turon tizimidan olinadi/)).toBeInTheDocument();
        expect(document.querySelector('.pf-avatar-cam')).toBeNull();           // no camera badge
        fireEvent.click(document.querySelector('.pf-avatar-wrap'));
        expect(screen.queryByText(/Saqlash/)).not.toBeInTheDocument();         // the upload modal never opens
    });

    test('a local-only account can still edit its name and photo', async () => {
        const local = { ...ME, identity_managed: false };
        mockRequest.mockImplementation((url, method) => Promise.resolve(method === 'GET' ? local : {}));
        render(<Profile user={local} onLogout={jest.fn()} />);
        const name = await screen.findByDisplayValue('Afruzbek Abdujjaborov');
        expect(name).not.toHaveAttribute('readonly');
        expect(document.querySelector('.pf-avatar-cam')).not.toBeNull();
    });
});
