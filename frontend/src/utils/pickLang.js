// AI-generated (and teacher-authored) task/project text carries a
// <field>_ru alongside the Uzbek <field> — this picks whichever the
// current UI language wants, falling back to the Uzbek field if the
// Russian one is missing/empty (an older row created before this
// existed, or one the AI skipped despite being asked to fill it in).
export function pickLang(obj, field, lang) {
    if (lang === 'ru') {
        const ru = obj?.[`${field}_ru`];
        if (ru && ru.trim()) return ru;
    }
    return obj?.[field] ?? '';
}

export function pickLangList(obj, field, lang) {
    if (lang === 'ru') {
        const ru = obj?.[`${field}_ru`];
        if (Array.isArray(ru) && ru.length > 0) return ru;
    }
    return obj?.[field] ?? [];
}
