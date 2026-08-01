import React from 'react';
import { highlight } from '../../../utils/highlight';
import { useTranslation } from '../../../i18n/useTranslation';
import { OPTION_LABELS, getAnswerState } from './StudentTeamGame';

/* ── Bug-hunt quiz arena pieces, shared by QuizOverlay (manual) and
   AutoQuizFlow (auto) ────────────────────────────────────────────────────
   The interaction is "tap the buggy line", not a detached A–D list — the
   diagnostic act should be pointing at the line itself. The gutter cell is
   the tap target (not the code text), sticky-left so it stays reachable
   even when a long line scrolls horizontally on a phone. `options` here is
   the same array the manual quiz uses, just holding line numbers as
   strings (e.g. ["3","7","12"]) instead of answer text — getAnswerState
   and the reveal color language (chosen/correct/wrongPick/faded) carry
   over unchanged. */

export function BugSnippet({ code, language, options, chosen, showResult, correctOption, onPick, disabled }) {
    const lines = (code || '').split('\n');
    const highlightedLines = highlight(code, language).split('\n');

    // 1-based line number -> its index within `options` (the candidate list)
    const candidateByLine = {};
    (options || []).forEach((lineStr, idx) => { candidateByLine[Number(lineStr)] = idx; });

    return (
        <div className="stg-bug-code" role="group">
            {lines.map((_, i) => {
                const lineNum = i + 1;
                const candidateIdx = candidateByLine[lineNum];
                const isCandidate = candidateIdx !== undefined;
                const state = isCandidate
                    ? getAnswerState(candidateIdx, { chosen, showResult, correctOption })
                    : null;
                const gutterStateClass = state && state !== 'neutral' ? ` stg-bug-gutter--${state}` : '';

                return (
                    <div key={i} className="stg-bug-line-row">
                        {isCandidate ? (
                            <button
                                type="button"
                                className={`stg-bug-gutter stg-bug-gutter--candidate${gutterStateClass}`}
                                onClick={() => onPick(candidateIdx)}
                                disabled={disabled}
                                aria-pressed={chosen === candidateIdx}
                                aria-label={`${OPTION_LABELS[candidateIdx]}: ${lineNum}`}
                            >
                                <span className="stg-bug-letter">{OPTION_LABELS[candidateIdx]}</span>
                                <span className="stg-bug-linenum">{lineNum}</span>
                            </button>
                        ) : (
                            <span className="stg-bug-gutter stg-bug-gutter--inert" aria-hidden="true">{lineNum}</span>
                        )}
                        <pre
                            className="stg-bug-line-code"
                            dangerouslySetInnerHTML={{ __html: highlightedLines[i] || ' ' }}
                        />
                    </div>
                );
            })}
        </div>
    );
}

export function BugExplanation({ lang, text, textRu, correctLine }) {
    const { t } = useTranslation();
    const shown = lang === 'ru' && textRu ? textRu : text;
    if (!shown) return null;
    return (
        <div className="stg-bug-explain">
            <div className="stg-bug-explain-title">{t('game.bug.explanationTitle')}</div>
            {correctLine != null && (
                <p className="stg-bug-explain-line">
                    {t('game.bug.correctLineLabel').replace('{line}', correctLine)}
                </p>
            )}
            <p className="stg-bug-explain-text">{shown}</p>
        </div>
    );
}
