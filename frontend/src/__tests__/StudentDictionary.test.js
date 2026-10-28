import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

const mockRequest = jest.fn();
jest.mock('../api/search/base', () => ({
  API_URL: 'http://test/api/',
  useHttp: () => ({ request: mockRequest }),
  headers: () => ({}),
}));

import StudentDictionary, { hardness, isHard, checkState } from '../views/teacher/mystudents/StudentDictionary';

const word = (o) => ({
  id: 1, word: 'closure', context: 'A closure remembers its scope.', lang: 'uz', lesson_id: 5,
  lesson_title: 'Funksiyalar', course_id: 3, course_title: 'JavaScript', review_count: 2,
  correct_count: 1, incorrect_count: 0, last_check_knows: null, last_checked_at: null, checks_count: 0, ...o,
});
const dictionary = (words) => ({ student_id: 9, total: words.length, words });

beforeEach(() => mockRequest.mockReset());

test('hardness: more wrong than right answers marks a word as hard', () => {
  expect(isHard(word({ correct_count: 1, incorrect_count: 3 }))).toBe(true);
  expect(isHard(word({ correct_count: 3, incorrect_count: 3 }))).toBe(false);
  expect(hardness(word({ correct_count: 0, incorrect_count: 0 }))).toBe(0);
});

test('lists the words with their lesson and stats', async () => {
  mockRequest.mockResolvedValue(dictionary([word({ id: 1 }), word({ id: 2, word: 'mutation', correct_count: 0, incorrect_count: 2 })]));
  render(<StudentDictionary studentId={9} />);
  expect(await screen.findByText('closure')).toBeInTheDocument();
  expect(screen.getByText('mutation')).toBeInTheDocument();
  expect(mockRequest.mock.calls[0][0]).toBe('http://test/api/v1/teacher/students/9/dictionary');
  expect(screen.getAllByText(/JavaScript · Funksiyalar/)).toHaveLength(2);
  expect(screen.getByText('qiyin')).toBeInTheDocument();                    // only "mutation" is hard
  expect(screen.getByText('2 / 2 so\'z')).toBeInTheDocument();
});

test('search narrows the list', async () => {
  mockRequest.mockResolvedValue(dictionary([word({ id: 1 }), word({ id: 2, word: 'mutation' })]));
  render(<StudentDictionary studentId={9} />);
  await screen.findByText('closure');
  fireEvent.change(screen.getByLabelText("So'z qidirish"), { target: { value: 'mut' } });
  expect(screen.queryByText('closure')).toBeNull();
  expect(screen.getByText('mutation')).toBeInTheDocument();
});

test('"hard first" puts the words the student gets wrong on top', async () => {
  mockRequest.mockResolvedValue(dictionary([
    word({ id: 1, word: 'easy', correct_count: 5, incorrect_count: 0 }),
    word({ id: 2, word: 'tricky', correct_count: 0, incorrect_count: 4 }),
  ]));
  const { container } = render(<StudentDictionary studentId={9} />);
  await screen.findByText('easy');
  fireEvent.click(screen.getByLabelText('Qiyinlari birinchi'));
  const order = [...container.querySelectorAll('.sdict-word')].map((n) => n.textContent);
  expect(order).toEqual(['tricky', 'easy']);
});

