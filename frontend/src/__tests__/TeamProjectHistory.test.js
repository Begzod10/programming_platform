import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

const mockRequest = jest.fn();
jest.mock('../api/search/base', () => ({
  API_URL: 'http://test/api/',
  useHttp: () => ({ request: mockRequest }),
  headers: () => ({}),
}));

import TeamProjectHistory from '../views/student/teamprojects/TeamProjectHistory';

const row = (o) => ({
  team_id: 1, name: 'Team 1', status: 'reviewed', place: 1, is_mine: false, approved_tasks: 4, total_tasks: 4,
  avg_score: 90, final_grade: 'B', points: 262, summary: '4/4 vazifa tasdiqlandi', summary_ru: '4/4', members: [], ...o,
});

const history = [{
  team_project_id: 6, title: "Onlayn do'kon", status: 'active', created_at: '2026-10-05T11:34:45Z',
  total_teams: 2, finished_teams: 1, my_place: 1,
  teams: [
    row({ team_id: 12, name: 'Team 2', is_mine: true, members: ['Ali Valiyev', 'Vali Aliyev'] }),
    row({ team_id: 11, name: 'Team 1', status: 'working', place: null, approved_tasks: 1, total_tasks: 5, avg_score: 95, final_grade: null,
          summary: 'Tugallanmagan: 1/5 vazifa tasdiqlandi' }),
  ],
}];

beforeEach(() => mockRequest.mockReset());

test('the icon opens a panel with the places, the own team summary, and an honest "unplaced" for unfinished teams', async () => {
  mockRequest.mockResolvedValueOnce(history);
  render(<TeamProjectHistory ru={false} />);

  expect(mockRequest).not.toHaveBeenCalled();               // nothing is fetched until the panel opens
  fireEvent.click(screen.getByRole('button', { name: /Natijalar va loyihalar arxivi/ }));

  expect(await screen.findByText("Onlayn do'kon")).toBeInTheDocument();
  expect(mockRequest.mock.calls[0][0]).toMatch(/team-projects\/my\/history$/);
  expect(screen.getAllByText(/🥇/).length).toBeGreaterThan(0);
  expect(screen.getByText("O'rinsiz")).toBeInTheDocument();                 // unfinished team has no place
  expect(screen.getByText('4/4 vazifa tasdiqlandi')).toBeInTheDocument();   // own summary
  expect(screen.getByText('Ali Valiyev · Vali Aliyev')).toBeInTheDocument();// own members only
  expect(screen.getByText(/faqat yakuniy loyihani topshirgan/)).toBeInTheDocument();
  expect(screen.getByText('Team 2 (siz)')).toBeInTheDocument();

  fireEvent.click(screen.getByRole('button', { name: 'Yopish' }));
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});

test('a failed load shows an error, an empty history shows the placeholder', async () => {
  mockRequest.mockRejectedValueOnce(new Error('boom'));
  const { unmount } = render(<TeamProjectHistory ru={false} />);
  fireEvent.click(screen.getByRole('button', { name: /Natijalar va loyihalar arxivi/ }));
  expect(await screen.findByRole('alert')).toHaveTextContent("Natijalarni yuklab bo'lmadi");
  unmount();

  mockRequest.mockResolvedValueOnce([]);
  render(<TeamProjectHistory ru />);
  fireEvent.click(screen.getByRole('button', { name: /Итоги и архив проектов/ }));
  await waitFor(() => expect(screen.getByText('Пока нет командных проектов.')).toBeInTheDocument());
});
