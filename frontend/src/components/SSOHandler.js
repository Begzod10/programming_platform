import { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

// Mirrored from axiosInstance.js (kept in sync there too). A plain axios
// call is used here rather than axiosInstance — a 401 from a bad/expired
// SSO token must not trigger axiosInstance's refresh-token interceptor
// with a stale token left over from a previous session.
const API_URL_DOC = process.env.REACT_APP_API_URL || 'http://localhost:8000/';
const API_URL = `${API_URL_DOC}api/`;

/**
 * classroom -> student_platform SSO handoff — see
 * docs/CLASSROOM_SSO_FOR_STUDENT_PLATFORM.md, section 6.
 *
 * A student arrives at https://<us>/#sso=<TOKEN> from inside classroom.
 * This exchanges that token for a normal session BEFORE rendering the rest
 * of the app (`children`, i.e. AppRouter) — otherwise RootRedirect sees the
 * pre-exchange unauthenticated state on the first render and bounces the
 * student to /login before the SSO call has a chance to complete.
 */
function SSOHandler({ children }) {
    const { login } = useAuth();
    const [pending, setPending] = useState(() =>
        new URLSearchParams(window.location.hash.slice(1)).has('sso')
    );

    useEffect(() => {
        if (!pending) return;

        const token = new URLSearchParams(window.location.hash.slice(1)).get('sso');

        // Clear the hash BEFORE the request resolves, not after — a page
        // refresh mid-flight (or the back button) must not re-send this
        // one-time token and hit the replay guard on the backend.
        window.history.replaceState(null, '', window.location.pathname + window.location.search);

        if (!token) {
            setPending(false);
            return;
        }

        axios
            .post(`${API_URL}v1/auth/sso`, { token })
            .then((response) => {
                login(response.data, true);
            })
            .catch(() => {
                // Not an error the student needs to see — they fall back to
                // the normal login page and use their gennis/turon
                // password, exactly as the doc specifies for a rejected
                // SSO token.
            })
            .finally(() => setPending(false));
        // Runs once: `pending`'s initial value already gates this to a
        // single execution, and login/token never change mid-flight.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    if (pending) {
        return <div className="sso-loading">Kirilmoqda...</div>;
    }

    return children;
}

export default SSOHandler;
