jest.mock('lucide-react', () => new Proxy({ __esModule: true }, {
    get: (t, p) => (p in t || typeof p === 'symbol' ? t[p] : () => null),
}));

import { blankWord } from '../views/student/dictionary/PracticeModes';

describe('blankWord (cloze)', () => {
    test('blanks every occurrence, not just the first', () => {
        expect(blankWord('array is an array of items', 'array')).toBe('_____ is an _____ of items');
    });

    test('finds Cyrillic words and symbol-edged words that \\b missed', () => {
        expect(blankWord('Это массив чисел', 'массив')).toBe('Это _____ чисел');
        expect(blankWord('Use C++ for speed', 'C++')).toBe('Use _____ for speed');
    });

    test('blanks Uzbek apostrophe and plain suffix forms', () => {
        expect(blankWord("JavaScript'da kod yoziladi", 'JavaScript')).toBe('_____ kod yoziladi');
        expect(blankWord('funksiyalar va funksiyani', 'funksiya')).toBe('_____ va _____');
    });

    test('does not blank part of a longer word for short targets', () => {
        expect(blankWord('interface in the end', 'in')).toBe('interface _____ the end');
    });

    test('returns null when the word is not in the sentence', () => {
        expect(blankWord('nothing here', 'array')).toBeNull();
        expect(blankWord('', 'array')).toBeNull();
    });
});
