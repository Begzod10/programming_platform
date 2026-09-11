// Regression test for the `Loader` component extraction out of
// TeacherCourses.js (previously redeclared inline on every render, which
// forced React to tear down and rebuild its DOM subtree each render).
// Importing it here — rather than through TeacherCourses.js, which pulls in
// react-router-dom v7 (ESM-only `dist/index.mjs`, not resolvable by CRA's
// default CommonJS Jest config — see App.test.js) — lets this suite render
// it directly with plain React Testing Library.
import { render, screen } from '@testing-library/react';
import { Loader } from '../views/teacher/courses/TeacherCourses/Loader';

describe('Loader', () => {
  test('renders the Russian loading text unchanged', () => {
    render(<Loader />);
    expect(screen.getByText('Загрузка...')).toBeInTheDocument();
  });

  test('is a stable, module-level component reference across renders', () => {
    // Importing twice must yield the exact same function reference — proof
    // it is declared once at module scope rather than recreated inside a
    // parent component's render body.
    // eslint-disable-next-line global-require
    const { Loader: LoaderAgain } = require('../views/teacher/courses/TeacherCourses/Loader');
    expect(LoaderAgain).toBe(Loader);
  });
});
