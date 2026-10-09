jest.mock('lucide-react', () => new Proxy({ __esModule: true }, {
    get: (t, p) => (p in t || typeof p === 'symbol' ? t[p] : () => null),
}));

const mockRequest = jest.fn();
jest.mock('../api/search/base', () => ({
    API_URL: 'http://test/api/',
    headers: () => ({}),
    useHttp: () => ({ request: mockRequest }),
}));

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TeacherCodeChecks from '../views/teacher/codechecks/TeacherCodeChecks';

const ROW = {
    id: 5, status: 'suspicious', reason: 'pace', needs_teacher: true,
    student: { id: 2, username: 'ali_dev', full_name: 'Ali Valiyev' },
    project: { id: 40, title: 'Capstone', points_earned: 95, grade: 'A' },
    code_lines: 300, pace: 100, gap_minutes: 3, correct: 3, total: 3, blur_count: 4, duration_seconds: 41,
    created_at: '2026-10-09T10:00:00Z', finished_at: '2026-10-09T10:05:00Z', resolution: null, teacher_note: null,
    questions: [{ q: 'append() nima qiladi?', options: ['Oxiriga qo\'shadi', 'Boshiga', 'O\'chiradi', 'Saralaydi'], correct: 0, answer: 0 }],
};

beforeEach(() => {
    mockRequest.mockReset();
    mockRequest.mockImplementation((url, method) => Promise.resolve(method === 'POST' ? { ...ROW, resolution: 'dismissed' } : [ROW]));
});

test('lists what needs the teacher, with the facts they need for the talk', async () => {
    render(<TeacherCodeChecks />);
    expect(await screen.findByText(/Ali Valiyev/)).toBeInTheDocument();
    expect(screen.getByText("To'g'ri, lekin boshqa oynaga o'tgan")).toBeInTheDocument();
    expect(screen.getByText('Juda tez topshirilgan')).toBeInTheDocument();
    expect(screen.getByText(/300 qator, oldingi loyihadan 3 daq\. keyin \(100 qator\/daq\)/)).toBeInTheDocument();
    expect(screen.getByText(/Boshqa oynaga o'tishlar: 4/)).toBeInTheDocument();
    expect(mockRequest.mock.calls[0][0]).toBe('http://test/api/v1/teacher/code-checks?all=false');
});

test('the questions, the right answer and the student\'s choice are available', async () => {
    render(<TeacherCodeChecks />);
    fireEvent.click(await screen.findByText(/Savollar va javoblar/));
    expect(screen.getByText(/append\(\) nima qiladi/)).toBeInTheDocument();
    expect(screen.getByText(/Oxiriga qo'shadi ✓ ← javobi/)).toBeInTheDocument();
});

test('revoking points asks for confirmation first and then posts the decision with the note', async () => {
    render(<TeacherCodeChecks />);
    fireEvent.click(await screen.findByRole('button', { name: 'Ballni bekor qilish' }));
    expect(screen.getByText(/95 ball bekor qilinadi/)).toBeInTheDocument();
    expect(mockRequest.mock.calls.filter(([, m]) => m === 'POST')).toHaveLength(0);       // nothing yet
    fireEvent.change(screen.getByPlaceholderText(/Izoh/), { target: { value: 'Suhbatda tushuntira olmadi' } });
    fireEvent.click(screen.getByRole('button', { name: 'Tasdiqlash' }));
    await waitFor(() => expect(screen.queryByText(/Ali Valiyev/)).not.toBeInTheDocument());   // leaves the queue
    const post = mockRequest.mock.calls.find(([, m]) => m === 'POST');
    expect(post[0]).toBe('http://test/api/v1/teacher/code-checks/5/resolve');
    expect(JSON.parse(post[2])).toEqual({ action: 'revoke_points', note: 'Suhbatda tushuntira olmadi' });
});

test('"everything is fine" does not touch points and can be cancelled', async () => {
    render(<TeacherCodeChecks />);
    fireEvent.click(await screen.findByRole('button', { name: 'Hammasi joyida' }));
    expect(screen.getByText(/ball o'zgarmaydi/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Bekor' }));
    expect(screen.getByRole('button', { name: 'Hammasi joyida' })).toBeInTheDocument();
    expect(mockRequest.mock.calls.filter(([, m]) => m === 'POST')).toHaveLength(0);
});

test('an empty queue and a failed load are both explained', async () => {
    mockRequest.mockResolvedValueOnce([]);
    const { unmount } = render(<TeacherCodeChecks />);
    expect(await screen.findByText(/e'tibor talab qiladigan tekshiruv yo'q/)).toBeInTheDocument();
    unmount();
    mockRequest.mockRejectedValueOnce({ response: { data: { error: { message: 'Ruxsat yo\'q' } } } });
    render(<TeacherCodeChecks />);
    expect(await screen.findByRole('alert')).toHaveTextContent("Ruxsat yo'q");
});

test('a fast-but-passed project is shown softly, below the real cases', async () => {
    const low = { ...ROW, id: 6, status: 'passed', low_priority: true, blur_count: 0, correct: 3 };
    mockRequest.mockImplementation((url, method) => Promise.resolve(method === 'POST' ? low : [ROW, low]));
    render(<TeacherCodeChecks />);
    await screen.findByText("Tez topshirilgan, lekin testdan o'tgan");
    const cards = document.querySelectorAll('.tcc-card');
    expect(cards).toHaveLength(2);
    expect(cards[0]).not.toHaveClass('tcc-card--low');
    expect(cards[1]).toHaveClass('tcc-card--low');
});
