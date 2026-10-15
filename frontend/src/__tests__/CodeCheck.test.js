jest.mock('lucide-react', () => new Proxy({ __esModule: true }, {
    get: (t, p) => (p in t || typeof p === 'symbol' ? t[p] : () => null),
}));

const mockRequest = jest.fn();
const mockNavigate = jest.fn();
jest.mock('../api/search/base', () => ({
    API_URL: 'http://test/api/',
    headers: () => ({}),
    useHttp: () => ({ request: mockRequest }),
}));
jest.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
    useParams: () => ({ id: '7' }),
}), { virtual: true });

import React from 'react';
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react';
import CodeCheck from '../views/student/codecheck/CodeCheck';
import CodeCheckBanner from '../views/student/codecheck/CodeCheckBanner';

const QUIZ = {
    id: 7, seconds_per_question: 30, total_questions: 3,
    questions: [
        { index: 0, q: 'Birinchi savol?', options: ['a0', 'a1', 'a2', 'a3'] },
        { index: 1, q: 'Ikkinchi savol?', options: ['b0', 'b1', 'b2', 'b3'] },
        { index: 2, q: 'Uchinchi savol?', options: ['c0', 'c1', 'c2', 'c3'] },
    ],
};

beforeEach(() => {
    jest.useFakeTimers();
    localStorage.setItem('lang', 'uz');
    mockRequest.mockReset(); mockNavigate.mockReset();
    mockRequest.mockImplementation((url) => Promise.resolve(url.includes('/start') ? QUIZ : { status: 'passed', passed: true }));
});
afterEach(() => { jest.useRealTimers(); });

const startQuiz = async () => {
    render(<CodeCheck />);
    fireEvent.click(screen.getByRole('button', { name: 'Boshlash' }));
    await screen.findByText('Birinchi savol?');
};
const submitCall = () => mockRequest.mock.calls.find(([u]) => u.includes('/submit'));

describe('CodeCheck', () => {
    test('nothing is asked until the student presses start, and "later" leaves', () => {
        render(<CodeCheck />);
        expect(mockRequest).not.toHaveBeenCalled();
        fireEvent.click(screen.getByRole('button', { name: 'Keyinroq' }));
        expect(mockNavigate).toHaveBeenCalledWith('/student/projects');
    });

    test('starts in the student\'s language and shows one question at a time with a 30 s timer', async () => {
        await startQuiz();
        expect(mockRequest.mock.calls[0][0]).toBe('http://test/api/v1/code-checks/7/start?lang=uz');
        expect(screen.getByLabelText('timer')).toHaveTextContent('30s');
        expect(screen.getByText('1 / 3')).toBeInTheDocument();
        expect(screen.queryByText('Ikkinchi savol?')).not.toBeInTheDocument();
    });

    test('answers advance the quiz and the last one is submitted with the answers and the timings', async () => {
        await startQuiz();
        fireEvent.click(screen.getByText('a1'));
        fireEvent.click(await screen.findByText('b0'));
        fireEvent.click(await screen.findByText('c3'));
        await waitFor(() => expect(submitCall()).toBeTruthy());
        const body = JSON.parse(submitCall()[2]);
        expect(body.answers).toEqual([1, 0, 3]);
        expect(body.times_ms).toHaveLength(3);
        expect(body.blur_count).toBe(0);
        expect(await screen.findByText("Tekshiruv o'tildi")).toBeInTheDocument();
    });

    test('a question left unanswered for 30 seconds counts as unanswered and the quiz moves on', async () => {
        await startQuiz();
        for (let i = 0; i < 30; i++) await act(async () => { jest.advanceTimersByTime(1000); });
        expect(await screen.findByText('Ikkinchi savol?')).toBeInTheDocument();
        fireEvent.click(screen.getByText('b2'));
        fireEvent.click(await screen.findByText('c1'));
        await waitFor(() => expect(submitCall()).toBeTruthy());
        expect(JSON.parse(submitCall()[2]).answers).toEqual([null, 2, 1]);
    });

    test('leaving the tab is counted (once per switch) and sent, but never mentioned on screen', async () => {
        await startQuiz();
        const hide = () => {
            Object.defineProperty(document, 'hidden', { configurable: true, value: true });
            document.dispatchEvent(new Event('visibilitychange'));
            window.dispatchEvent(new Event('blur'));          // fires together with it: one switch
        };
        hide();
        await act(async () => { jest.advanceTimersByTime(1500); });
        hide();
        Object.defineProperty(document, 'hidden', { configurable: true, value: false });
        fireEvent.click(screen.getByText('a0'));
        fireEvent.click(await screen.findByText('b0'));
        fireEvent.click(await screen.findByText('c0'));
        await waitFor(() => expect(submitCall()).toBeTruthy());
        expect(JSON.parse(submitCall()[2]).blur_count).toBe(2);
        expect(screen.queryByText(/oyna|tab|вклад/i)).not.toBeInTheDocument();
    });

    test('a result that needs the teacher is worded neutrally', async () => {
        mockRequest.mockImplementation((url) => Promise.resolve(url.includes('/start') ? QUIZ : { status: 'suspicious', passed: false }));
        await startQuiz();
        fireEvent.click(screen.getByText('a0'));
        fireEvent.click(await screen.findByText('b0'));
        fireEvent.click(await screen.findByText('c0'));
        expect(await screen.findByText('Javoblar qabul qilindi')).toBeInTheDocument();
        expect(screen.getByText(/o'qituvchiga yuborildi/)).toBeInTheDocument();
    });

    test('shows the server message when the quiz cannot start', async () => {
        mockRequest.mockRejectedValue({ response: { data: { error: { message: 'Tekshiruv muddati o\'tgan.' } } } });
        render(<CodeCheck />);
        fireEvent.click(screen.getByRole('button', { name: 'Boshlash' }));
        expect(await screen.findByRole('alert')).toHaveTextContent("Tekshiruv muddati o'tgan.");
    });

    test('Russian text for a Russian student', async () => {
        localStorage.setItem('lang', 'ru');
        render(<CodeCheck />);
        expect(screen.getByRole('button', { name: 'Начать' })).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: 'Начать' }));
        expect(mockRequest.mock.calls[0][0]).toContain('lang=ru');
    });
});

describe('CodeCheckBanner', () => {
    test('shows nothing without a pending quiz and a way in when there is one', async () => {
        mockRequest.mockResolvedValueOnce([]);
        const { container, rerender } = render(<CodeCheckBanner />);
        await act(async () => {});
        expect(container).toBeEmptyDOMElement();

        mockRequest.mockResolvedValueOnce([{ id: 9, project_title: 'Mening loyiham', total_questions: 3 }]);
        rerender(<div><CodeCheckBanner key="again" /></div>);
        const go = await screen.findByRole('button', { name: "O'tish" });
        expect(screen.getByText(/Mening loyiham/)).toBeInTheDocument();
        fireEvent.click(go);
        expect(mockNavigate).toHaveBeenCalledWith('/student/code-check/9');
    });
});
