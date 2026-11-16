import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import MatchingActivity from '../views/student/early-learning/MatchingActivity';
import BuildActivity from '../views/student/early-learning/BuildActivity';
import CompareActivity from '../views/student/early-learning/CompareActivity';
import EarlyActivityCelebration from '../views/student/early-learning/EarlyActivityCelebration';
import RoundsActivity from '../views/student/early-learning/RoundsActivity';
import MergeActivity from '../views/student/early-learning/MergeActivity';
import ChartActivity from '../views/student/early-learning/ChartActivity';
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

test('listen rounds do not read the instruction over the spoken letter and do not cheer', () => {
    window.speechSynthesis = { speak: jest.fn(), cancel: jest.fn(), getVoices: () => [] };
    global.SpeechSynthesisUtterance = function U(text) { this.text = text; };
    render(<RoundsActivity activity={{ id: 8, title: 'Eshit', ...instruction, content: { mode: 'rounds', kind: 'listen', set: 'numbers', rounds_count: 1 } }} {...base} />);
    expect(screen.getByText('Mevalarni top.')).toBeInTheDocument();
    expect(voice.playVoice).not.toHaveBeenCalled();
    fireEvent.click(screen.getAllByRole('button').find((b) => /^\d$/.test(b.textContent)));
    expect(voice.cheer).not.toHaveBeenCalled();
});

test('a merge slide is not praised as an answer', () => {
    render(<MergeActivity activity={{ id: 9, title: '2048', content: { mode: 'merge', goal: 64 } }} {...base} />);
    ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].forEach((key) => fireEvent.keyDown(window, { key }));
    expect(voice.cheer).not.toHaveBeenCalledWith('correct');
});

test('ChartActivity shows and reads its instruction', () => {
    render(<ChartActivity activity={{ id: 10, title: 'Diagramma', ...instruction, instruction_text: 'Diagrammaga qara.', content: { mode: 'chart' } }} {...base} />);
    expect(screen.getByText('Diagrammaga qara.')).toBeInTheDocument();
    expect(voice.playVoice).toHaveBeenCalled();
});
