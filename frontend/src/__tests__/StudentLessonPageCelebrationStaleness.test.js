// Regression test for a live bug: the "project approved, 75+ points"
// celebration overlay (CelebrationOverlay.js) was appearing on EVERY lesson
// entry instead of only once, right after a real qualifying submission —
// including on lessons the student never submitted anything for, where it
// showed a spurious "0/100".
//
// Root cause: navigating from a lesson with an approved 80+ project straight
// into the next lesson (same StudentLessonPage instance, lesson prop just
// changes — this component is not remounted between lessons) left
// projectSubmission state holding the PREVIOUS lesson's data for the first
// render after lesson.id changed, since its fetch effect hadn't resolved
// yet. The celebration effect (keyed by the NEW lesson.id) read that stale
// passed:true/high-score combination as "a fresh pass on this lesson" and
// fired — then re-rendered with the new lesson's real score (usually 0)
// once the fetch resolved, which is exactly the "0/100" symptom reported.
//
// This only reproduces with CelebrationOverlay NOT mocked to () => null
// (unlike StudentLessonPage.test.js), since the whole point is asserting
// whether — and with what score — it actually renders.
jest.mock('mermaid', () => ({
  initialize: jest.fn(),
  run: jest.fn(() => Promise.resolve()),
}));
jest.mock('lucide-react', () => ({ Lock: () => null, Trophy: () => null }));
jest.mock('../views/student/courses/LessonPage/Dictselectionpopup', () => () => null);
jest.mock('../views/student/courses/LessonPage/LessonDictionaryDrawer', () => () => null);
jest.mock('../views/student/courses/LessonPage/LessonVocabCard', () => () => null);
jest.mock('../views/student/courses/LessonPage/LessonFeedback', () => ({
  LessonFeedbackWidget: () => null,
}));
jest.mock('../views/student/courses/LessonPage/LessonProjectModal', () => ({
  LessonProjectModal: () => null,
}));
jest.mock('../views/student/courses/LessonPage/LessonContentBlocks', () => ({
  LessonContentBlocks: () => null,
}));
jest.mock('../api/axiosInstance', () => ({
  __esModule: true,
  default: { request: jest.fn() },
}));

import React from 'react';
import {render, screen, waitFor} from '@testing-library/react';
import '@testing-library/jest-dom';
import axiosInstance from '../api/axiosInstance';
import StudentLessonPage from '../views/student/courses/LessonPage/StudentLessonPage';

const PROJECT_SECTION = [{type: 'project', title: 'Loyiha'}];

const lessonA = {id: 617, title: 'Lesson A', sections: PROJECT_SECTION, completed: false, course_id: 74};
const lessonB = {id: 618, title: 'Lesson B', sections: PROJECT_SECTION, completed: false, course_id: 74};
const course = {id: 74, title: 'Course'};

describe('StudentLessonPage — celebration overlay does not leak across lesson navigation', () => {
  beforeEach(() => {
    axiosInstance.request.mockReset();
    axiosInstance.request.mockImplementation(({url}) => {
      if (url.includes('/lessons/617/submission')) {
        return Promise.resolve({
          data: {submitted: true, reviewed: true, passed: true, points_earned: 85, pass_threshold: 90},
        });
      }
      if (url.includes('/lessons/618/submission')) {
        return Promise.resolve({data: {submitted: false, pass_threshold: 90}});
      }
      return Promise.resolve({data: {}});
    });
  });

  test('a real 85-point pass on lesson A celebrates once, then does not leak onto lesson B', async () => {
    const {rerender} = render(
      <StudentLessonPage
        lesson={lessonA} course={course} allLessons={[lessonA, lessonB]}
        onBack={jest.fn()} onNavigate={jest.fn()} onComplete={jest.fn()}
      />
    );

    // Lesson A genuinely passed with 85 — the overlay is expected here.
    await waitFor(() => {
      expect(screen.getByText('85')).toBeInTheDocument();
    });

    rerender(
      <StudentLessonPage
        lesson={lessonB} course={course} allLessons={[lessonA, lessonB]}
        onBack={jest.fn()} onNavigate={jest.fn()} onComplete={jest.fn()}
      />
    );

    // Lesson B has no submission at all. The overlay must never appear for
    // it — neither the stale 85 nor a spurious 0.
    await waitFor(() => {
      expect(axiosInstance.request.mock.calls.some(([c]) => c.url.includes('/lessons/618/submission'))).toBe(true);
    });
    expect(screen.queryByText('85')).not.toBeInTheDocument();
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });

  test('entering an unsubmitted lesson directly never shows the celebration overlay', async () => {
    render(
      <StudentLessonPage
        lesson={lessonB} course={course} allLessons={[lessonA, lessonB]}
        onBack={jest.fn()} onNavigate={jest.fn()} onComplete={jest.fn()}
      />
    );

    await waitFor(() => {
      expect(axiosInstance.request.mock.calls.some(([c]) => c.url.includes('/lessons/618/submission'))).toBe(true);
    });
    expect(screen.queryByText('0')).not.toBeInTheDocument();
    expect(screen.queryByText("Qabul qilindi!")).not.toBeInTheDocument();
  });
});
