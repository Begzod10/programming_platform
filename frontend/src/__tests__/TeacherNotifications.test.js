jest.mock('lucide-react', () => new Proxy({ __esModule: true }, {
    get: (t, p) => (p in t || typeof p === 'symbol' ? t[p] : () => null),
}));
const mockRequest = jest.fn();
const mockNavigate = jest.fn();
let socketHandler = null;
jest.mock('../api/search/base', () => ({ API_URL: 'http://test/api/', headers: () => ({}), useHttp: () => ({ request: mockRequest }) }));
jest.mock('../api/notificationsSocket', () => ({
    subscribeNotifications: (fn) => { socketHandler = fn; return () => { socketHandler = null; }; },
    closeNotificationsSocket: () => {},
}));
jest.mock('react-router-dom', () => ({ useNavigate: () => mockNavigate }), { virtual: true });

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import TeacherNotifications from '../views/teacher/notifications/TeacherNotifications';

const NOTE = { id: 1, type: 'code_check_teacher', title: "Kod tekshiruvi: e'tibor kerak", body: "Ali: «Capstone» — kod testidan o'tmadi.",
    link: '/teacher/code-checks', icon: '📝', is_read: false, created_at: new Date().toISOString() };

beforeEach(() => {
    mockRequest.mockReset(); mockNavigate.mockReset(); socketHandler = null;
    mockRequest.mockImplementation((url, method) => Promise.resolve(method === 'POST' ? { unread_count: 0 } : { items: [NOTE], unread_count: 1 }));
});

test('lists the notifications; opening one marks it read and goes to its link', async () => {
    render(<TeacherNotifications />);
    expect(await screen.findByText("Kod tekshiruvi: e'tibor kerak")).toBeInTheDocument();
    expect(screen.getByText('1 ta o\'qilmagan')).toBeInTheDocument();
    fireEvent.click(screen.getByText(/Capstone/));
    expect(mockNavigate).toHaveBeenCalledWith('/teacher/code-checks');
    expect(mockRequest.mock.calls.some(([u, m]) => u === 'http://test/api/v1/notifications/1/read' && m === 'POST')).toBe(true);
    expect(screen.getByText("Hammasi o'qilgan")).toBeInTheDocument();
});

test('a new notification arrives live over the socket', async () => {
    render(<TeacherNotifications />);
    await screen.findByText("Kod tekshiruvi: e'tibor kerak");
    act(() => socketHandler({ type: 'notification', notification: { ...NOTE, id: 2, title: 'Yangi: Vali', body: 'x' }, unread_count: 2 }));
    expect(await screen.findByText('Yangi: Vali')).toBeInTheDocument();
    act(() => socketHandler({ type: 'notification', notification: { ...NOTE, id: 2, title: 'Yangi: Vali' }, unread_count: 2 }));   // duplicate frame
    expect(screen.getAllByText('Yangi: Vali')).toHaveLength(1);
});

test('mark all read, and an empty list says so', async () => {
    render(<TeacherNotifications />);
    fireEvent.click(await screen.findByRole('button', { name: "Hammasini o'qilgan qilish" }));
    expect(mockRequest.mock.calls.some(([u, m]) => u.endsWith('/notifications/read-all') && m === 'POST')).toBe(true);
    expect(screen.queryByRole('button', { name: "Hammasini o'qilgan qilish" })).not.toBeInTheDocument();
});

test('empty state', async () => {
    mockRequest.mockResolvedValue({ items: [], unread_count: 0 });
    render(<TeacherNotifications />);
    expect(await screen.findByText("Hozircha bildirishnoma yo'q.")).toBeInTheDocument();
});