test('random word shows one word from the filtered list; context stays hidden until asked', async () => {
  mockRequest.mockResolvedValue(dictionary([word({ id: 1 }), word({ id: 2, word: 'mutation', context: 'State changes.' })]));
  const { container } = render(<StudentDictionary studentId={9} />);
  await screen.findByText('closure');
  fireEvent.change(screen.getByLabelText("So'z qidirish"), { target: { value: 'mut' } });
  fireEvent.click(screen.getByText(/Tasodifiy so'z/));
  expect(container.querySelector('.sdict-picked-word')).toHaveTextContent('mutation');
  expect(screen.queryByText('State changes.')).toBeNull();
  fireEvent.click(screen.getByText("Kontekstni ko'rsatish"));
  expect(screen.getByText('State changes.')).toBeInTheDocument();
});

test('empty dictionary and load errors have their own messages', async () => {
  mockRequest.mockResolvedValueOnce(dictionary([]));
  const { unmount } = render(<StudentDictionary studentId={9} />);
  expect(await screen.findByText(/hali lug'atga so'z qo'shmagan/)).toBeInTheDocument();
  unmount();
  mockRequest.mockRejectedValueOnce(new Error('x'));
  render(<StudentDictionary studentId={9} />);
  await waitFor(() => expect(screen.getByText(/yuklab bo'lmadi/)).toBeInTheDocument());
  expect(screen.getByText('Qayta urinish')).toBeInTheDocument();
});

describe("the teacher's oral checks", () => {
  test('checkState maps the latest verdict', () => {
    expect(checkState(word({ last_check_knows: true }))).toBe('known');
    expect(checkState(word({ last_check_knows: false }))).toBe('unknown');
    expect(checkState(word({ last_check_knows: null }))).toBe('unchecked');
  });

  test('shows the tally and each word state', async () => {
    mockRequest.mockResolvedValue(dictionary([
      word({ id: 1, word: 'a', last_check_knows: true, last_checked_at: '2026-10-20T10:00:00Z', checks_count: 1 }),
      word({ id: 2, word: 'b', last_check_knows: false, checks_count: 2, last_checked_at: '2026-10-21T10:00:00Z' }),
      word({ id: 3, word: 'c' }),
    ]));
    const { container } = render(<StudentDictionary studentId={9} />);
    await screen.findByText('a');
    expect(container.querySelector('.sdict-tally')).toHaveTextContent("Biladi 1 · Bilmaydi 1 · So'ralmagan 1");
    expect(container.querySelector('.sdict-state--known')).toBeInTheDocument();
    expect(container.querySelector('.sdict-state--unknown')).toHaveTextContent('2x');
  });

  test('the status filter narrows the list to unknown or unasked words', async () => {
    mockRequest.mockResolvedValue(dictionary([
      word({ id: 1, word: 'known1', last_check_knows: true }),
      word({ id: 2, word: 'unknown1', last_check_knows: false }),
      word({ id: 3, word: 'fresh1' }),
    ]));
    render(<StudentDictionary studentId={9} />);
    await screen.findByText('known1');
    fireEvent.change(screen.getByLabelText('Holat'), { target: { value: 'unknown' } });
    expect(screen.getByText('unknown1')).toBeInTheDocument();
    expect(screen.queryByText('known1')).toBeNull();
    fireEvent.change(screen.getByLabelText('Holat'), { target: { value: 'unchecked' } });
    expect(screen.getByText('fresh1')).toBeInTheDocument();
    expect(screen.queryByText('unknown1')).toBeNull();
  });

  test('"Biladi" on a row saves the verdict through the API and updates the row and the tally', async () => {
    mockRequest.mockResolvedValueOnce(dictionary([word({ id: 7, word: 'closure' })]));
    const { container } = render(<StudentDictionary studentId={9} />);
    await screen.findByText('closure');
    mockRequest.mockResolvedValueOnce(word({ id: 7, word: 'closure', last_check_knows: true, last_checked_at: '2026-10-28T09:00:00Z', checks_count: 1 }));
    fireEvent.click(screen.getByLabelText('closure: biladi'));
    await waitFor(() => expect(container.querySelector('.sdict-state--known')).toBeInTheDocument());
    const call = mockRequest.mock.calls[1];
    expect(call[0]).toBe('http://test/api/v1/teacher/students/9/dictionary/7/check');
    expect(call[1]).toBe('POST');
    expect(JSON.parse(call[2])).toEqual({ knows: true });
    expect(container.querySelector('.sdict-tally')).toHaveTextContent('Biladi 1 · Bilmaydi 0');
  });

  test('on the random card, a verdict is saved and the next word comes up', async () => {
    mockRequest.mockResolvedValueOnce(dictionary([word({ id: 1, word: 'first' }), word({ id: 2, word: 'second' })]));
    const { container } = render(<StudentDictionary studentId={9} />);
    await screen.findByText('first');
    fireEvent.click(screen.getByText(/Tasodifiy so'z/));
    const shownFirst = container.querySelector('.sdict-picked-word').textContent;
    const other = shownFirst === 'first' ? 'second' : 'first';
    const pickedId = shownFirst === 'first' ? 1 : 2;
    mockRequest.mockResolvedValueOnce(word({ id: pickedId, word: shownFirst, last_check_knows: false, checks_count: 1, last_checked_at: '2026-10-28T09:00:00Z' }));
    fireEvent.click(screen.getByText('✗ Bilmaydi'));
    await waitFor(() => expect(container.querySelector('.sdict-picked-word')).toHaveTextContent(other));
    expect(JSON.parse(mockRequest.mock.calls[1][2])).toEqual({ knows: false });
  });

  test('a failed save shows an error and keeps the old state', async () => {
    mockRequest.mockResolvedValueOnce(dictionary([word({ id: 7, word: 'closure' })]));
    const { container } = render(<StudentDictionary studentId={9} />);
    await screen.findByText('closure');
    mockRequest.mockRejectedValueOnce(new Error('boom'));
    fireEvent.click(screen.getByLabelText('closure: bilmaydi'));
    expect(await screen.findByRole('alert')).toHaveTextContent("saqlab bo'lmadi");
    expect(container.querySelector('.sdict-tally')).toHaveTextContent("Biladi 0 · Bilmaydi 0 · So'ralmagan 1");
  });
});

