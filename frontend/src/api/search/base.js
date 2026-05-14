import { useCallback } from 'react';

export const API_URL_DOC = process.env.REACT_APP_API_URL || `http://localhost:8000/`
export const API_URL = `${API_URL_DOC}api/`

// Backend stores uploaded files as "/uploads/..." paths.
// External images may be stored as full URLs (http/https/data:).
// This helper resolves either form into an absolute URL the browser can load.
export const resolveImageUrl = (src) => {
    if (!src) return '';
    if (/^(https?:|data:|blob:)/.test(src)) return src;
    return API_URL_DOC + src.replace(/^\//, '');
};

export const headers = () => {
    const token = localStorage.getItem("token")
    return {
        "Authorization": "Bearer " + token,
        'Content-Type': 'application/json'
    }
}

export const header = () => {
    return {'Content-Type': 'application/json'}
}

export const headersImg = () => {
    const token = localStorage.getItem("token")
    return {"Authorization": "Bearer " + token}
}

export const headerImg = () => {
    return {"Authorization": ""}
}

export const branchQuery = () => {
    const branch = localStorage.getItem("selectedBranch")
    return `branch=${branch}`
}

export const branchQueryId = () => {
    return localStorage.getItem("selectedBranch")
}

export const useHttp = () => {
    const request = useCallback(async (url, method = 'GET', body = null, headers = {'Content-Type': 'application/json'}) => {
        try {
            const response = await fetch(url, {method, mode: 'cors', body, headers});
            if (!response.ok) {
                throw new Error(`Could not fetch ${url}, status: ${response.status}`);
            }
            return await response.json();
        } catch (e) {
            throw e;
        }
    }, []);
    return {request}
}

export const ParamUrl = (params = {}) => {
    return Object.entries(params)
        .filter(([_, value]) => value !== undefined && value !== null && value !== "all" && value !== "")
        .map(([key, value]) => {
            if (Array.isArray(value)) return `${encodeURIComponent(key)}=${value.join(",")}`;
            return `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`;
        })
        .join("&");
};