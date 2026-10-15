import { debtMessage } from '../utils/certificateDebt';

const refusal = (extra = {}) => ({
    response: {
        status: 403,
        // downloads are requested as blobs, so the JSON error arrives as a Blob
        data: new Blob([JSON.stringify({
            success: false,
            error: { code: 403, message: {
                code: 'negative_balance', debt: 250000,
                message_uz: "Hisobingizda 250 000 so'm qarz bor.", message_ru: 'На вашем счёте задолженность 250 000 сум.',
                ...extra,
            } },
        })]),
    },
});

describe('debtMessage', () => {
    test('returns the Uzbek text for an Uzbek student', async () => {
        expect(await debtMessage(refusal(), 'uz')).toBe("Hisobingizda 250 000 so'm qarz bor.");
    });

    test('returns the Russian text for a Russian student', async () => {
        expect(await debtMessage(refusal(), 'ru')).toBe('На вашем счёте задолженность 250 000 сум.');
    });

    test('reads a plain (non-blob) body too', async () => {
        const e = { response: { status: 403, data: { error: { message: { code: 'negative_balance', message_uz: 'uz', message_ru: 'ru' } } } } };
        expect(await debtMessage(e, 'ru')).toBe('ru');
    });

    test('ignores other errors', async () => {
        expect(await debtMessage({ response: { status: 404, data: new Blob(['{}']) } }, 'uz')).toBeNull();
        expect(await debtMessage({ response: { status: 403, data: new Blob([JSON.stringify({ error: { message: 'Ruxsat yo\'q' } })]) } }, 'uz')).toBeNull();
        expect(await debtMessage({ response: { status: 403, data: new Blob(['not json']) } }, 'uz')).toBeNull();
        expect(await debtMessage(new Error('network'), 'uz')).toBeNull();
        expect(await debtMessage(null, 'uz')).toBeNull();
    });
});
