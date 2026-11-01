import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

const mockRequest = jest.fn();
jest.mock('../api/search/base', () => ({
  API_URL: 'http://test/api/',
  useHttp: () => ({ request: mockRequest }),
  headers: () => ({}),
}));

import DictionarySummaryCard from '../views/teacher/mystudents/DictionarySummaryCard';

const summary = (o) => ({
  student_id: 9, total: 10, known: 6, unknown: 2, unchecked: 2, checked: 8, percent_known: 75,
  last_checked_at: '2026-10-28T09:00:00Z', ...o,
});

beforeEach(() => mockRequest.mockReset());

test('shows the percentage over the checked words, the counts and the unasked remainder', async () => {
  mockRequest.mockResolvedValue(summary());
  render(<DictionarySummaryCard studentId={9} onOpen={() => {}} />);
  expect(await screen.findByText('75%')).toBeInTheDocument();
  expect(screen.getByText(/8 ta so'raldi, 6 tasini biladi, 2 tasini bilmaydi/)).toBeInTheDocument();
  expect(screen.getByText(/So'ralmagan: 2 \/ 10/)).toBeInTheDocument();
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '75');
  expect(mockRequest.mock.calls[0][0]).toBe('http://test/api/v1/teacher/students/9/dictionary/summary');
});

test('before the first check there is no percentage, only a prompt to start asking', async () => {
  const onOpen = jest.fn();
  mockRequest.mockResolvedValue(summary({ known: 0, unknown: 0, unchecked: 10, checked: 0, percent_known: null, last_checked_at: null }));
  render(<DictionarySummaryCard studentId={9} onOpen={onOpen} />);
  expect(await screen.findByText(/hali birortasi so'ralmagan/)).toBeInTheDocument();
  expect(screen.queryByText(/%/)).toBeNull();
  fireEvent.click(screen.getByText(/So'rashni boshlash/));
  expect(onOpen).toHaveBeenCalled();
});

test('the open link goes to the dictionary tab', async () => {
  const onOpen = jest.fn();
  mockRequest.mockResolvedValue(summary());
  render(<DictionarySummaryCard studentId={9} onOpen={onOpen} />);
  fireEvent.click(await screen.findByText(/Lug'atni ochish/));
  expect(onOpen).toHaveBeenCalledTimes(1);
});

test('a student without saved words and a failed request both render nothing', async () => {
  mockRequest.mockResolvedValueOnce(summary({ total: 0, known: 0, unknown: 0, unchecked: 0, checked: 0, percent_known: null }));
  const { container, unmount } = render(<DictionarySummaryCard studentId={9} onOpen={() => {}} />);
  await waitFor(() => expect(mockRequest).toHaveBeenCalled());
  expect(container).toBeEmptyDOMElement();
  unmount();
  mockRequest.mockRejectedValueOnce(new Error('x'));
  const second = render(<DictionarySummaryCard studentId={9} onOpen={() => {}} />);
  await waitFor(() => expect(mockRequest).toHaveBeenCalledTimes(2));
  expect(second.container).toBeEmptyDOMElement();
});
