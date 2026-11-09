import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import '@testing-library/jest-dom';

const mockRequest = jest.fn();
jest.mock('../api/search/base', () => ({
  API_URL: 'http://test/api/',
  useHttp: () => ({ request: mockRequest }),
  headers: () => ({}),
}));
jest.mock('../components/CodeEditor/LazyCodeEditor', () => ({
  __esModule: true,
  default: ({ value }) => <pre data-testid="code">{value}</pre>,
}));

import StudentCodeTasks, { pasteShare } from '../views/teacher/mystudents/StudentCodeTasks';
import { tabFromQuery } from '../views/teacher/mystudents/StudentProfile';

const LIST = 'GET v1/teacher/code-tasks/student/9';
const task = (o) => ({
  id: 1, student_id: 9, title: 'Bubble sort', description: 'Saralang', language: 'python', starter_code: null,
  max_points: 20, deadline: null, status: 'assigned', graded_points: null, teacher_feedback: null, graded_at: null,
  created_at: '2026-11-09T08:00:00Z', ...o,
});
const sub = (o) => ({
  attempt_no: 1, submitted_at: '2026-11-09T09:00:00Z', code: 'print(1)', ai_status: 'done',
  ai_review: { summary: 'Yaxshi boshlanish', strengths: ['Aniq nomlar'], issues: ["Test yo'q"], looks_complete: true, suggested_points: 15 },
  started_at: null, active_seconds: 180, typed_chars: 8, pasted_chars: 92, paste_events: 1, return_feedback: null, returned_at: null, ...o,
});
const detail = (t, subs) => ({ ...t, submissions: subs });

/** Route requests by "METHOD path"; a value may be a function of the parsed body. */
const serve = (routes) => mockRequest.mockImplementation((url, method = 'GET', body) => {
  const key = `${method} ${url.replace('http://test/api/', '')}`;
  if (!(key in routes)) return Promise.reject(new Error(`unrouted ${key}`));
  const v = routes[key];
  return Promise.resolve(typeof v === 'function' ? v(body ? JSON.parse(body) : null) : v);
});

beforeEach(() => { mockRequest.mockReset(); localStorage.clear(); });

test('pasteShare is the share of pasted characters, null when nothing was recorded', () => {
  expect(pasteShare({ typed_chars: 8, pasted_chars: 92 })).toBe(92);
  expect(pasteShare({ typed_chars: 0, pasted_chars: 0 })).toBeNull();
  expect(pasteShare({ typed_chars: 5, pasted_chars: 0 })).toBe(0);
});

test('tabFromQuery opens the tasks tab for ?tab=tasks and falls back to overview', () => {
  expect(tabFromQuery('tasks')).toBe('tasks');
  expect(tabFromQuery('dictionary')).toBe('dictionary');
  expect(tabFromQuery('nope')).toBe('overview');
  expect(tabFromQuery(null)).toBe('overview');
});

test('lists the tasks with their status and points', async () => {
  serve({ [LIST]: [task({ id: 2, title: 'Graded one', status: 'graded', graded_points: 14 }),
    task({ id: 1, status: 'submitted' })] });
  render(<StudentCodeTasks studentId="9" />);
  expect(await screen.findByText('Graded one')).toBeInTheDocument();
  expect(screen.getByText('Baholangan')).toBeInTheDocument();
  expect(screen.getByText('14/20')).toBeInTheDocument();
  expect(screen.getByText('Tekshirishni kutmoqda')).toBeInTheDocument();
  expect(mockRequest.mock.calls[0][0]).toBe('http://test/api/v1/teacher/code-tasks/student/9');
});

test('giving a task posts the exact body and shows it in the list', async () => {
  const created = task({ id: 5, title: 'New task', language: 'javascript', max_points: 30 });
  let listed = [];
  serve({
    [LIST]: () => listed,
    'POST v1/teacher/code-tasks/': (b) => { listed = [created]; return created; },
  });
  render(<StudentCodeTasks studentId="9" />);
  fireEvent.click(await screen.findByRole('button', { name: 'Yangi vazifa' }));
  fireEvent.change(screen.getByLabelText('Sarlavha'), { target: { value: 'New task' } });
  fireEvent.change(screen.getByLabelText('Shart'), { target: { value: 'Do it' } });
  fireEvent.change(screen.getByLabelText('Til'), { target: { value: 'javascript' } });
  fireEvent.change(screen.getByLabelText("Boshlang'ich kod"), { target: { value: '// x' } });
  fireEvent.change(screen.getByLabelText("Eng ko'p ball"), { target: { value: '30' } });
  fireEvent.click(screen.getByRole('button', { name: 'Vazifa berish' }));
  expect(await screen.findByText('New task')).toBeInTheDocument();
  const post = mockRequest.mock.calls.find((c) => c[1] === 'POST');
  expect(JSON.parse(post[2])).toEqual({
    student_id: 9, title: 'New task', description: 'Do it', language: 'javascript', starter_code: '// x',
    max_points: 30, deadline: null, lang: 'uz',
  });
});

test('the task carries the teacher UI language so the AI answers in it', async () => {
  localStorage.setItem('lang', 'ru');
  serve({ [LIST]: [], 'POST v1/teacher/code-tasks/': task() });
  render(<StudentCodeTasks studentId="9" />);
  fireEvent.click(await screen.findByRole('button', { name: 'Новое задание' }));
  fireEvent.change(screen.getByLabelText('Название'), { target: { value: 'T' } });
  fireEvent.change(screen.getByLabelText('Условие'), { target: { value: 'D' } });
  fireEvent.click(screen.getByRole('button', { name: 'Выдать задание' }));
  await waitFor(() => expect(mockRequest.mock.calls.some((c) => c[1] === 'POST')).toBe(true));
  expect(JSON.parse(mockRequest.mock.calls.find((c) => c[1] === 'POST')[2]).lang).toBe('ru');
});

