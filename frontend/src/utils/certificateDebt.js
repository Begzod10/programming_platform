// A student with a negative balance (owes tuition) is refused a certificate
// download: the backend answers 403 with {code: "negative_balance", message_uz,
// message_ru}. Downloads are requested as blobs, so the JSON error body arrives
// as a Blob and has to be read before it can be shown.

const readBlob = (blob) => (typeof blob.text === 'function'
    ? blob.text()
    : new Promise((resolve, reject) => {
        const r = new FileReader();
        r.onload = () => resolve(String(r.result));
        r.onerror = reject;
        r.readAsText(blob);
    }));

const parseBody = async (data) => {
    try {
        if (typeof Blob !== 'undefined' && data instanceof Blob) return JSON.parse(await readBlob(data));
        if (typeof data === 'string') return JSON.parse(data);
        return data || null;
    } catch {
        return null;
    }
};

/** Localized "you have a debt" text when `error` is the negative-balance refusal, else null. */
export async function debtMessage(error, lang) {
    const res = error?.response;
    if (!res || res.status !== 403) return null;
    const body = await parseBody(res.data);
    const detail = body?.error?.message ?? body?.detail;
    if (!detail || detail.code !== 'negative_balance') return null;
    return lang === 'ru' ? detail.message_ru : detail.message_uz;
}
