/**
 * Regression tests for MyProjects.js (Phase 4 — frontend correctness):
 *
 * 1. Deleting a project used to go through window.confirm()/window.alert(),
 *    which are blocked/no-op in some embedded webviews and inconsistent
 *    with the rest of the app's modal-confirmation pattern. Deletion now
 *    goes through the shared ConfirmModal component (the same one used by
 *    teacher/courses/TeacherCourses/TeacherCourses.js).
 * 2. The ZIP upload requests used to call raw fetch() directly, bypassing
 *    the axios interceptor (auth refresh, etc.). They now go through
 *    useHttp()'s request(), which is backed by axiosInstance.
 */
import React from 'react';
import { render, screen, within, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

jest.mock('lucide-react', () => ({ Trophy: () => null }));

jest.mock('../api/axiosInstance', () => ({
  __esModule: true,
  default: { request: jest.fn() },
}));

import axiosInstance from '../api/axiosInstance';
import MyProjects from '../views/student/projects/MyProjects';

const mockProject = {
  id: 42,
  title: 'Test Project',
  status: 'Draft',
  difficulty_level: 'Easy',
  points_earned: 10,
  technologies_used: ['React'],
  grade: null,
  views_count: 3,
  description: 'A test project',
  github_url: 'https://github.com/example/repo',
};

beforeEach(() => {
  axiosInstance.request.mockReset();
  window.fetch = jest.fn(() => {
    throw new Error('raw fetch() must not be used — use useHttp().request() instead');
  });
});

afterEach(() => {
  delete window.fetch;
});

const openDetailModal = async () => {
  axiosInstance.request.mockImplementation((config) => {
    if (config.method === 'GET' && config.url.endsWith('v1/project/my')) {
      return Promise.resolve({ data: [mockProject] });
    }
    return Promise.resolve({ data: {} });
  });

  render(<MyProjects />);

  const detailsBtn = await screen.findByRole('button', { name: 'Детали' });
  fireEvent.click(detailsBtn);

  await screen.findByText('📋 Test Project');
};

describe('MyProjects — delete confirmation', () => {
  test('clicking delete opens the shared ConfirmModal instead of window.confirm', async () => {
    const confirmSpy = jest.spyOn(window, 'confirm').mockImplementation(() => {
      throw new Error('window.confirm should not be called');
    });

    await openDetailModal();

    fireEvent.click(screen.getByRole('button', { name: /Удалить/ }));

    expect(await screen.findByText('Удалить проект?')).toBeInTheDocument();
    expect(confirmSpy).not.toHaveBeenCalled();

    confirmSpy.mockRestore();
  });

  test('cancelling the modal closes it without issuing a DELETE request', async () => {
    await openDetailModal();

    fireEvent.click(screen.getByRole('button', { name: /Удалить/ }));
    const dialogTitle = await screen.findByText('Удалить проект?');
    const dialog = dialogTitle.closest('.tc-confirm');

    fireEvent.click(within(dialog).getByText('Отмена'));

    await waitFor(() => expect(screen.queryByText('Удалить проект?')).not.toBeInTheDocument());
    expect(axiosInstance.request).not.toHaveBeenCalledWith(
      expect.objectContaining({ method: 'DELETE' })
    );
  });

  test('confirming the modal issues a DELETE through the axios-backed request(), not fetch()', async () => {
    await openDetailModal();

    fireEvent.click(screen.getByRole('button', { name: /Удалить/ }));
    const dialogTitle = await screen.findByText('Удалить проект?');
    const dialog = dialogTitle.closest('.tc-confirm');

    fireEvent.click(within(dialog).getByText('🗑️ Удалить'));

    await waitFor(() => {
      expect(axiosInstance.request).toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'DELETE',
          url: expect.stringContaining('v1/project/42'),
        })
      );
    });

    // The project list should now be empty — confirming the delete succeeded
    // through the mocked axios path, and the raw fetch() spy (which throws)
    // was never hit.
    await screen.findByText('У вас пока нет проектов');
    expect(window.fetch).not.toHaveBeenCalled();
  });
});
