import { strings } from '../views/teacher/pccontrol/pcStrings';

describe('pcStrings', () => {
    it('uz and ru have identical key sets', () => {
        expect(Object.keys(strings.uz).sort()).toEqual(Object.keys(strings.ru).sort());
    });
    it('has no empty values', () => {
        for (const lang of ['uz', 'ru']) {
            for (const [k, v] of Object.entries(strings[lang])) {
                expect(typeof v).toBe('string');
                expect(v.trim()).not.toBe('');
            }
        }
    });
});
