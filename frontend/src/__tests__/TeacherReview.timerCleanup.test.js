/**
 * Regression test for Bug B: TeacherReview.js scheduled a setTimeout after
 * saving a review (to close the modal + refetch the project list) but never
 * cleared it on unmount. If the teacher navigated away inside that 900ms
 * window, the timer would still fire and call setDetail()/fetchProjects()
 * on a component that no longer exists.
 *
 * The fix tracks the timer id in a ref and clears it in an unmount cleanup
 * effect. We verify this behaviorally: after unmounting, advancing past the
 * timer's delay must NOT trigger another network request (which is what
 * fetchProjects() would do if the leaked timer fired).
 */
import { render, screen, fireEvent, act } from '@testing-library/react';
import TeacherReview from '../views/teacher/teacherreview/TeacherReview';

const mockRequest = jest.fn();

jest.mock('../api/search/base', () => ({
  API_URL: 'http://test.local/api/',
  headers: () => ({}),
  useHttp: () => ({ request: mockRequest }),
}));

describe('TeacherReview — unmount during the post-review close timer', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    mockRequest.mockReset();
  });

  afterEach(() => {
    act(() => {
      jest.runOnlyPendingTimers();
    });
    jest.useRealTimers();
  });

  test('unmounting before the 900ms close delay does not leak a refetch call', async () => {
    const project = {
      id: 1,
      title: 'Test loyiha',
      status: 'Submitted',
      difficulty_level: 'Easy',
      grade: null,
      points_earned: 0,
      project_files: null,
      student: { full_name: 'Student One', username: 'student1', email: 's@example.com' },
    };

    // 1st request: initial project list load on mount.
    mockRequest.mockResolvedValueOnce({
      items: [project],
      total: 1,
      counts: { all: 1, pending: 1, approved: 0, rejected: 0 },
    });

    const { unmount } = render(<TeacherReview />);

    // Flush the debounced-search timer and let the initial fetch resolve.
    await act(async () => {
      jest.advanceTimersByTime(300);
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(mockRequest).toHaveBeenCalledTimes(1);

    // Open the review modal.
    fireEvent.click(screen.getByText('Test loyiha'));

    fireEvent.change(
      screen.getByPlaceholderText('Напишите подробный отзыв о работе студента...'),
      { target: { value: 'Great work!' } }
    );

    // 2nd request: the review POST.
    mockRequest.mockResolvedValueOnce({});

    fireEvent.click(screen.getByText('💾 Сохранить проверку'));

    // Let the POST resolve — this is where the 900ms close/refetch timer
    // gets scheduled.
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(mockRequest).toHaveBeenCalledTimes(2);

    // Unmount well before the 900ms timer would fire.
    expect(() => unmount()).not.toThrow();

    // Advance past the delay. Without the fix, the leaked timer calls
    // fetchProjects() here, producing a 3rd request on a dead component.
    expect(() => {
      act(() => {
        jest.advanceTimersByTime(1000);
      });
    }).not.toThrow();

    expect(mockRequest).toHaveBeenCalledTimes(2);
  });
});
