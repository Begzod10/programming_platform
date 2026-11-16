import { API_URL, API_URL_DOC } from '../../../api/search/base';

/** One shared voice player for the kids' games: read-aloud instructions and short praise phrases.
 * Every failure (no file, offline, browser refuses autoplay, no localStorage) ends in silence, never an error.
 * See docs/superpowers/specs/2026-11-11-early-voice-instructions-design.md §3.4-3.5. */

export const CHEER_GAP_MS = 4000;
const OFF_KEY = 'el_voice_off';
const CORRECT = ['correct1', 'correct2', 'correct3', 'correct4'];
const WRONG = ['wrong1', 'wrong2'];

let audio = null;
let playing = false;
let playingKind = null;
let lastCheerAt = -Infinity;
const phrases = {};      // lang -> {key: url} once loaded
const loading = {};      // lang -> Promise
let generation = 0;      // bumped by the test reset so a stale request cannot refill the cache

function player() {
    if (!audio) {
        audio = new Audio();
        const stopped = () => { playing = false; playingKind = null; };
        audio.addEventListener('ended', stopped);
        audio.addEventListener('pause', stopped);
        audio.addEventListener('error', stopped);
    }
    return audio;
}

function absolute(url) {
    if (/^https?:\/\//.test(url)) return url;
    return `${API_URL_DOC.replace(/\/$/, '')}/${url.replace(/^\//, '')}`;
}

export function isVoiceOn() {
    try { return localStorage.getItem(OFF_KEY) !== '1'; } catch { return true; }
}

export function setVoiceOn(on) {
    try {
        if (on) localStorage.removeItem(OFF_KEY); else localStorage.setItem(OFF_KEY, '1');
    } catch { /* not saved, still applies to this page */ }
    if (!on) stopVoice();
}

export function currentLang() {
    try { return localStorage.getItem('lang') === 'ru' ? 'ru' : 'uz'; } catch { return 'uz'; }
}

export function stopVoice() {
    if (!audio) return;
    try { audio.pause(); } catch { /* ignore */ }
    playing = false;
    playingKind = null;
}

export function isPlaying(kind) {
    return playing && (!kind || playingKind === kind);
}

export async function playVoice(url, { force = false, kind = 'instruction' } = {}) {
    if (!url || (!force && !isVoiceOn())) return false;
    const a = player();
    stopVoice();
    try {
        a.src = absolute(url);
        playingKind = kind;
        playing = true;
        await a.play();
        return true;
    } catch {
        playing = false;
        playingKind = null;
        return false;
    }
}

export function loadPhrases(lang) {
    if (phrases[lang]) return Promise.resolve(phrases[lang]);
    if (!loading[lang]) {
        const gen = generation;
        const keep = (value) => { if (gen === generation) phrases[lang] = value; return value; };
        loading[lang] = fetch(`${API_URL}v1/early-learning/public/voice?lang=${lang}`)
            .then((r) => (r.ok ? r.json() : { phrases: {} }))
            .then((data) => keep((data && data.phrases) || {}))
            .catch(() => keep({}));
    }
    return loading[lang];
}

function phraseUrls(keys) {
    const lang = currentLang();
    const loaded = phrases[lang];
    if (!loaded) { loadPhrases(lang); return null; }
    return keys.map((k) => loaded[k]).filter(Boolean);
}

/** Short praise after an answer: at most one every CHEER_GAP_MS, never over a playing instruction. */
export function cheer(kind) {
    if (!isVoiceOn() || isPlaying('instruction')) return false;
    if (Date.now() - lastCheerAt < CHEER_GAP_MS) return false;
    const urls = phraseUrls(kind === 'wrong' ? WRONG : CORRECT);
    if (!urls || !urls.length) return false;
    lastCheerAt = Date.now();
    playVoice(urls[Math.floor(Math.random() * urls.length)], { kind: 'cheer' });
    return true;
}

/** The end-of-game phrase for 1-3 stars; ignores the gap and interrupts whatever is playing. */
export function cheerStars(stars) {
    if (!isVoiceOn()) return false;
    const urls = phraseUrls([`star${Math.min(3, Math.max(1, stars || 1))}`]);
    if (!urls || !urls.length) return false;
    lastCheerAt = Date.now();
    playVoice(urls[0], { kind: 'cheer' });
    return true;
}

export function __resetVoiceForTests() {
    stopVoice();
    audio = null;
    lastCheerAt = -Infinity;
    generation += 1;
    Object.keys(phrases).forEach((k) => delete phrases[k]);
    Object.keys(loading).forEach((k) => delete loading[k]);
}

export function __audioForTests() {
    return audio;
}
