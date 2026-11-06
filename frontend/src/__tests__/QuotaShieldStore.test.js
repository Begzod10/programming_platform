import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Store from '../views/student/store/Store';
import DailyRules from '../views/student/dailyrules/DailyRules';
import { present } from '../views/student/notifications/Notifications';

jest.mock('../api/search/base', () => {
    const request = jest.fn();
    return { useHttp: () => ({ request }), API_URL: '/api/', headers: () => ({}), resolveImageUrl: u => u };
});
jest.mock('../context/StoreContext', () => ({ useStore: jest.fn() }));
jest.mock('../components/appheader/AppHeader', () => () => null);
jest.mock('../api/notificationsSocket', () => ({ subscribeNotifications: () => () => {} }));

const { useHttp } = require('../api/search/base');
const { useStore } = require('../context/StoreContext');

const SHIELD = {
    id: 9, kind: 'boost', slug: 'quota_shield', title: 'Norma himoyasi', title_ru: 'Защита нормы',
    description: 'tavsif', description_ru: 'описание', price_coins: 500, can_afford: true, owned: false,
    purchasable: true, asset_ref: { effect: 'quota_shield', max_owned: 2 },
};
const THEME = {
    id: 1, kind: 'theme', slug: 'theme.x', title: 'Tema', price_coins: 100, can_afford: true, owned: true,
    purchasable: true, asset_ref: { tokens: {} },
};

let request;
const setStore = (inventory, balance = 1000) => useStore.mockReturnValue({
    balance, lifetimePoints: 1000, inventory, refreshAll: jest.fn().mockResolvedValue(null),
});

beforeEach(() => {
    jest.clearAllMocks();
    localStorage.setItem('lang', 'uz');
    request = useHttp().request;
    request.mockImplementation((url) => Promise.resolve(url.includes('/items') ? [SHIELD, THEME] : {}));
});

const openShieldTab = async () => {
    render(<Store />);
    fireEvent.click(await screen.findByRole('button', { name: /Himoya/ }));
};

describe('Himoya tab in the store', () => {
    it('shows the stock as 1/2', async () => {
        setStore([{ store_item_id: 9, kind: 'boost', quantity: 1, inventory_id: 5 }]);
        await openShieldTab();
        expect(screen.getByText(/1\s*\/\s*2/)).toBeInTheDocument();
    });

    it('buying calls the purchase endpoint with the shield id', async () => {
        setStore([]);
        await openShieldTab();
        fireEvent.click(screen.getByRole('button', { name: /500/ }));
        await waitFor(() => expect(request.mock.calls.some(c => c[0].includes('/store/purchase'))).toBe(true));
        const call = request.mock.calls.find(c => c[0].includes('/store/purchase'));
        expect(JSON.parse(call[2]).store_item_id).toBe(9);
    });

    it('at the stock cap the buy button is disabled and says why', async () => {
        setStore([{ store_item_id: 9, kind: 'boost', quantity: 2, inventory_id: 5 }]);
        await openShieldTab();
        expect(screen.getByRole('button', { name: /500/ })).toBeDisabled();
        expect(screen.getByText(/zaxira to'lgan/i)).toBeInTheDocument();
    });

    it('a 409 shows the stock-full message, not "already owned"', async () => {
        setStore([]);
        request.mockImplementation((url) => url.includes('/store/purchase')
            ? Promise.reject(new Error('409')) : Promise.resolve(url.includes('/items') ? [SHIELD] : {}));
        await openShieldTab();
        fireEvent.click(screen.getByRole('button', { name: /500/ }));
        expect(await screen.findByText(/Zaxira to'lgan/)).toBeInTheDocument();
        expect(screen.queryByText(/Allaqachon sizniki/)).toBeNull();
    });

    it('a shield card has no equip button but a cosmetic card still does', async () => {
        setStore([{ store_item_id: 9, kind: 'boost', quantity: 1, inventory_id: 5 },
                  { store_item_id: 1, kind: 'theme', quantity: 1, inventory_id: 6, is_equipped: false }]);
        await openShieldTab();
        expect(screen.queryByRole('button', { name: /Yoqish/ })).toBeNull();
        fireEvent.click(screen.getByRole('button', { name: /Ranglar/ }));
        expect(screen.getByRole('button', { name: /Yoqish/ })).toBeInTheDocument();
    });
});

describe('quota_shield_used notification', () => {
    const n = { type: 'quota_shield_used', tone: 'ok', title: '', extra: '5', points: 0 };
    it('is worded in uz and ru', () => {
        expect(present(n, false).heading).toBe('Norma himoyasi ishlatildi');
        expect(present(n, true).heading).toBe('Защита нормы использована');
        expect(present(n, false).text).toMatch(/jarima yechilmadi/i);
        expect(present(n, true).text).toMatch(/штраф не списан/i);
    });
});

describe('quota_shield_used notification without a streak', () => {
    it('does not claim a streak was saved when there was none', () => {
        const n = { type: 'quota_shield_used', tone: 'ok', title: '', extra: '0', points: 0 };
        expect(present(n, false).text).toMatch(/jarima yechilmadi/i);
        expect(present(n, false).text).not.toMatch(/seriya/i);
        expect(present(n, true).text).not.toMatch(/серия/i);
    });
});

describe('shield badge on the daily-rules page', () => {
    it('shows how many shields are in stock', async () => {
        global.fetch = jest.fn((url) => {
            const body = url.includes('/store/inventory')
                ? [{ kind: 'boost', slug: 'quota_shield', quantity: 2 }]
                : url.includes('/daily/status') ? { base_required: 2, penalty_per_lesson: 100 } : {};
            return Promise.resolve({ ok: true, json: () => Promise.resolve(body) });
        });
        render(<DailyRules />);
        await waitFor(() => expect(screen.getByTestId('shield-count')).toHaveTextContent('2'));
    });
});
