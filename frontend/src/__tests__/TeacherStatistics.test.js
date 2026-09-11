/**
 * Regression test for TeacherStatistics.js (Phase 4 — frontend correctness):
 * the statistics fetch used to call raw fetch() directly, bypassing the
 * axios interceptor (auth header injection, 401 → refresh-token retry).
 * It now goes through useHttp()'s request(), which is backed by
 * axiosInstance.
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

jest.mock('../api/axiosInstance', () => ({
  __esModule: true,
  default: { request: jest.fn() },
}));

import axiosInstance from '../api/axiosInstance';
import TeacherStatistics from '../views/teacher/statistics/TeacherStatistics';

const statsData = {
  total_students: 12,
  active_groups: 3,
  average_points: 88.4,
  checked_works: 20,
  pending_works: 2,
  advanced_students: 4,
  dynamics: [],
  weekly_activity: [],
  level_breakdown: null,
  top_students: [],
  grade_distribution: [],
};

beforeEach(() => {
  axiosInstance.request.mockReset();
  localStorage.setItem('token', 'test-token');
  window.fetch = jest.fn(() => {
    throw new Error('raw fetch() must not be used — use useHttp().request() instead');
  });
});

afterEach(() => {
  delete window.fetch;
  localStorage.clear();
});

test('loads statistics through the axios-backed request(), never through raw fetch()', async () => {
  axiosInstance.request.mockResolvedValue({ data: statsData });

  render(<TeacherStatistics />);

  await screen.findByText('Статистика преподавателя');

  expect(axiosInstance.request).toHaveBeenCalledWith(
    expect.objectContaining({
      method: 'GET',
      url: expect.stringContaining('v1/teacher/statistics'),
    })
  );
  expect(window.fetch).not.toHaveBeenCalled();
});

test('shows a friendly error message when the request fails, without falling back to fetch()', async () => {
  axiosInstance.request.mockRejectedValue(new Error('network error'));

  render(<TeacherStatistics />);

  await waitFor(() => {
    expect(screen.getByText(/Не удалось загрузить статистику/)).toBeInTheDocument();
  });
  expect(window.fetch).not.toHaveBeenCalled();
});
