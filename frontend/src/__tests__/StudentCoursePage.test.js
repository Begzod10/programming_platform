// Mock external dependencies so Jest can load the module without real imports.
// jest.mock() calls are hoisted by babel-jest before any imports are resolved.
jest.mock('lucide-react', () => ({ Lock: () => null }));

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import StudentCoursePage from '../views/student/courses/CoursePage/StudentCoursePage';

// Regression test for: chapter groups were keyed by their array index
// (`key={gi}`) instead of a stable identity. When lessons reorder such that
// chapters change position, index-based keys cause React to reuse each
// ChapterBlock's local `open` (expanded/collapsed) state for whatever
// chapter now occupies that slot, silently expanding/collapsing the wrong
// chapter. Keying by the chapter's own identity (`g.key`, derived from the
// lesson's `chapter` field) keeps each chapter's UI state attached to that
// chapter, regardless of position.
describe('StudentCoursePage chapter list keys', () => {
    const lessonA1 = {
        id: 1,
        chapter: 'Chapter A',
        title: 'A1',
        completed: false,
        is_published: true,
        sections: [],
    };
    const lessonB1 = {
        id: 2,
        chapter: 'Chapter B',
        title: 'B1',
        completed: false,
        is_published: true,
        sections: [],
    };

    const noop = () => {};

    test('preserves each chapter\'s collapsed/expanded state when chapters reorder', () => {
        const { rerender } = render(
            <StudentCoursePage
                course={{ lessons: [lessonA1, lessonB1] }}
                onBack={noop}
                onOpenLesson={noop}
            />
        );

        // Both chapters start open — both lesson titles are visible.
        expect(screen.getByText('A1')).toBeInTheDocument();
        expect(screen.getByText('B1')).toBeInTheDocument();

        // Collapse "Chapter A" only.
        fireEvent.click(screen.getByText('Chapter A').closest('button'));
        expect(screen.queryByText('A1')).not.toBeInTheDocument();
        expect(screen.getByText('B1')).toBeInTheDocument();

        // Simulate the chapters reordering (Chapter B's lesson now appears
        // first in the underlying lesson list, so its group is built first).
        rerender(
            <StudentCoursePage
                course={{ lessons: [lessonB1, lessonA1] }}
                onBack={noop}
                onOpenLesson={noop}
            />
        );

        // Chapter A must still be collapsed (state follows the chapter, not
        // the slot), and Chapter B must still be open.
        expect(screen.queryByText('A1')).not.toBeInTheDocument();
        expect(screen.getByText('B1')).toBeInTheDocument();
    });
});
