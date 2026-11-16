import React from 'react';
import { render, screen } from '@testing-library/react';
import EarlyLearning from '../views/student/early-learning/EarlyLearning';

jest.mock('../api/search/base', () => {
    const request = jest.fn();
    return {
        __request: request, useHttp: () => ({ request }), API_URL: '/api/', headers: () => ({}),
        getCurrentUser: () => ({ id: 7 }), resolveImageUrl: (u) => u,
    };
});
jest.mock('react-router-dom', () => ({
    useNavigate: () => jest.fn(),
    useLocation: () => ({ pathname: '/student/early-learning/1', search: '', hash: '', state: { autoplay: true }, key: 'k1' }),
    useParams: () => ({ moduleId: '1' }),
}), { virtual: true });
jest.mock('../hooks/useDailyQuota', () => ({ useDailyQuota: () => ({ loading: false, unlocked: true }) }));
jest.mock('../components/QuotaLockScreen', () => () => null);
const stub = (name) => function Stub({ activity }) {
    return <span>{`${name}-${activity.id}-${(activity.content?.correct_items || []).length}`}</span>;
};
jest.mock('../views/student/early-learning/MatchingActivity', () => stub('matching'));
jest.mock('../views/student/early-learning/CollectActivity', () => stub('collect'));
jest.mock('../views/student/early-learning/ConnectActivity', () => stub('connect'));
jest.mock('../views/student/early-learning/CatchActivity', () => stub('catch'));
jest.mock('../views/student/early-learning/DragSortActivity', () => stub('dragsort'));

const { __request: request } = require('../api/search/base');

const items = (p, n) => Array.from({ length: n }, (_, i) => ({ id: `${p}${i}`, label: `${p} ${i}`, emoji: ['🍎', '🍐', '🍌', '🍇'][i] }));
const content = (mode, over = {}) => ({
    mode, character: { emoji: '🧺', label: 'Savat' }, correct_items: items('Meva', 4), distractor_items: items('Narsa', 2), ...over,
});

function open(mode, over) {
    const detail = {
        id: 1, title: 'Modul', activities: [{ id: 21, order: 0, attempts: 0, best_stars: 0, title: 'G', content: content(mode, over) }],
    };
    request.mockImplementation((url) => {
        if (/modules\/\d+/.test(url)) return Promise.resolve(detail);
        if (url.includes('modules')) return Promise.resolve([]);
        return Promise.reject(new Error('not in this test'));
    });
    return render(<EarlyLearning />);
}

beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    localStorage.setItem('lang', 'uz');
});

test('the games page opens collect and connect for their modes', async () => {
    open('collect');
    expect(await screen.findByText('collect-21-4')).toBeInTheDocument();
});

test('the games page opens connect for its mode', async () => {
    open('connect');
    expect(await screen.findByText('connect-21-4')).toBeInTheDocument();
});

test('the games page opens catch and dragsort for their modes', async () => {
    open('catch');
    expect(await screen.findByText('catch-21-4')).toBeInTheDocument();
});

const partner = { character: { emoji: '👩‍⚕️', label: 'Shifokor' },
    correct_items: [{ id: 'p0', label: 'Shprits', emoji: '💉' }, { id: 'p1', label: 'Dori', emoji: '💊' }, { id: 'p2', label: 'Bint', emoji: '🩹' }] };

test('the games page opens dragsort when it has a partner', async () => {
    open('dragsort', { partner });
    expect(await screen.findByText('dragsort-21-4')).toBeInTheDocument();
});

test('dragsort without a partner plays as connect', async () => {
    open('dragsort');
    expect(await screen.findByText('connect-21-4')).toBeInTheDocument();
});
