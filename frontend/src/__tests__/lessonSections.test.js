import { ensureSectionIds, sectionId } from '../utils/lessonSections';

describe('ensureSectionIds', () => {
    test('gives sections without an id a stable, unique one (the bulk-imported lessons)', () => {
        const s = ensureSectionIds(529, [{ type: 'text' }, { type: 'code' }, { type: 'code' }, { type: 'exercise' }]);
        expect(s.map(x => x.id)).toEqual(['s529-0', 's529-1', 's529-2', 's529-3']);
        expect(new Set(s.map(x => x.id)).size).toBe(4);
        expect(s[0].id).toBe(sectionId(529, 0));
    });

    test('keeps the ids that are already there, including numbers', () => {
        const s = ensureSectionIds(5, [{ id: 'abc' }, { id: 7 }, { id: 'p5' }]);
        expect(s.map(x => x.id)).toEqual(['abc', 7, 'p5']);
    });

    test('repairs blank and duplicate ids but never renames the first holder', () => {
        const s = ensureSectionIds(9, [{ id: 'x' }, { id: '' }, { id: 'x' }, { id: null }, { id: 'y' }]);
        expect(s.map(x => x.id)).toEqual(['x', 's9-1', 's9-2', 's9-3', 'y']);
    });

    test('is idempotent and tolerates garbage', () => {
        const s = ensureSectionIds(1, [{}, {}]);
        const again = ensureSectionIds(1, JSON.parse(JSON.stringify(s)));
        expect(again).toEqual(s);
        expect(ensureSectionIds(1, null)).toBeNull();
        expect(ensureSectionIds(1, [null, 'x', 3, {}]).length).toBe(4);
    });
});
