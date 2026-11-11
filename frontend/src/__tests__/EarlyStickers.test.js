import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import StickerAlbum from '../views/student/early-learning/StickerAlbum';
import StickerStrip from '../views/student/early-learning/StickerStrip';
import StickerReveal from '../views/student/early-learning/StickerReveal';
import EarlyLearning from '../views/student/early-learning/EarlyLearning';
import translations from '../i18n/translations';

jest.mock('../api/search/base', () => {
    const request = jest.fn();
    return {
        useHttp: () => ({ request }), API_URL: '/api/', headers: () => ({}),
        getCurrentUser: () => ({ id: 7 }), resolveImageUrl: (u) => u,
    };
});

// The project stubs react-router-dom for every test (see setupTests.js);
// this file needs a controllable location, params and navigate spy.
const mockNavigate = jest.fn();
let mockPath = '/student/early-learning';
let mockParams = {};
jest.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
    useLocation: () => ({ pathname: mockPath, search: '', hash: '', state: null }),
    useParams: () => mockParams,
}), { virtual: true });
jest.mock('../hooks/useDailyQuota', () => ({ useDailyQuota: () => ({ loading: false, unlocked: true }) }));
jest.mock('../components/QuotaLockScreen', () => () => null);
jest.mock('../views/student/early-learning/MatchingActivity', () => ({ onComplete }) => (
    <button onClick={() => onComplete(global.__completionResult)}>finish-game</button>
));

const { useHttp } = require('../api/search/base');
const t = (key) => translations.uz[key] || key;

const sticker = (over) => ({
    key: 'star:10', emoji: '🐱', name: 'Mushuk', kind: 'star', rarity: 'common',
    owned: true, is_new: false, hint: null, ...over,
});
const ALBUM = {
    owned_count: 1, total: 101, streak: 0,
    today: { played: 0, needed: 3, earned: false },
    next_star: { at: 20, have: 12 },
    stickers: [
        sticker(),
        sticker({ key: 'star:20', emoji: '🐶', name: 'Kuchuk', owned: false, hint: "20 yulduz yig'" }),
        sticker({ key: 'daily:01', emoji: '🚗', name: 'Mashina', kind: 'daily', owned: false, hint: "Bir kunda 3 ta o'yin o'yna" }),
        sticker({ key: 'streak:3', emoji: '🥉', name: '3 kun', kind: 'streak', rarity: 'epic', owned: false, hint: "3 kun ketma-ket o'yna" }),
        sticker({ key: 'module:5', emoji: '🎨', name: 'Rang olami', kind: 'module', rarity: 'rare', owned: false, hint: '«Rang olami»ni tugat' }),
    ],
};

let request;
const seenCalls = () => request.mock.calls.filter(([url]) => url.includes('stickers/seen'));

beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    localStorage.setItem('lang', 'uz');
    request = useHttp().request;
    mockPath = '/student/early-learning';
    mockParams = {};
});

const renderAlbum = () => render(<StickerAlbum />);

describe('sticker album', () => {
    test('shows owned sticker name, locked hint and the count', async () => {
        request.mockResolvedValue(ALBUM);
        renderAlbum();
        expect(await screen.findByText('Mushuk')).toBeInTheDocument();
        expect(screen.getByText("20 yulduz yig'")).toBeInTheDocument();
        expect(screen.queryByText('Kuchuk')).not.toBeInTheDocument();
        expect(screen.getByText('1 / 101')).toBeInTheDocument();
        expect(screen.getByText('Yulduz stikerlari')).toBeInTheDocument();
        expect(screen.getByText('Modul nishonlari')).toBeInTheDocument();
        expect(request.mock.calls[0][0]).toContain('v1/early-learning/stickers?lang=uz');
    });

    test('marks new stickers as seen once', async () => {
        request.mockImplementation((url) => Promise.resolve(
            url.includes('stickers/seen') ? { marked: 1 } : { ...ALBUM, stickers: [sticker({ is_new: true })] }
        ));
        renderAlbum();
        expect(await screen.findByText('Yangi!')).toBeInTheDocument();
        await waitFor(() => expect(seenCalls()).toHaveLength(1));
        expect(seenCalls()[0][1]).toBe('POST');
        expect(screen.getByText('Yangi!')).toBeInTheDocument();
    });

    test('without new stickers does not call seen', async () => {
        request.mockResolvedValue(ALBUM);
        renderAlbum();
        await screen.findByText('Mushuk');
        expect(seenCalls()).toHaveLength(0);
    });

    test('shows an error when the request fails', async () => {
        request.mockRejectedValue(new Error('offline'));
        renderAlbum();
        expect(await screen.findByText("Kolleksiya ochilmadi, keyinroq urinib ko'ring.")).toBeInTheDocument();
        expect(screen.getByText('Qaytish')).toBeInTheDocument();
    });

    test('uses Russian headings when the language is Russian', async () => {
        localStorage.setItem('lang', 'ru');
        request.mockResolvedValue(ALBUM);
        renderAlbum();
        expect(await screen.findByText('Наклейки за звёзды')).toBeInTheDocument();
        expect(request.mock.calls[0][0]).toContain('lang=ru');
    });
});

