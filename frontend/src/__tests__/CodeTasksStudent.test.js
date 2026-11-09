import React from 'react';
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

const mockRequest = jest.fn();
const mockNavigate = jest.fn();
// react-router-dom v7 ships only ESM, which CRA's Jest cannot load: mocked, as the other page tests do.
jest.mock('react-router-dom', () => ({ useNavigate: () => mockNavigate, useParams: () => ({ id: '7' }) }), { virtual: true });
let mockEditor = null;
jest.mock('../api/search/base', () => ({
  API_URL: 'http://test/api/',
  useHttp: () => ({ request: mockRequest }),
  headers: () => ({}),
}));
jest.mock('../components/appheader/AppHeader', () => () => null);
jest.mock('../components/CodeEditor/LazyCodeEditor', () => ({
  __esModule: true,
  default: (props) => {
    mockEditor = props;
    return <textarea data-testid="editor" value={props.value} readOnly={props.readOnly}
                     onChange={(e) => props.onChange(e.target.value)} />;
  },
}));

import CodeTasks from '../views/student/codetasks/CodeTasks';
import CodeTaskPage from '../views/student/codetasks/CodeTaskPage';
import translations from '../i18n/translations';

const task = (o) => ({
  id: 7, title: 'Bubble sort', language: 'python', status: 'assigned', max_points: 20, deadline: null,
  graded_points: null, description: 'Saralang', starter_code: '# start', code: '# start', draft_saved_at: null,
  teacher_feedback: null, graded_at: null, returned_feedback: null, ...o,
});

const serve = (routes) => mockRequest.mockImplementation((url, method = 'GET', body) => {
  const key = `${method} ${url.replace('http://test/api/', '')}`;
  if (!(key in routes)) return Promise.reject(new Error(`unrouted ${key}`));
  const v = routes[key];
  if (typeof v === 'function') return v(body ? JSON.parse(body) : null);
  return Promise.resolve(v);
});
const GET = 'GET v1/code-tasks/7';
const PUT = 'PUT v1/code-tasks/7/draft';
const POST = 'POST v1/code-tasks/7/submit';

const renderPage = () => render(<CodeTaskPage />);
const type = (value) => fireEvent.change(screen.getByTestId('editor'), { target: { value } });

beforeEach(() => { mockRequest.mockReset(); mockNavigate.mockReset(); localStorage.clear(); mockEditor = null; });
afterEach(() => { jest.useRealTimers(); });

test('the list groups tasks: to write, waiting for the teacher, graded', async () => {
  serve({ 'GET v1/code-tasks/': [
    task({ id: 1, title: 'A', status: 'assigned' }), task({ id: 2, title: 'B', status: 'returned' }),
    task({ id: 3, title: 'C', status: 'submitted' }), task({ id: 4, title: 'D', status: 'graded', graded_points: 14 }),
  ] });
  render(<CodeTasks />);
  expect(await screen.findByText('Yozish kerak')).toBeInTheDocument();
  expect(screen.getByText('Tekshirilmoqda')).toBeInTheDocument();
  expect(screen.getByText('Baholangan')).toBeInTheDocument();
  expect(screen.getByText('14/20')).toBeInTheDocument();
  ['A', 'B', 'C', 'D'].forEach((n) => expect(screen.getByText(n)).toBeInTheDocument());
  fireEvent.click(screen.getByText('B'));
  expect(mockNavigate).toHaveBeenCalledWith('/student/code-tasks/2');
});

