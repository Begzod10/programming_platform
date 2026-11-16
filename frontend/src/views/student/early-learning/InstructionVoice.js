import React, { useEffect } from 'react';
import { useTranslation } from '../../../i18n/useTranslation';
import { currentLang, loadPhrases, playVoice, stopVoice } from './earlyVoice';

/** The activity's instruction text with a 🔊 button; reads itself aloud when shown and when the
 * language (so the audio url) changes. No text -> nothing; no audio file -> text only. */
export default function InstructionVoice({ activity, className }) {
    const { t } = useTranslation();
    const text = activity && activity.instruction_text;
    const url = activity && activity.instruction_audio_url;

    useEffect(() => {
        loadPhrases(currentLang());
        if (url) playVoice(url);
        return () => stopVoice();
    }, [url]);

    if (!text) return null;
    return (
        <p className={className}>
            {text}
            {url && (
                <button
                    type="button"
                    className="el-listen-btn"
                    aria-label={t('el.listen')}
                    onClick={() => playVoice(url, { force: true })}
                >
                    🔊
                </button>
            )}
        </p>
    );
}
