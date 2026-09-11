// Regression coverage for two TeacherCourses.js fixes:
//   1. Raw fetch() calls bypassing the axios interceptor (401 → refresh
//      token flow never fired for these call sites).
//   3. saveCourse() reading the current user via getCurrentUser()
//      (localStorage/sessionStorage) instead of the reactive AuthContext
//      state, which could silently send instructor_id: undefined.
//
// TeacherCourses.js cannot be rendered directly in this suite: it imports
// react-router-dom v7, which ships only an ESM build
// (node_modules/react-router-dom/dist/index.mjs) that CRA's default
// CommonJS Jest config cannot resolve (see the note in App.test.js, and
// react-router-dom/package.json's "main" pointing at a non-existent
// dist/main.js). That is a pre-existing repo/tooling limitation unrelated
// to this fix, so these regressions are instead asserted against the
// component's source text — a practical substitute that still fails loudly
// if either bug is reintroduced.
import fs from 'fs';
import path from 'path';

const SOURCE_PATH = path.join(
  __dirname,
  '../views/teacher/courses/TeacherCourses/TeacherCourses.js'
);
const source = fs.readFileSync(SOURCE_PATH, 'utf8');

describe('TeacherCourses.js — network calls go through useHttp()', () => {
  test('contains no raw fetch(...) calls', () => {
    // Matches bare `fetch(` calls (global fetch), but not things like
    // `.catch(` or identifiers merely containing "fetch".
    const rawFetchCalls = source.match(/(?<![.\w])fetch\(/g) || [];
    expect(rawFetchCalls).toEqual([]);
  });

  test('imports and uses request() from useHttp() for course deletion', () => {
    expect(source).toMatch(/const \{ request \}\s*=\s*useHttp\(\);/);
    expect(source).toMatch(
      /request\(`\$\{API_URL\}v1\/courses\/\$\{id\}`,\s*'DELETE',\s*null,\s*headers\(\)\)/
    );
  });

  test('syncExercises uses request() instead of fetch() for create/update/delete', () => {
    const syncExercisesMatch = source.match(
      /const syncExercises = async[\s\S]*?\n {4}\};/
    );
    expect(syncExercisesMatch).not.toBeNull();
    const syncExercisesBody = syncExercisesMatch[0];
    expect(syncExercisesBody).not.toMatch(/(?<![.\w])fetch\(/);
    expect(syncExercisesBody).toMatch(/request\(/);
  });
});

describe('TeacherCourses.js — saveCourse reads the user from AuthContext', () => {
  test('imports useAuth from AuthContext', () => {
    expect(source).toMatch(
      /import \{ useAuth \} from '\.\.\/\.\.\/\.\.\/\.\.\/context\/AuthContext';/
    );
  });

  test('destructures user from useAuth() at component scope', () => {
    expect(source).toMatch(/const \{ user \}\s*=\s*useAuth\(\);/);
  });

  test('saveCourse no longer calls getCurrentUser()', () => {
    const saveCourseMatch = source.match(
      /const saveCourse = \(\) => \{[\s\S]*?\n {4}\};/
    );
    expect(saveCourseMatch).not.toBeNull();
    const saveCourseBody = saveCourseMatch[0];
    expect(saveCourseBody).not.toMatch(/getCurrentUser\(\)/);
    // Guards against a missing/undefined user id instead of silently
    // sending instructor_id: undefined.
    expect(saveCourseBody).toMatch(/if \(!user\?\.id\)/);
    expect(saveCourseBody).toMatch(/instructor_id:\s*user\.id/);
  });
});
