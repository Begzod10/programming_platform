jest.mock('lucide-react', () => new Proxy({ __esModule: true }, {
    get: (t, p) => (p in t || typeof p === 'symbol' ? t[p] : () => null),
}));

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskCard, deadlineInfo, initials } from '../views/teacher/teamprojects/TeacherTaskCard';

const DAY = 86400000;
const NOW = new Date('2026-10-06T10:00:00Z').getTime();

const members = [
    { student_id: 1, full_name: 'Aziz Karimov' },
    { student_id: 2, full_name: 'Dilnoza Rahimova' },
    { student_id: 3, full_name: 'Sardor Aliyev' },
];

const baseTask = {
    id: 10, order: 1, status: 'assigned', required_level: 'Advanced', estimated_hours: 8,
    title: 'Backend API', title_ru: 'Бэкенд API',
    description: 'Flask yordamida REST API yarating.', description_ru: 'Создайте REST API на Flask.',
    acceptance_criteria: ['Birinchi mezon', 'Ikkinchi mezon', 'Uchinchi mezon', "To'rtinchi mezon"],
    acceptance_criteria_ru: [],
    depends_on: [0], deadline_at: new Date(NOW + 5 * DAY).toISOString(),
    assigned_student_id: 1, assigned_student_name: 'Aziz Karimov',
    submission_url: null, ai_feedback: null, ai_score: null, lead_comment: null,
};
const allTasks = [{ ...baseTask, id: 9, order: 0, title: 'Avvalgi vazifa' }, baseTask];

const renderCard = (task = baseTask, handlers = {}) => render(
    <TaskCard
        task={task} members={members} allTasks={allTasks} lang="uz"
        onReassign={handlers.onReassign || jest.fn()}
        onDelete={handlers.onDelete || jest.fn()}
        onReview={handlers.onReview || jest.fn()}
    />,
);

describe('deadlineInfo', () => {
    test('counts days left, flags the last two days and overdue work', () => {
        expect(deadlineInfo(new Date(NOW + 5 * DAY).toISOString(), 'assigned', NOW))
            .toEqual({ text: '5 kun qoldi', tone: 'ok' });
        expect(deadlineInfo(new Date(NOW + 2 * DAY).toISOString(), 'assigned', NOW).tone).toBe('soon');
        expect(deadlineInfo(new Date(NOW + 3600000).toISOString(), 'assigned', NOW))
            .toEqual({ text: '1 kun qoldi', tone: 'soon' });
        expect(deadlineInfo(new Date(NOW - DAY).toISOString(), 'assigned', NOW))
            .toEqual({ text: "Muddati o'tgan", tone: 'late' });
    });

    test('says nothing for approved work or a missing/invalid deadline', () => {
        expect(deadlineInfo(new Date(NOW - DAY).toISOString(), 'approved', NOW)).toBeNull();
        expect(deadlineInfo(null, 'assigned', NOW)).toBeNull();
        expect(deadlineInfo('not a date', 'assigned', NOW)).toBeNull();
    });
});

describe('initials', () => {
    test('first + last name initials, tolerant of odd input', () => {
        expect(initials('Aziz Karimov')).toBe('AK');
        expect(initials('  Madina  ')).toBe('M');
        expect(initials('Muhammad Ali Saparov')).toBe('MS');
        expect(initials('')).toBe('?');
        expect(initials(null)).toBe('?');
    });
});

