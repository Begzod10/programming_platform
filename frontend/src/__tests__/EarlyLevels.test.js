import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import {
    recordGuestCompletion, guestLevels, applyGuestActivityStars, applyGuestModuleStars,
    queueCompletion, flushCompletionQueue,
} from '../views/student/early-learning/earlyLearningUtils';
import {
    nextStep, isFinished, isDone, pickContinue, startLevel, levelsOf, groupBySection,
} from '../views/student/early-learning/earlyHome';
import MatchingActivity from '../views/student/early-learning/MatchingActivity';
import { useActivityCompletion } from '../views/student/early-learning/ActivityShell';
import translations from '../i18n/translations';

const mockRequest = jest.fn(() => Promise.resolve({ activity_id: 1, stars_earned: 3, attempts: 1 }));
jest.mock('../api/search/base', () => ({
    useHttp: () => ({ request: mockRequest }),
    API_URL: '/api/', API_URL_DOC: '/', headers: () => ({}),
}));
jest.mock('../utils/soundSynth', () => ({ playSynth: jest.fn(), playSoundAsset: jest.fn() }));
jest.mock('../views/student/early-learning/earlyVoice', () => ({
    cheer: jest.fn(() => true),
    cheerStars: jest.fn(() => true),
    playVoice: jest.fn(() => Promise.resolve(true)),
    stopVoice: jest.fn(),
    loadPhrases: jest.fn(() => Promise.resolve({})),
    currentLang: () => 'uz',
    isVoiceOn: () => true,
    setVoiceOn: jest.fn(),
}));

const t = (key) => translations.uz[key] || key;

beforeEach(() => {
    localStorage.clear();
    mockRequest.mockImplementation(() => Promise.resolve({ activity_id: 1, stars_earned: 3, attempts: 1 }));
});

const lv = (level, best, attempts, unlocked) => ({ level, best_stars: best, attempts, unlocked });
const a = (id, order, levels, over) => ({
    id, order, best_stars: levels[0].best_stars, attempts: levels[0].attempts, levels, ...over,
});
const fresh = () => [lv(1, 0, 0, true), lv(2, 0, 0, false), lv(3, 0, 0, false)];

test('guest progress stores levels separately and unlocks at two stars', () => {
    recordGuestCompletion(7, 1);
    expect(guestLevels(7)).toEqual([lv(1, 1, 1, true), lv(2, 0, 0, false), lv(3, 0, 0, false)]);
    recordGuestCompletion(7, 2, 1);
    recordGuestCompletion(7, 3, 2);
    expect(guestLevels(7)).toEqual([lv(1, 2, 2, true), lv(2, 3, 1, true), lv(3, 0, 0, true)]);
    const stored = JSON.parse(localStorage.getItem('el_guest_progress'));
    expect(Object.keys(stored).sort()).toEqual(['7', '7:2']);
    const detail = applyGuestActivityStars({ activities: [{ id: 7, best_stars: 0, attempts: 0 }], earned_stars: 0 });
    expect(detail.activities[0].levels[1]).toEqual(lv(2, 3, 1, true));
    expect(detail.activities[0].best_stars).toBe(2);
    expect(detail.earned_stars).toBe(5);
    expect(detail.level_plays).toBe(2);
    const [mod] = applyGuestModuleStars([{ id: 1, activity_ids: [7, 8], max_stars: 18 }]);
    expect(mod).toMatchObject({ earned_stars: 5, completed_count: 1, level_plays: 2, max_level_plays: 6, max_stars: 18 });
});

test('offline queue keeps level and old entries default to level 1', async () => {
    localStorage.setItem('el_star_queue_v1', JSON.stringify([{ activityId: 4, stars: 2 }]));
    queueCompletion(4, 3, 2);
    queueCompletion(4, 1, 2);
    queueCompletion(4, 3);
    const sent = [];
    await flushCompletionQueue(async (id, stars, level) => { sent.push([id, stars, level]); });
    expect(sent).toEqual([[4, 3, 1], [4, 3, 2]]);
    expect(JSON.parse(localStorage.getItem('el_star_queue_v1'))).toEqual([]);
});

test('nextStep: unplayed level 1 first, then lowest unlocked unplayed level', () => {
    const acts = [
        a(1, 0, [lv(1, 3, 1, true), lv(2, 0, 0, true), lv(3, 0, 0, false)]),
        a(2, 1, fresh()),
    ];
    expect(nextStep(acts)).toEqual({ activity: acts[1], level: 1 });
    const played = [acts[0], a(2, 1, [lv(1, 2, 1, true), lv(2, 3, 1, true), lv(3, 0, 0, true)])];
    expect(nextStep(played)).toEqual({ activity: played[0], level: 2 });
    const second = [a(1, 0, [lv(1, 3, 1, true), lv(2, 1, 1, true), lv(3, 0, 0, false)]), played[1]];
    expect(nextStep(second)).toEqual({ activity: second[1], level: 3 });
});

