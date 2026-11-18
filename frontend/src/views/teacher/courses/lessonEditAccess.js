// Only these teachers may change lessons (add, edit, publish/unpublish, reorder); every other teacher
// sees the courses and lessons read-only. The frontend hides the controls; the backend still decides.
export const LESSON_EDITOR_USERNAMES = new Set(['rimefara_teach', 'Shahzodweb']);

export const canEditLessons = (user) => LESSON_EDITOR_USERNAMES.has(user?.username);
