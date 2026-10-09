/** The text of an API error: the app wraps FastAPI errors as {error: {message}}. */
export const apiErrorMessage = (e) => {
    const body = e?.response?.data;
    const msg = body?.error?.message ?? body?.detail;
    return typeof msg === 'string' ? msg : '';
};
