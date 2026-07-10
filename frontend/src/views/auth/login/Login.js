import { useState, useRef, useMemo } from 'react';
import { useNavigate, Link }         from 'react-router-dom';
import { Eye, EyeOff, Check, AlertCircle, Loader2 } from 'lucide-react';

import { useTranslation }  from '../../../i18n/useTranslation';
import { API_URL }         from '../../../api/search/base';
import Constellation       from './Constellation';
import ChargeRing          from './ChargeRing';
import './Login.css';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function detectLite() {
  try {
    return (
      window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
      window.innerWidth < 700 ||
      (navigator.deviceMemory !== undefined && navigator.deviceMemory < 4) ||
      (navigator.hardwareConcurrency !== undefined && navigator.hardwareConcurrency <= 2)
    );
  } catch {
    return false;
  }
}

export default function Login({ onLogin }) {
  const navigate = useNavigate();
  const { t, lang, toggleLang } = useTranslation();

  const [username,    setUsername]    = useState('');
  const [password,    setPassword]    = useState('');
  const [showPass,    setShowPass]    = useState(false);
  const [remember,    setRemember]    = useState(false);
  const [submitting,  setSubmitting]  = useState(false);
  const [error,       setError]       = useState('');
  const [success,     setSuccess]     = useState(false);
  const [errorKey,    setErrorKey]    = useState(0);

  const cardRef = useRef(null);
  const lite    = useMemo(detectLite, []);

  // ── Validation ───────────────────────────────────────────────────────────────
  const loginTrimmed = username.trim();
  const loginValid   = loginTrimmed.length >= 3 &&
    (!loginTrimmed.includes('@') || EMAIL_RE.test(loginTrimmed));
  const passValid    = password.length >= 6;
  const ready        = loginValid && passValid;

  // ── Ring progress — each field fills to 0.45 max on length alone,
  //    the final 0.05 per field only unlocks when truly valid ─────────────────
  const lp = loginValid ? 0.5 : Math.min(0.44, (loginTrimmed.length / 3) * 0.44);
  const pp = passValid  ? 0.5 : Math.min(0.44, (password.length  / 6) * 0.44);
  const ringProgress = lp + pp;

  // ── Handlers ─────────────────────────────────────────────────────────────────
  const handleChange = (setter) => (e) => {
    setter(e.target.value);
    if (error)   setError('');
    if (success) setSuccess(false);
  };

  const handleSubmit = async () => {
    if (!ready || submitting) return;
    setSubmitting(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}v1/auth/login`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ username: loginTrimmed, password }),
      });
      if (!res.ok) throw new Error('invalid');
      const data = await res.json();
      setSuccess(true);
      if (onLogin) onLogin(data, remember);
      setTimeout(() => {
        const role = (data.user || data).role || 'student';
        navigate(role === 'teacher' ? '/teacher' : '/student');
      }, 700);
    } catch {
      setError(t('auth.errorInvalid'));
      setErrorKey(k => k + 1);
    } finally {
      setSubmitting(false);
    }
  };

  const handleKeyDown = (e) => { if (e.key === 'Enter') handleSubmit(); };

  // ── Render ───────────────────────────────────────────────────────────────────
  return (
    <div className="lp-root">

      {/* ── Fixed background layers ── */}
      <div className="lp-bg" aria-hidden="true" />
      <div className={`lp-aurora lp-aurora--purple${lite ? ' lp-aurora--static' : ''}`} aria-hidden="true" />
      <div className={`lp-aurora lp-aurora--blue${lite   ? ' lp-aurora--static' : ''}`} aria-hidden="true" />
      {!lite && <Constellation />}

      {/* ── Language toggle ── */}
      <button
        className="lp-lang"
        onClick={toggleLang}
        aria-label={lang === 'uz' ? 'Switch to Russian' : "O'zbekchaga o'tish"}
      >
        {lang === 'uz' ? 'RU' : 'UZ'}
      </button>

      {/* ── Centered stage (ring + card) ── */}
      <div className="lp-center">
        <div className="lp-stage">

          {/* Charge ring — sits in the same position context as the card */}
          <ChargeRing
            progress={ringProgress}
            error={!!error}
            success={success}
            cardRef={cardRef}
          />

          {/* ── Frosted card ── */}
          <div className="lp-card" ref={cardRef}>
            <div className="lp-halo" aria-hidden="true" />

            {/* Logo tile */}
            <div className="lp-logo">
              <img src="https://play-lh.googleusercontent.com/xiJhv9DqAZaOq6htMaZSAQ5DBoH_v7fripUMYx04Kv-5iQnfWAFopqZIED6Sr7Q7wN0" alt="Gennis" />
            </div>

            <h2 className="lp-title">{t('auth.welcome')}</h2>
            <p className="lp-subtitle">{t('auth.subtitle')}</p>

            {/* Error / success banners */}
            {error && (
              <div className="lp-banner lp-banner--error" key={errorKey} role="alert">
                <AlertCircle size={15} strokeWidth={2} aria-hidden="true" />
                <span>{error}</span>
              </div>
            )}
            {success && !error && (
              <div className="lp-banner lp-banner--success" role="status">
                <Check size={15} strokeWidth={2.5} aria-hidden="true" />
                <span>{t('auth.success')}</span>
              </div>
            )}

            {/* ── Login field ── */}
            <div className="lp-field">
              <label className="lp-label" htmlFor="lp-login">
                {t('auth.login')}
              </label>
              <div className={`lp-input-wrap${error ? ' lp-input-wrap--error' : ''}`}>
                <input
                  id="lp-login"
                  type="text"
                  className="lp-input"
                  value={username}
                  onChange={handleChange(setUsername)}
                  onKeyDown={handleKeyDown}
                  placeholder="username / email"
                  autoComplete="username"
                  disabled={submitting}
                  aria-invalid={!!error}
                  aria-describedby={error ? 'lp-error-msg' : undefined}
                />
                {loginValid && (
                  <span className="lp-field-icon" aria-hidden="true">
                    <Check size={14} strokeWidth={2.5} />
                  </span>
                )}
              </div>
            </div>

            {/* ── Password field ── */}
            <div className="lp-field">
              <label className="lp-label" htmlFor="lp-password">
                {t('auth.password')}
              </label>
              <div className={`lp-input-wrap${error ? ' lp-input-wrap--error' : ''}`}>
                <input
                  id="lp-password"
                  type={showPass ? 'text' : 'password'}
                  className="lp-input lp-input--icons"
                  value={password}
                  onChange={handleChange(setPassword)}
                  onKeyDown={handleKeyDown}
                  placeholder="••••••"
                  autoComplete="current-password"
                  disabled={submitting}
                  aria-invalid={!!error}
                />
                {passValid && (
                  <span className="lp-field-icon lp-field-icon--pass-check" aria-hidden="true">
                    <Check size={14} strokeWidth={2.5} />
                  </span>
                )}
                <button
                  type="button"
                  className="lp-eye"
                  onClick={() => setShowPass(v => !v)}
                  aria-label={showPass ? 'Hide password' : 'Show password'}
                  tabIndex={0}
                >
                  {showPass
                    ? <EyeOff size={16} strokeWidth={2} aria-hidden="true" />
                    : <Eye    size={16} strokeWidth={2} aria-hidden="true" />
                  }
                </button>
              </div>
            </div>

            {/* ── Remember me + Forgot ── */}
            <div className="lp-meta-row">
              <label className="lp-remember">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={e => setRemember(e.target.checked)}
                />
                <span>{t('auth.remember')}</span>
              </label>
              <button type="button" className="lp-forgot">
                {t('auth.forgot')}
              </button>
            </div>

            {/* ── Submit ── */}
            <button
              type="button"
              className={`lp-submit${success ? ' lp-submit--success' : ''}`}
              onClick={handleSubmit}
              disabled={!ready || submitting}
              aria-busy={submitting}
            >
              {submitting && (
                <Loader2
                  size={17}
                  strokeWidth={2.5}
                  className="lp-spinner"
                  aria-hidden="true"
                />
              )}
              {submitting ? t('auth.signingIn') : t('auth.signin')}
            </button>

            {/* ── OR divider ── */}
            <div className="lp-divider" aria-hidden="true">
              <span>{t('auth.or')}</span>
            </div>

            {/* ── Register link ── */}
            <Link to="/register" className="lp-register">
              {t('auth.noAccount')}&nbsp;<strong>{t('auth.register')}</strong>
            </Link>

            {/* Dev-only credential hint */}
            {process.env.NODE_ENV === 'development' && (
              <p className="lp-demo-hint">demo: student / 12345678</p>
            )}
          </div>
          {/* end .lp-card */}
        </div>
        {/* end .lp-stage */}
      </div>
      {/* end .lp-center */}
    </div>
  );
}
