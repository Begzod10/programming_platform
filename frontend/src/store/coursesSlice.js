import { createSlice } from '@reduxjs/toolkit';

/* ─── Initial shared data ─── */
const initialCourses = [
  {
    id: 1,
    title: 'Основы React',
    description: 'Изучите основы React с нуля и создайте свои первые компоненты',
    image: 'https://www.fullstackpython.com/img/logos/react.png',
    studentsCount: 45,
    lessons: [
      {
        id: 101,
        title: 'Введение в React',
        chapter: 'Basic',
        image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/React_Logo_SVG.svg/langfr-250px-React_Logo_SVG.svg.png',
        completed: false,
        sections: [
          { id: 1, type: 'text',  label: 'Что такое React?', html: '<p>React — это библиотека JavaScript для построения пользовательских интерфейсов.</p>' },
          { id: 2, type: 'video', label: 'Видео урок', videoUrl: 'https://youtu.be/GeulXZP_kZ8' },
        ],
      },
      {
        id: 102,
        title: 'Компоненты и Props',
        chapter: 'Basic',
        image: 'https://miro.medium.com/1*NJSv6DGoKTloI8d8im98zg.png',
        completed: false,
        sections: [
          { id: 3, type: 'text', label: 'Компоненты', html: '<p>Компоненты позволяют разбить UI на независимые части.</p>' },
          { id: 4, type: 'code', label: 'Пример', lang: 'jsx', code: 'function Hello({ name }) {\n  return <h1>Hello, {name}!</h1>;\n}' },
        ],
      },
      {
        id: 103,
        title: 'Хуки и State',
        chapter: 'Advanced',
        image: '',
        completed: false,
        sections: [],
      },
    ],
  },
  {
    id: 2,
    title: 'JavaScript Продвинутый',
    description: 'Углубленное изучение JavaScript: замыкания, прототипы, асинхронность',
    image: 'https://itproger.com/img/news/1545489100.jpg',
    studentsCount: 32,
    lessons: [],
  },
];

const initialChapters = ['Basic', 'Advanced', 'Test'];

/* ─── Slice ─── */
const coursesSlice = createSlice({
  name: 'courses',
  initialState: {
    courses:  initialCourses,
    chapters: initialChapters,
  },
  reducers: {

    /* ── Course CRUD ── */
    addCourse(state, action) {
      state.courses.push({
        id: Date.now(),
        studentsCount: 0,
        lessons: [],
        ...action.payload,
      });
    },

    updateCourse(state, action) {
      const { id, ...changes } = action.payload;
      const course = state.courses.find(c => c.id === id);
      if (course) Object.assign(course, changes);
    },

    deleteCourse(state, action) {
      state.courses = state.courses.filter(c => c.id !== action.payload);
    },

    /* ── Lesson CRUD ── */
    addLesson(state, action) {
      const { courseId, lesson } = action.payload;
      const course = state.courses.find(c => c.id === courseId);
      if (course) {
        course.lessons.push({ id: Date.now(), completed: false, ...lesson });
      }
    },

    updateLesson(state, action) {
      const { courseId, lessonId, changes } = action.payload;
      const course = state.courses.find(c => c.id === courseId);
      if (course) {
        const lesson = course.lessons.find(l => l.id === lessonId);
        if (lesson) Object.assign(lesson, changes);
      }
    },

    deleteLesson(state, action) {
      const { courseId, lessonId } = action.payload;
      const course = state.courses.find(c => c.id === courseId);
      if (course) {
        course.lessons = course.lessons.filter(l => l.id !== lessonId);
      }
    },

    /* ── Student: mark lesson complete ── */
    markLessonComplete(state, action) {
      const { courseId, lessonId } = action.payload;
      const course = state.courses.find(c => c.id === courseId);
      if (course) {
        const lesson = course.lessons.find(l => l.id === lessonId);
        if (lesson) lesson.completed = true;
      }
    },

    /* ── Chapters ── */
    setChapters(state, action) {
      state.chapters = action.payload;
    },

    addChapter(state, action) {
      if (!state.chapters.includes(action.payload)) {
        state.chapters.push(action.payload);
      }
    },

    deleteChapter(state, action) {
      state.chapters = state.chapters.filter(ch => ch !== action.payload);
    },
  },
});

export const {
  addCourse,
  updateCourse,
  deleteCourse,
  addLesson,
  updateLesson,
  deleteLesson,
  markLessonComplete,
  setChapters,
  addChapter,
  deleteChapter,
} = coursesSlice.actions;

/* ─── Selectors ─── */
export const selectCourses  = (state) => state.courses.courses;
export const selectChapters = (state) => state.courses.chapters;
export const selectCourseById = (id) => (state) =>
  state.courses.courses.find(c => c.id === id);

export default coursesSlice.reducer;