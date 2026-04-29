import { useState, useEffect } from 'react';
import translations from './translations';

export const useTranslation = () => {
  const [lang, setLang] = useState(localStorage.getItem('lang') || 'uz');

  useEffect(() => {
    const handleLangChange = (e) => {
      setLang(e.detail);
    };
    window.addEventListener('languageChange', handleLangChange);
    return () => window.removeEventListener('languageChange', handleLangChange);
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
