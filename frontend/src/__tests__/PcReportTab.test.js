import React from 'react';
import { render, screen, fireEvent, waitFor, within, act } from '@testing-library/react';
import ReportTab from '../views/teacher/pccontrol/ReportTab';
import * as api from '../views/teacher/pccontrol/pcApi';
import { strings } from '../views/teacher/pccontrol/pcStrings';

jest.mock('../views/teacher/pccontrol/pcApi');
jest.mock('../api/search/base', () => {
    const request = jest.fn();
    return { useHttp: () => ({ request }), API_URL: '/api/', headers: () => ({}) };
});
const { useHttp } = require('../api/search/base');

const S = strings.ru;
const GROUPS = [{ id: 10, name: 'Python 1' }];
const UNLOCK = '2026-10-20T04:05:00+00:00'; // 09:05 in Tashkent
const ROWS = [
    { student_id: 1, full_name: 'Ali', date: '2026-10-20', quota_met: true, unlocked_at: UNLOCK,
        minutes_locked: 10, minutes_unlocked: 42, top_apps: [{ app: 'code.exe', minutes: 42 }, { app: 'chrome.exe', minutes: 3.14 }] },
    { student_id: 1, full_name: 'Ali', date: '2026-10-21', quota_met: false, unlocked_at: null,
        minutes_locked: 5.55, minutes_unlocked: 0, top_apps: [] },
    { student_id: 2, full_name: 'Bobur', date: '2026-10-21', quota_met: true, unlocked_at: null,
        minutes_locked: 1, minutes_unlocked: 1, top_apps: [] },
];

beforeEach(() => {
    jest.clearAllMocks();
    localStorage.setItem('lang', 'ru');
    jest.useFakeTimers('modern');
    jest.setSystemTime(new Date('2026-10-24T20:30:00Z')); // Tashkent date is already 2026-10-25
    api.listMyGroups.mockResolvedValue(GROUPS);
    api.getReport.mockResolvedValue(ROWS);
});
afterEach(() => jest.useRealTimers());

const setup = async () => {
    render(<ReportTab />);
    await act(async () => {});
};
const load = async () => {
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: S.load })); });
};
const setDate = (label, v) => fireEvent.change(screen.getByLabelText(label), { target: { value: v } });

describe('ReportTab', () => {
    it('defaults to the last 7 days and does not fetch on mount', async () => {
        await setup();
        expect(screen.getByLabelText(S.dateFrom)).toHaveValue('2026-10-19');
        expect(screen.getByLabelText(S.dateTo)).toHaveValue('2026-10-25');
        expect(api.getReport).not.toHaveBeenCalled();
    });

    it('builds the request with from/to and group id', async () => {
        await setup();
        fireEvent.change(screen.getByLabelText(S.groupScope), { target: { value: '10' } });
        await load();
        expect(api.getReport).toHaveBeenCalledWith(useHttp().request,
            { from: '2026-10-19', to: '2026-10-25', groupId: 10 });
    });

    it('uses a null group by default', async () => {
        await setup();
        await load();
        expect(api.getReport).toHaveBeenCalledWith(useHttp().request,
            { from: '2026-10-19', to: '2026-10-25', groupId: null });
    });

    it('blocks a range longer than 31 days', async () => {
        await setup();
        setDate(S.dateFrom, '2026-09-23');
        await load();
        expect(api.getReport).not.toHaveBeenCalled();
        expect(screen.getByRole('alert')).toHaveTextContent(S.rangeTooLong);
    });

    it('blocks an empty date with the invalid message', async () => {
        await setup();
        setDate(S.dateFrom, '');
        await load();
        expect(api.getReport).not.toHaveBeenCalled();
        expect(screen.getByRole('alert')).toHaveTextContent(S.rangeInvalid);
    });

    it('notes that days and times are Tashkent time', async () => {
        await setup();
        expect(screen.getByText(S.tzNote)).toBeInTheDocument();
    });

    it('blocks from after to', async () => {
        await setup();
        setDate(S.dateFrom, '2026-10-26');
        await load();
        expect(api.getReport).not.toHaveBeenCalled();
        expect(screen.getByRole('alert')).toHaveTextContent(S.rangeOrder);
    });

    it('renders rows sorted with exact values', async () => {
        await setup();
        await load();
        const table = await screen.findByTestId('pc-report-table');
        const rows = within(table).getAllByTestId('pc-report-row');
        expect(rows).toHaveLength(3);
        expect(rows[0]).toHaveTextContent('2026-10-21');
        expect(rows[0]).toHaveTextContent('Ali');
        expect(rows[1]).toHaveTextContent('Bobur');
        expect(rows[2]).toHaveTextContent('2026-10-20');
        // 2026-10-20 Ali row
        expect(rows[2]).toHaveTextContent('✓');
        expect(rows[2]).toHaveTextContent('09:05');
        expect(rows[2]).toHaveTextContent('10,0');
        expect(rows[2]).toHaveTextContent(`code.exe 42,0 ${S.min}, chrome.exe 3,1 ${S.min}`);
        // 2026-10-21 Ali row: quota not met, no unlock time
        expect(rows[0]).toHaveTextContent('✗');
        const cells0 = within(rows[0]).getAllByRole('cell');
        expect(cells0[3]).toHaveTextContent(/^—$/);       // unlock time cell
        expect(within(cells0[2]).getByRole('img')).toHaveAccessibleName(S.quotaMissed);
        expect(within(within(rows[2]).getAllByRole('cell')[2]).getByRole('img')).toHaveAccessibleName(S.quotaMetShort);
        expect(within(rows[2]).getAllByRole('cell')[3]).toHaveTextContent(/^09:05$/);
        expect(within(table).getAllByRole('columnheader')[0]).toHaveAttribute('scope', 'col');
    });

    it('shows per-student trend and the header summary', async () => {
        await setup();
        await load();
        await screen.findByTestId('pc-report-table');
        const sum = screen.getByTestId('pc-report-summary');
        expect(sum).toHaveTextContent('2');      // students
        expect(sum).toHaveTextContent('2/3');    // met / total
        expect(sum).toHaveTextContent('67%');
        const ali = screen.getByTestId('pc-trend-1');
        expect(ali).toHaveTextContent('Ali');
        expect(ali).toHaveTextContent('1/2');
        expect(screen.getByTestId('pc-trend-2')).toHaveTextContent('1/1');
    });

    it('shows a friendly empty state', async () => {
        api.getReport.mockResolvedValue([]);
        await setup();
        await load();
        expect(await screen.findByText(S.reportEmpty)).toBeInTheDocument();
        expect(screen.queryByTestId('pc-report-table')).not.toBeInTheDocument();
    });

    it('shows the server message on 403', async () => {
        api.getReport.mockRejectedValue({ response: { status: 403, data: { detail: 'Not your group' } } });
        await setup();
        await load();
        expect(await screen.findByRole('alert')).toHaveTextContent('Not your group');
    });

    it('shows a generic error and clears old rows', async () => {
        await setup();
        await load();
        await screen.findByTestId('pc-report-table');
        api.getReport.mockRejectedValue({});
        await load();
        expect(await screen.findByRole('alert')).toHaveTextContent(S.reportError);
        expect(screen.queryByTestId('pc-report-table')).not.toBeInTheDocument();
    });
});
