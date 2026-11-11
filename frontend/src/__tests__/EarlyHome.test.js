import {
    SECTIONS, isFinished, pickContinue, pickNew, groupBySection, nextActivity,
} from '../views/student/early-learning/earlyHome';
import { applyGuestModuleStars } from '../views/student/early-learning/earlyLearningUtils';

const m = (id, over) => ({
    id, title: `M${id}`, display_order: id, activities_count: 10, completed_count: 0,
    last_played_at: null, section: 'world', earned_stars: 0, max_stars: 30, ...over,
});

beforeEach(() => { localStorage.clear(); });

describe('home selection logic', () => {
    test('sections are in the agreed order', () => {
        expect(SECTIONS.map((s) => s.key)).toEqual(['world', 'logic', 'make', 'letters']);
    });

    test('pickContinue takes the most recently played unfinished module', () => {
        const pick = pickContinue([
            m(1, { completed_count: 3, last_played_at: '2026-11-01T10:00:00Z' }),
            m(2, { completed_count: 1, last_played_at: '2026-11-10T10:00:00Z' }),
            m(3, { completed_count: 10, last_played_at: '2026-11-11T10:00:00Z' }),
        ]);
        expect(pick.module.id).toBe(2);
        expect(pick.started).toBe(true);
    });

    test('pickContinue falls back to a started module without timestamps (guest)', () => {
        const pick = pickContinue([m(1), m(2, { completed_count: 4 })]);
        expect(pick.module.id).toBe(2);
        expect(pick.started).toBe(true);
    });

    test('pickContinue offers the first module as a start', () => {
        const pick = pickContinue([m(2), m(1)]);
        expect(pick.module.id).toBe(1);
        expect(pick.started).toBe(false);
    });

    test('pickContinue returns null when everything is finished or the list is empty', () => {
        expect(pickContinue([m(1, { completed_count: 10 }), m(2, { completed_count: 12 })])).toBeNull();
        expect(pickContinue([])).toBeNull();
        expect(pickContinue(undefined)).toBeNull();
    });

    test('pickContinue skips empty modules', () => {
        expect(pickContinue([m(1, { activities_count: 0 }), m(2)]).module.id).toBe(2);
        expect(pickContinue([m(1, { activities_count: 0 })])).toBeNull();
    });

    test('isFinished is false for an empty module', () => {
        expect(isFinished(m(1, { activities_count: 0 }))).toBe(false);
        expect(isFinished(m(1, { completed_count: 10 }))).toBe(true);
        expect(isFinished(m(1, { completed_count: 9 }))).toBe(false);
        expect(isFinished({ id: 1 })).toBe(false);
    });

    test('pickNew lists untouched modules newest first, without the continue module, capped at 6', () => {
        const modules = [m(1, { completed_count: 2 }), ...[2, 3, 4, 5, 6, 7, 8, 9].map((id) => m(id))];
        expect(pickNew(modules, modules[0]).map((x) => x.id)).toEqual([9, 8, 7, 6, 5, 4]);
        expect(pickNew(modules, modules[0], 2).map((x) => x.id)).toEqual([9, 8]);
        // an untouched module chosen as "continue" is not repeated in the row
        const mixed = [m(1, { completed_count: 10 }), m(2), m(3)];
        expect(pickNew(mixed, mixed[1]).map((x) => x.id)).toEqual([3]);
    });

    test('pickNew is empty when nothing was played yet', () => {
        expect(pickNew([m(1), m(2)], null)).toEqual([]);
        expect(pickNew([], null)).toEqual([]);
    });

    test('pickNew leaves out empty modules', () => {
        const modules = [m(1, { completed_count: 2 }), m(2, { activities_count: 0 }), m(3)];
        expect(pickNew(modules, modules[0]).map((x) => x.id)).toEqual([3]);
    });

    test('groupBySection orders sections and sinks finished modules', () => {
        const groups = groupBySection([
            m(5, { section: 'logic' }), m(2, { completed_count: 10 }), m(3), m(1),
        ]);
        expect(groups.map((g) => g.key)).toEqual(['world', 'logic']);
        expect(groups[0].modules.map((x) => x.id)).toEqual([1, 3, 2]);
        expect(groups[0].titleKey).toBe('el.homeWorld');
    });

    test('groups modules without a section under world', () => {
        const groups = groupBySection([{ id: 7, title: 'Old', display_order: 1 }, m(8, { section: 'no_such' })]);
        expect(groups).toHaveLength(1);
        expect(groups[0].key).toBe('world');
        expect(groups[0].modules.map((x) => x.id)).toEqual([7, 8]);
    });

    test('nextActivity returns the first unplayed by order, or null', () => {
        const acts = [{ id: 1, order: 2, attempts: 0 }, { id: 2, order: 1, attempts: 0 }, { id: 3, order: 0, attempts: 2 }];
        expect(nextActivity(acts).id).toBe(2);
        expect(nextActivity(acts.map((a) => ({ ...a, attempts: 1 })))).toBeNull();
        expect(nextActivity([])).toBeNull();
        expect(nextActivity(undefined)).toBeNull();
    });

    test('guest progress fills completed_count', () => {
        localStorage.setItem('el_guest_progress', JSON.stringify({ 11: { stars_earned: 2, attempts: 1 } }));
        const [patched] = applyGuestModuleStars([{ id: 1, activity_ids: [11, 12] }]);
        expect(patched.completed_count).toBe(1);
        expect(patched.earned_stars).toBe(2);
    });
});
