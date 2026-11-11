import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import EarlyLearning from '../views/student/early-learning/EarlyLearning';
import { elCacheKey, elCacheSet } from '../views/student/early-learning/earlyLearningUtils';

jest.mock('../api/search/base', () => {
    const request = jest.fn();
    return {
        useHttp: () => ({ request }), API_URL: '/api/', headers: () => ({}),
        getCurrentUser: () => ({ id: 7 }), resolveImageUrl: (u) => u,
    };
});
// The project stubs react-router-dom for every test (see setupTests.js);
// this file needs a controllable location (with state), params and navigate spy.
const mockNavigate = jest.fn();
let mockPath = '/student/early-learning';
let mockParams = {};
let mockState = null;
jest.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
    useLocation: () => ({ pathname: mockPath, search: '', hash: '', state: mockState }),
    useParams: () => mockParams,
}), { virtual: true });
jest.mock('../hooks/useDailyQuota', () => ({ useDailyQuota: () => ({ loading: false, unlocked: true }) }));
jest.mock('../components/QuotaLockScreen', () => () => null);
jest.mock('../views/student/early-learning/MatchingActivity', () => ({ activity, onBack }) => (
    <div>
        <span>{`playing-${activity.id}`}</span>
        <button onClick={onBack}>leave-game</button>
    </div>
));

const { useHttp } = require('../api/search/base');

const mod = (id, over) => ({
    id, title: `Modul ${id}`, description: `Tavsif ${id}`, icon_emoji: '🎲', display_order: id,
    activities_count: 10, completed_count: 0, last_played_at: null, section: 'world',
    earned_stars: 0, max_stars: 30, earned_stars_today: 0, ...over,
});
const A = mod(1, { title: 'Kasblar', completed_count: 3, last_played_at: '2026-11-10T10:00:00Z', earned_stars: 9 });
const B = mod(2, { title: 'Sanash', section: 'logic' });
const C = mod(3, { title: 'Fasllar' });
const D = mod(4, { title: 'Klaviatura', section: 'letters', completed_count: 10, earned_stars: 30 });

const activity = (id, order, attempts) => ({
    id, order, attempts, best_stars: attempts ? 3 : 0, title: `Game ${id}`,
    content: { mode: 'select', character: { emoji: '🍎', label: `Qizil ${id}` } },
});
const detail = (attempts) => ({ ...A, activities: attempts.map((n, i) => activity(11 + i, i, n)) });

let request;
let modules;
let moduleDetail;
const route = (url) => {
    if (url.includes('/stickers')) return Promise.reject(new Error('no album in this test'));
    if (url.includes('leaderboard')) return Promise.resolve({ has_class: false, entries: [] });
    if (/modules\/\d+/.test(url)) return Promise.resolve(moduleDetail);
    if (url.includes('modules')) return Promise.resolve(modules);
    return Promise.resolve({});
};

beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    localStorage.setItem('lang', 'uz');
    request = useHttp().request;
    request.mockImplementation(route);
    modules = [A, B, C, D];
    moduleDetail = detail([1, 0, 0]);
    mockPath = '/student/early-learning';
    mockParams = {};
    mockState = null;
});

const renderHome = ({ guest = false } = {}) => {
    mockPath = guest ? '/play' : '/student/early-learning';
    return render(<EarlyLearning guest={guest} />);
};
const renderModule = (state = null) => {
    mockPath = '/student/early-learning/1';
    mockParams = { moduleId: '1' };
    mockState = state;
    return render(<EarlyLearning />);
};
const headings = () => screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent);

