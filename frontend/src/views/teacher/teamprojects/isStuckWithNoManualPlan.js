// A team stuck at "forming" with no plan AND no attempts left has no way
// forward except a teacher-authored manual plan (ManualPlanForm on the
// detail page) — but TeacherTeamProjects.js's list view used to silently
// drop the regenerate button once generation_attempts hits 3, with nothing
// else distinguishing that card from one still genuinely mid-formation. A
// teacher scanning many assignments had no reason to notice. This flag
// drives an explicit banner instead of a quiet omission.
//
// Extracted into its own module (rather than living inline in
// TeacherTeamProjects.js) so it can be unit-tested directly: that file
// imports react-router-dom v7 (ESM-only `dist/index.mjs`, not resolvable by
// CRA's default CommonJS Jest config — see TeacherCoursesLoader.test.js for
// the same constraint hit before), so anything declared inside it can't be
// imported into a test file at all, even a pure function that never
// touches routing.
export function isStuckWithNoManualPlan(team) {
    return team.status === 'forming' && team.tasks.length === 0 && team.generation_attempts >= 3;
}
