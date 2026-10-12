import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import UnmetLessons from '../components/teamprojects/UnmetLessons';

const lessons = ['JavaScript: fetch va REST API', 'Flask: Parol hashing'];

test('teacher sees a warning with the missing lessons', () => {
  render(<UnmetLessons lessons={lessons} ru={false} audience="teacher" />);
  expect(screen.getByText(/hali o'rganmagan/)).toBeInTheDocument();
  expect(screen.getByText('Flask: Parol hashing')).toBeInTheDocument();
});

test('student sees a gentler hint, in russian too', () => {
  const { rerender } = render(<UnmetLessons lessons={lessons} ru={false} audience="student" />);
  expect(screen.getByText(/Avval shu darslarni tugatish foydali/)).toBeInTheDocument();
  rerender(<UnmetLessons lessons={lessons} ru audience="student" />);
  expect(screen.getByText(/Полезно сначала пройти эти уроки/)).toBeInTheDocument();
});

test('renders nothing when nothing is missing (or for older teams)', () => {
  expect(render(<UnmetLessons lessons={[]} ru={false} audience="student" />).container).toBeEmptyDOMElement();
  expect(render(<UnmetLessons lessons={undefined} ru={false} audience="teacher" />).container).toBeEmptyDOMElement();
});