describe('games home page', () => {
    test('shows continue, new-for-you and sections', async () => {
        renderHome();
        expect(await screen.findByText('Davom et')).toBeInTheDocument();
        expect(screen.getByText("3 / 10 o'yin")).toBeInTheDocument();
        const all = headings();
        expect(all.some((h) => h.includes('Sen uchun yangi'))).toBe(true);
        expect(all.some((h) => h.includes('Atrofimizdagi dunyo'))).toBe(true);
        expect(all.some((h) => h.includes('Sanoq va mantiq'))).toBe(true);
        expect(all.some((h) => h.includes('Harf va klaviatura'))).toBe(true);
        expect(all.some((h) => h.includes('Chizish va yasash'))).toBe(false);
        expect(screen.queryByText('Tavsif 2')).not.toBeInTheDocument();
        expect(screen.getByLabelText('Tugallandi')).toBeInTheDocument();
        // untouched modules appear in the "new" row and in their own section
        expect(screen.getAllByText('Sanash')).toHaveLength(2);
        // the continue module: once on the card, once in its section
        expect(screen.getAllByText('Kasblar')).toHaveLength(2);
    });

    test('continue navigates with autoplay', async () => {
        renderHome();
        fireEvent.click((await screen.findByText('Davom et')).closest('button'));
        expect(mockNavigate).toHaveBeenCalledWith('/student/early-learning/1', { state: { autoplay: true } });
    });

    test('a module card opens its module without autoplay', async () => {
        renderHome();
        await screen.findByText('Davom et');
        fireEvent.click(screen.getByText('Klaviatura').closest('button'));
        expect(mockNavigate).toHaveBeenCalledWith('/student/early-learning/4');
    });

    test('fresh player sees Boshlash and no new-for-you row', async () => {
        modules = [mod(1), mod(2, { section: 'logic' })];
        renderHome();
        expect(await screen.findByText('Boshlash')).toBeInTheDocument();
        expect(headings().some((h) => h.includes('Sen uchun yangi'))).toBe(false);
    });

    test('no continue card when everything is finished', async () => {
        modules = [D];
        renderHome();
        expect(await screen.findByText('Klaviatura')).toBeInTheDocument();
        expect(screen.queryByText('Davom et')).not.toBeInTheDocument();
        expect(screen.queryByText('Boshlash')).not.toBeInTheDocument();
    });

    test('guest home has continue and sections', async () => {
        modules = [
            { ...mod(1, { title: 'Kasblar' }), activity_ids: [11, 12] },
            { ...mod(2, { title: 'Sanash', section: 'logic' }), activity_ids: [21] },
        ];
        localStorage.setItem('el_guest_progress', JSON.stringify({ 11: { stars_earned: 3, attempts: 1 } }));
        renderHome({ guest: true });
        expect(await screen.findByText('Davom et')).toBeInTheDocument();
        expect(screen.getByText("1 / 10 o'yin")).toBeInTheDocument();
        expect(headings().some((h) => h.includes('Sanoq va mantiq'))).toBe(true);
        fireEvent.click(screen.getByText('Davom et').closest('button'));
        expect(mockNavigate).toHaveBeenCalledWith('/play/1', { state: { autoplay: true } });
    });

    test('old cached list without new fields still renders', async () => {
        elCacheSet(elCacheKey(false, 7, 'modules', 'uz'), [
            { id: 9, title: 'Eski modul', icon_emoji: '🧸', display_order: 1, activities_count: 10, earned_stars: 3, max_stars: 30 },
        ]);
        request.mockImplementation((url) => (url.includes('modules') ? Promise.reject(new Error('offline')) : route(url)));
        renderHome();
        expect((await screen.findAllByText('Eski modul')).length).toBeGreaterThan(0);
        expect(headings().some((h) => h.includes('Atrofimizdagi dunyo'))).toBe(true);
        expect(screen.getByText('Boshlash')).toBeInTheDocument();
    });
});

describe('module page path', () => {
    test('shows the path and plays a clicked game', async () => {
        renderModule();
        expect(await screen.findByText('Qizil 13')).toBeInTheDocument();
        expect(screen.getByText("Keyingi o'yin ▶")).toBeInTheDocument();
        expect(screen.queryByText(/^playing-/)).not.toBeInTheDocument();
        fireEvent.click(screen.getByText('Qizil 13').closest('button'));
        expect(await screen.findByText('playing-13')).toBeInTheDocument();
    });

    test('autoplay opens the next game once', async () => {
        renderModule({ autoplay: true });
        expect(await screen.findByText('playing-12')).toBeInTheDocument();
        fireEvent.click(screen.getByText('leave-game'));
        expect(await screen.findByText('Qizil 12')).toBeInTheDocument();
        await waitFor(() => expect(screen.queryByText(/^playing-/)).not.toBeInTheDocument());
    });

    test('autoplay does nothing when every game was played', async () => {
        moduleDetail = detail([1, 2, 1]);
        renderModule({ autoplay: true });
        expect(await screen.findByText('Qizil 11')).toBeInTheDocument();
        expect(screen.queryByText(/^playing-/)).not.toBeInTheDocument();
        expect(screen.queryByText("Keyingi o'yin ▶")).not.toBeInTheDocument();
    });
});
