/**
 * Regression tests for the "stuck team" visibility gap flagged by a full
 * feature audit: a team that burns all 3 AI generation_attempts with no
 * plan ever created has no way forward except a teacher-authored manual
 * plan, but the assignments list (TeacherTeamProjects.js) silently dropped
 * the regenerate button once attempts hit 3 with nothing else distinguishing
 * that card from one still genuinely mid-formation — a teacher scanning many
 * assignments had no reason to notice. isStuckWithNoManualPlan now drives an
 * explicit "Reja yaratilmadi" banner instead.
 *
 * Importing it from its own module (not from TeacherTeamProjects.js, which
 * pulls in react-router-dom v7 — ESM-only `dist/index.mjs`, not resolvable
 * by CRA's default CommonJS Jest config, see TeacherCoursesLoader.test.js
 * for the same constraint hit before) lets this run as a plain unit test.
 */
import { isStuckWithNoManualPlan } from '../views/teacher/teamprojects/isStuckWithNoManualPlan';

const baseTeam = (overrides = {}) => ({
  id: 1, name: 'Team 1', status: 'forming', generation_attempts: 0, tasks: [],
  ...overrides,
});

describe('isStuckWithNoManualPlan', () => {
  test('true when forming, no tasks, and attempts exhausted', () => {
    expect(isStuckWithNoManualPlan(baseTeam({ generation_attempts: 3 }))).toBe(true);
  });

  test('false when attempts remain, even with no tasks', () => {
    expect(isStuckWithNoManualPlan(baseTeam({ generation_attempts: 2 }))).toBe(false);
  });

  test('false once a plan exists, regardless of attempts', () => {
    expect(isStuckWithNoManualPlan(baseTeam({
      generation_attempts: 3,
      tasks: [{ id: 1, status: 'assigned', title: 'T', assigned_student_name: 'Aziz' }],
    }))).toBe(false);
  });

  test('false once the team has moved past forming', () => {
    expect(isStuckWithNoManualPlan(baseTeam({ status: 'working', generation_attempts: 3 }))).toBe(false);
  });

  test('still true with more than 3 attempts recorded (>=, not ==)', () => {
    expect(isStuckWithNoManualPlan(baseTeam({ generation_attempts: 4 }))).toBe(true);
  });
});
