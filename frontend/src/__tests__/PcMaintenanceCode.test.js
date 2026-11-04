import React from 'react';
import { render, screen, fireEvent, within, act } from '@testing-library/react';
import DevicesTab from '../views/teacher/pccontrol/DevicesTab';
import * as api from '../views/teacher/pccontrol/pcApi';
import { strings } from '../views/teacher/pccontrol/pcStrings';

jest.mock('../views/teacher/pccontrol/pcApi');
jest.mock('../api/search/base', () => {
    const request = jest.fn();
    return { useHttp: () => ({ request }), API_URL: '/api/', headers: () => ({}) };
});

const S = strings.ru;
const NOW = 1700000000000;
const dev = { id: 7, hostname: 'LAB-07', group_id: null, online: true, student: null,
    locked: false, reason: 'quota_met', last_app: null, last_seen_at: new Date(NOW).toISOString() };
const created = (secs = 300) => ({ code: '123456', minutes: 60, expires_at: new Date(NOW + secs * 1000).toISOString() });

const open = async () => {
    api.listDevices.mockResolvedValue([dev]);
    api.listMyGroups.mockResolvedValue([]);
    render(<DevicesTab />);
    await screen.findByText('LAB-07');
    await act(async () => {
        fireEvent.click(screen.getByRole('button', { name: new RegExp(S.maintCode) }));
    });
    return screen.getByRole('dialog');
};
const create = async (dlg) => {
    await act(async () => { fireEvent.click(within(dlg).getByRole('button', { name: S.maintCreate })); });
};

beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers('modern');
    jest.setSystemTime(NOW);
    localStorage.setItem('lang', 'ru');
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: jest.fn().mockResolvedValue() } });
});
afterEach(() => { jest.useRealTimers(); });

describe('maintenance code', () => {
    it('button opens the modal with 15 min preselected', async () => {
        const dlg = await open();
        expect(within(dlg).getByRole('combobox')).toHaveValue('15');
        expect(within(dlg).getAllByRole('option').map(o => o.value)).toEqual(['15', '60', '240']);
    });

    it('sends the chosen minutes and shows the code large and spaced', async () => {
        api.createMaintenanceCode.mockResolvedValue(created());
        const dlg = await open();
        fireEvent.change(within(dlg).getByRole('combobox'), { target: { value: '240' } });
        await create(dlg);
        expect(api.createMaintenanceCode).toHaveBeenCalledWith(expect.anything(), 7, 240);
        expect(within(dlg).getByTestId('pc-maint-code')).toHaveTextContent('123 456');
        expect(within(dlg).getByText(S.maintNote)).toBeInTheDocument();
    });

    it('counts down and turns grey with "expired"', async () => {
        api.createMaintenanceCode.mockResolvedValue(created(65));
        const dlg = await open();
        await create(dlg);
        expect(within(dlg).getByTestId('pc-maint-left')).toHaveTextContent('1:05');
        await act(async () => { jest.advanceTimersByTime(5000); });
        expect(within(dlg).getByTestId('pc-maint-left')).toHaveTextContent('1:00');
        await act(async () => { jest.advanceTimersByTime(61000); });
        expect(within(dlg).getByText(S.maintExpired)).toBeInTheDocument();
        expect(within(dlg).getByTestId('pc-maint-code')).toHaveClass('expired');
    });

    it('copies the plain code', async () => {
        api.createMaintenanceCode.mockResolvedValue(created());
        const dlg = await open();
        await create(dlg);
        await act(async () => { fireEvent.click(within(dlg).getByRole('button', { name: S.maintCopy })); });
        expect(navigator.clipboard.writeText).toHaveBeenCalledWith('123456');
        expect(within(dlg).getByText(S.maintCopied)).toBeInTheDocument();
    });

    it('maps 429, 404 and generic errors', async () => {
        for (const [status, text] of [[429, S.maintTooMany], [404, S.maintNoDevice], [500, S.maintFailed]]) {
            api.createMaintenanceCode.mockRejectedValueOnce(Object.assign(new Error('x'), { status }));
            const dlg = await open();
            await create(dlg);
            expect(within(dlg).getByRole('alert')).toHaveTextContent(text);
            expect(within(dlg).queryByTestId('pc-maint-code')).toBeNull();
            fireEvent.click(within(dlg).getByRole('button', { name: S.maintClose }));
            document.body.innerHTML = '';
        }
    });

    it('close clears the code; reopening shows no code; nothing stored', async () => {
        api.createMaintenanceCode.mockResolvedValue(created());
        const dlg = await open();
        await create(dlg);
        fireEvent.click(within(dlg).getByRole('button', { name: S.maintClose }));
        expect(screen.queryByRole('dialog')).toBeNull();
        expect(document.body.textContent).not.toMatch(/123\s?456/);
        fireEvent.click(screen.getByRole('button', { name: new RegExp(S.maintCode) }));
        expect(screen.queryByTestId('pc-maint-code')).toBeNull();
        expect(JSON.stringify(localStorage)).not.toMatch(/123456/);
    });

    it('creating without changing the duration sends 15 minutes', async () => {
        api.createMaintenanceCode.mockResolvedValue(created());
        const dlg = await open();
        await create(dlg);
        expect(api.createMaintenanceCode).toHaveBeenCalledWith(expect.anything(), 7, 15);
    });
});
