import {useCallback} from 'react';
import axiosInstance from '../axiosInstance';

// ── API URL ──
// Используй нужную строку, остальные закомментируй
export const API_URL_DOC = process.env.REACT_APP_API_URL || `http://localhost:8000/`
// export const API_URL_DOC = `http://192.168.43.70:8000/`
// export const API_URL_DOC = `http://100.67.61.71:8000/`
// export const API_URL_DOC = `http://100.68.60.126:8000/`
// export const API_URL_DOC = `http://192.168.1.40:8000/`
// export const API_URL_DOC = `http://100.109.36.66:8000/`

export const API_URL = `${API_URL_DOC}api/`

// Backend stores uploaded files as "/uploads/..." paths.
// External images may be stored as full URLs (http/https/data:).
// This helper resolves either form into an absolute URL the browser can load.
export const resolveImageUrl = (src) => {
    if (!src) return '';
    if (/^(https?:|data:|blob:)/.test(src)) return src;
    return API_URL_DOC + src.replace(/^\//, '');
};

// ── Headers ──
// Kept for legacy call-sites that still build their own headers. New code
// should let axiosInstance attach the Authorization header automatically.
export const headers = () => {
    const token = localStorage.getItem('token');
    return {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    };
};

export const header = () => {
    return {'Content-Type': 'application/json'};
};

export const headersImg = () => {
    const token = localStorage.getItem('token');
    return {'Authorization': 'Bearer ' + token};
};

export const headerImg = () => {
    return {'Authorization': ''};
};

// ── Branch helpers ──
export const branchQuery = () => {
    const branch = localStorage.getItem('selectedBranch');
    return `branch=${branch}`;
};

export const branchQueryId = () => {
    return localStorage.getItem('selectedBranch');
};

// ── HTTP hook ──
// Routes every request through axiosInstance so the 401 → refresh-token
// interceptor actually fires. Previously this used raw fetch() and the
// refresh flow was dead code.
export const useHttp = () => {
    const request = useCallback(async (url, method = 'GET', body = null, customHeaders = null) => {
        // Body shape compatibility: existing callers pass either an object,
        // a JSON string, or FormData. axios handles plain objects natively
        // and FormData automatically; JSON strings we parse back to object.
        let data = body;
        if (typeof body === 'string') {
            try {
                data = JSON.parse(body);
            } catch {
                data = body;
            }
        }

        const isFormData = typeof FormData !== 'undefined' && data instanceof FormData;
        const config = {
            url,
            method,
            data,
        };
        if (customHeaders && !isFormData) {
            // Don't override Content-Type for FormData (axios sets the
            // multipart boundary automatically).
            const {Authorization: _drop, ...rest} = customHeaders;
            config.headers = rest;
        }

        try {
            const response = await axiosInstance.request(config);
            return response.data;
        } catch (e) {
            // Preserve old error shape for callers that .catch on it.
            const status = e.response?.status;
            const message = e.response?.data?.detail || e.message || 'Request failed';
            const err = new Error(`Could not fetch ${url}, status: ${status}: ${message}`);
            err.status = status;
            err.response = e.response;
            throw err;
        }
    }, []);
    return {request};
};

// ── URL params builder ──
export const ParamUrl = (params = {}) => {
    return Object.entries(params)
        .filter(([_, value]) => value !== undefined && value !== null && value !== 'all' && value !== '')
        .map(([key, value]) => {
            if (Array.isArray(value)) return `${encodeURIComponent(key)}=${value.join(',')}`;
            return `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`;
        })
        .join('&');
};

// ── Token helpers (refresh token flow) ──
export const getRefreshToken = () => localStorage.getItem('refresh_token');

export const setTokens = (accessToken, refreshToken) => {
    if (accessToken) localStorage.setItem('token', accessToken);
    if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
};

export const clearTokens = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
};
