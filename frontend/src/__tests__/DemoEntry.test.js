jest.mock('lucide-react', () => new Proxy({ __esModule: true }, {
    get: (t, p) => (p in t || typeof p === 'symbol' ? t[p] : () => null),
}));

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DemoEntry, { validName } from '../views/auth/login/DemoEntry';

beforeEach(() => localStorage.setItem('lang', 'uz'));
afterEach(() => { delete window.fetch; });

describe('validName', () => {
    test('accepts Latin, Uzbek apostrophes, Cyrillic, hyphen and spaces', () => {
        ['Ali', "G'ulom", 'Oʻtkir', 'Анна', 'Мария-Луиза', 'Ali Vali'].forEach((n) => expect(validName(n)).toBe(true));
    });
    test('rejects digits, markup, links, one letter and empty', () => {
        ['A', '', '  ', 'Ali1', '<b>', 'http://x.co', 'a@b', 'x'.repeat(41)].forEach((n) => expect(validName(n)).toBe(false));
    });
});

describe('DemoEntry', () => {
    const setup = () => {
        const onLogin = jest.fn(); const navigate = jest.fn(); const onBack = jest.fn();
        render(<DemoEntry onLogin={onLogin} onBack={onBack} navigate={navigate} />);
        return { onLogin, navigate, onBack };
    };
    const fill = (first, last) => {
        fireEvent.change(screen.getByLabelText('Ism'), { target: { value: first } });
        fireEvent.change(screen.getByLabelText('Familiya'), { target: { value: last } });
    };

    test('the start button needs a valid first and last name', () => {
        setup();
        const btn = screen.getByRole('button', { name: /Demo darsni boshlash/ });
        expect(btn).toBeDisabled();
        fill('Ali', '');
        expect(btn).toBeDisabled();
        fill('Ali', 'Valiyev');
        expect(btn).toBeEnabled();
    });

    test('posts only the name, logs in for this tab only and opens the demo course', async () => {
        const { onLogin, navigate } = setup();
        window.fetch = jest.fn(() => Promise.resolve({
            ok: true, status: 201,
            json: () => Promise.resolve({ access_token: 't', user: { is_demo: true, role: 'student' } }),
        }));
        fill(' Ali ', 'Valiyev');
        fireEvent.click(screen.getByRole('button', { name: /Demo darsni boshlash/ }));

        await waitFor(() => expect(navigate).toHaveBeenCalledWith('/student/courses/9'));
        const [url, init] = window.fetch.mock.calls[0];
        expect(url).toMatch(/v1\/auth\/demo$/);
        expect(JSON.parse(init.body)).toEqual({ first_name: 'Ali', last_name: 'Valiyev' });
        expect(onLogin).toHaveBeenCalledWith(expect.objectContaining({ access_token: 't' }), false);
    });

    test('shows an error and does not log in when the server refuses', async () => {
        const { onLogin, navigate } = setup();
        window.fetch = jest.fn(() => Promise.resolve({ ok: false, status: 429, json: () => Promise.resolve({}) }));
        fill('Ali', 'Valiyev');
        fireEvent.click(screen.getByRole('button', { name: /Demo darsni boshlash/ }));
        expect(await screen.findByRole('alert')).toHaveTextContent(/Juda ko'p urinish/);
        expect(onLogin).not.toHaveBeenCalled();
        expect(navigate).not.toHaveBeenCalled();
    });

    test('the back button returns to the login form', () => {
        const { onBack } = setup();
        fireEvent.click(screen.getByRole('button', { name: /Kirishga qaytish/ }));
        expect(onBack).toHaveBeenCalled();
    });
});
