jest.mock('lucide-react', () => new Proxy({ __esModule: true }, {
    get: (t, p) => (p in t || typeof p === 'symbol' ? t[p] : () => null),
}));
const mockRequest = jest.fn();
jest.mock('../api/search/base', () => ({
    API_URL: 'http://test/api/', headers: () => ({}), useHttp: () => ({ request: mockRequest }),
}));
let socketHandler = null;
jest.mock('../api/notificationsSocket', () => ({
    subscribeNotifications: (fn) => { socketHandler = fn; return () => {}; },
    closeNotificationsSocket: () => {},
}));
jest.mock('../context/StoreContext', () => ({ useStore: () => ({ equipped: {}, terminalMenuHidden: true }) }));
jest.mock('../components/sidebar/CoinChip', () => ({ __esModule: true, default: () => null }));

import React from 'react';
import { render, screen, act } from '@testing-library/react';
import TeacherSidebar from '../components/sidebar/TeacherSidebar';

beforeEach(() => mockRequest.mockReset());

test('the "Kod tekshiruvi" item shows how many checks wait for the teacher', async () => {
    mockRequest.mockImplementation((url) => Promise.resolve(url.includes('unread-count') ? { unread_count: 0 } : { count: 3, low: 5 }));
    render(<TeacherSidebar activeTab="profile" onLogout={() => {}} username="t" />);
    expect(await screen.findByLabelText('3 ta kutayotgan tekshiruv')).toHaveTextContent('3');
    expect(mockRequest.mock.calls.some(([u]) => u === 'http://test/api/v1/teacher/code-checks/count')).toBe(true);
});

test('no badge when nothing waits (fast-but-passed ones do not count)', async () => {
    mockRequest.mockImplementation((url) => Promise.resolve(url.includes('unread-count') ? { unread_count: 0 } : { count: 0, low: 7 }));
    render(<TeacherSidebar activeTab="profile" onLogout={() => {}} username="t" />);
    await screen.findByText('Kod tekshiruvi');
    expect(screen.queryByLabelText(/kutayotgan tekshiruv/)).not.toBeInTheDocument();
});

test('unread notifications show a badge, kept live by the socket', async () => {
    mockRequest.mockImplementation((url) => Promise.resolve(url.includes('unread-count') ? { unread_count: 2 } : { count: 0, low: 0 }));
    render(<TeacherSidebar activeTab="profile" onLogout={() => {}} username="t" />);
    expect(await screen.findByLabelText("2 ta o'qilmagan bildirishnoma")).toHaveTextContent('2');
    act(() => socketHandler({ type: 'notification', unread_count: 5 }));
    expect(await screen.findByLabelText("5 ta o'qilmagan bildirishnoma")).toBeInTheDocument();
    act(() => socketHandler({ type: 'unread', unread_count: 0 }));
    expect(screen.queryByLabelText(/o'qilmagan bildirishnoma/)).not.toBeInTheDocument();
});
