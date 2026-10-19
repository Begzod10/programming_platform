import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

const mockRequest = jest.fn();
jest.mock('../api/search/base', () => ({
  API_URL: 'http://test/api/',
  useHttp: () => ({ request: mockRequest }),
  headers: () => ({}),
}));

import StudentDictionary, { hardness, isHard } from '../views/teacher/mystudents/StudentDictionary';

const word = (o) => ({
  id: 1, word: 'closure', context: 'A closure remembers its scope.', lang: 'uz', lesson_id: 5,
  lesson_title: 'Funksiyalar', course_id: 3, course_title: 'JavaScript', review_count: 2,
  correct_count: 1, incorrect_count: 0, ...o,
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
