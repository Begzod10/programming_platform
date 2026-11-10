import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

let mockLang = 'uz';
jest.mock('../api/search/base', () => ({ API_URL: 'http://test/api/v1', headers: () => ({}) }));
jest.mock('../i18n/useTranslation', () => ({ useTranslation: () => ({ lang: mockLang, t: (k) => k }) }));

import LessonVocabCard, { pickDefinition } from '../views/student/courses/LessonPage/LessonVocabCard';
import LessonVocabEditor from '../views/teacher/courses/LessonEditor/LessonVocabEditor';

const BASE = '/api/v1/courses/3/lessons/7/vocabulary';
const json = (body, ok = true, status = 200) => Promise.resolve({ ok, status, json: () => Promise.resolve(body) });

// fetch stand-in: `routes` maps "METHOD url" to a response factory; every call is recorded.
let calls;
const mockFetch = (routes) => {
  calls = [];
  global.fetch = jest.fn((url, opts = {}) => {
    const method = opts.method || 'GET';
    calls.push({ url, method, body: opts.body ? JSON.parse(opts.body) : undefined });
    const hit = routes[`${method} ${url}`];
    return hit ? hit() : json([]);
  });
};
const sent = (method, url) => calls.filter(c => c.method === method && c.url === url);

beforeEach(() => { mockLang = 'uz'; });

describe('pickDefinition', () => {
  const w = { definition: 'tanlagich', definition_ru: 'селектор' };
  test('Russian reader gets the Russian definition', () => expect(pickDefinition(w, true)).toBe('селектор'));
  test('Uzbek reader gets the Uzbek definition', () => expect(pickDefinition(w, false)).toBe('tanlagich'));
  test('falls back to Uzbek when there is no Russian definition', () => {
    expect(pickDefinition({ definition: 'tanlagich', definition_ru: null }, true)).toBe('tanlagich');
    expect(pickDefinition({ definition: 'tanlagich', definition_ru: '  ' }, true)).toBe('tanlagich');
    expect(pickDefinition({ definition: 'tanlagich' }, true)).toBe('tanlagich');
  });
});

describe('LessonVocabCard', () => {
  const words = [
    { id: 1, word: 'selector', definition: 'tanlagich', definition_ru: 'селектор' },
    { id: 2, word: 'property', definition: 'xossa', definition_ru: null },
  ];
  const routes = { 'GET http://test/api/v1/courses/3/lessons/7/vocabulary': () => json(words) };

  test('shows Uzbek definitions to an Uzbek reader', async () => {
    mockFetch(routes);
    render(<LessonVocabCard courseId={3} lessonId={7} />);
    expect(await screen.findByText('tanlagich')).toBeInTheDocument();
    expect(screen.queryByText('селектор')).not.toBeInTheDocument();
  });

  test('shows Russian definitions to a Russian reader, Uzbek where there is none', async () => {
    mockLang = 'ru';
    mockFetch(routes);
    render(<LessonVocabCard courseId={3} lessonId={7} />);
    expect(await screen.findByText('селектор')).toBeInTheDocument();
    expect(screen.queryByText('tanlagich')).not.toBeInTheDocument();
    expect(screen.getByText('xossa')).toBeInTheDocument();
  });
});

describe('LessonVocabEditor', () => {
  const existing = [{ id: 1, word: 'selector', definition: 'tanlagich', definition_ru: 'селектор', source: 'manual', order: 4 }];
  const generated = [
    { id: 8, word: 'property', definition: 'xossa', definition_ru: 'свойство', source: 'ai', order: 5 },
    { id: 9, word: 'value', definition: 'qiymat', definition_ru: 'значение', source: 'ai', order: 6 },
  ];
  const open = async (routes = {}) => {
    mockFetch({ [`GET ${BASE}`]: () => json(existing), ...routes });
    render(<LessonVocabEditor courseId={3} lessonId={7} />);
    await screen.findByText('selector');
  };

  test('lists both definitions and marks AI rows', async () => {
    await open({ [`GET ${BASE}`]: () => json([...existing, generated[0]]) });
    expect(screen.getByText('селектор')).toBeInTheDocument();
    expect(screen.getByText('свойство')).toBeInTheDocument();
    expect(screen.getAllByText('AI')).toHaveLength(1);
  });

  test('the generate button asks the server and appends what came back', async () => {
    await open({ [`POST ${BASE}/generate`]: () => json({ added: generated }) });
    fireEvent.click(screen.getByRole('button', { name: /Avtomatik yaratish/ }));
    expect(await screen.findByText('property')).toBeInTheDocument();
    expect(screen.getByText('значение')).toBeInTheDocument();
    expect(sent('POST', `${BASE}/generate`)).toHaveLength(1);
    expect(screen.getByText('2 ta atama qo\'shildi')).toBeInTheDocument();
  });

  test('says so when the AI found nothing new', async () => {
    await open({ [`POST ${BASE}/generate`]: () => json({ added: [] }) });
    fireEvent.click(screen.getByRole('button', { name: /Avtomatik yaratish/ }));
    expect(await screen.findByText(/Yangi atama topilmadi/)).toBeInTheDocument();
  });

  test('shows the server message when generation fails', async () => {
    await open({ [`POST ${BASE}/generate`]: () => json(
      { success: false, error: { code: 502, message: 'AI hozircha ishlamayapti, keyinroq urinib ko\'ring' } }, false, 502) });
    fireEvent.click(screen.getByRole('button', { name: /Avtomatik yaratish/ }));
    expect(await screen.findByText(/AI hozircha ishlamayapti/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Avtomatik yaratish/ })).not.toBeDisabled();
  });

  test('a network failure during generation is reported, not swallowed', async () => {
    await open({ [`POST ${BASE}/generate`]: () => Promise.reject(new Error('offline')) });
    fireEvent.click(screen.getByRole('button', { name: /Avtomatik yaratish/ }));
    expect(await screen.findByText(/Yaratib bo'lmadi/)).toBeInTheDocument();
  });

  test('a new word is sent with its Russian definition', async () => {
    await open({ [`POST ${BASE}`]: () => json({ id: 5, word: 'margin', definition: 'chekka', definition_ru: 'отступ', source: 'manual', order: 1 }) });
    fireEvent.change(screen.getByPlaceholderText("Atama (so'z)"), { target: { value: 'margin' } });
    fireEvent.change(screen.getByPlaceholderText("Ta'rifi (o'zbek tilida)"), { target: { value: 'chekka' } });
    fireEvent.change(screen.getByPlaceholderText('Определение (на русском)'), { target: { value: 'отступ' } });
    fireEvent.click(screen.getByRole('button', { name: /Qo'sh/ }));
    expect(await screen.findByText('margin')).toBeInTheDocument();
    expect(sent('POST', BASE)[0].body).toEqual({ word: 'margin', definition: 'chekka', definition_ru: 'отступ', order: 1 });
  });

  test('editing sends the Russian definition and keeps the row order', async () => {
    await open({ [`PUT ${BASE}/1`]: () => json({ ...existing[0], definition_ru: 'новое' }) });
    fireEvent.click(screen.getByRole('button', { name: '✎' }));
    fireEvent.change(screen.getByDisplayValue('селектор'), { target: { value: 'новое' } });
    fireEvent.click(screen.getByRole('button', { name: 'Saqlash' }));
    expect(await screen.findByText('новое')).toBeInTheDocument();
    expect(sent('PUT', `${BASE}/1`)[0].body).toEqual({ word: 'selector', definition: 'tanlagich', definition_ru: 'новое', order: 4 });
  });
});
