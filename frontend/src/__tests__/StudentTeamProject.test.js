/**
 * Regression tests for StudentTeamProject.js (student "Jamoaviy loyiha" page):
 *
 *  - submitTask/finalize/submitRatings/reload used to end in a bare
 *    `catch {}`, leaving the student staring at a button that silently
 *    reverts to idle with zero feedback on failure. Now each sets a visible
 *    `.stp-error-banner` message.
 *  - Task completion had no at-a-glance summary — a `.stp-progress` bar +
 *    label now shows "<approved>/<total> vazifa tasdiqlandi".
 *  - Tasks carry `deadline_at` but nothing surfaced it proactively — a
 *    `.stp-deadline` chip now warns when a task's deadline is close, but
 *    only while the task is still actionable (not approved/blocked).
 *  - The lead crown was conveyed only via an emoji with no text
 *    alternative — screen-reader-only text "(jamoa boshlig'i)" was added.
 */
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

const mockRequest = jest.fn();
jest.mock('../api/search/base', () => ({
  API_URL: 'http://test/api/',
  useHttp: () => ({ request: mockRequest }),
  headers: () => ({}),
}));

jest.mock('../hooks/useSessionSocket', () => ({
  useSessionSocket: () => {},
}));

import StudentTeamProject from '../views/student/teamprojects/StudentTeamProject';

const baseMember = (overrides = {}) => ({
  student_id: 1,
  full_name: 'Aziz Aliyev',
  role: 'member',
  ...overrides,
});

const baseTask = (overrides = {}) => ({
  id: 100,
  title: 'Login sahifasi',
  description: 'Login formasini yasang',
  status: 'assigned',
  assigned_student_id: 1,
  assigned_student_name: 'Aziz Aliyev',
  acceptance_criteria: [],
  ai_feedback: null,
  ai_score: null,
  deadline_at: null,
  ...overrides,
});

const baseEntry = (teamOverrides = {}) => ({
  my_role: 'member',
  my_team: {
    id: 5,
    name: 'Jamoa A',
    theme_label: null,
    tech_stack_label: null,
    project_title: null,
    project_description: null,
    status: 'active',
    members: [baseMember()],
    tasks: [baseTask()],
    ...teamOverrides,
  },
});

beforeEach(() => {
  mockRequest.mockReset();
  localStorage.setItem('user', JSON.stringify({ id: 1 }));
});

afterEach(() => {
  localStorage.clear();
});

describe('StudentTeamProject — visible error handling', () => {
  test('a failed submitTask shows the fallback error message in the error banner', async () => {
    mockRequest.mockResolvedValueOnce([baseEntry()]);
    render(<StudentTeamProject />);

    const input = await screen.findByLabelText('GitHub havolasi');
    fireEvent.change(input, { target: { value: 'https://github.com/foo/bar' } });

    mockRequest.mockRejectedValueOnce(new Error('boom'));
    const submitBtn = screen.getByRole('button', { name: 'Topshirish' });
    fireEvent.click(submitBtn);

    const banner = await screen.findByRole('alert');
    expect(banner).toHaveClass('stp-error-banner');
    expect(banner).toHaveTextContent("Vazifani topshirib bo'lmadi");
  });

  test('a failed submitTask surfaces the backend error message when present', async () => {
    mockRequest.mockResolvedValueOnce([baseEntry()]);
    render(<StudentTeamProject />);

    const input = await screen.findByLabelText('GitHub havolasi');
    fireEvent.change(input, { target: { value: 'https://github.com/foo/bar' } });

    const backendError = new Error('rejected');
    backendError.response = { data: { detail: 'Havola noto\'g\'ri formatda' } };
    mockRequest.mockRejectedValueOnce(backendError);
    const submitBtn = screen.getByRole('button', { name: 'Topshirish' });
    fireEvent.click(submitBtn);

    const banner = await screen.findByRole('alert');
    expect(banner).toHaveTextContent("Havola noto'g'ri formatda");
  });
});

