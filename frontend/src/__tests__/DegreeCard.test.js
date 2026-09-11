/**
 * Regression tests for DegreeCard.js (student "Мои сертификаты" page):
 *
 *  - The initial Promise.all([my-progress, my]) load used to swallow any
 *    rejection with a bare `.catch(() => {})`, leaving the user staring at
 *    a silent "no certificates" empty state with no indication anything
 *    went wrong and no way to retry.
 *  - The PDF download flow called the browser's raw `fetch()` directly,
 *    bypassing the shared axios instance's auth-refresh interceptor, so a
 *    download made right after token expiry would fail outright instead of
 *    transparently refreshing the token first.
 */
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

const mockRequest = jest.fn();
jest.mock('../api/search/base', () => ({
  API_URL: 'http://test/api/',
  useHttp: () => ({ request: mockRequest }),
  headers: () => ({}),
  resolveImageUrl: (src) => src,
}));

const mockAxiosGet = jest.fn();
jest.mock('../api/axiosInstance', () => ({
  __esModule: true,
  default: { get: (...args) => mockAxiosGet(...args) },
}));

import Degrees from '../views/student/degrees/DegreeCard';

describe('DegreeCard (Degrees) — initial load failure handling', () => {
  beforeEach(() => {
    mockRequest.mockReset();
    mockAxiosGet.mockReset();
  });

  test('a failed Promise.all shows an inline error + retry instead of a silent empty state', async () => {
    mockRequest.mockRejectedValue(new Error('network down'));

    render(<Degrees />);

    // Loading state first.
    expect(screen.getByText(/Загрузка сертификатов/i)).toBeInTheDocument();

    // An error + retry control appears once the load settles.
    await screen.findByText(/Failed to load certificates/i);
    const retryBtn = screen.getByRole('button', { name: /Qayta urinish|Повторить/i });
    expect(retryBtn).toBeInTheDocument();

    // This must NOT be the plain "nothing here yet" empty state — the user
    // needs to know the load actually failed.
    expect(screen.queryByText('Пока нет доступных сертификатов')).not.toBeInTheDocument();
  });

  test('clicking retry re-triggers the fetch', async () => {
    mockRequest.mockRejectedValue(new Error('fail'));
    render(<Degrees />);

    await screen.findByText(/Failed to load certificates/i);
    const retryBtn = screen.getByRole('button', { name: /Qayta urinish|Повторить/i });
    expect(mockRequest).toHaveBeenCalledTimes(2); // my-progress + my

    mockRequest.mockReset();
    mockRequest.mockResolvedValue([]);

    fireEvent.click(retryBtn);

    await waitFor(() => expect(mockRequest).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(screen.getByText('Пока нет доступных сертификатов')).toBeInTheDocument());
  });

  test('successful load never touches the raw fetch API', async () => {
    const fetchMock = jest.fn(() => Promise.reject(new Error('fetch must not be called')));
    global.fetch = fetchMock;

    mockRequest.mockResolvedValue([]);
    render(<Degrees />);

    await waitFor(() => expect(mockRequest).toHaveBeenCalledTimes(2));
    expect(fetchMock).not.toHaveBeenCalled();

    delete global.fetch;
  });
});

describe('DegreeCard (Degrees) — PDF download goes through the axios interceptor', () => {
  beforeEach(() => {
    mockRequest.mockReset();
    mockAxiosGet.mockReset();
    global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
    global.URL.revokeObjectURL = jest.fn();
  });

  afterEach(() => {
    delete global.URL.createObjectURL;
    delete global.URL.revokeObjectURL;
  });

  test('download uses axiosInstance.get with responseType "blob" instead of a bare fetch()', async () => {
    const fetchMock = jest.fn(() => Promise.reject(new Error('fetch must not be called')));
    global.fetch = fetchMock;

    mockRequest.mockImplementation((url) => {
      if (url.includes('check-and-earn-certificate')) return Promise.resolve({});
      if (url.includes('my-progress')) {
        return Promise.resolve([{
          achievement_id: 1,
          name: 'Cert A',
          description: 'desc',
          points_reward: 5,
          is_earned: true,
          progress: 100,
          current_value: 1,
          criteria_value: 1,
        }]);
      }
      if (url.includes('/achievements/my')) {
        return Promise.resolve([{ achievement_name: 'Cert A', course_id: 42, earned_at: '2024-01-01' }]);
      }
      return Promise.resolve([]);
    });

    mockAxiosGet.mockResolvedValue({ data: new Blob(['pdf-bytes'], { type: 'application/pdf' }) });

    render(<Degrees />);

    const downloadBtn = await screen.findByRole('button', { name: /Скачать PDF/i });
    fireEvent.click(downloadBtn);

    await waitFor(() => expect(mockAxiosGet).toHaveBeenCalledWith(
      expect.stringContaining('v1/achievements/course/42/download'),
      expect.objectContaining({ responseType: 'blob' }),
    ));

    expect(fetchMock).not.toHaveBeenCalled();

    delete global.fetch;
  });
});