const openSubmitted = async (subs = [sub()], extra = {}) => {
  const t = task({ status: 'submitted', ...extra });
  serve({ [LIST]: [t], 'GET v1/teacher/code-tasks/1': detail(t, subs) });
  const view = render(<StudentCodeTasks studentId="9" />);
  fireEvent.click(await screen.findByText('Bubble sort'));
  await screen.findByTestId('code');
  return view;
};

test('the review panel shows the code, the AI summary, the integrity hint — and does not pre-fill the points', async () => {
  const { container } = await openSubmitted();
  expect(screen.getByTestId('code')).toHaveTextContent('print(1)');
  expect(screen.getByText('Yaxshi boshlanish')).toBeInTheDocument();
  expect(screen.getByText('Aniq nomlar')).toBeInTheDocument();
  expect(screen.getByText("Test yo'q")).toBeInTheDocument();
  expect(screen.getByText(/AI tavsiyasi: 15 \/ 20/)).toBeInTheDocument();
  expect(screen.getByText(/92% qo'yilgan/)).toBeInTheDocument();
  expect(screen.getByText(/3 daq/)).toBeInTheDocument();
  expect(screen.getByLabelText('Ball')).toHaveValue(null);
  expect(container.querySelector('script')).toBeNull();
});

test('the AI states: pending and failed each say what to do', async () => {
  await openSubmitted([sub({ ai_status: 'pending', ai_review: null })]);
  expect(screen.getByText(/AI xulosa tayyorlanmoqda/)).toBeInTheDocument();
});

test('a failed AI review tells the teacher to review it themselves', async () => {
  await openSubmitted([sub({ ai_status: 'failed', ai_review: null })]);
  expect(screen.getByText(/AI xulosa tayyor bo'lmadi/)).toBeInTheDocument();
});

test('late work is flagged', async () => {
  await openSubmitted([sub({ submitted_at: '2026-11-12T09:00:00Z' })], { deadline: '2026-11-10T00:00:00Z' });
  expect(screen.getByText('Kech topshirilgan')).toBeInTheDocument();
});

test('markup-like code is shown as text, never as an element', async () => {
  const { container } = await openSubmitted([sub({ code: '<script>alert(1)</script>' })]);
  expect(screen.getByTestId('code')).toHaveTextContent('<script>alert(1)</script>');
  expect(container.querySelector('script')).toBeNull();
});

test('Baholash posts the points and note and the row shows the result', async () => {
  const graded = task({ status: 'graded', graded_points: 14, teacher_feedback: 'Yaxshi' });
  let current = task({ status: 'submitted' });
  serve({
    [LIST]: () => [current],
    'GET v1/teacher/code-tasks/1': () => detail(current, [sub()]),
    'POST v1/teacher/code-tasks/1/grade': (b) => { current = graded; return graded; },
  });
  render(<StudentCodeTasks studentId="9" />);
  fireEvent.click(await screen.findByText('Bubble sort'));
  await screen.findByTestId('code');
  fireEvent.change(screen.getByLabelText('Ball'), { target: { value: '14' } });
  fireEvent.change(screen.getByLabelText('Izoh'), { target: { value: 'Yaxshi' } });
  fireEvent.click(screen.getByRole('button', { name: 'Baholash' }));
  expect(await screen.findByText('14/20')).toBeInTheDocument();
  const post = mockRequest.mock.calls.find((c) => String(c[0]).endsWith('/grade'));
  expect(JSON.parse(post[2])).toEqual({ points: 14, feedback: 'Yaxshi' });
});

test('Qaytarish stays disabled until there is feedback, then posts it', async () => {
  let current = task({ status: 'submitted' });
  serve({
    [LIST]: () => [current],
    'GET v1/teacher/code-tasks/1': () => detail(current, [sub()]),
    'POST v1/teacher/code-tasks/1/return': () => { current = task({ status: 'returned' }); return current; },
  });
  render(<StudentCodeTasks studentId="9" />);
  fireEvent.click(await screen.findByText('Bubble sort'));
  await screen.findByTestId('code');
  const btn = screen.getByRole('button', { name: 'Qaytarish' });
  expect(btn).toBeDisabled();
  fireEvent.change(screen.getByLabelText('Izoh'), { target: { value: '   ' } });
  expect(btn).toBeDisabled();
  fireEvent.change(screen.getByLabelText('Izoh'), { target: { value: 'Funksiyaga ajrating' } });
  expect(btn).toBeEnabled();
  fireEvent.click(btn);
  expect(await screen.findByText('Qaytarilgan')).toBeInTheDocument();
  const post = mockRequest.mock.calls.find((c) => String(c[0]).endsWith('/return'));
  expect(JSON.parse(post[2])).toEqual({ feedback: 'Funksiyaga ajrating' });
});

test('a task that is not submitted has no grading controls', async () => {
  const t = task({ status: 'assigned' });
  serve({ [LIST]: [t], 'GET v1/teacher/code-tasks/1': detail(t, []) });
  render(<StudentCodeTasks studentId="9" />);
  fireEvent.click(await screen.findByText('Bubble sort'));
  await screen.findByText('Saralang');
  expect(screen.queryByRole('button', { name: 'Baholash' })).toBeNull();
});
