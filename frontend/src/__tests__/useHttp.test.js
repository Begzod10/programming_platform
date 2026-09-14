// Regression test for the ZIP-upload 422 bug: uploadZip() (and every other
// FormData caller) goes through useHttp().request(), which hands the
// request off to axiosInstance — created with a default `Content-Type:
// application/json` header (see api/axiosInstance.js). Axios's own default
// transformRequest checks that default BEFORE deciding how to serialize a
// FormData body: if Content-Type already reads application/json, axios
// silently JSON.stringifies the FormData instead of sending it as
// multipart, dropping the actual file bytes. The backend then sees no
// multipart "file" part and 422s with "file: Field required" — this is
// exactly what broke ZIP project uploads once uploadZip() was migrated onto
// this shared request() helper.
//
// This test doesn't re-verify axios's own internals (that's axios's library
// code); it verifies OUR wrapper does what fixes the bug: explicitly clears
// Content-Type on the outgoing config when the body is FormData, so axios's
// transformRequest takes the multipart path instead of the JSON one.

import {renderHook} from '@testing-library/react';
import axiosInstance from '../api/axiosInstance';
import {useHttp} from '../api/search/base';

jest.mock('../api/axiosInstance', () => ({
    __esModule: true,
    default: {request: jest.fn()},
}));

describe('useHttp().request — FormData bodies', () => {
    beforeEach(() => {
        axiosInstance.request.mockReset();
        axiosInstance.request.mockResolvedValue({data: {ok: true}});
    });

    test('clears Content-Type when the body is FormData, so axios sends multipart instead of JSON-stringifying it', async () => {
        const {result} = renderHook(() => useHttp());
        const formData = new FormData();
        formData.append('file', new Blob(['zip-bytes'], {type: 'application/zip'}), 'project.zip');

        await result.current.request('v1/project/1/upload-zip', 'POST', formData);

        expect(axiosInstance.request).toHaveBeenCalledTimes(1);
        const [config] = axiosInstance.request.mock.calls[0];
        expect(config.data).toBe(formData);
        expect(config.headers).toBeDefined();
        expect(config.headers['Content-Type']).toBeUndefined();
        expect('Content-Type' in config.headers).toBe(true);
    });

    test('a plain JSON-string body is unaffected — still parsed and sent without the FormData override', async () => {
        const {result} = renderHook(() => useHttp());

        await result.current.request('v1/some-endpoint', 'POST', JSON.stringify({a: 1}), {Authorization: 'Bearer x'});

        const [config] = axiosInstance.request.mock.calls[0];
        expect(config.data).toEqual({a: 1});
        expect(config.headers).toEqual({});
    });
});
