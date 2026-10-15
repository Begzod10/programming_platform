// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// react-router-dom v7 ships ESM only, which CRA's Jest (CommonJS) can't
// resolve, so any test that renders a component importing it failed with
// "Cannot find module 'react-router-dom'". Stub it for every test file; a
// test that needs different behaviour can call jest.mock(...) itself.
jest.mock('react-router-dom', () => {
    const React = require('react');
    const passthrough = ({ children }) => React.createElement(React.Fragment, null, children);
    const anchor = ({ to, children, ...rest }) =>
        React.createElement('a', { href: typeof to === 'string' ? to : '#', ...rest }, children);
    return {
        useNavigate: () => jest.fn(),
        useLocation: () => ({ pathname: '/', search: '', hash: '', state: null }),
        useParams: () => ({}),
        useSearchParams: () => [new URLSearchParams(), jest.fn()],
        Link: anchor,
        NavLink: anchor,
        Navigate: () => null,
        Outlet: () => null,
        BrowserRouter: passthrough,
        MemoryRouter: passthrough,
        Routes: passthrough,
        Route: () => null,
    };
}, { virtual: true });

// The shared student header (AppHeader) needs the auth context, a router, a
// dozen icons and its own network polling. Page tests are about the page —
// and several assert exact call order on the mocked request() — so they get an
// empty header. AppHeader has its own test (AppHeader.test.js), which mocks
// this stub away and exercises the real component.
jest.mock('./components/appheader/AppHeader', () => ({
    __esModule: true,
    default: () => null,
}));
