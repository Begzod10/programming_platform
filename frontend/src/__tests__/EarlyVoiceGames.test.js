import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import MatchingActivity from '../views/student/early-learning/MatchingActivity';
import BuildActivity from '../views/student/early-learning/BuildActivity';
import CompareActivity from '../views/student/early-learning/CompareActivity';
import EarlyActivityCelebration from '../views/student/early-learning/EarlyActivityCelebration';
import translations from '../i18n/translations';

jest.mock('../api/search/base', () => ({
    useHttp: () => ({ request: jest.fn(() => Promise.resolve({})) }),
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

const voice = require('../views/student/early-learning/earlyVoice');
const t = (key) => translations.uz[key] || key;
const base = { onBack: jest.fn(), onComplete: jest.fn(), lang: 'uz', toggleLang: jest.fn(), t };
const instruction = { instruction_text: "Mevalarni top.", instruction_audio_url: '/uploads/early-audio/uz/m.mp3' };

beforeEach(() => jest.clearAllMocks());

const matching = () => ({
    id: 5, title: 'Mevalar', ...instruction,
    content: {
        mode: 'select', character: { emoji: '🧺', label: 'Savat' },
        correct_items: [{ id: 'a', label: 'Olma', emoji: '🍎' }, { id: 'b', label: 'Nok', emoji: '🍐' }],
        distractor_items: [{ id: 'c', label: 'Mashina', emoji: '🚗' }],
    },
});

test('MatchingActivity shows the instruction with a listen button', () => {
    render(<MatchingActivity activity={matching()} {...base} />);
    expect(screen.getByText('Mevalarni top.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Eshitish' })).toBeInTheDocument();
    expect(voice.playVoice).toHaveBeenCalledWith('/uploads/early-audio/uz/m.mp3');
});

test('a correct pick in MatchingActivity cheers correct, a wrong pick cheers wrong', () => {
    render(<MatchingActivity activity={matching()} {...base} />);
    fireEvent.click(screen.getByText('Olma'));
    expect(voice.cheer).toHaveBeenCalledWith('correct');
    fireEvent.click(screen.getByText('Mashina'));
    expect(voice.cheer).toHaveBeenCalledWith('wrong');
});

test('BuildActivity shows the instruction', () => {
    render(<BuildActivity activity={{
        id: 6, title: 'Uy', ...instruction, instruction_text: 'Uyni yasa.',
        content: { mode: 'build', character: { emoji: '🏠', label: 'Uy' }, slots: [], pieces: [] },
    }} {...base} />);
    expect(screen.getByText('Uyni yasa.')).toBeInTheDocument();
});

test('ActivityShell games keep the instruction class name', () => {
    const { container } = render(<CompareActivity activity={{
        id: 7, title: 'Taqqosla', ...instruction, instruction_text: 'Belgini tanla.',
        content: { mode: 'compare', rounds: 3 },
    }} {...base} />);
    expect(container.querySelector('.aa-instruction')).toHaveTextContent('Belgini tanla.');
});

test('celebration says the phrase for its star count', () => {
    render(<EarlyActivityCelebration stars={2} onDone={jest.fn()} t={t} />);
    expect(voice.cheerStars).toHaveBeenCalledWith(2);
});
