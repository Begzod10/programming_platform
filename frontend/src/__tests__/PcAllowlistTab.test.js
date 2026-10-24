import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import AllowlistTab from '../views/teacher/pccontrol/AllowlistTab';
import * as api from '../views/teacher/pccontrol/pcApi';
import { strings } from '../views/teacher/pccontrol/pcStrings';

jest.mock('../views/teacher/pccontrol/pcApi');
jest.mock('../api/search/base', () => {
    const request = jest.fn();
    return { useHttp: () => ({ request }), API_URL: '/api/', headers: () => ({}) };
});
const { useHttp } = require('../api/search/base');

const S = strings.ru;
const GROUPS = [{ id: 10, name: 'Python 1' }, { id: 11, name: 'Web 2' }];
const GLOBAL = { entries: [{ exe: 'chrome.exe', publisher: 'Google LLC' }, { exe: 'code.exe', publisher: null }],
    effective: [{ exe: 'chrome.exe', publisher: 'Google LLC' }, { exe: 'code.exe', publisher: null }] };

const setup = async (data = GLOBAL) => {
    api.listMyGroups.mockResolvedValue(GROUPS);
    api.getAllowlist.mockResolvedValue(data);
    const utils = render(<AllowlistTab />);
    await screen.findByTestId('pc-al-entries'); await within(screen.getByTestId('pc-al-entries')).findByText('chrome.exe');
    return utils;
};
const add = (v) => {
    fireEvent.change(screen.getByLabelText(S.exeName), { target: { value: v } });
    fireEvent.click(screen.getByRole('button', { name: S.add }));
};
const save = () => screen.getByRole('button', { name: S.save });
const entriesList = () => screen.getByTestId('pc-al-entries');

beforeEach(() => { jest.clearAllMocks(); localStorage.setItem('lang', 'ru'); });

describe('AllowlistTab', () => {
    it('loads global entries and the effective list', async () => {
        await setup();
        expect(api.getAllowlist).toHaveBeenCalledWith(useHttp().request, null);
        expect(within(entriesList()).getByText('chrome.exe')).toBeInTheDocument();
        expect(within(screen.getByTestId('pc-al-effective')).getByText('code.exe')).toBeInTheDocument();
        expect(screen.getByText(S.publisherNote)).toBeInTheDocument();
    });

    it('normalises an added name', async () => {
        await setup();
        add('Notepad.EXE');
        expect(within(entriesList()).getByText('notepad.exe')).toBeInTheDocument();
    });

    it.each([
        ['C:\\x\\a.exe', 'errPath'], ['a.txt', 'errExt'], ['CHROME.exe', 'errDup'], ['  ', 'errEmpty'],
    ])('rejects %s', async (v, key) => {
        await setup();
        add(v);
        expect(screen.getByRole('alert')).toHaveTextContent(S[key]);
        expect(within(entriesList()).getAllByRole('listitem')).toHaveLength(2);
        expect(save()).toBeDisabled();
    });

    it('Save is disabled when unchanged and enabled after an add', async () => {
        await setup();
        expect(save()).toBeDisabled();
        add('notepad.exe');
        expect(save()).toBeEnabled();
    });

    it('Save is disabled for an empty list with a hint', async () => {
        await setup();
        fireEvent.click(screen.getByRole('button', { name: `${S.remove} chrome.exe` }));
        fireEvent.click(screen.getByRole('button', { name: `${S.remove} code.exe` }));
        expect(save()).toBeDisabled();
        expect(screen.getByText(S.emptyHint)).toBeInTheDocument();
    });

    it('global save calls putAllowlist(request, null, entries) and refreshes from the response', async () => {
        await setup();
        const fresh = { entries: [...GLOBAL.entries, { exe: 'notepad.exe', publisher: null }],
            effective: [{ exe: 'zzz.exe', publisher: null }] };
        api.putAllowlist.mockResolvedValue(fresh);
        add('Notepad.EXE');
        fireEvent.click(save());
        await waitFor(() => expect(api.putAllowlist).toHaveBeenCalledTimes(1));
        expect(api.putAllowlist).toHaveBeenCalledWith(useHttp().request, null, [
            { exe: 'chrome.exe', publisher: 'Google LLC' },
            { exe: 'code.exe', publisher: null },
            { exe: 'notepad.exe', publisher: null },
        ]);
        await within(screen.getByTestId('pc-al-effective')).findByText('zzz.exe');
        expect(screen.getByText(S.saved)).toBeInTheDocument();
        expect(save()).toBeDisabled();
    });

    it('group save passes the numeric group id', async () => {
        await setup();
        api.getAllowlist.mockResolvedValue({ entries: [{ exe: 'a.exe', publisher: null }], effective: [] });
        fireEvent.change(screen.getByLabelText(S.scope), { target: { value: '10' } });
        await screen.findByText('a.exe');
        expect(api.getAllowlist).toHaveBeenLastCalledWith(useHttp().request, 10);
        api.putAllowlist.mockResolvedValue({ entries: [], effective: [] });
        add('b.exe');
        fireEvent.click(save());
        await waitFor(() => expect(api.putAllowlist).toHaveBeenCalled());
        expect(api.putAllowlist).toHaveBeenCalledWith(useHttp().request, 10, [
            { exe: 'a.exe', publisher: null }, { exe: 'b.exe', publisher: null },
        ]);
    });

    it('a 422 with array detail shows readable text and keeps the list', async () => {
        await setup();
        api.putAllowlist.mockRejectedValue({ response: { data: { detail: [{ msg: 'bad exe name' }] } } });
        add('notepad.exe');
        fireEvent.click(save());
        expect(await screen.findByRole('alert')).toHaveTextContent('bad exe name');
        expect(within(entriesList()).getByText('notepad.exe')).toBeInTheDocument();
        expect(save()).toBeEnabled();
    });

    it('switching scope with unsaved changes asks to confirm', async () => {
        await setup();
        add('notepad.exe');
        api.getAllowlist.mockClear();
        fireEvent.change(screen.getByLabelText(S.scope), { target: { value: '11' } });
        expect(screen.getByText(S.discardAsk)).toBeInTheDocument();
        expect(api.getAllowlist).not.toHaveBeenCalled();
        // cancel keeps the edits and the scope
        fireEvent.click(screen.getByRole('button', { name: S.keepEditing }));
        expect(within(entriesList()).getByText('notepad.exe')).toBeInTheDocument();
        expect(screen.getByLabelText(S.scope)).toHaveValue('');
        // confirm switches
        api.getAllowlist.mockResolvedValue({ entries: [{ exe: 'w.exe', publisher: null }], effective: [] });
        fireEvent.change(screen.getByLabelText(S.scope), { target: { value: '11' } });
        fireEvent.click(screen.getByRole('button', { name: S.discard }));
        await screen.findByText('w.exe');
        expect(api.getAllowlist).toHaveBeenCalledWith(useHttp().request, 11);
    });

    it('switching scope without changes does not ask', async () => {
        await setup();
        api.getAllowlist.mockResolvedValue({ entries: [{ exe: 'w.exe', publisher: null }], effective: [] });
        fireEvent.change(screen.getByLabelText(S.scope), { target: { value: '11' } });
        await screen.findByText('w.exe');
        expect(screen.queryByText(S.discardAsk)).not.toBeInTheDocument();
    });

    it('shows a load error', async () => {
        api.listMyGroups.mockResolvedValue([]);
        api.getAllowlist.mockRejectedValue({ response: { data: { detail: 'Not your group' } } });
        render(<AllowlistTab />);
        expect(await screen.findByRole('alert')).toHaveTextContent('Not your group');
    });
});
