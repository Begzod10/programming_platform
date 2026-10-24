import React from 'react';
import { render, screen, fireEvent, within, act, waitFor } from '@testing-library/react';
import DevicesTab from '../views/teacher/pccontrol/DevicesTab';
import * as api from '../views/teacher/pccontrol/pcApi';
import { strings } from '../views/teacher/pccontrol/pcStrings';

jest.mock('../views/teacher/pccontrol/pcApi');
jest.mock('../api/search/base', () => {
    const request = jest.fn();
    return { useHttp: () => ({ request }), API_URL: '/api/', headers: () => ({}) };
});

const S = strings.ru;
const dev = (o = {}) => ({
    id: 1, hostname: 'LAB-01', group_id: null, online: true,
    student: { id: 5, full_name: 'Ali Valiyev' },
    locked: false, reason: 'quota_met', last_app: 'chrome.exe',
    last_seen_at: new Date().toISOString(), ...o,
});
const GROUPS = [{ id: 10, name: 'Python 1' }, { id: 11, name: 'Web 2' }];

const setup = async (devices = [dev()]) => {
    api.listDevices.mockResolvedValue(devices);
    api.listMyGroups.mockResolvedValue(GROUPS);
    api.sendCommand.mockResolvedValue({});
    api.patchDevice.mockResolvedValue({});
    const utils = render(<DevicesTab />);
    await screen.findByText(devices[0].hostname);
    return utils;
};

beforeEach(() => {
    jest.clearAllMocks();
    localStorage.setItem('lang', 'ru');
    visibility = 'visible';
    Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => visibility });
});
let visibility = 'visible';
afterEach(() => { jest.useRealTimers(); visibility = 'visible'; });

