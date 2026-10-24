import React from 'react';
import { render, screen, fireEvent, waitFor, within, act } from '@testing-library/react';
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

describe('AllowlistTab races and edits', () => {
    const deferred = () => { let res, rej; const p = new Promise((a, b) => { res = a; rej = b; }); return { p, res, rej }; };

    it('scope select is disabled and ignored while a save is in flight; late response applies to its own scope', async () => {
        await setup();
        api.getAllowlist.mockResolvedValue({ entries: [{ exe: 'a.exe', publisher: null }], effective: [] });
        fireEvent.change(screen.getByLabelText(S.scope), { target: { value: '10' } });
        await screen.findByText('a.exe');
        const d = deferred();
        api.putAllowlist.mockReturnValue(d.p);
        add('b.exe');
        fireEvent.click(save());
        expect(screen.getByLabelText(S.scope)).toBeDisabled();
        api.getAllowlist.mockClear();
        fireEvent.change(screen.getByLabelText(S.scope), { target: { value: '11' } });
        expect(api.getAllowlist).not.toHaveBeenCalled();
        expect(screen.getByLabelText(S.scope)).toHaveValue('10');
        await act(async () => { d.res({ entries: [{ exe: 'a.exe', publisher: null }, { exe: 'b.exe', publisher: null }], effective: [] }); });
        expect(screen.getByLabelText(S.scope)).toBeEnabled();
        expect(within(entriesList()).getByText('b.exe')).toBeInTheDocument();
        expect(screen.getByLabelText(S.scope)).toHaveValue('10');
    });

    it('scope select is disabled while a load is in flight', async () => {
        api.listMyGroups.mockResolvedValue(GROUPS);
        const d = deferred();
        api.getAllowlist.mockReturnValue(d.p);
        render(<AllowlistTab />);
        expect(screen.getByLabelText(S.scope)).toBeDisabled();
        await act(async () => { d.res(GLOBAL); });
        expect(screen.getByLabelText(S.scope)).toBeEnabled();
    });

    it('double-click on Save sends one PUT', async () => {
        await setup();
        const d = deferred();
        api.putAllowlist.mockReturnValue(d.p);
        add('notepad.exe');
        fireEvent.click(save());
        fireEvent.click(save());
        expect(api.putAllowlist).toHaveBeenCalledTimes(1);
        await act(async () => { d.res({ entries: GLOBAL.entries, effective: [] }); });
    });

    it('a language change keeps unsaved edits and does not reload', async () => {
        await setup();
        add('notepad.exe');
        api.getAllowlist.mockClear();
        await act(async () => { window.dispatchEvent(new CustomEvent('languageChange', { detail: 'uz' })); });
        expect(screen.getByLabelText(strings.uz.scope)).toBeInTheDocument();
        expect(within(entriesList()).getByText('notepad.exe')).toBeInTheDocument();
        expect(api.getAllowlist).not.toHaveBeenCalled();
        await act(async () => { window.dispatchEvent(new CustomEvent('languageChange', { detail: 'ru' })); });
    });

    it('a trailing space in publisher does not make the form dirty', async () => {
        await setup();
        fireEvent.change(screen.getByLabelText(`${S.publisher}: chrome.exe`), { target: { value: 'Google LLC  ' } });
        expect(save()).toBeDisabled();
        fireEvent.change(screen.getByLabelText(`${S.publisher}: code.exe`), { target: { value: '   ' } });
        expect(save()).toBeDisabled();
    });

    it('editing a publisher is saved trimmed', async () => {
        await setup();
        api.putAllowlist.mockResolvedValue(GLOBAL);
        fireEvent.change(screen.getByLabelText(`${S.publisher}: code.exe`), { target: { value: ' Microsoft ' } });
        fireEvent.click(save());
        await waitFor(() => expect(api.putAllowlist).toHaveBeenCalled());
        expect(api.putAllowlist.mock.calls[0][2]).toEqual([
            { exe: 'chrome.exe', publisher: 'Google LLC' }, { exe: 'code.exe', publisher: 'Microsoft' },
        ]);
    });

    it('rejects the 201st entry in the UI', async () => {
        const many = Array.from({ length: 200 }, (_, i) => ({ exe: `a${i}.exe`, publisher: null }));
        api.listMyGroups.mockResolvedValue([]);
        api.getAllowlist.mockResolvedValue({ entries: many, effective: many });
        render(<AllowlistTab />);
        await within(await screen.findByTestId('pc-al-entries')).findByText('a0.exe');
        add('extra.exe');
        expect(screen.getByRole('alert')).toHaveTextContent(S.errMax);
        expect(within(entriesList()).getAllByRole('listitem')).toHaveLength(200);
    });

    it('a pending scope-switch confirm is cleared when a save completes', async () => {
        await setup();
        api.putAllowlist.mockResolvedValue({ entries: [...GLOBAL.entries, { exe: 'n.exe', publisher: null }], effective: [] });
        add('n.exe');
        fireEvent.change(screen.getByLabelText(S.scope), { target: { value: '11' } });
        expect(screen.getByText(S.discardAsk)).toBeInTheDocument();
        fireEvent.click(save());
        await screen.findByText(S.saved);
        expect(screen.queryByText(S.discardAsk)).not.toBeInTheDocument();
    });

    it('loading text is a status region', async () => {
        api.listMyGroups.mockResolvedValue([]);
        api.getAllowlist.mockReturnValue(new Promise(() => {}));
        render(<AllowlistTab />);
        expect(screen.getByRole('status')).toHaveTextContent(S.loading);
    });
});
