// Every lesson section needs a stable id: the blocks, the "Mundarija" jump links, the
// scroll-spy and the video-watch tracking all key on it. Bulk-imported lessons had
// sections without one, so every block shared `undefined` and the contents list could
// not jump anywhere. The API now fills them in; this keeps the page right on its own
// too. Same rule as backend/app/utils/lesson_sections.py (so both always agree).
export const sectionId = (lessonId, index) => `s${lessonId}-${index}`;

/** Mutates and returns `sections`: a missing, blank or duplicate id becomes `s{lessonId}-{index}`. */
export function ensureSectionIds(lessonId, sections) {
    if (!Array.isArray(sections)) return sections;
    const seen = new Set();
    sections.forEach((sec, i) => {
        if (!sec || typeof sec !== 'object') return;
        if (sec.id == null || sec.id === '' || seen.has(String(sec.id))) sec.id = sectionId(lessonId, i);
        seen.add(String(sec.id));
    });
    return sections;
}