const STRIP = {
    owned_count: 12, total: 101, streak: 3,
    today: { played: 1, needed: 3, earned: false },
    next_star: { at: 130, have: 126 },
    stickers: [sticker()],
};

describe('sticker strip', () => {
    test('shows count, remaining stars, plays today and streak', () => {
        const onOpen = jest.fn();
        render(<StickerStrip album={STRIP} t={t} onOpen={onOpen} />);
        expect(screen.getByText(/12\/101/)).toBeInTheDocument();
        expect(screen.getByText('Keyingi stikergacha 4 yulduz')).toBeInTheDocument();
        expect(screen.getByText("Bugun 1/3 o'yin")).toBeInTheDocument();
        expect(screen.getByText('🔥 3')).toBeInTheDocument();
        expect(screen.queryByLabelText('Yangi!')).not.toBeInTheDocument();
        fireEvent.click(screen.getByRole('button'));
        expect(onOpen).toHaveBeenCalledTimes(1);
    });

    test('shows today done, no streak at zero, and a dot for unseen stickers', () => {
        render(<StickerStrip t={t} onOpen={() => {}} album={{
            ...STRIP, streak: 0, today: { played: 3, needed: 3, earned: true }, stickers: [sticker({ is_new: true })],
        }} />);
        expect(screen.getByText('Bugungi stiker olindi ✓')).toBeInTheDocument();
        expect(screen.queryByText(/🔥/)).not.toBeInTheDocument();
        expect(screen.getByLabelText('Yangi!')).toBeInTheDocument();
    });

    test('hides the progress bar when every star sticker is owned', () => {
        render(<StickerStrip t={t} onOpen={() => {}} album={{ ...STRIP, next_star: null }} />);
        expect(screen.queryByText(/Keyingi stikergacha/)).not.toBeInTheDocument();
        expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
});

const NEW = [1, 2, 3, 4, 5].map((n) => ({
    key: `star:${n}0`, emoji: '🐱', name: `Uz${n}`, name_ru: `Ru${n}`, kind: 'star', rarity: 'common',
}));

describe('sticker reveal', () => {
    test('shows three stickers and +N', () => {
        render(<StickerReveal stickers={NEW} lang="uz" t={t} onClose={() => {}} onOpenAlbum={() => {}} />);
        expect(screen.getByText('Yangi stiker!')).toBeInTheDocument();
        expect(screen.getByText('Uz1')).toBeInTheDocument();
        expect(screen.getByText('Uz3')).toBeInTheDocument();
        expect(screen.queryByText('Uz4')).not.toBeInTheDocument();
        expect(screen.getByText('+2')).toBeInTheDocument();
    });

    test('uses Russian names for Russian and no +N for a single sticker', () => {
        render(<StickerReveal stickers={NEW.slice(0, 1)} lang="ru" t={t} onClose={() => {}} onOpenAlbum={() => {}} />);
        expect(screen.getByText('Ru1')).toBeInTheDocument();
        expect(screen.queryByText(/^\+/)).not.toBeInTheDocument();
    });

    test('buttons call onClose and onOpenAlbum', () => {
        const onClose = jest.fn();
        const onOpenAlbum = jest.fn();
        render(<StickerReveal stickers={NEW} lang="uz" t={t} onClose={onClose} onOpenAlbum={onOpenAlbum} />);
        fireEvent.click(screen.getByText('Kolleksiyamga'));
        expect(onOpenAlbum).toHaveBeenCalledTimes(1);
        fireEvent.click(screen.getByText('Davom etish →'));
        expect(onClose).toHaveBeenCalledTimes(1);
    });
});

const MODULES = [{ id: 5, title: 'Rang olami', description: '', icon_emoji: '🎨', earned_stars: 2, max_stars: 30, earned_stars_today: 0 }];
const DETAIL = {
    ...MODULES[0],
    activities: [{ id: 1, title: 'Qizil', best_stars: 0, attempts: 0, content: { mode: 'select' } }],
};
const BOARD = { has_class: true, entries: [{ student_id: 7, name: 'Ali', total_stars: 2, rank: 1, is_me: true }] };

const route = (albumReply) => (url) => {
    if (url.includes('/stickers')) return albumReply();
    if (url.includes('leaderboard')) return Promise.resolve(BOARD);
    if (/modules\/\d+/.test(url)) return Promise.resolve(DETAIL);
    if (url.includes('modules')) return Promise.resolve(MODULES);
    return Promise.resolve({});
};
const urls = (part) => request.mock.calls.map(([url]) => url).filter((url) => url.includes(part));

const renderHome = ({ guest = false, moduleId } = {}) => {
    mockPath = guest ? '/play' : `/student/early-learning${moduleId ? `/${moduleId}` : ''}`;
    mockParams = moduleId ? { moduleId: String(moduleId) } : {};
    return render(<EarlyLearning guest={guest} />);
};

describe('games home', () => {
    test('shows the strip and opens the album', async () => {
        request.mockImplementation(route(() => Promise.resolve(STRIP)));
        renderHome();
        fireEvent.click(await screen.findByText(/12\/101/));
        expect(mockNavigate).toHaveBeenCalledWith('/student/stickers');
    });

    test('strip hidden when the request fails', async () => {
        request.mockImplementation(route(() => Promise.reject(new Error('423'))));
        renderHome();
        expect(await screen.findByText('Rang olami')).toBeInTheDocument();
        await waitFor(() => expect(urls('/stickers')).toHaveLength(1));
        expect(screen.queryByText(/Kolleksiyam/)).not.toBeInTheDocument();
    });

    test('guest sees the sign-in invite instead of the strip', async () => {
        request.mockImplementation(route(() => Promise.resolve(STRIP)));
        renderHome({ guest: true });
        expect(await screen.findByText(/Kirsang, stiker yig'asan!/)).toBeInTheDocument();
        expect(urls('/stickers')).toHaveLength(0);
        fireEvent.click(screen.getByText('Kirish'));
        expect(mockNavigate).toHaveBeenCalledWith('/login');
    });

    test('daily button hides the browser streak for signed-in students but not guests', async () => {
        const { recordDaily } = require('../views/student/early-learning/earlyLearningUtils');
        recordDaily();
        request.mockImplementation(route(() => Promise.resolve(STRIP)));
        const student = renderHome();
        expect((await screen.findByText(/Kunlik vazifa/)).textContent).not.toContain('🔥');
        student.unmount();
        renderHome({ guest: true });
        expect((await screen.findByText(/Kunlik vazifa/)).textContent).toContain('🔥1');
    });

    test('leaderboard defaults to today and switches period', async () => {
        request.mockImplementation(route(() => Promise.resolve(STRIP)));
        renderHome();
        await screen.findByText(/Ali/);
        expect(urls('leaderboard')[0]).toContain('period=today');
        fireEvent.click(screen.getByText('Umumiy'));
        await waitFor(() => expect(urls('leaderboard').some((u) => u.includes('period=all_time'))).toBe(true));
    });

    test('finishing a game that earned stickers shows the reveal', async () => {
        global.__completionResult = { activity_id: 1, stars_earned: 3, attempts: 1, new_stickers: NEW.slice(0, 1) };
        request.mockImplementation(route(() => Promise.resolve(STRIP)));
        renderHome({ moduleId: 5 });
        fireEvent.click(await screen.findByText('Qizil'));
        fireEvent.click(await screen.findByText('finish-game'));
        expect(await screen.findByText('Yangi stiker!')).toBeInTheDocument();
        expect(screen.getByText('Uz1')).toBeInTheDocument();
        fireEvent.click(screen.getByText('Kolleksiyamga'));
        expect(mockNavigate).toHaveBeenCalledWith('/student/stickers');
        await waitFor(() => expect(screen.queryByText('Yangi stiker!')).not.toBeInTheDocument());
    });

    test('teacher preview gets the games and leaderboard but no strip', async () => {
        request.mockImplementation(route(() => Promise.resolve(STRIP)));
        mockPath = '/teacher/early-learning';
        render(<EarlyLearning />);
        expect(await screen.findByText('Rang olami')).toBeInTheDocument();
        await screen.findByText(/Ali/);
        expect(urls('/stickers')).toHaveLength(0);
        expect(screen.queryByText(/Kolleksiyam/)).not.toBeInTheDocument();
    });

    test('an offline completion (no server reply) shows no reveal', async () => {
        global.__completionResult = { stars_earned: 3, attempts: 1 };
        request.mockImplementation(route(() => Promise.resolve(STRIP)));
        renderHome({ moduleId: 5 });
        fireEvent.click(await screen.findByText('Qizil'));
        fireEvent.click(await screen.findByText('finish-game'));
        await screen.findByText('Qizil');
        expect(screen.queryByText('Yangi stiker!')).not.toBeInTheDocument();
    });

    test('finishing a game without stickers shows no reveal', async () => {
        global.__completionResult = { activity_id: 1, stars_earned: 3, attempts: 1, new_stickers: [] };
        request.mockImplementation(route(() => Promise.resolve(STRIP)));
        renderHome({ moduleId: 5 });
        fireEvent.click(await screen.findByText('Qizil'));
        fireEvent.click(await screen.findByText('finish-game'));
        await screen.findByText('Qizil');
        expect(screen.queryByText('Yangi stiker!')).not.toBeInTheDocument();
    });
});
