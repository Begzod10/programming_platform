import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import {
    playVoice, setVoiceOn, isVoiceOn, cheer, cheerStars, loadPhrases, CHEER_GAP_MS,
    __resetVoiceForTests, __audioForTests,
} from '../views/student/early-learning/earlyVoice';
import InstructionVoice from '../views/student/early-learning/InstructionVoice';
import VoiceToggle from '../views/student/early-learning/VoiceToggle';

jest.mock('../api/search/base', () => ({ API_URL: 'http://api.test/api/', API_URL_DOC: 'http://api.test/' }));

let play;
let pause;
const PHRASES = {
    correct1: '/uploads/early-audio/uz/c1.mp3', wrong1: '/uploads/early-audio/uz/w1.mp3',
    star2: '/uploads/early-audio/uz/s2.mp3',
};

beforeEach(() => {
    __resetVoiceForTests();
    localStorage.clear();
    play = jest.spyOn(window.HTMLMediaElement.prototype, 'play').mockImplementation(() => Promise.resolve());
    pause = jest.spyOn(window.HTMLMediaElement.prototype, 'pause').mockImplementation(() => {});
    global.fetch = jest.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ phrases: PHRASES }) }));
});

afterEach(() => {
    jest.restoreAllMocks();
    delete global.fetch;
});

const activity = (over) => ({
    id: 1, instruction_text: 'Harfni chiz.', instruction_audio_url: '/uploads/early-audio/uz/a.mp3', ...over,
});

const flush = () => act(async () => { await Promise.resolve(); await Promise.resolve(); });

test('playVoice is silent when voice is off unless forced', async () => {
    setVoiceOn(false);
    expect(isVoiceOn()).toBe(false);
    expect(await playVoice('/uploads/x.mp3')).toBe(false);
    expect(play).not.toHaveBeenCalled();
    expect(await playVoice('/uploads/x.mp3', { force: true })).toBe(true);
    expect(play).toHaveBeenCalledTimes(1);
});

test('playVoice resolves false when the browser refuses to play', async () => {
    const err = jest.spyOn(console, 'error').mockImplementation(() => {});
    play.mockImplementation(() => Promise.reject(new Error('NotAllowedError')));
    expect(await playVoice('/uploads/x.mp3')).toBe(false);
    expect(err).not.toHaveBeenCalled();
});

test('playVoice makes the url absolute against API_URL_DOC', async () => {
    await playVoice('/uploads/early-audio/uz/k.mp3');
    expect(__audioForTests().src).toBe('http://api.test/uploads/early-audio/uz/k.mp3');
});

test('playVoice with an empty url does nothing', async () => {
    expect(await playVoice(null)).toBe(false);
    expect(play).not.toHaveBeenCalled();
});

test('InstructionVoice reads aloud on mount and on the listen button', async () => {
    render(<InstructionVoice activity={activity()} className="aa-instruction" />);
    await flush();
    expect(play).toHaveBeenCalledTimes(1);
    expect(screen.getByText('Harfni chiz.').closest('.aa-instruction')).not.toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'Eshitish' }));
    await flush();
    expect(play).toHaveBeenCalledTimes(2);
});

test('InstructionVoice without audio url shows text but no button', async () => {
    render(<InstructionVoice activity={activity({ instruction_audio_url: null })} className="x" />);
    await flush();
    expect(screen.getByText('Harfni chiz.')).toBeInTheDocument();
    expect(screen.queryByRole('button')).toBeNull();
    expect(play).not.toHaveBeenCalled();
});

test('InstructionVoice without instruction text renders nothing', () => {
    const { container } = render(<InstructionVoice activity={activity({ instruction_text: null })} className="x" />);
    expect(container).toBeEmptyDOMElement();
});

test('InstructionVoice replays in the new language and stops on unmount', async () => {
    const { rerender, unmount } = render(<InstructionVoice activity={activity()} className="x" />);
    await flush();
    rerender(<InstructionVoice activity={activity({ instruction_text: 'Обведи.', instruction_audio_url: '/uploads/early-audio/ru/b.mp3' })} className="x" />);
    await flush();
    expect(play).toHaveBeenCalledTimes(2);
    expect(__audioForTests().src).toBe('http://api.test/uploads/early-audio/ru/b.mp3');
    pause.mockClear();
    unmount();
    expect(pause).toHaveBeenCalled();
});

test('VoiceToggle persists off, stops the voice, and auto-read stays silent', async () => {
    render(<VoiceToggle />);
    fireEvent.click(screen.getByRole('button', { name: "Ovozni o'chirish" }));
    expect(localStorage.getItem('el_voice_off')).toBe('1');
    expect(screen.getByRole('button', { name: 'Ovozni yoqish' })).toBeInTheDocument();
    render(<InstructionVoice activity={activity()} className="x" />);
    await flush();
    expect(play).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Eshitish' }));
    await flush();
    expect(play).toHaveBeenCalledTimes(1);
});

