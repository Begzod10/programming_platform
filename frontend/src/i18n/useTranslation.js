import { useState, useEffect } from 'react';
import translations from './translations';

export const useTranslation = () => {
  const [lang, setLang] = useState(localStorage.getItem('lang') || 'uz');

  useEffect(() => {
    const handleLangChange = (e) => {
      setLang(e.detail);
    };
    // Fires in OTHER tabs/windows when `lang` changes in localStorage (the
    // tab that made the change never receives its own `storage` event, so
    // this complements — not replaces — the custom `languageChange` event
    // used for same-tab updates).
    const handleStorageChange = (e) => {
      if (e.key === 'lang' && e.newValue) {
        setLang(e.newValue);
      }
    };
    window.addEventListener('languageChange', handleLangChange);
    window.addEventListener('storage', handleStorageChange);
    return () => {
      window.removeEventListener('languageChange', handleLangChange);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const toggleLang = () => {
    const newLang = lang === 'uz' ? 'ru' : 'uz';
    localStorage.setItem('lang', newLang);
    window.dispatchEvent(new CustomEvent('languageChange', { detail: newLang }));
  };

  const t = (key) => {
    return translations[lang][key] || key;
  };

  return { t, lang, toggleLang };
};
