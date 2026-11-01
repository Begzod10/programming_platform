import * as api from '../views/teacher/pccontrol/pcApi';

jest.mock('../api/search/base', () => ({ API_URL: '/api/', headers: () => ({ H: '1' }) }));

const fake = () => { const request = jest.fn().mockResolvedValue({}); return request; };
const BASE = '/api/v1/teacher/pc';

describe('pcApi request building', () => {
    it('listDevices', async () => {
        const r = fake(); await api.listDevices(r);
        expect(r).toHaveBeenCalledWith(`${BASE}/devices`, 'GET', null, { H: '1' });
    });
    it('patchDevice sends group_id (number or null)', async () => {
        const r = fake();
        await api.patchDevice(r, 7, 3);
        await api.patchDevice(r, 7, null);
        expect(r).toHaveBeenNthCalledWith(1, `${BASE}/devices/7`, 'PATCH', { group_id: 3 }, { H: '1' });
        expect(r).toHaveBeenNthCalledWith(2, `${BASE}/devices/7`, 'PATCH', { group_id: null }, { H: '1' });
    });
    it('sendCommand: scope_id null for all, no payload unless given', async () => {
        const r = fake();
        await api.sendCommand(r, { scope_type: 'all', type: 'lock' });
        await api.sendCommand(r, { scope_type: 'group', scope_id: 4, type: 'message', payload: { text: 'hi' } });
        expect(r).toHaveBeenNthCalledWith(1, `${BASE}/commands`, 'POST',
            { scope_type: 'all', scope_id: null, type: 'lock' }, { H: '1' });
        expect(r).toHaveBeenNthCalledWith(2, `${BASE}/commands`, 'POST',
            { scope_type: 'group', scope_id: 4, type: 'message', payload: { text: 'hi' } }, { H: '1' });
    });
    it('getAllowlist omits group_id when null', async () => {
        const r = fake();
        await api.getAllowlist(r, null);
        await api.getAllowlist(r, 12);
        expect(r).toHaveBeenNthCalledWith(1, `${BASE}/allowlist`, 'GET', null, { H: '1' });
        expect(r).toHaveBeenNthCalledWith(2, `${BASE}/allowlist?group_id=12`, 'GET', null, { H: '1' });
    });
    it('putAllowlist body and query', async () => {
        const r = fake();
        const entries = [{ exe: 'a.exe', publisher: null }];
        await api.putAllowlist(r, null, entries);
        await api.putAllowlist(r, 5, entries);
        expect(r).toHaveBeenNthCalledWith(1, `${BASE}/allowlist`, 'PUT', { entries }, { H: '1' });
        expect(r).toHaveBeenNthCalledWith(2, `${BASE}/allowlist?group_id=5`, 'PUT', { entries }, { H: '1' });
    });
    it('getReport from/to/group_id', async () => {
        const r = fake();
        await api.getReport(r, { from: '2026-10-01', to: '2026-10-07', groupId: null });
        await api.getReport(r, { from: '2026-10-01', to: '2026-10-07', groupId: 9 });
        expect(r).toHaveBeenNthCalledWith(1, `${BASE}/report?from=2026-10-01&to=2026-10-07`, 'GET', null, { H: '1' });
        expect(r).toHaveBeenNthCalledWith(2, `${BASE}/report?from=2026-10-01&to=2026-10-07&group_id=9`, 'GET', null, { H: '1' });
    });
    it('listMyGroups', async () => {
        const r = fake(); await api.listMyGroups(r);
        expect(r).toHaveBeenCalledWith('/api/v1/groups/', 'GET', null, { H: '1' });
    });
});
