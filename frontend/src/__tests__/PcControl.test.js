import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import PcControl from '../views/teacher/pccontrol/PcControl';
import * as api from '../views/teacher/pccontrol/pcApi';
import { strings } from '../views/teacher/pccontrol/pcStrings';

jest.mock('../views/teacher/pccontrol/pcApi');
jest.mock('../api/search/base', () => {
    const request = jest.fn();
    return { useHttp: () => ({ request }), API_URL: '/api/', headers: () => ({}) };
});
const S = strings.ru;

it('switches between tabs, mounting and unmounting each without errors', async () => {
    localStorage.setItem('lang', 'ru');
    api.listDevices.mockResolvedValue([]);
    api.listMyGroups.mockResolvedValue([]);
    api.getAllowlist.mockResolvedValue({ entries: [{ exe: 'a.exe', publisher: null }], effective: [] });
    const err = jest.spyOn(console, 'error').mockImplementation(() => {});
    render(<PcControl />);
    await act(async () => {});
    expect(screen.getByTestId('pc-all-bar')).toBeInTheDocument();
    await act(async () => { fireEvent.click(screen.getByRole('tab', { name: S.tabAllowlist })); });
    expect(await screen.findByText('a.exe')).toBeInTheDocument();
    expect(screen.queryByTestId('pc-all-bar')).not.toBeInTheDocument();
    await act(async () => { fireEvent.click(screen.getByRole('tab', { name: S.tabReport })); });
    expect(screen.getByRole('button', { name: S.load })).toBeInTheDocument();
    expect(screen.queryByText('a.exe')).not.toBeInTheDocument();
    await act(async () => { fireEvent.click(screen.getByRole('tab', { name: S.tabDevices })); });
    expect(screen.getByTestId('pc-all-bar')).toBeInTheDocument();
    expect(err).not.toHaveBeenCalled();
    err.mockRestore();
});
