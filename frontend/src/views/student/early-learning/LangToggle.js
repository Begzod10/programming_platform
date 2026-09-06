import React from 'react';
import './EarlyLearning.css';

/** UZ/RU pill toggle, matching the sidebar's own lang switch
 * (sidebar-lang__pill) — repeated here because this whole feature runs
 * full-bleed with no sidebar (see StudentLayout.js/TeacherLayout.js's
 * "isImmersive" branch), so there's otherwise no way to reach the app's
 * language switch from inside it. Uses the same global toggleLang()/
 * localStorage('lang') as the sidebar (from useTranslation()), so a change
 * here also sticks everywhere else in the app. Its own file (rather than
 * living inside EarlyLearning.js) so both EarlyLearning.js and
 * MatchingActivity.js can import it without an EarlyLearning<->
 * MatchingActivity circular import. */
export default function LangToggle({ lang, toggleLang }) {
    return (
        <div className="el-lang-toggle">
            <button
                type="button"
                className={`el-lang-pill ${lang === 'uz' ? 'is-active' : ''}`}
                onClick={() => { if (lang !== 'uz') toggleLang(); }}
                aria-pressed={lang === 'uz'}
            >
                UZ
            </button>
            <button
                type="button"
                className={`el-lang-pill ${lang === 'ru' ? 'is-active' : ''}`}
                onClick={() => { if (lang !== 'ru') toggleLang(); }}
                aria-pressed={lang === 'ru'}
            >
                RU
            </button>
        </div>
    );
}