describe('StudentTeamProject — initial load failure', () => {
  test('a failed initial reload shows the error banner instead of the generic "no team project yet" placeholder', async () => {
    const backendError = new Error('network down');
    backendError.response = { data: { detail: 'Server bilan aloqa yo\'q' } };
    mockRequest.mockRejectedValueOnce(backendError);
    render(<StudentTeamProject />);

    const banner = await screen.findByRole('alert');
    expect(banner).toHaveTextContent("Server bilan aloqa yo'q");
    expect(screen.queryByText('Sizga hali jamoaviy loyiha topshirilmagan.')).not.toBeInTheDocument();
  });
});

describe('StudentTeamProject — progress summary', () => {
  test('renders "2/4 vazifa tasdiqlandi" for a team with 4 tasks, 2 approved', async () => {
    const tasks = [
      baseTask({ id: 1, status: 'approved' }),
      baseTask({ id: 2, status: 'approved' }),
      baseTask({ id: 3, status: 'assigned' }),
      baseTask({ id: 4, status: 'submitted' }),
    ];
    mockRequest.mockResolvedValueOnce([baseEntry({ tasks })]);
    render(<StudentTeamProject />);

    expect(await screen.findByText('2/4 vazifa tasdiqlandi')).toBeInTheDocument();
  });
});

describe('StudentTeamProject — deadline chip', () => {
  test('a task 2 days from deadline (status assigned) shows a warning deadline chip', async () => {
    const inTwoDays = new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString();
    const tasks = [baseTask({ id: 1, status: 'assigned', deadline_at: inTwoDays })];
    mockRequest.mockResolvedValueOnce([baseEntry({ tasks })]);
    render(<StudentTeamProject />);

    const chip = await screen.findByText('2 kun qoldi');
    expect(chip).toHaveClass('stp-deadline');
    expect(chip).toHaveClass('stp-deadline--warning');
  });

  test('a blocked task with a past deadline does not render a second, duplicate deadline chip', async () => {
    const inThePast = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString();
    const tasks = [baseTask({ id: 1, status: 'blocked', deadline_at: inThePast })];
    mockRequest.mockResolvedValueOnce([baseEntry({ tasks })]);
    render(<StudentTeamProject />);

    const matches = await screen.findAllByText('Muddati o\'tgan');
    expect(matches).toHaveLength(1); // the existing status chip only, not a second deadline chip
    expect(screen.queryByText(/kun qoldi/)).not.toBeInTheDocument();
  });

  test('a still-actionable task past its deadline shows a deadline chip proactively, before the backend catches up and flips status to blocked', async () => {
    const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString();
    const tasks = [baseTask({ id: 1, status: 'assigned', deadline_at: twoHoursAgo })];
    mockRequest.mockResolvedValueOnce([baseEntry({ tasks })]);
    render(<StudentTeamProject />);

    const chip = await screen.findByText("Muddati o'tgan");
    expect(chip).toHaveClass('stp-deadline');
    expect(chip).toHaveClass('stp-deadline--warning');
  });

  test('a deadline under 24h away does not claim it is "tomorrow"', async () => {
    const inFiveHours = new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString();
    const tasks = [baseTask({ id: 1, status: 'assigned', deadline_at: inFiveHours })];
    mockRequest.mockResolvedValueOnce([baseEntry({ tasks })]);
    render(<StudentTeamProject />);

    const chip = await screen.findByText('24 soatdan kam qoldi');
    expect(chip).toHaveClass('stp-deadline--warning');
    expect(screen.queryByText(/ertaga/i)).not.toBeInTheDocument();
  });
});

describe('StudentTeamProject — accessible lead indicator', () => {
  test('the lead member row contains screen-reader text "(jamoa boshlig\'i)"', async () => {
    const members = [
      baseMember({ student_id: 1, full_name: 'Aziz Aliyev', role: 'lead' }),
      baseMember({ student_id: 2, full_name: 'Vali Valiyev', role: 'member' }),
    ];
    mockRequest.mockResolvedValueOnce([baseEntry({ members })]);
    render(<StudentTeamProject />);

    await waitFor(() => expect(screen.getByText('Aziz Aliyev')).toBeInTheDocument());
    expect(screen.getByText("(jamoa boshlig'i)")).toBeInTheDocument();
  });
});
