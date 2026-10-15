import { useState } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';

import { useTranslation } from '../../../i18n/useTranslation';
import { API_URL } from '../../../api/search/base';
import { DEMO_HOME } from '../../../constants/demo';

// Letters (any alphabet), apostrophes, hyphen, spaces — mirrors the backend rule.
const NAME_RE = /^[\p{L}][\p{L}\s'’ʻʼ`-]{1,39}$/u;
export const validName = (v) => NAME_RE.test((v || '').trim().replace(/\s+/g, ' '));

/** Demo sign-in: just a first and last name, no password. */
export default function DemoEntry({ onLogin, onBack, navigate }) {
  const { t } = useTranslation();
  const [first, setFirst] = useState('');
  const [last, setLast] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const ready = validName(first) && validName(last);

  const start = async () => {
    if (!ready || busy) return;
    setBusy(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}v1/auth/demo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ first_name: first.trim(), last_name: last.trim() }),
      });
      if (res.status === 422) { setError(t('auth.demoInvalid')); return; }
      if (res.status === 429) { setError(t('auth.demoLimit')); return; }
      if (!res.ok) throw new Error('demo');
      const data = await res.json();
      // Demo sessions are short-lived: keep them in this tab only.
      onLogin(data, false);
      navigate(DEMO_HOME);
    } catch {
      setError(t('auth.demoFailed'));
    } finally {
      setBusy(false);
    }
  };

  const onKey = (e) => { if (e.key === 'Enter') start(); };

  return (
    <div className="lp-demo">
      <h2 className="lp-title">{t('auth.demoTitle')}</h2>
      <p className="lp-subtitle">{t('auth.demoLead')}</p>

      {error && (
        <div className="lp-banner lp-banner--error" role="alert">
          <AlertCircle size={15} strokeWidth={2} aria-hidden="true" />
          <span>{error}</span>
        </div>
      )}

      <div className="lp-field">
        <label className="lp-label" htmlFor="lp-demo-first">{t('auth.demoFirst')}</label>
        <div className="lp-input-wrap">
          <input id="lp-demo-first" className="lp-input" type="text" value={first}
                 onChange={(e) => { setFirst(e.target.value); setError(''); }} onKeyDown={onKey}
                 autoComplete="given-name" maxLength={40} disabled={busy} />
        </div>
      </div>
      <div className="lp-field">
        <label className="lp-label" htmlFor="lp-demo-last">{t('auth.demoLast')}</label>
        <div className="lp-input-wrap">
          <input id="lp-demo-last" className="lp-input" type="text" value={last}
                 onChange={(e) => { setLast(e.target.value); setError(''); }} onKeyDown={onKey}
                 autoComplete="family-name" maxLength={40} disabled={busy} />
        </div>
      </div>

      <button type="button" className="lp-submit" onClick={start} disabled={!ready || busy} aria-busy={busy}>
        {busy && <Loader2 size={17} strokeWidth={2.5} className="lp-spinner" aria-hidden="true" />}
        {t('auth.demoStart')}
      </button>
      <button type="button" className="lp-guest-link" onClick={onBack}>{t('auth.demoBack')}</button>
    </div>
  );
}
