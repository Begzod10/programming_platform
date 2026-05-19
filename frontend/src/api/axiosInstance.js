import axios from 'axios';
import { API_URL } from './search/base';

// [REFACTOR] Centralized Axios instance with interceptors for auth token management
const axiosInstance = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' },
});

// ── Flag to prevent multiple simultaneous refresh attempts ──
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(({ resolve, reject }) => {
        if (error) reject(error);
        else resolve(token);
    });
    failedQueue = [];
};

// ── Request interceptor: attach access token ──
axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// ── Response interceptor: handle 401 + refresh token flow ──
axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Only attempt refresh on 401 and if we haven't already retried
        if (error.response?.status === 401 && !originalRequest._retry) {
            // Don't try to refresh if this IS the refresh request or login/register
            const url = originalRequest.url || '';
            if (url.includes('/auth/refresh') || url.includes('/auth/login') || url.includes('/auth/register')) {
                return Promise.reject(error);
            }

            if (isRefreshing) {
                // Queue this request until refresh completes
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                }).then((token) => {
                    originalRequest.headers['Authorization'] = `Bearer ${token}`;
                    return axiosInstance(originalRequest);
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            const refreshToken = localStorage.getItem('refresh_token');

            if (!refreshToken) {
                // No refresh token available — force logout
                isRefreshing = false;
                processQueue(error);
                // Dispatch custom event so AuthContext can handle logout
                window.dispatchEvent(new Event('auth:logout'));
                return Promise.reject(error);
            }

            try {
                const response = await axios.post(`${API_URL}v1/auth/refresh`, {
                    refresh_token: refreshToken,
                });

                const newAccessToken = response.data.access_token || response.data.token || response.data.access;
                const newRefreshToken = response.data.refresh_token;

                if (newAccessToken) {
                    localStorage.setItem('token', newAccessToken);
                }
                if (newRefreshToken) {
                    localStorage.setItem('refresh_token', newRefreshToken);
                }

                isRefreshing = false;
                processQueue(null, newAccessToken);

                // Retry the original request with new token
                originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
                return axiosInstance(originalRequest);
            } catch (refreshError) {
                isRefreshing = false;
                processQueue(refreshError);

                // Refresh failed — clear tokens and force logout
                localStorage.removeItem('token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user');
                window.dispatchEvent(new Event('auth:logout'));
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default axiosInstance;
