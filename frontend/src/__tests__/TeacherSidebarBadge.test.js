jest.mock('lucide-react', () => new Proxy({ __esModule: true }, {
    get: (t, p) => (p in t || typeof p === 'symbol' ? t[p] : () => null),
}));
const mockRequest = jest.fn();
jest.mock('../api/search/base', () => ({
    API_URL: 'http://test/api/', headers: () => ({}), useHttp: () => ({ request: mockRequest }),
}));
jest.mock('../context/StoreContext', () => ({ useStore: () => ({ equipped: {}, terminalMenuHidden: true }) }));
jest.mock('../components/sidebar/CoinChip', () => ({ __esModule: true, default: () => null }));

import React from 'react';
import { render, screen } from '@testing-library/react';
import TeacherSidebar from '../components/sidebar/TeacherSidebar';

beforeEach(() => mockRequest.mockReset());

test('the "Kod tekshiruvi" item shows how many checks wait for the teacher', async () => {
    mockRequest.mockResolvedValue({ count: 3, low: 5 });
    render(<TeacherSidebar activeTab="profile" onLogout={() => {}} username="t" />);
    expect(await screen.findByLabelText('3 ta kutayotgan tekshiruv')).toHaveTextContent('3');
    expect(mockRequest.mock.calls[0][0]).toBe('http://test/api/v1/teacher/code-checks/count');
});

test('no badge when nothing waits (fast-but-passed ones do not count)', async () => {
    mockRequest.mockResolvedValue({ count: 0, low: 7 });
    render(<TeacherSidebar activeTab="profile" onLogout={() => {}} username="t" />);
    await screen.findByText('Kod tekshiruvi');
    expect(screen.queryByLabelText(/kutayotgan tekshiruv/)).not.toBeInTheDocument();
});
