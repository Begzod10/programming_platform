import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import StickerAlbum from '../views/student/early-learning/StickerAlbum';

jest.mock('../api/search/base', () => {
    const request = jest.fn();
    return {
        useHttp: () => ({ request }), API_URL: '/api/', headers: () => ({}),
        getCurrentUser: () => ({ id: 7 }), resolveImageUrl: (u) => u,
    };
});

const { useHttp } = require('../api/search/base');

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
});

const renderAlbum = () => render(<MemoryRouter><StickerAlbum /></MemoryRouter>);

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