test('cheer waits 4 seconds between phrases and stays quiet during the instruction', async () => {
    const now = jest.spyOn(Date, 'now').mockReturnValue(100000);
    await loadPhrases('uz');
    expect(cheer('correct')).toBe(true);
    now.mockReturnValue(100000 + CHEER_GAP_MS - 1);
    expect(cheer('wrong')).toBe(false);
    now.mockReturnValue(100000 + CHEER_GAP_MS);
    expect(cheer('wrong')).toBe(true);
    await flush();
    expect(__audioForTests().src).toContain('/w1.mp3');

    now.mockReturnValue(200000);
    await playVoice('/uploads/early-audio/uz/a.mp3');
    expect(cheer('correct')).toBe(false);
    act(() => { __audioForTests().dispatchEvent(new Event('ended')); });
    expect(cheer('correct')).toBe(true);
});

test('cheer is silent until phrases are loaded and when the request failed', async () => {
    expect(cheer('correct')).toBe(false);
    expect(global.fetch).toHaveBeenCalledTimes(1);
    __resetVoiceForTests();
    global.fetch = jest.fn(() => Promise.reject(new Error('offline')));
    await loadPhrases('uz');
    expect(cheer('correct')).toBe(false);
    expect(play).not.toHaveBeenCalled();
});

test('cheerStars plays the matching star phrase even inside the 4 second gap', async () => {
    jest.spyOn(Date, 'now').mockReturnValue(100000);
    await loadPhrases('uz');
    expect(cheer('correct')).toBe(true);
    await flush();
    act(() => { __audioForTests().dispatchEvent(new Event('ended')); });   // praise finished, still within 4 s
    expect(cheerStars(2)).toBe(true);
    await flush();
    expect(__audioForTests().src).toContain('/s2.mp3');
});

test('phrases follow the app language', async () => {
    localStorage.setItem('lang', 'ru');
    cheer('correct');
    expect(global.fetch).toHaveBeenCalledWith('http://api.test/api/v1/early-learning/public/voice?lang=ru');
});

/* ── review fixes ── */

test('a late pause event from the stopped clip does not mark the new instruction as finished', async () => {
    jest.spyOn(Date, 'now').mockReturnValue(500000);
    await loadPhrases('uz');
    await playVoice('/uploads/early-audio/uz/a.mp3');
    await playVoice('/uploads/early-audio/uz/a.mp3', { force: true });      // child taps 🔊 again
    act(() => { __audioForTests().dispatchEvent(new Event('pause')); });   // queued pause of the first clip
    expect(cheer('correct')).toBe(false);
});

test('a rejected older play does not clear the newer clip', async () => {
    jest.spyOn(Date, 'now').mockReturnValue(600000);
    await loadPhrases('uz');
    let rejectFirst;
    play.mockImplementationOnce(() => new Promise((_, rej) => { rejectFirst = rej; }));
    const first = playVoice('/uploads/early-audio/uz/a.mp3');
    await playVoice('/uploads/early-audio/uz/b.mp3');
    rejectFirst(new Error('AbortError'));
    await first;
    expect(cheer('correct')).toBe(false);
});

test('cheerStars waits for the praise that is still playing', async () => {
    jest.spyOn(Date, 'now').mockReturnValue(700000);
    await loadPhrases('uz');
    expect(cheer('correct')).toBe(true);
    await flush();
    play.mockClear();
    expect(cheerStars(2)).toBe(true);
    await flush();
    expect(play).not.toHaveBeenCalled();
    act(() => { __audioForTests().dispatchEvent(new Event('ended')); });
    await flush();
    expect(play).toHaveBeenCalledTimes(1);
    expect(__audioForTests().src).toContain('/s2.mp3');
});

test('leaving a game does not cut the star phrase', async () => {
    jest.spyOn(Date, 'now').mockReturnValue(800000);
    await loadPhrases('uz');
    const { unmount } = render(<InstructionVoice activity={activity({ instruction_audio_url: null })} className="x" />);
    cheerStars(3);
    await flush();
    pause.mockClear();
    unmount();
    expect(pause).not.toHaveBeenCalled();
});

test('InstructionVoice with autoplay off waits for the button', async () => {
    render(<InstructionVoice activity={activity()} className="x" autoplay={false} />);
    await flush();
    expect(play).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Eshitish' }));
    await flush();
    expect(play).toHaveBeenCalledTimes(1);
});

test('the mute switch does not look like the listen button', () => {
    render(<VoiceToggle />);
    const btn = screen.getByRole('button', { name: "Ovozni o'chirish" });
    expect(btn.textContent).not.toContain('🔊');
    expect(btn.querySelector('svg')).not.toBeNull();
});
