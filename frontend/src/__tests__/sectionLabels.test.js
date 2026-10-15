import { isGenericLabel, sectionLabel } from '../utils/sectionLabels';

test('generic labels follow the viewer language, whichever language they were saved in', () => {
  expect(sectionLabel('Текст', false)).toBe('Matn');
  expect(sectionLabel('Код', false)).toBe('Kod');
  expect(sectionLabel('Видео', false)).toBe('Video');
  expect(sectionLabel('Упражнения', false)).toBe('Mashqlar');
  expect(sectionLabel('Matn', true)).toBe('Текст');
  expect(sectionLabel('Mashqlar', true)).toBe('Упражнения');
  expect(sectionLabel('Nazariya', true)).toBe('Теория');
  expect(sectionLabel('Kod namunasi', true)).toBe('Пример кода');
});

test('matching ignores case and surrounding spaces', () => {
  expect(sectionLabel('  КОД ', false)).toBe('Kod');
  expect(isGenericLabel(' mashqlar')).toBe(true);
});

test('a teacher-written label is shown exactly as written', () => {
  expect(sectionLabel('Loyiha: Rangli sahifa', true)).toBe('Loyiha: Rangli sahifa');
  expect(isGenericLabel('Loyiha: Rangli sahifa')).toBe(false);
});

test('empty or missing labels stay empty (the caller supplies a default)', () => {
  expect(sectionLabel('', false)).toBe('');
  expect(sectionLabel(undefined, true)).toBe('');
  expect(isGenericLabel(undefined)).toBe(false);
});