test('nextStep: a 1-star game is offered with an unlock hint when nothing else is open', () => {
    const acts = [
        a(1, 0, [lv(1, 3, 1, true), lv(2, 3, 1, true), lv(3, 3, 1, true)]),
        a(2, 1, [lv(1, 3, 1, true), lv(2, 1, 2, true), lv(3, 0, 0, false)]),
        a(3, 2, [lv(1, 1, 1, true), lv(2, 0, 0, false), lv(3, 0, 0, false)]),
    ];
    expect(nextStep(acts)).toEqual({ activity: acts[1], level: 2, unlockHint: 3 });
    // Every level-1 played with one star: the first game is offered again.
    const ones = [a(1, 0, [lv(1, 1, 1, true), lv(2, 0, 0, false), lv(3, 0, 0, false)]),
        a(2, 1, [lv(1, 1, 1, true), lv(2, 0, 0, false), lv(3, 0, 0, false)])];
    expect(nextStep(ones)).toEqual({ activity: ones[0], level: 1, unlockHint: 2 });
});

test('nextStep returns null only when every level is played', () => {
    const all = [a(1, 0, [lv(1, 3, 1, true), lv(2, 2, 1, true), lv(3, 1, 1, true)])];
    expect(nextStep(all)).toBeNull();
    expect(nextStep([])).toBeNull();
    expect(nextStep(undefined)).toBeNull();
});

test('isFinished means crown (all levels), isDone means level 1 complete', () => {
    const m = (over) => ({ id: 1, activities_count: 2, completed_count: 2, level_plays: 2, max_level_plays: 6, ...over });
    expect(isDone(m())).toBe(true);
    expect(isFinished(m())).toBe(false);
    expect(isFinished(m({ level_plays: 6 }))).toBe(true);
    expect(isDone(m({ completed_count: 1 }))).toBe(false);
    expect(isDone({ id: 1, activities_count: 0 })).toBe(false);
    expect(isFinished({ id: 1, activities_count: 0, max_level_plays: 0 })).toBe(false);
    expect(isFinished({ id: 1, activities_count: 2, completed_count: 2 })).toBe(false); // old cache
});

test('pickContinue skips crowned modules and keeps ✓-only modules', () => {
    const crowned = { id: 1, display_order: 1, activities_count: 2, completed_count: 2, level_plays: 6,
        max_level_plays: 6, last_played_at: '2026-11-15T10:00:00Z' };
    const checked = { id: 2, display_order: 2, activities_count: 2, completed_count: 2, level_plays: 3,
        max_level_plays: 6, last_played_at: '2026-11-10T10:00:00Z' };
    expect(pickContinue([crowned, checked]).module.id).toBe(2);
    expect(pickContinue([crowned])).toBeNull();
    const groups = groupBySection([crowned, checked]);
    expect(groups[0].modules.map((x) => x.id)).toEqual([2, 1]);
});

test('startLevel picks the highest open level without three stars', () => {
    expect(startLevel(a(1, 0, fresh()))).toBe(1);
    expect(startLevel(a(1, 0, [lv(1, 3, 1, true), lv(2, 1, 1, true), lv(3, 0, 0, false)]))).toBe(2);
    expect(startLevel(a(1, 0, [lv(1, 2, 1, true), lv(2, 2, 1, true), lv(3, 0, 0, true)]))).toBe(3);
    expect(startLevel(a(1, 0, [lv(1, 3, 1, true), lv(2, 3, 1, true), lv(3, 3, 1, true)]))).toBe(3);
    expect(startLevel(a(1, 0, [lv(1, 1, 1, true), lv(2, 0, 0, false), lv(3, 0, 0, false)]))).toBe(1);
});

test('levelsOf falls back to level 1 only for an old cached activity', () => {
    expect(levelsOf({ id: 1, best_stars: 3, attempts: 2 })).toEqual([lv(1, 3, 2, true), lv(2, 0, 0, false), lv(3, 0, 0, false)]);
    expect(levelsOf({ id: 1 })).toEqual(fresh());
    const levels = [lv(1, 3, 1, true), lv(2, 1, 1, true), lv(3, 0, 0, false)];
    expect(levelsOf({ id: 1, levels })).toBe(levels);
});

function ShellHarness({ activity }) {
    const completion = useActivityCompletion(activity, false, () => {});
    return (
        <div>
            <button type="button" onClick={() => completion.finish(2)}>finish</button>
            {completion.celebration !== null && <button type="button" onClick={completion.done}>done</button>}
        </div>
    );
}

test('every completion request sends the level', async () => {
    render(<ShellHarness activity={{ id: 9, level: 2, content: {} }} />);
    fireEvent.click(screen.getByText('finish'));
    await act(async () => { fireEvent.click(screen.getByText('done')); });
    expect(mockRequest).toHaveBeenLastCalledWith('/api/v1/early-learning/activities/9/complete', 'POST', { stars: 2, level: 2 }, {});

    jest.useFakeTimers();
    try {
        const onComplete = jest.fn();
        render(<MatchingActivity
            activity={{ id: 5, title: 'M', content: { mode: 'select', correct_items: [{ id: 'a', label: 'Olma', emoji: '🍎' }], distractor_items: [] } }}
            onBack={() => {}} onComplete={onComplete} lang="uz" toggleLang={() => {}} t={t}
        />);
        fireEvent.click(screen.getByText('Olma'));
        act(() => { jest.advanceTimersByTime(1000); });
        await act(async () => {
            fireEvent.click(screen.getByText(t('el.continueBtn')));
            jest.advanceTimersByTime(500);
        });
        expect(mockRequest).toHaveBeenLastCalledWith('/api/v1/early-learning/activities/5/complete', 'POST', { stars: 3, level: 1 }, {});
    } finally {
        jest.useRealTimers();
    }
});
