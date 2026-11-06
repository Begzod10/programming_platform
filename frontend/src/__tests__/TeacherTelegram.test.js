import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TeacherTelegram from '../views/teacher/telegram/TeacherTelegram';

jest.mock('../api/search/base', () => {
    const request = jest.fn();
    return { useHttp: () => ({ request }), API_URL: '/api/', headers: () => ({}), resolveImageUrl: u => u };
});
const { useHttp } = require('../api/search/base');

const CHAT = { id: 4, title: '7-A guruhi', is_active: true, linked_at: '2026-11-06T10:00:00Z', last_error: null,
    students: [{ id: 1, name: 'Ali Valiyev' }] };
const STUDENTS = [
    { id: 1, name: 'Ali Valiyev', classes: ['7-A'] },
    { id: 2, name: 'Bobur Aliyev', classes: ['7-A'] },
    { id: 3, name: 'Vali Karimov', classes: ['8-B'] },
];

let request;
const setup = (chats = [CHAT]) => {
    request.mockImplementation((url, method) => {
        if (url.endsWith('/link-code')) return Promise.resolve({ code: 'abc', url: 'https://t.me/gennis_parent_bot?startgroup=abc', expires_at: '2026-11-06T11:00:00Z' });
        if (url.includes('/students') && method === 'GET') return Promise.resolve(STUDENTS);
        if (url.includes('/students') && method === 'PUT') return Promise.resolve({ students: [] });
        if (url.endsWith('/chats') && method === 'GET') return Promise.resolve(chats);
        return Promise.resolve({});
    });
    render(<TeacherTelegram />);
};
const calls = (needle, method) => request.mock.calls.filter(c => c[0].includes(needle) && c[1] === method);

beforeEach(() => {
    jest.clearAllMocks();
    localStorage.setItem('lang', 'uz');
    request = useHttp().request;
});

describe('TeacherTelegram', () => {
    it('shows an empty state and the parents bot link when there are no chats', async () => {
        setup([]);
        expect(await screen.findByText(/Hali guruh ulanmagan/)).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /@gennis_parent_bot/ })).toHaveAttribute('href', 'https://t.me/gennis_parent_bot');
    });

    it('lists a chat with its status and selected-student count; a removed bot is flagged', async () => {
        setup([CHAT, { ...CHAT, id: 5, title: 'Eski guruh', is_active: false, students: [] }]);
        expect(await screen.findByText('7-A guruhi')).toBeInTheDocument();
        expect(screen.getByText(/1 ta o'quvchi/)).toBeInTheDocument();
        expect(screen.getByText(/Bot guruhdan chiqarilgan/)).toBeInTheDocument();
    });

    it('creating a code shows the t.me link and the one-hour note', async () => {
        setup([]);
        fireEvent.click(await screen.findByRole('button', { name: /Guruh qo'shish/ }));
        const link = await screen.findByRole('link', { name: /Telegramda ochish/ });
        expect(link).toHaveAttribute('href', 'https://t.me/gennis_parent_bot?startgroup=abc');
        expect(screen.getByText(/1 soat amal qiladi/)).toBeInTheDocument();
        expect(calls('/link-code', 'POST')).toHaveLength(1);
    });

    it('selecting students saves them with PUT', async () => {
        setup();
        fireEvent.click(await screen.findByRole('button', { name: /O'quvchilarni tanlash/ }));
        fireEvent.click(await screen.findByLabelText('Bobur Aliyev'));
        fireEvent.click(screen.getByRole('button', { name: /Saqlash/ }));
        await waitFor(() => expect(calls('/chats/4/students', 'PUT')).toHaveLength(1));
        expect(JSON.parse(calls('/chats/4/students', 'PUT')[0][2]).student_ids.sort()).toEqual([1, 2]);
    });

    it('the class shortcut ticks every student of that class', async () => {
        setup([{ ...CHAT, students: [] }]);
        fireEvent.click(await screen.findByRole('button', { name: /O'quvchilarni tanlash/ }));
        fireEvent.click(await screen.findByRole('button', { name: /Sinfni belgilash: 7-A/ }));
        expect(screen.getByLabelText('Ali Valiyev')).toBeChecked();
        expect(screen.getByLabelText('Bobur Aliyev')).toBeChecked();
        expect(screen.getByLabelText('Vali Karimov')).not.toBeChecked();
    });

    it('disconnect asks for confirmation then deletes', async () => {
        setup();
        fireEvent.click(await screen.findByRole('button', { name: /^Uzish/ }));
        expect(calls('/chats/4', 'DELETE')).toHaveLength(0);
        fireEvent.click(screen.getByRole('button', { name: /Ha, uzish/ }));
        await waitFor(() => expect(calls('/chats/4', 'DELETE')).toHaveLength(1));
        await waitFor(() => expect(screen.queryByText('7-A guruhi')).toBeNull());
    });
});
