// Canonical penalty types. The `key`s MUST stay in sync with the backend
// (backend/app/models/teacher_penalty.py → PENALTY_TYPES). Labels are localized
// here on the client so the stored notification/row stays language-neutral.
export const PENALTY_TYPES = [
    { key: 'rule_violation',  emoji: '🚫', ru: 'Нарушение правил',    uz: 'Qoidabuzarlik' },
    { key: 'ai_abuse',        emoji: '🤖', ru: 'Злоупотребление ИИ',  uz: "AI suiiste'moli" },
    { key: 'plagiarism',      emoji: '📋', ru: 'Плагиат',             uz: 'Plagiat' },
    { key: 'missed_deadline', emoji: '⏰', ru: 'Срыв дедлайна',       uz: 'Muddat buzildi' },
    { key: 'inactivity',      emoji: '😴', ru: 'Неактивность',        uz: 'Faolsizlik' },
    { key: 'behavior',        emoji: '🗣️', ru: 'Поведение',           uz: 'Xulq-atvor' },
    { key: 'other',           emoji: '✏️', ru: 'Другое',              uz: 'Boshqa' },
];

export const penaltyType = (key) =>
    PENALTY_TYPES.find(p => p.key === key) || PENALTY_TYPES[PENALTY_TYPES.length - 1];

// "🚫 Нарушение правил" — the full localized label with its emoji.
export const penaltyLabel = (key, ru) => {
    const t = penaltyType(key);
    return `${t.emoji} ${ru ? t.ru : t.uz}`;
};
