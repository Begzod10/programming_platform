// Regression test for the "raw fetch() bypasses the axios interceptor" bug
// (docs/FRONTEND_BUGS.md HIGH: StudentLessonPage.js). Several handlers used
// to call fetch(...) directly with a manually-built Authorization header,
// which never goes through axiosInstance and therefore never triggers the
// 401 -> refresh-token flow. They were converted to useHttp().request(...).
//
// This test stubs axiosInstance (the one real network seam) and asserts
// that completing the last lesson of a course drives its network call
// through axiosInstance rather than through window.fetch.
//
// Heavy/unrelated children are mocked out so the component can mount
// without pulling in mermaid, dictionary popovers, project modals, etc.
jest.mock('mermaid', () => ({
  initialize: jest.fn(),
  run: jest.fn(() => Promise.resolve()),
}));
jest.mock('lucide-react', () => ({ Lock: () => null }));
jest.mock('../views/student/courses/LessonPage/Dictselectionpopup', () => () => null);
jest.mock('../views/student/courses/LessonPage/LessonDictionaryDrawer', () => () => null);
jest.mock('../views/student/courses/LessonPage/LessonVocabCard', () => () => null);
jest.mock('../views/student/courses/LessonPage/CelebrationOverlay', () => () => null);
jest.mock('../views/student/courses/LessonPage/LessonFeedback', () => ({
  LessonFeedbackWidget: () => null,
}));
jest.mock('../views/student/courses/LessonPage/LessonProjectModal', () => ({
  LessonProjectModal: () => null,
}));
jest.mock('../views/student/courses/LessonPage/LessonContentBlocks', () => ({
  LessonContentBlocks: () => null,
}));
// The seam every request must actually cross: axiosInstance.request(config).
// base.js's useHttp() calls this; raw fetch() never does.
jest.mock('../api/axiosInstance', () => ({
  __esModule: true,
  default: { request: jest.fn() },
}));

import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import '@testing-library/jest-dom';
import axiosInstance from '../api/axiosInstance';
import StudentLessonPage from '../views/student/courses/LessonPage/StudentLessonPage';

describe('StudentLessonPage — network calls go through axiosInstance, not fetch', () => {
  let originalFetch;

  beforeEach(() => {
    axiosInstance.request.mockReset();
    axiosInstance.request.mockResolvedValue({data: {}});
    originalFetch = global.fetch;
    global.fetch = jest.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  test('completing the last lesson hits the certificate-check endpoint via axiosInstance, never window.fetch', async () => {
    const lesson = {id: 1, title: 'Intro', sections: [], completed: false, course_id: 10};
    const course = {id: 10, title: 'Course'};
    const onComplete = jest.fn();

    render(
      <StudentLessonPage
        lesson={lesson}
        course={course}
        allLessons={[lesson]}
        onBack={jest.fn()}
        onNavigate={jest.fn()}
        onComplete={onComplete}
      />
    );

    const completeBtn = screen.getByText('Отметить как пройденный');
    fireEvent.click(completeBtn);

    await waitFor(() => {
      expect(
        axiosInstance.request.mock.calls.some(([config]) =>
          config.method === 'POST' &&
          config.url.includes('v1/achievements/check-and-earn-certificate')
        )
      ).toBe(true);
    });

    expect(onComplete).toHaveBeenCalled();
    // The whole point of the fix: this call must never fall back to a raw
    // fetch() that skips the 401 -> refresh interceptor.
    expect(global.fetch).not.toHaveBeenCalled();
  });
});
