import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import FormatWarnings from '../components/formatwarnings/FormatWarnings';

const warnings = [
  { file: 'OK.html', message: "«OK.html» fayli .html deb nomlangan, lekin ichida Python kodi bor. Fayl kengaytmasini .py qilib o'zgartiring.",
    message_ru: 'Файл «OK.html» назван .html, но внутри код Python. Измените расширение файла на .py.' },
];

test('shows each warning in Uzbek and says the upload was accepted', () => {
  render(<FormatWarnings warnings={warnings} ru={false} />);
  expect(screen.getByRole('status')).toHaveTextContent('Fayl formati');
  expect(screen.getByText(/Python kodi bor/)).toBeInTheDocument();
  expect(screen.getByText(/Loyiha qabul qilindi/)).toBeInTheDocument();
});

test('shows the Russian text for Russian users', () => {
  render(<FormatWarnings warnings={warnings} ru />);
  expect(screen.getByText(/внутри код Python/)).toBeInTheDocument();
  expect(screen.getByText(/Проект принят/)).toBeInTheDocument();
});

test('renders nothing without warnings', () => {
  const { container, rerender } = render(<FormatWarnings warnings={[]} ru={false} />);
  expect(container).toBeEmptyDOMElement();
  rerender(<FormatWarnings warnings={undefined} ru={false} />);
  expect(container).toBeEmptyDOMElement();
});
