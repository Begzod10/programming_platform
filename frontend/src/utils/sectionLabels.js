// Lesson sections carry a free-text `label`. Many lessons (198 of 618) were saved with the generic
// Russian defaults ("Текст", "Код", "Видео", "Упражнения"), which an Uzbek student then sees in the
// "Mundarija" and block headers. Generic labels are rendered in the viewer's language instead; a
// teacher-written label (e.g. a project name) is shown exactly as written.
const GENERIC = {
    'matn': ['Matn', 'Текст'], 'текст': ['Matn', 'Текст'], 'text': ['Matn', 'Текст'],
    'nazariya': ['Nazariya', 'Теория'], 'теория': ['Nazariya', 'Теория'],
    'amaliyot': ['Amaliyot', 'Практика'], 'практика': ['Amaliyot', 'Практика'],
    'kod': ['Kod', 'Код'], 'код': ['Kod', 'Код'], 'code': ['Kod', 'Код'],
    'misol': ['Misol', 'Пример'], 'пример': ['Misol', 'Пример'],
    'kod namunasi': ['Kod namunasi', 'Пример кода'], 'пример кода': ['Kod namunasi', 'Пример кода'],
    'mashqlar': ['Mashqlar', 'Упражнения'], 'упражнения': ['Mashqlar', 'Упражнения'], 'exercises': ['Mashqlar', 'Упражнения'],
    'video': ['Video', 'Видео'], 'видео': ['Video', 'Видео'],
};

const key = (label) => (label || '').trim().toLowerCase();

export const isGenericLabel = (label) => key(label) in GENERIC;

/** The label to show for a section: a generic one in the viewer's language, a custom one verbatim. */
export function sectionLabel(label, ru) {
    const hit = GENERIC[key(label)];
    return hit ? hit[ru ? 1 : 0] : (label || '');
}
