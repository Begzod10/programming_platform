import React from 'react';
import { render, screen, fireEvent, act, within } from '@testing-library/react';
import ActivityPath from '../views/student/early-learning/ActivityPath';
import ModuleCard from '../views/student/early-learning/ModuleCard';
import EarlyActivityCelebration, { LevelUnlockContext } from '../views/student/early-learning/EarlyActivityCelebration';
import translations from '../i18n/translations';

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
const lv = (level, best, attempts, unlocked) => ({ level, best_stars: best, attempts, unlocked });
const game = (id, order, levels) => ({
    id, order, title: `Game ${id}`, best_stars: levels ? levels[0].best_stars : 0,
    attempts: levels ? levels[0].attempts : 0, levels,
    content: { character: { emoji: '🍎', label: `Qizil ${id}` } },
});
const stepOf = (id) => screen.getByText(`Qizil ${id}`).closest('li');

test('path node shows three star rows and locks unopened levels', () => {
    render(<ActivityPath t={t} moduleEmoji="🎨" onPlay={() => {}} activities={[
        game(1, 0, [lv(1, 3, 1, true), lv(2, 1, 1, true), lv(3, 0, 0, false)]),
    ]} />);
    const step = within(stepOf(1));
    expect(step.getByRole('button', { name: '1-daraja' })).toBeEnabled();
    expect(step.getByRole('button', { name: '2-daraja' })).toBeEnabled();
    const locked = step.getByRole('button', { name: 'Qulflangan' });
    expect(locked).toBeDisabled();
    expect(locked).toHaveTextContent('🔒');
    expect(stepOf(1).querySelectorAll('.el-star-row')).toHaveLength(2);
});

test('tapping a node starts the highest open level; the picker replays level 1', () => {
    const onPlay = jest.fn();
    const a = game(1, 0, [lv(1, 3, 1, true), lv(2, 1, 1, true), lv(3, 0, 0, false)]);
    render(<ActivityPath t={t} moduleEmoji="🎨" onPlay={onPlay} activities={[a]} />);
    fireEvent.click(screen.getByText('Qizil 1').closest('button'));
    expect(onPlay).toHaveBeenLastCalledWith(a, 2);
    fireEvent.click(within(stepOf(1)).getByRole('button', { name: '1-daraja' }));
    expect(onPlay).toHaveBeenLastCalledWith(a, 1);
    fireEvent.click(within(stepOf(1)).getByRole('button', { name: 'Qulflangan' }));
    expect(onPlay).toHaveBeenCalledTimes(2);
});

test('next node shows the unlock hint for a 1-star game', () => {
    const onPlay = jest.fn();
    const one = game(2, 1, [lv(1, 1, 1, true), lv(2, 0, 0, false), lv(3, 0, 0, false)]);
    const { container } = render(<ActivityPath t={t} moduleEmoji="🎨" onPlay={onPlay} activities={[
        game(1, 0, [lv(1, 3, 1, true), lv(2, 3, 1, true), lv(3, 2, 1, true)]), one,
    ]} />);
    expect(within(stepOf(2)).getByText('Yana 1 yulduz — 2-daraja ochiladi')).toBeInTheDocument();
    expect(stepOf(2).querySelector('.ep-next')).not.toBeNull();
    expect(stepOf(1).querySelector('.ep-next')).toBeNull();
    fireEvent.click(screen.getByText("Keyingi o'yin ▶"));
    expect(onPlay).toHaveBeenLastCalledWith(one, 1);
    expect(container.querySelector('.ep-badge')).toHaveClass('ep-badge-owned');
});

test('module card shows ✓ for level 1 and 👑 for all levels', () => {
    const m = (over) => ({ id: 1, title: 'Rang', activities_count: 2, completed_count: 2, level_plays: 3,
        max_level_plays: 6, earned_stars: 9, max_stars: 18, ...over });
    const { rerender } = render(<ModuleCard t={t} onOpen={() => {}} module={m()} />);
    expect(screen.getByLabelText('Tugallandi')).toHaveTextContent('✓');
    expect(screen.queryByLabelText(t('el.crown'))).not.toBeInTheDocument();
    expect(screen.getByText('9 / 18')).toBeInTheDocument();
    rerender(<ModuleCard t={t} onOpen={() => {}} module={m({ level_plays: 6 })} />);
    expect(screen.getByLabelText(t('el.crown'))).toHaveTextContent('👑');
    expect(screen.queryByLabelText('Tugallandi')).not.toBeInTheDocument();
    rerender(<ModuleCard t={t} onOpen={() => {}} module={m({ completed_count: 1, level_plays: 1 })} />);
    expect(screen.queryByLabelText('Tugallandi')).not.toBeInTheDocument();
});

test('celebration offers the newly opened level and starts it', () => {
    jest.useFakeTimers();
    try {
        const onDone = jest.fn();
        const onPlayNext = jest.fn();
        const { unmount } = render(
            <LevelUnlockContext.Provider value={{ nextLevel: 2, onPlayNext }}>
                <EarlyActivityCelebration stars={2} onDone={onDone} t={t} />
            </LevelUnlockContext.Provider>
        );
        expect(screen.getByText('🔓 2-daraja ochildi!')).toBeInTheDocument();
        // The offer waits for the kid instead of closing itself.
        act(() => { jest.advanceTimersByTime(5000); });
        expect(onDone).not.toHaveBeenCalled();
        fireEvent.click(screen.getByRole('button', { name: "O'ynash" }));
        act(() => { jest.advanceTimersByTime(500); });
        expect(onPlayNext).toHaveBeenCalledTimes(1);
        expect(onDone).toHaveBeenCalledTimes(1);
        unmount();
        // One star opens nothing: no offer.
        render(
            <LevelUnlockContext.Provider value={{ nextLevel: 2, onPlayNext }}>
                <EarlyActivityCelebration stars={1} onDone={onDone} t={t} />
            </LevelUnlockContext.Provider>
        );
        expect(screen.queryByText('🔓 2-daraja ochildi!')).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: "O'ynash" })).not.toBeInTheDocument();
    } finally {
        jest.useRealTimers();
    }
});

test('an old cached module without levels still plays level 1', () => {
    const onPlay = jest.fn();
    const old = { ...game(1, 0, undefined), best_stars: 3, attempts: 1 };
    delete old.levels;
    render(<ActivityPath t={t} moduleEmoji="🎨" onPlay={onPlay} activities={[old]} />);
    expect(within(stepOf(1)).queryByRole('button', { name: '2-daraja' })).not.toBeInTheDocument();
    expect(within(stepOf(1)).queryByRole('button', { name: 'Qulflangan' })).not.toBeInTheDocument();
    expect(stepOf(1).querySelectorAll('.el-star-row')).toHaveLength(1);
    fireEvent.click(screen.getByText('Qizil 1').closest('button'));
    expect(onPlay).toHaveBeenLastCalledWith(old, 1);
});
