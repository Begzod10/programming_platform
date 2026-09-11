// Regression test for the "key={index} on drag-drop chips" bug
// (docs/FRONTEND_BUGS.md MEDIUM). The doc originally pointed at
// StudentLessonPage.js:218, but that render logic moved into
// LessonExercise.js's drag_and_drop chip lists (dragDropped/dragAvailable)
// during a later refactor — the doc's target file was stale, the bug
// itself was real and still present there.
//
// Both lists' membership and order change as chips move between them
// (drop appends, click-to-remove splices from the middle), so a bare
// index key reuses a slot's React identity for whatever chip now occupies
// it after a removal. These chips render no per-item local state, so a
// stale identity doesn't produce visibly wrong text — but it does mean a
// removed chip's key can collide with a still-present one at the same
// duplicate word/position, which this test would catch via React's
// "two children with the same key" console warning. Keying by
// `${word}__${index}` instead keeps each chip's identity tied to both its
// content and its slot.
//
// This also exercises the drag_and_drop flow itself (drop / remove /
// re-drop), which otherwise has no coverage at all.
jest.mock('../api/axiosInstance', () => ({
  __esModule: true,
  default: { request: jest.fn() },
}));

import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ExerciseCard } from '../views/student/courses/LessonPage/LessonExercise';

// Deliberate duplicate word ("hello" appears twice) — the case that most
// directly stresses key stability.
const dragDropExercise = {
  id: 1,
  exercise_type: 'drag_and_drop',
  description: 'Order the words',
  options: 'hello,world,hello',
};

const drop = (zone, word) =>
  fireEvent.drop(zone, { dataTransfer: { getData: () => word, setData: jest.fn() } });

test('drag-drop chip add/remove/re-add never triggers a duplicate-key warning and renders correctly', () => {
  const errorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

  const { container } = render(
    <ExerciseCard ex={dragDropExercise} courseId={1} lessonId={1} index={0} />
  );
  const dropzone = container.querySelector('.slp-ex-dropzone');
  expect(dropzone).toBeInTheDocument();

  // Drop both "hello"s, then "world" — dragDropped: [hello, hello, world].
  drop(dropzone, 'hello');
  drop(dropzone, 'hello');
  drop(dropzone, 'world');
  let chips = container.querySelectorAll('.slp-ex-dropped-chip');
  expect(chips).toHaveLength(3);
  expect([...chips].map(c => c.textContent.replace(/^\d+/, '').replace('✕', ''))).toEqual([
    'hello', 'hello', 'world',
  ]);

  // Remove the first chip (splices index 0 out) — dragDropped: [hello, world].
  // With a plain index key this reuses slot 0's identity for what is now
  // "hello" (was "hello" too, so content matches) and slot 1 for "world"
  // (was "world"'s own slot 2) — exercising exactly the reorder path the
  // original bug report was about.
  fireEvent.click(chips[0]);
  chips = container.querySelectorAll('.slp-ex-dropped-chip');
  expect(chips).toHaveLength(2);
  expect([...chips].map(c => c.textContent.replace(/^\d+/, '').replace('✕', ''))).toEqual([
    'hello', 'world',
  ]);

  // Re-drop the removed "hello" back in — dragDropped: [hello, world, hello],
  // two "hello" chips present simultaneously again post-removal/re-add.
  drop(dropzone, 'hello');
  chips = container.querySelectorAll('.slp-ex-dropped-chip');
  expect(chips).toHaveLength(3);
  expect([...chips].map(c => c.textContent.replace(/^\d+/, '').replace('✕', ''))).toEqual([
    'hello', 'world', 'hello',
  ]);

  const duplicateKeyWarning = errorSpy.mock.calls.some(args =>
    String(args[0]).includes('same key')
  );
  expect(duplicateKeyWarning).toBe(false);

  errorSpy.mockRestore();
});