describe('TaskCard', () => {
    test('shows the title, assignee, level, hours and the dependency', () => {
        renderCard();
        expect(screen.getByText('Backend API')).toBeInTheDocument();
        expect(screen.getByText('Aziz Karimov')).toBeInTheDocument();
        expect(screen.getByText("Ilg'or")).toBeInTheDocument();
        expect(screen.getByText(/8 soat/)).toBeInTheDocument();
        expect(screen.getByText(/#1 dan keyin/)).toBeInTheDocument();
    });

    test('lists the first two criteria and counts the rest', () => {
        renderCard();
        expect(screen.getByText('Birinchi mezon')).toBeInTheDocument();
        expect(screen.getByText('Ikkinchi mezon')).toBeInTheDocument();
        expect(screen.queryByText('Uchinchi mezon')).not.toBeInTheDocument();
        expect(screen.getByText('+2 ta mezon')).toBeInTheDocument();
    });

    test('a not-yet-submitted task has no review buttons', () => {
        renderCard();
        expect(screen.queryByRole('button', { name: /Tasdiqlash/ })).not.toBeInTheDocument();
    });

    test('a submitted task can be approved or sent back', () => {
        const onReview = jest.fn();
        renderCard({ ...baseTask, status: 'submitted' }, { onReview });
        fireEvent.click(screen.getByRole('button', { name: /Tasdiqlash/ }));
        fireEvent.click(screen.getByRole('button', { name: /O'zgartirish so'rash/ }));
        expect(onReview).toHaveBeenNthCalledWith(1, 10, 'approve');
        expect(onReview).toHaveBeenNthCalledWith(2, 10, 'request_changes');
    });

    test('an overdue task shows the red deadline chip', () => {
        renderCard({ ...baseTask, deadline_at: new Date(Date.now() - DAY).toISOString() });
        expect(screen.getByText("Muddati o'tgan")).toBeInTheDocument();
    });

    test('reassign and delete live in the "..." menu', () => {
        const onReassign = jest.fn();
        const onDelete = jest.fn();
        renderCard(baseTask, { onReassign, onDelete });

        expect(screen.queryByText(/Vazifani o'chirish/)).not.toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: 'Boshqa amallar' }));

        // current assignee is not offered
        const select = screen.getByLabelText("A'zoni tanlang");
        expect(Array.from(select.options).map(o => o.textContent)).toEqual(
            ["A'zoni tanlang…", 'Dilnoza Rahimova', 'Sardor Aliyev']);

        expect(screen.getByRole('button', { name: 'Tayinlash' })).toBeDisabled();
        fireEvent.change(select, { target: { value: '2' } });
        fireEvent.click(screen.getByRole('button', { name: 'Tayinlash' }));
        expect(onReassign).toHaveBeenCalledWith(10, 2);
        expect(screen.queryByText(/Vazifani o'chirish/)).not.toBeInTheDocument();   // menu closed

        fireEvent.click(screen.getByRole('button', { name: 'Boshqa amallar' }));
        fireEvent.click(screen.getByText(/Vazifani o'chirish/));
        expect(onDelete).toHaveBeenCalledWith(10);
    });

    test('the menu closes on Escape and on an outside click', () => {
        renderCard();
        fireEvent.click(screen.getByRole('button', { name: 'Boshqa amallar' }));
        expect(screen.getByText(/Vazifani o'chirish/)).toBeInTheDocument();
        fireEvent.keyDown(document, { key: 'Escape' });
        expect(screen.queryByText(/Vazifani o'chirish/)).not.toBeInTheDocument();

        fireEvent.click(screen.getByRole('button', { name: 'Boshqa amallar' }));
        fireEvent.mouseDown(document.body);
        expect(screen.queryByText(/Vazifani o'chirish/)).not.toBeInTheDocument();
    });

    test('opens the details modal', () => {
        renderCard();
        fireEvent.click(screen.getByRole('button', { name: /Batafsil/ }));
        expect(screen.getByText('Qabul mezonlari')).toBeInTheDocument();
        expect(screen.getByText("To'rtinchi mezon")).toBeInTheDocument();   // the full list, not just two
    });

    test('shows Russian text when the language is ru', () => {
        render(
            <TaskCard
                task={baseTask} members={members} allTasks={allTasks} lang="ru"
                onReassign={jest.fn()} onDelete={jest.fn()} onReview={jest.fn()}
            />,
        );
        expect(screen.getByText('Бэкенд API')).toBeInTheDocument();
        expect(screen.getByText('Создайте REST API на Flask.')).toBeInTheDocument();
    });
});
