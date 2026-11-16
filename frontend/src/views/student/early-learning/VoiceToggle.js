import React, { useState } from 'react';
import { useTranslation } from '../../../i18n/useTranslation';
import { isVoiceOn, setVoiceOn } from './earlyVoice';

/** 🔊/🔇 switch for the games' voice; remembered on this device. */
export default function VoiceToggle() {
    const { t } = useTranslation();
    const [on, setOn] = useState(isVoiceOn);
    const toggle = () => {
        setVoiceOn(!on);
        setOn(!on);
    };
    return (
        <button
            type="button"
            className="el-voice-btn"
            onClick={toggle}
            aria-pressed={!on}
            aria-label={on ? t('el.voiceOn') : t('el.voiceOff')}
        >
            {on ? '🔊' : '🔇'}
        </button>
    );
}
