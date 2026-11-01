import { API_URL, headers } from '../../../api/search/base';

// Every function takes the `request` function from useHttp() first so tests
// can inject a fake.
const BASE = `${API_URL}v1/teacher/pc`;

export const listDevices = (request) =>
    request(`${BASE}/devices`, 'GET', null, headers());

export const patchDevice = (request, id, groupId) =>
    request(`${BASE}/devices/${id}`, 'PATCH', { group_id: groupId }, headers());

export const sendCommand = (request, { scope_type, scope_id, type, payload }) =>
    request(`${BASE}/commands`, 'POST',
        { scope_type, scope_id: scope_id ?? null, type, ...(payload ? { payload } : {}) }, headers());

export const getAllowlist = (request, groupId) => {
    const qs = groupId != null ? `?group_id=${encodeURIComponent(groupId)}` : '';
    return request(`${BASE}/allowlist${qs}`, 'GET', null, headers());
};

export const putAllowlist = (request, groupId, entries) => {
    const qs = groupId != null ? `?group_id=${encodeURIComponent(groupId)}` : '';
    return request(`${BASE}/allowlist${qs}`, 'PUT', { entries }, headers());
};

export const getReport = (request, { from, to, groupId } = {}) => {
    const p = new URLSearchParams();
    if (from) p.set('from', from);
    if (to) p.set('to', to);
    if (groupId != null) p.set('group_id', groupId);
    const qs = p.toString();
    return request(`${BASE}/report${qs ? `?${qs}` : ''}`, 'GET', null, headers());
};

// GET /v1/groups/ is already teacher-scoped (same call MyGroups.js makes).
export const listMyGroups = (request) =>
    request(`${API_URL}v1/groups/`, 'GET', null, headers());
