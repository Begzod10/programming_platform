// Only this teacher may change lessons (add, edit, publish/unpublish, reorder); every other teacher
// sees the courses and lessons read-only. The frontend hides the controls; the backend still decides.
export const LESSON_EDITOR_USERNAME = 'rimefara_teach';

export const canEditLessons = (user) => user?.username === LESSON_EDITOR_USERNAME;