test('an empty list says so', async () => {
  serve({ 'GET v1/code-tasks/': [] });
  render(<CodeTasks />);
  expect(await screen.findByText(/Hali vazifa yo'q/)).toBeInTheDocument();
});

test('the page shows the statement as text and opens the editor with the starter code', async () => {
  serve({ [GET]: task({ description: '<img src=x onerror=alert(1)>' }) });
  const { container } = renderPage();
  expect(await screen.findByTestId('editor')).toHaveValue('# start');
  expect(screen.getByText('<img src=x onerror=alert(1)>')).toBeInTheDocument();
  expect(container.querySelector('img')).toBeNull();
});

test('typing is autosaved 10 seconds after the last change', async () => {
  jest.useFakeTimers();
  serve({ [GET]: task(), [PUT]: task() });
  renderPage();
  await screen.findByTestId('editor');
  type('x = 1');
  act(() => { jest.advanceTimersByTime(9000); });
  expect(mockRequest.mock.calls.some((c) => c[1] === 'PUT')).toBe(false);
  type('x = 12');                                                           // another change restarts the wait
  act(() => { jest.advanceTimersByTime(9000); });
  expect(mockRequest.mock.calls.some((c) => c[1] === 'PUT')).toBe(false);
  await act(async () => { jest.advanceTimersByTime(1000); });
  const puts = mockRequest.mock.calls.filter((c) => c[1] === 'PUT');
  expect(puts).toHaveLength(1);
  expect(JSON.parse(puts[0][2])).toEqual({ code: 'x = 12' });
  expect(await screen.findByText(/Saqlandi/)).toBeInTheDocument();
});

test('leaving the editor saves at once', async () => {
  serve({ [GET]: task(), [PUT]: task() });
  renderPage();
  await screen.findByTestId('editor');
  type('y = 2');
  fireEvent.blur(screen.getByTestId('editor'));
  await waitFor(() => expect(mockRequest.mock.calls.some((c) => c[1] === 'PUT')).toBe(true));
});

test('a failed save says so and the retry saves', async () => {
  let fail = true;
  serve({ [GET]: task(), [PUT]: () => (fail ? Promise.reject(new Error('net')) : Promise.resolve(task())) });
  renderPage();
  await screen.findByTestId('editor');
  type('z = 3');
  fireEvent.blur(screen.getByTestId('editor'));
  expect(await screen.findByRole('alert')).toHaveTextContent(/saqlab bo'lmadi/i);
  fail = false;
  fireEvent.click(screen.getByRole('button', { name: 'Qayta urinish' }));
  expect(await screen.findByText(/Saqlandi/)).toBeInTheDocument();
});

test('leaving the page with unsaved changes is warned about, and not after saving', async () => {
  serve({ [GET]: task(), [PUT]: task() });
  renderPage();
  await screen.findByTestId('editor');
  const probe = () => { const e = new Event('beforeunload', { cancelable: true }); window.dispatchEvent(e); return e.defaultPrevented; };
  expect(probe()).toBe(false);
  type('w = 4');
  expect(probe()).toBe(true);
  fireEvent.blur(screen.getByTestId('editor'));
  await screen.findByText(/Saqlandi/);
  expect(probe()).toBe(false);
});

test('submitting needs a confirmation and posts the code with the typing telemetry', async () => {
  jest.useFakeTimers();
  serve({ [GET]: task(), [POST]: task({ status: 'submitted' }) });
  renderPage();
  await screen.findByTestId('editor');
  act(() => { mockEditor.onInsert('typed', 8); mockEditor.onInsert('pasted', 92); });
  type('print(1)');
  act(() => { jest.advanceTimersByTime(5000); });
  fireEvent.click(screen.getByRole('button', { name: 'Topshirish' }));
  expect(mockRequest.mock.calls.some((c) => c[1] === 'POST')).toBe(false);   // not yet: it asks first
  await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Ha, topshirish' })); });
  const post = mockRequest.mock.calls.find((c) => c[1] === 'POST');
  const body = JSON.parse(post[2]);
  expect(body).toMatchObject({ code: 'print(1)', typed_chars: 8, pasted_chars: 92, paste_events: 1 });
  expect(body.active_seconds).toBeGreaterThanOrEqual(4);
  expect(typeof body.started_at).toBe('string');
  expect(screen.getByTestId('editor')).toHaveAttribute('readonly');
  expect(screen.getByText(/Tekshirishni kutmoqda/)).toBeInTheDocument();
});

test('the confirmation can be declined', async () => {
  serve({ [GET]: task() });
  renderPage();
  await screen.findByTestId('editor');
  fireEvent.click(screen.getByRole('button', { name: 'Topshirish' }));
  fireEvent.click(screen.getByRole('button', { name: "Yo'q" }));
  expect(screen.getByRole('button', { name: 'Topshirish' })).toBeInTheDocument();
  expect(mockRequest.mock.calls.some((c) => c[1] === 'POST')).toBe(false);
});

test('a 409 on submit says the task changed and reloads it', async () => {
  let reads = 0;
  serve({
    [GET]: () => { reads += 1; return Promise.resolve(reads === 1 ? task() : task({ status: 'submitted' })); },
    [POST]: () => Promise.reject({ status: 409 }),
  });
  renderPage();
  await screen.findByTestId('editor');
  type('print(1)');
  fireEvent.click(screen.getByRole('button', { name: 'Topshirish' }));
  fireEvent.click(screen.getByRole('button', { name: 'Ha, topshirish' }));
  expect(await screen.findByRole('alert')).toHaveTextContent(/holati o'zgargan/);
  await waitFor(() => expect(screen.getByTestId('editor')).toHaveAttribute('readonly'));
});

test('a returned task shows the teacher note on top and can be edited again', async () => {
  serve({ [GET]: task({ status: 'returned', returned_feedback: 'Funksiyaga ajrating' }) });
  renderPage();
  expect(await screen.findByText(/Funksiyaga ajrating/)).toBeInTheDocument();
  expect(screen.getByTestId('editor')).not.toHaveAttribute('readonly');
});

test('a graded task shows the points and the note and is read-only', async () => {
  serve({ [GET]: task({ status: 'graded', graded_points: 14, teacher_feedback: 'Barakalla' }) });
  renderPage();
  expect(await screen.findByText(/14\/20/)).toBeInTheDocument();
  expect(screen.getByText(/Barakalla/)).toBeInTheDocument();
  expect(screen.getByTestId('editor')).toHaveAttribute('readonly');
  expect(screen.queryByRole('button', { name: 'Topshirish' })).toBeNull();
});

test('the menu label exists in uz and ru', () => {
  expect(translations.uz.codeTasks).toBe('Kod vazifalari');
  expect(translations.ru.codeTasks).toBe('Задания по коду');
});

test('a task the teacher deleted says so, with a way back, instead of a useless retry', async () => {
  serve({ [GET]: () => Promise.reject({ status: 404 }) });
  renderPage();
  expect(await screen.findByText(/o'chirgan bo'lishi mumkin/)).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Qayta urinish' })).toBeNull();
  fireEvent.click(screen.getByRole('button', { name: /Orqaga/ }));
  expect(mockNavigate).toHaveBeenCalledWith('/student/code-tasks');
});

test('a task deleted while the student is typing is reported as deleted, not as a network error', async () => {
  serve({ [GET]: task(), [PUT]: () => Promise.reject({ status: 404 }) });
  renderPage();
  await screen.findByTestId('editor');
  type('x = 1');
  fireEvent.blur(screen.getByTestId('editor'));
  expect(await screen.findByText(/o'chirgan bo'lishi mumkin/)).toBeInTheDocument();
  expect(screen.queryByText(/tarmoq xatosi/)).toBeNull();
});
