import React, { useState } from 'react';
import { useTranslation } from '../../../i18n/useTranslation';
import { Volume2, VolumeX } from 'lucide-react';
import { isVoiceOn, setVoiceOn } from './earlyVoice';

/** Voice on/off switch, remembered on this device. A small grey line icon on purpose: the big yellow 🔊
 * beside an instruction means "listen", and a child must not mistake one for the other. */
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
            {on ? <Volume2 size={16} /> : <VolumeX size={16} />}
        </button>
    );
}
