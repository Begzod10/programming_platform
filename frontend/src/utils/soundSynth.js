/**
 * Tiny procedural sound synthesizer.
 *
 * Used by the store's sound-pack preview button and (later) the exercise
 * celebration hook. Two motives ship in Phase 1:
 *
 *   'arcade'    — an 8-bit rising blip. Cheerful, short, on-brand for a
 *                 correct-answer cue.
 *   'applause'  — a soft chord swell with a filtered noise wash on top,
 *                 evoking a small applause without needing an audio file.
 *
 * The functions are self-contained (no shared context) so the caller can
 * fire-and-forget: every play() creates its own AudioContext, runs a
 * short envelope, then close()s. Browsers require a user gesture before
 * playing audio; this is always invoked from a click handler.
 */

function getAudioContext() {
    const Ctor = window.AudioContext || window.webkitAudioContext;
    if (!Ctor) return null;
    return new Ctor();
}


/** Rising 8-bit blip. ~220ms. */
function playArcade(volume = 0.5) {
    const ctx = getAudioContext();
    if (!ctx) return;
    const now = ctx.currentTime;

    const osc = ctx.createOscillator();
    osc.type = 'square';
    // Two-note bleep: 660Hz → 990Hz, ramp then hop.
    osc.frequency.setValueAtTime(660, now);
    osc.frequency.exponentialRampToValueAtTime(990, now + 0.08);
    osc.frequency.setValueAtTime(880, now + 0.12);

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(volume, now + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.22);

    osc.connect(gain).connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.24);
    osc.onended = () => { try { ctx.close(); } catch { /* already closed */ } };
}


/** Warm chord swell + a hint of filtered noise. ~800ms. */
function playApplause(volume = 0.35) {
    const ctx = getAudioContext();
    if (!ctx) return;
    const now = ctx.currentTime;

    // 3-voice chord: C E G one octave up (523, 659, 784Hz).
    const freqs = [523.25, 659.25, 783.99];
    const chordGain = ctx.createGain();
    chordGain.gain.setValueAtTime(0.0001, now);
    chordGain.gain.exponentialRampToValueAtTime(volume, now + 0.06);
    chordGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.8);
    chordGain.connect(ctx.destination);

    freqs.forEach((f, i) => {
        const osc = ctx.createOscillator();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(f, now);
        // Detune each voice a hair so it doesn't sound synthy.
        osc.detune.setValueAtTime((i - 1) * 4, now);
        osc.connect(chordGain);
        osc.start(now);
        osc.stop(now + 0.85);
    });

    // Soft noise wash — high-passed white noise as pseudo-applause.
    const bufferSize = ctx.sampleRate * 0.7;
    const noiseBuf = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = noiseBuf.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) data[i] = (Math.random() * 2 - 1) * 0.6;

    const noise = ctx.createBufferSource();
    noise.buffer = noiseBuf;
    const noiseHP = ctx.createBiquadFilter();
    noiseHP.type = 'highpass';
    noiseHP.frequency.value = 2200;
    const noiseGain = ctx.createGain();
    noiseGain.gain.setValueAtTime(0.0001, now);
    noiseGain.gain.exponentialRampToValueAtTime(volume * 0.6, now + 0.04);
    noiseGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.75);
    noise.connect(noiseHP).connect(noiseGain).connect(ctx.destination);
    noise.start(now);
    noise.stop(now + 0.8);
    noise.onended = () => { try { ctx.close(); } catch { /* already closed */ } };
}


const REGISTRY = {
    arcade: playArcade,
    applause: playApplause,
};


/**
 * Play a synth preset by name. Returns true if the preset exists.
 * Safe to call anywhere — if WebAudio is unavailable or the preset is
 * unknown, this is a silent no-op.
 */
export function playSynth(name, opts = {}) {
    const fn = REGISTRY[name];
    if (!fn) return false;
    try {
        fn(opts.volume);
        return true;
    } catch {
        return false;
    }
}


/**
 * Play a sound-pack's preview.
 *
 * Prefers a real URL if the asset_ref carries one (future: real .mp3
 * files shipped in /static/sounds). Falls back to the procedural synth
 * named in `asset_ref.synth`.
 */
export function playSoundAsset(assetRef) {
    if (!assetRef) return;
    const url = assetRef.submit_ok_url || assetRef.celebration_url;
    if (url) {
        try {
            const a = new Audio(url);
            a.volume = 0.6;
            a.play().catch(() => {
                // File missing / blocked — fall through to synth if provided.
                if (assetRef.synth) playSynth(assetRef.synth);
            });
            return;
        } catch {
            // Fall through.
        }
    }
    if (assetRef.synth) playSynth(assetRef.synth);
}
