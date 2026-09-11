/**
 * Regression tests for Teachercertificates.js (teacher "Управление
 * сертификатами" page):
 *
 *  - The initial `GET /v1/achievements/all` load used to swallow any
 *    rejection with a bare `.catch(() => {})`, leaving the teacher staring
 *    at a silent "no certificates" empty state with no error and no retry.
 *  - `showToast` fired a bare `setTimeout(() => setToast(''), 2800)` with no
 *    cleanup, so unmounting the page (e.g. navigating away) inside that
 *    window used to trigger a React "state update on an unmounted
 *    component" warning once the timer fired.
 *  - `handleDelete` called the browser's raw `fetch()` directly, bypassing
 *    the shared axios instance's auth-refresh interceptor.
 */
import React from 'react';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';

const mockRequest = jest.fn();
jest.mock('../api/search/base', () => ({
  API_URL: 'http://test/api/',
  useHttp: () => ({ request: mockRequest }),
  headers: () => ({}),
  resolveImageUrl: (src) => src,
}));

import TeacherCertificates from '../views/teacher/TeacherCertificates/Teachercertificates';

const sampleCert = {
  id: 1,
  name: 'Test Cert',
  description: 'A test certificate',
  points_reward: 10,
  criteria_type: 'project_count',
  criteria_value: 1,
  badge_image_url: '',
};

describe('TeacherCertificates — initial load failure handling', () => {
  beforeEach(() => {
    mockRequest.mockReset();
  });

  test('a failed initial load shows an inline error + retry instead of a silent empty list', async () => {
    mockRequest.mockRejectedValue(new Error('boom'));

    render(<TeacherCertificates />);

    expect(screen.getByText(/Загрузка/i)).toBeInTheDocument();

    // Wait for the load to settle and the fallback error message to render.
    await screen.findByText(/Failed to load certificates/i);

    // Locate the retry control specifically (not the header "+ Создать" button).
    const retryButtons = screen.getAllByRole('button');
    const hasRetry = retryButtons.some(b => /Qayta urinish|Повторить/i.test(b.textContent));
    expect(hasRetry).toBe(true);

    // Must not silently render the "nothing created yet" empty state.
    expect(screen.queryByText('Нет сертификатов')).not.toBeInTheDocument();
  });

  test('clicking retry re-fetches the certificate list', async () => {
    mockRequest.mockRejectedValueOnce(new Error('boom'));
    render(<TeacherCertificates />);

    await screen.findByText(/Failed to load certificates/i);
    const retryButtons = screen.getAllByRole('button');
    const retryBtn = retryButtons.find(b => /Qayta urinish|Повторить/i.test(b.textContent));
    expect(retryBtn).toBeTruthy();

    mockRequest.mockReset();
    mockRequest.mockResolvedValueOnce([sampleCert]);

    fireEvent.click(retryBtn);

    await waitFor(() => expect(mockRequest).toHaveBeenCalledTimes(1));
    await screen.findByText('Test Cert');
  });

  test('successful load never touches the raw fetch API', async () => {
    const fetchMock = jest.fn(() => Promise.reject(new Error('fetch must not be called')));
    global.fetch = fetchMock;

    mockRequest.mockResolvedValue([]);
    render(<TeacherCertificates />);

    await waitFor(() => expect(mockRequest).toHaveBeenCalledTimes(1));
    expect(fetchMock).not.toHaveBeenCalled();

    delete global.fetch;
  });
});

describe('TeacherCertificates — delete goes through the axios interceptor', () => {
  beforeEach(() => {
    mockRequest.mockReset();
  });

  test('deleting a certificate calls useHttp().request(), not a bare fetch()', async () => {
    const fetchMock = jest.fn(() => Promise.reject(new Error('fetch must not be called')));
    global.fetch = fetchMock;

    mockRequest.mockImplementation((url, method) => {
      if (method === 'DELETE') return Promise.resolve({});
      return Promise.resolve([sampleCert]);
    });

    const { container } = render(<TeacherCertificates />);
    await screen.findByText('Test Cert');

    const deleteBtn = container.querySelector('.tc-row-btn.del');
    fireEvent.click(deleteBtn);

    const confirmDeleteBtn = await screen.findByRole('button', { name: 'Удалить' });
    fireEvent.click(confirmDeleteBtn);

    await waitFor(() => expect(mockRequest).toHaveBeenCalledWith(
      expect.stringContaining('v1/achievements/1'),
      'DELETE',
      null,
      expect.anything(),
    ));
    expect(fetchMock).not.toHaveBeenCalled();

    delete global.fetch;
  });
});

describe('TeacherCertificates — toast timer cleanup on unmount', () => {
  beforeEach(() => {
    mockRequest.mockReset();
  });

  test('unmounting before the toast timeout fires does not update state on an unmounted component', async () => {
    jest.useFakeTimers({ legacyFakeTimers: false });
    const errorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    mockRequest.mockImplementation((url, method) => {
      if (method === 'DELETE') return Promise.resolve({});
      return Promise.resolve([sampleCert]);
    });

    const { container, unmount } = render(<TeacherCertificates />);
    await screen.findByText('Test Cert');

    const deleteBtn = container.querySelector('.tc-row-btn.del');
    fireEvent.click(deleteBtn);

    const confirmDeleteBtn = await screen.findByRole('button', { name: 'Удалить' });
    await act(async () => {
      fireEvent.click(confirmDeleteBtn);
      // Flush the mocked DELETE request's promise so showToast() runs and
      // starts its setTimeout before we unmount.
      await Promise.resolve();
      await Promise.resolve();
    });

    unmount();

    // Advance past the toast's 2800ms auto-dismiss timer. Before the fix,
    // this fired setToast('') on an unmounted component.
    act(() => {
      jest.advanceTimersByTime(3000);
    });

    const unmountWarning = errorSpy.mock.calls.some(args =>
      typeof args[0] === 'string'
      && args[0].includes("Can't perform a React state update on an unmounted component"),
    );
    expect(unmountWarning).toBe(false);

    errorSpy.mockRestore();
    jest.useRealTimers();
  });
});
