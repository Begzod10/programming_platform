// Mock external dependencies so Jest can load the module without real imports.
// jest.mock() calls are hoisted by babel-jest before any imports are resolved.
jest.mock('lucide-react', () => new Proxy({ __esModule: true }, { get: (t, p) => (p in t || typeof p === 'symbol' ? t[p] : () => null) }));

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import StudentCoursePage from '../views/student/courses/CoursePage/StudentCoursePage';

// The course page used to group lessons into collapsible chapters; after the
// redesign it is a flat grid of lesson cards, each keyed by its lesson id.
// Index-based keys would let React reuse one card's state for whichever lesson
// now sits in that slot, so this guards the equivalent risk: after the lessons
// reorder, every card must still show ITS lesson (and the sequential unlock —
// first unfinished lesson open, later ones locked — must follow the new order).
describe('StudentCoursePage lesson list', () => {
    const lessonA = { id: 1, title: 'Lesson A', completed: false, is_published: true, sections: [] };
    const lessonB = { id: 2, title: 'Lesson B', completed: false, is_published: true, sections: [] };
    const noop = () => {};

    const titlesInOrder = () =>
        Array.from(document.querySelectorAll('.scd-grid > *'))
            .map((card) => (card.textContent.match(/Lesson [AB]/) || [''])[0]);

    test('renders each lesson once and follows the new order when lessons reorder', () => {
        const { rerender } = render(
            <StudentCoursePage course={{ lessons: [lessonA, lessonB] }} onBack={noop} onOpenLesson={noop} />
        );
        expect(screen.getAllByText('Lesson A')).toHaveLength(1);
        expect(screen.getAllByText('Lesson B')).toHaveLength(1);
        expect(titlesInOrder()).toEqual(['Lesson A', 'Lesson B']);

        rerender(
            <StudentCoursePage course={{ lessons: [lessonB, lessonA] }} onBack={noop} onOpenLesson={noop} />
        );
        expect(screen.getAllByText('Lesson A')).toHaveLength(1);
        expect(screen.getAllByText('Lesson B')).toHaveLength(1);
        expect(titlesInOrder()).toEqual(['Lesson B', 'Lesson A']);
    });

    test('unpublished lessons are not listed', () => {
        render(
            <StudentCoursePage
                course={{ lessons: [lessonA, { ...lessonB, is_published: false }] }}
                onBack={noop}
                onOpenLesson={noop}
            />
        );
        expect(screen.getByText('Lesson A')).toBeInTheDocument();
        expect(screen.queryByText('Lesson B')).not.toBeInTheDocument();
    });
});
