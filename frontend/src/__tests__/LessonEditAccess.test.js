import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import CourseModal from '../views/teacher/courses/CourseModal/CourseModal';
import { canEditLessons } from '../views/teacher/courses/lessonEditAccess';

const course = {
  id: 1, title: 'Python', description: 'd', image: '', studentsCount: 3,
  lessons: [
    { id: 11, title: 'Dars 1', is_published: true, sections: [] },
    { id: 12, title: 'Dars 2', is_published: false, sections: [] },
  ],
};
const noop = () => {};
const renderModal = (canEdit) => render(
  <CourseModal course={course} onBack={noop} onOpenLesson={noop} onAddLesson={noop}
               onToggleLessonPublish={noop} onReorderLessons={noop} canEdit={canEdit} />,
);

describe('who may change lessons', () => {
  test('only the rimefara_teach teacher', () => {
    expect(canEditLessons({ username: 'rimefara_teach' })).toBe(true);
    expect(canEditLessons({ username: 'someone_else' })).toBe(false);
    expect(canEditLessons({ username: 'Rimefara_teach' })).toBe(false);
    expect(canEditLessons(null)).toBe(false);
    expect(canEditLessons(undefined)).toBe(false);
  });
});

describe('course lessons page', () => {
  test('the editing teacher sees add, publish toggle and drag handles', () => {
    const { container } = renderModal(true);
    expect(screen.getByText(/Добавить урок/)).toBeInTheDocument();
    expect(container.querySelectorAll('button.cdp-lesson-publish-btn')).toHaveLength(2);
    expect(container.querySelectorAll('.cdp-drag-handle')).toHaveLength(2);
  });

  test('any other teacher sees the lessons read-only', () => {
    const { container } = renderModal(false);
    expect(screen.queryByText(/Добавить урок/)).toBeNull();
    expect(container.querySelectorAll('button.cdp-lesson-publish-btn')).toHaveLength(0);
    expect(container.querySelectorAll('.cdp-drag-handle')).toHaveLength(0);
    expect(screen.getByText('Dars 1')).toBeInTheDocument();              // still readable
    expect(screen.getAllByText(/Опубликован|Черновик/)).toHaveLength(2);   // status still shown, not clickable
  });
});
