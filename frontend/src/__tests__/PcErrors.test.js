import { errorMessage } from '../views/teacher/pccontrol/pcErrors';

describe('errorMessage', () => {
    it('string detail as is', () => {
        expect(errorMessage({ response: { data: { detail: 'Nope' } } }, 'F')).toBe('Nope');
    });
    it('array detail -> joined msgs', () => {
        const e = { response: { data: { detail: [{ msg: 'x', loc: [] }, { msg: 'y' }, { loc: [] }] } } };
        expect(errorMessage(e, 'F')).toBe('x; y');
    });
    it('array without usable msgs -> fallback', () => {
        expect(errorMessage({ response: { data: { detail: [{ loc: [] }] } } }, 'F')).toBe('F');
    });
    it('object detail -> fallback', () => {
        expect(errorMessage({ response: { data: { detail: { a: 1 } } } }, 'F')).toBe('F');
    });
    it('custom handler error.message', () => {
        expect(errorMessage({ response: { data: { error: { message: 'Bad' } } } }, 'F')).toBe('Bad');
    });
    it('missing response / network error', () => {
        expect(errorMessage({}, 'F')).toBe('F');
        expect(errorMessage(new Error('Network Error'), 'F')).toBe('Network Error');
        expect(errorMessage(undefined, 'F')).toBe('F');
        expect(errorMessage({ message: { x: 1 } }, 'F')).toBe('F');
    });
});
