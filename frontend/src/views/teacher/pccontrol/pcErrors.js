// Always returns a string: FastAPI 422s carry `detail` as an array of objects.
const str = (v) => (typeof v === 'string' && v.trim() ? v : null);

export function errorMessage(e, fallback) {
    const data = e?.response?.data;
    const detail = data?.detail;
    if (str(detail)) return detail;
    if (Array.isArray(detail)) {
        const msgs = detail.map(i => str(i?.msg)).filter(Boolean);
        if (msgs.length) return msgs.join('; ');
    }
    // No e.message: axios/fetch network errors carry raw English text with URLs.
    return str(data?.error?.message) || fallback;
}

// Maintenance-code errors are mapped by status, never by server text.
export function maintenanceError(e, t) {
    const status = e?.status ?? e?.response?.status;
    if (status === 429) return t.maintTooMany;
    if (status === 404) return t.maintNoDevice;
    return t.maintFailed;
}
