// Mock external dependencies so Jest can load the module without real imports.
// jest.mock() calls are hoisted by babel-jest before any imports are resolved.
jest.mock('lucide-react', () => ({ Flame: () => null }));
jest.mock('../api/search/base', () => ({
  API_URL: 'http://test/',
  headers: () => ({}),
}));

import {
  norm,
  editDistance,
  judgeTyped,
  fireLevelFor,
} from '../views/student/dictionary/practiceUtils';

// ─── norm ──────────────────────────────────────────────────────────────────

describe('norm', () => {
  test('returns empty string for empty input', () => {
    expect(norm('')).toBe('');
  });

  test('returns empty string for null / falsy', () => {
    expect(norm(null)).toBe('');
    expect(norm(undefined)).toBe('');
  });

  test('trims leading and trailing whitespace', () => {
    expect(norm('  hello  ')).toBe('hello');
  });

  test('lowercases the result', () => {
    expect(norm('HELLO')).toBe('hello');
    expect(norm('MiXeD')).toBe('mixed');
  });

  test('strips combining diacritical marks from accented characters', () => {
    // é → e + U+0301 after NFKD, combining mark stripped → e
    expect(norm('café')).toBe('cafe');
    // ñ → n + U+0303 after NFKD → n
    expect(norm('español')).toBe('espanol');
    // ü → u + U+0308 after NFKD → u
    expect(norm('über')).toBe('uber');
  });

  test('combines trimming, lowercasing, and diacritic removal', () => {
    expect(norm('  Ñoño  ')).toBe('nono');
  });
});

// ─── editDistance ──────────────────────────────────────────────────────────

describe('editDistance', () => {
  test('returns 0 for identical strings', () => {
    expect(editDistance('hello', 'hello')).toBe(0);
  });

  test('returns 0 for two empty strings', () => {
    expect(editDistance('', '')).toBe(0);
  });

  test('returns length of b when a is empty', () => {
    expect(editDistance('', 'abc')).toBe(3);
  });

  test('returns length of a when b is empty', () => {
    expect(editDistance('abc', '')).toBe(3);
  });

  test('single substitution', () => {
    expect(editDistance('cat', 'cut')).toBe(1);
  });

  test('single insertion', () => {
    expect(editDistance('hello', 'helllo')).toBe(1);
  });

  test('single deletion', () => {
    expect(editDistance('helllo', 'hello')).toBe(1);
  });

  test('classic kitten → sitting = 3', () => {
    expect(editDistance('kitten', 'sitting')).toBe(3);
  });

  test('completely different strings', () => {
    // "abc" → "xyz": 3 substitutions
    expect(editDistance('abc', 'xyz')).toBe(3);
  });
});

// ─── judgeTyped ────────────────────────────────────────────────────────────

describe('judgeTyped', () => {
  test('exact match returns {ok:true, exact:true}', () => {
    expect(judgeTyped('hello', 'hello')).toEqual({ ok: true, exact: true });
  });

  test('exact match is case-insensitive (normalisation)', () => {
    expect(judgeTyped('HELLO', 'hello')).toEqual({ ok: true, exact: true });
  });

  test('exact match ignores surrounding whitespace', () => {
    expect(judgeTyped('  hello  ', 'hello')).toEqual({ ok: true, exact: true });
  });

  test('empty input returns {ok:false, exact:false}', () => {
    expect(judgeTyped('', 'hello')).toEqual({ ok: false, exact: false });
    expect(judgeTyped('   ', 'hello')).toEqual({ ok: false, exact: false });
  });

  test('off-by-1 on a word with >= 4 chars returns {ok:true, exact:false}', () => {
    // "helllo" vs "hello": dist 1, b.length 5 >= 4
    expect(judgeTyped('helllo', 'hello')).toEqual({ ok: true, exact: false });
  });

  test('off-by-2 on a word with >= 4 chars returns {ok:true, exact:false}', () => {
    // "hellloo" vs "hello": dist 2, b.length 5 >= 4
    expect(judgeTyped('hellloo', 'hello')).toEqual({ ok: true, exact: false });
  });

  test('off-by-3 on a word with >= 4 chars returns {ok:false, exact:false}', () => {
    // "helllooo" vs "hello": dist 3, exceeds threshold
    expect(judgeTyped('helllooo', 'hello')).toEqual({ ok: false, exact: false });
  });

  test('short target (< 4 chars) only accepts exact match', () => {
    // "cat" vs "cut": dist 1, but b.length 3 < 4 → reject
    expect(judgeTyped('cat', 'cut')).toEqual({ ok: false, exact: false });
  });

  test('short target exact match still accepted', () => {
    expect(judgeTyped('cat', 'cat')).toEqual({ ok: true, exact: true });
  });

  test('diacritics are normalised before comparison', () => {
    // "cafe" matches "café" after norm strips the accent
    expect(judgeTyped('cafe', 'café')).toEqual({ ok: true, exact: true });
  });
});

// ─── fireLevelFor ─────────────────────────────────────────────────────────

describe('fireLevelFor', () => {
  test('streak 0 → level 0', () => {
    expect(fireLevelFor(0)).toBe(0);
  });

  test('streak 2 → level 0 (below threshold)', () => {
    expect(fireLevelFor(2)).toBe(0);
  });

  test('streak 3 → level 1', () => {
    expect(fireLevelFor(3)).toBe(1);
  });

  test('streak 4 → level 1 (upper edge of range)', () => {
    expect(fireLevelFor(4)).toBe(1);
  });

  test('streak 5 → level 2', () => {
    expect(fireLevelFor(5)).toBe(2);
  });

  test('streak 7 → level 2 (upper edge of range)', () => {
    expect(fireLevelFor(7)).toBe(2);
  });

  test('streak 8 → level 3', () => {
    expect(fireLevelFor(8)).toBe(3);
  });

  test('streak 10 → level 3 (well above threshold)', () => {
    expect(fireLevelFor(10)).toBe(3);
  });
});
