import React from 'react';
import { render, screen, fireEvent, act, within } from '@testing-library/react';
import TeacherPenalties from '../views/teacher/penalties/TeacherPenalties';

jest.mock('../api/search/base', () => {
    const request = jest.fn();
    return {
        useHttp: () => ({ request }), API_URL: '/api/', headers: () => ({}),
        resolveImageUrl: (u) => u,
    };
});
const { useHttp } = require('../api/search/base');

const PENALTY = {
    id: 7, student_id: 3, student_name: 'Ali', teacher_id: 1, teacher_name: 'Ustoz', amount: 900,
    penalty_type: 'plagiarism', comment: null, points_before: 11854, points_after: 10954,
    created_at: new Date().toISOString(), reverted_at: null,
};

let request;
beforeEach(() => {
    jest.clearAllMocks();
    localStorage.setItem('lang', 'uz');
    request = useHttp().request;
    request.mockImplementation((url, method) => {
        if (url.includes('/revert')) {
            return Promise.resolve({ ...PENALTY, reverted_at: new Date().toISOString(), reverted_by_name: 'Ustoz', refunded_points: 900, refunded_wallet: 900 });
        }
        if (url.includes('/students')) return Promise.resolve([]);
        return Promise.resolve([PENALTY]);
    });
});

const setup = async () => { render(<TeacherPenalties />); await act(async () => {}); };

describe('penalty revert', () => {
    it('asks for confirmation, then calls the revert endpoint and marks the row', async () => {
        await setup();
        fireEvent.click(screen.getByRole('button', { name: /Qaytarish/ }));
        expect(screen.getByText(/qaytarasizmi/)).toBeInTheDocument();
        expect(request).not.toHaveBeenCalledWith(expect.stringContaining('/revert'), 'POST', null, expect.anything());

        await act(async () => { fireEvent.click(screen.getByRole('button', { name: /Ha, qaytarish/ })); });
        expect(request).toHaveBeenCalledWith('/api/v1/teacher/penalties/7/revert', 'POST', null, {});
        expect(screen.getByText(/Qaytarilgan/)).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: /Qaytarish/ })).toBeNull();
    });

    it('cancelling the confirmation sends nothing', async () => {
        await setup();
        fireEvent.click(screen.getByRole('button', { name: /Qaytarish/ }));
        fireEvent.click(screen.getByRole('button', { name: /Yo'q/ }));
        expect(request).not.toHaveBeenCalledWith(expect.stringContaining('/revert'), expect.anything(), expect.anything(), expect.anything());
        expect(screen.getByRole('button', { name: /Qaytarish/ })).toBeInTheDocument();
    });

    it('an already reverted penalty has no revert button', async () => {
        request.mockImplementation((url) => Promise.resolve(url.includes('/students') ? []
            : [{ ...PENALTY, reverted_at: new Date().toISOString(), reverted_by_name: 'Ustoz', refunded_points: 900 }]));
        await setup();
        expect(screen.queryByRole('button', { name: /Qaytarish/ })).toBeNull();
        expect(screen.getByText(/Qaytarilgan/)).toBeInTheDocument();
    });
});
