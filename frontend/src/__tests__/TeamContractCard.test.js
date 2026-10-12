import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import TeamContractCard from '../views/student/teamprojects/TeamContractCard';

const contract = {
  base_url: 'http://127.0.0.1:5000',
  auth: { header: 'Authorization: Bearer <token>', token_key: 'auth_token' },
  endpoints: [
    { id: 'auth.login', method: 'POST', path: '/api/login', auth: false, request: { username: 'str', password: 'str' }, response: { token: 'str' } },
    { id: 'bookings.list', method: 'GET', path: '/api/bookings', auth: true, request: null, response: [{ id: 'int' }] },
  ],
  files: { skeleton: ['README.md', 'backend/app.py'], backend: ['backend/routes.py'], frontend: ['frontend/index.html'] },
  run: { backend: 'cd backend && python app.py', frontend: 'backend serves frontend/' },
};

test('renders the endpoints, the token key, the files and the run commands', () => {
  render(<TeamContractCard contract={contract} ru={false} />);
  expect(screen.getByText('Jamoa shartnomasi (API)')).toBeInTheDocument();
  expect(screen.getByText('auth.login')).toBeInTheDocument();
  expect(screen.getByText('/api/bookings')).toBeInTheDocument();
  expect(screen.getByText('auth_token')).toBeInTheDocument();
  expect(screen.getByText('POST')).toBeInTheDocument();
  expect(screen.getByText(/README.md, backend\/app.py/)).toBeInTheDocument();
  expect(screen.getByText('cd backend && python app.py')).toBeInTheDocument();
});

test('russian labels', () => {
  render(<TeamContractCard contract={contract} ru />);
  expect(screen.getByText('Контракт команды (API)')).toBeInTheDocument();
  expect(screen.getByText('Запуск')).toBeInTheDocument();
});

test('renders nothing for a team without a contract (older teams)', () => {
  const { container } = render(<TeamContractCard contract={null} ru={false} />);
  expect(container).toBeEmptyDOMElement();
  const { container: c2 } = render(<TeamContractCard contract={{ base_url: 'x' }} ru={false} />);
  expect(c2).toBeEmptyDOMElement();
});