describe('DevicesTab', () => {
    it('renders a card with hostname and student name', async () => {
        await setup();
        const card = screen.getByTestId('pc-card-1');
        expect(within(card).getByText('LAB-01')).toBeInTheDocument();
        expect(within(card).getByText('Ali Valiyev')).toBeInTheDocument();
        expect(within(card).getByText(S.online)).toBeInTheDocument();
        expect(within(card).getByText(S.unlocked)).toBeInTheDocument();
        expect(within(card).getByText(S.reasonQuotaMet)).toBeInTheDocument();
    });

    it('shows a dash for a hidden student', async () => {
        await setup([dev({ student: { id: null, full_name: null } })]);
        expect(within(screen.getByTestId('pc-card-1')).getByTestId('pc-student')).toHaveTextContent('—');
    });

    it('offline device shows offline badge and disables its buttons', async () => {
        await setup([dev({ online: false })]);
        const card = screen.getByTestId('pc-card-1');
        expect(within(card).getByText(S.offline)).toBeInTheDocument();
        for (const label of [S.lock, S.unlock, S.resume]) {
            expect(within(card).getByRole('button', { name: label })).toBeDisabled();
        }
    });

    it('Lock all needs two clicks', async () => {
        await setup();
        const bar = screen.getByTestId('pc-all-bar');
        fireEvent.click(within(bar).getByRole('button', { name: S.lockAll }));
        expect(api.sendCommand).not.toHaveBeenCalled();
        fireEvent.click(within(bar).getByRole('button', { name: S.confirm }));
        await waitFor(() => expect(api.sendCommand).toHaveBeenCalledTimes(1));
        expect(api.sendCommand.mock.calls[0][1]).toEqual({ scope_type: 'all', scope_id: null, type: 'lock' });
    });

    it('Resume all sends immediately', async () => {
        await setup();
        fireEvent.click(within(screen.getByTestId('pc-all-bar')).getByRole('button', { name: S.resumeAll }));
        await waitFor(() => expect(api.sendCommand).toHaveBeenCalledTimes(1));
        expect(api.sendCommand.mock.calls[0][1]).toMatchObject({ scope_type: 'all', type: 'clear' });
    });

    it('sends a message with payload text', async () => {
        await setup();
        const box = screen.getByTestId('pc-message-box');
        fireEvent.change(within(box).getByRole('textbox'), { target: { value: 'Hello class' } });
        fireEvent.click(within(box).getByRole('button', { name: S.send }));
        await waitFor(() => expect(api.sendCommand).toHaveBeenCalledTimes(1));
        expect(api.sendCommand.mock.calls[0][1]).toMatchObject({
            scope_type: 'all', type: 'message', payload: { text: 'Hello class' },
        });
    });

    it('group lock uses scope_type group with the chosen id', async () => {
        await setup();
        const bar = screen.getByTestId('pc-group-bar');
        await within(bar).findByRole('option', { name: 'Web 2' });
        fireEvent.change(within(bar).getByRole('combobox'), { target: { value: '11' } });
        fireEvent.click(within(bar).getByRole('button', { name: S.lock }));
        await waitFor(() => expect(api.sendCommand).toHaveBeenCalledTimes(1));
        expect(api.sendCommand.mock.calls[0][1]).toMatchObject({ scope_type: 'group', scope_id: 11, type: 'lock' });
    });

    it('changing a device group calls patchDevice', async () => {
        await setup();
        const sel = within(screen.getByTestId('pc-card-1')).getByRole('combobox');
        await within(sel).findByRole('option', { name: 'Python 1' });
        fireEvent.change(sel, { target: { value: '10' } });
        await waitFor(() => expect(api.patchDevice).toHaveBeenCalledTimes(1));
        expect(api.patchDevice.mock.calls[0].slice(1)).toEqual([1, 10]);
        fireEvent.change(sel, { target: { value: '' } });
        await waitFor(() => expect(api.patchDevice).toHaveBeenCalledTimes(2));
        expect(api.patchDevice.mock.calls[1].slice(1)).toEqual([1, null]);
    });

    it('shows the server detail on a failed command, dismissible', async () => {
        await setup();
        api.sendCommand.mockRejectedValue({ response: { data: { detail: 'Bu guruh sizga tegishli emas' } } });
        fireEvent.click(within(screen.getByTestId('pc-all-bar')).getByRole('button', { name: S.resumeAll }));
        expect(await screen.findByText('Bu guruh sizga tegishli emas')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: S.dismiss }));
        expect(screen.queryByText('Bu guruh sizga tegishli emas')).not.toBeInTheDocument();
    });

    it('polls every 5s and stops on unmount', async () => {
        jest.useFakeTimers();
        api.listDevices.mockResolvedValue([dev()]);
        api.listMyGroups.mockResolvedValue(GROUPS);
        const { unmount } = render(<DevicesTab />);
        await act(async () => { await Promise.resolve(); });
        expect(api.listDevices).toHaveBeenCalledTimes(1);
        await act(async () => { jest.advanceTimersByTime(5000); });
        expect(api.listDevices).toHaveBeenCalledTimes(2);
        unmount();
        await act(async () => { jest.advanceTimersByTime(15000); });
        expect(api.listDevices).toHaveBeenCalledTimes(2);
    });

    it('Lock all confirm expires after 4s and the next click only re-arms', async () => {
        await setup();
        jest.useFakeTimers();
        const bar = screen.getByTestId('pc-all-bar');
        fireEvent.click(within(bar).getByRole('button', { name: S.lockAll }));
        expect(within(bar).getByRole('button', { name: S.confirm })).toBeInTheDocument();
        act(() => { jest.advanceTimersByTime(4000); });
        expect(within(bar).queryByRole('button', { name: S.confirm })).not.toBeInTheDocument();
        fireEvent.click(within(bar).getByRole('button', { name: S.lockAll }));
        expect(api.sendCommand).not.toHaveBeenCalled();
    });

    it('another action disarms a pending confirm', async () => {
        await setup();
        const bar = screen.getByTestId('pc-all-bar');
        fireEvent.click(within(bar).getByRole('button', { name: S.lockAll }));
        fireEvent.click(within(bar).getByRole('button', { name: S.resumeAll }));
        expect(within(bar).queryByRole('button', { name: S.confirm })).not.toBeInTheDocument();
        await waitFor(() => expect(api.sendCommand).toHaveBeenCalledTimes(1));
    });

    it('hidden tab pauses polling; becoming visible refreshes at once', async () => {
        jest.useFakeTimers();
        api.listDevices.mockResolvedValue([dev()]);
        api.listMyGroups.mockResolvedValue(GROUPS);
        render(<DevicesTab />);
        await act(async () => { await Promise.resolve(); });
        expect(api.listDevices).toHaveBeenCalledTimes(1);
        visibility = 'hidden';
        await act(async () => { jest.advanceTimersByTime(5000); });
        expect(api.listDevices).toHaveBeenCalledTimes(1);
        visibility = 'visible';
        await act(async () => { document.dispatchEvent(new Event('visibilitychange')); });
        expect(api.listDevices).toHaveBeenCalledTimes(2);
    });

    it('array-detail 422 shows readable text and does not throw', async () => {
        await setup();
        api.sendCommand.mockRejectedValue({ response: { data: { detail: [{ msg: 'Field required', loc: ['body'] }] } } });
        fireEvent.click(within(screen.getByTestId('pc-all-bar')).getByRole('button', { name: S.resumeAll }));
        expect(await screen.findByText('Field required')).toBeInTheDocument();
        expect(screen.getByTestId('pc-card-1')).toBeInTheDocument();
    });

    it('double click sends only one command', async () => {
        await setup();
        let release;
        api.sendCommand.mockReturnValue(new Promise(r => { release = r; }));
        const btn = within(screen.getByTestId('pc-all-bar')).getByRole('button', { name: S.resumeAll });
        fireEvent.click(btn);
        fireEvent.click(btn);
        expect(api.sendCommand).toHaveBeenCalledTimes(1);
        await act(async () => { release({}); });
    });

    it('slow poll does not start a second request', async () => {
        jest.useFakeTimers();
        let release;
        api.listDevices.mockReturnValueOnce(new Promise(r => { release = r; }));
        api.listDevices.mockResolvedValue([dev()]);
        api.listMyGroups.mockResolvedValue(GROUPS);
        render(<DevicesTab />);
        await act(async () => { jest.advanceTimersByTime(10000); });
        expect(api.listDevices).toHaveBeenCalledTimes(1);
        await act(async () => { release([dev()]); });
        await act(async () => { jest.advanceTimersByTime(5000); });
        expect(api.listDevices).toHaveBeenCalledTimes(2);
    });

    it('a stale older response does not overwrite a newer one', async () => {
        jest.useFakeTimers();
        let releaseOld;
        api.listDevices.mockReturnValueOnce(new Promise(r => { releaseOld = r; }));
        api.listDevices.mockResolvedValue([dev({ hostname: 'NEW-PC' })]);
        api.listMyGroups.mockResolvedValue(GROUPS);
        render(<DevicesTab />);
        await act(async () => { document.dispatchEvent(new Event('visibilitychange')); });
        expect(screen.getByText('NEW-PC')).toBeInTheDocument();
        await act(async () => { releaseOld([dev({ hostname: 'OLD-PC' })]); });
        expect(screen.getByText('NEW-PC')).toBeInTheDocument();
        expect(screen.queryByText('OLD-PC')).not.toBeInTheDocument();
    });

    it('failed poll keeps data and shows a stale hint, not the red banner', async () => {
        jest.useFakeTimers();
        api.listDevices.mockResolvedValueOnce([dev()]);
        api.listDevices.mockRejectedValue(new Error('x'));
        api.listMyGroups.mockResolvedValue(GROUPS);
        render(<DevicesTab />);
        await act(async () => { await Promise.resolve(); });
        await act(async () => { jest.advanceTimersByTime(5000); });
        expect(screen.getByText('LAB-01')).toBeInTheDocument();
        expect(screen.getByText(S.staleHint)).toBeInTheDocument();
        expect(screen.queryByText(S.loadError)).not.toBeInTheDocument();
    });

    it('first-load failure shows the red banner', async () => {
        api.listDevices.mockRejectedValue(new Error('x'));
        api.listMyGroups.mockResolvedValue(GROUPS);
        render(<DevicesTab />);
        expect(await screen.findByText(S.loadError)).toBeInTheDocument();
    });

    it('unknown device group id gets a disabled option', async () => {
        await setup([dev({ group_id: 99 })]);
        const sel = within(screen.getByTestId('pc-card-1')).getByRole('combobox');
        expect(sel.value).toBe('99');
        expect(within(sel).getByRole('option', { name: new RegExp(S.otherGroup) })).toBeDisabled();
    });
});
