import { createSlice } from '@reduxjs/toolkit';

const initialStudents = [
  {
    id: 1,
    name: 'Алия Сейткали',
    email: 'aliya@student.com',
    phone: '+998 70 123 4567',
    groupId: 1,
    password: 'student123',
    role: 'student',
    avatar: '👩‍💻',
    registeredAt: '2025-01-10',
    level: 'Beginner',
  },
  {
    id: 2,
    name: 'Данияр Ахметов',
    email: 'daniyar@student.com',
    phone: '+998 70 234 5678',
    groupId: 1,
    password: 'student123',
    role: 'student',
    avatar: '👨‍💻',
    registeredAt: '2025-01-12',
    level: 'Intermediate',
  },
  {
    id: 3,
    name: 'Мадина Жакупова',
    email: 'madina@student.com',
    phone: '+998 95 345 6789',
    groupId: 2,
    password: 'student123',
    role: 'student',
    avatar: '👩‍🎓',
    registeredAt: '2025-02-01',
    level: 'Advanced',
  },
];

const initialGroups = [
  {
    id: 1,
    name: 'React - Группа 1',
    description: 'Основной поток по React разработке',
    courseIds: [1],
    createdAt: '2025-01-01',
    color: '#6c5ce7',
  },
  {
    id: 2,
    name: 'Python - Группа 1',
    description: 'Начинающие Python разработчики',
    courseIds: [2],
    createdAt: '2025-02-01',
    color: '#00b894',
  },
];

const studentsSlice = createSlice({
  name: 'students',
  initialState: {
    students: initialStudents,
    groups: initialGroups,
  },
  reducers: {

    /* ── Students ── */
    addStudent(state, action) {
      state.students.push({
        id: Date.now(),
        role: 'student',
        avatar: '👤',
        registeredAt: new Date().toISOString().split('T')[0],
        level: 'Beginner',
        ...action.payload,
      });
    },

    updateStudent(state, action) {
      const { id, ...changes } = action.payload;
      const s = state.students.find(s => s.id === id);
      if (s) Object.assign(s, changes);
    },

    deleteStudent(state, action) {
      state.students = state.students.filter(s => s.id !== action.payload);
    },

    /* ── Groups ── */
    addGroup(state, action) {
      const colors = ['#6c5ce7','#00b894','#0984e3','#e17055','#fdcb6e','#fd79a8'];
      state.groups.push({
        id: Date.now(),
        courseIds: [],
        createdAt: new Date().toISOString().split('T')[0],
        color: colors[state.groups.length % colors.length],
        ...action.payload,
      });
    },

    updateGroup(state, action) {
      const { id, ...changes } = action.payload;
      const g = state.groups.find(g => g.id === id);
      if (g) Object.assign(g, changes);
    },

    deleteGroup(state, action) {
      state.groups = state.groups.filter(g => g.id !== action.payload);
      // unassign students from deleted group
      state.students.forEach(s => {
        if (s.groupId === action.payload) s.groupId = null;
      });
    },

    addStudentToGroup(state, action) {
      const { studentId, groupId } = action.payload;
      const s = state.students.find(s => s.id === studentId);
      if (s) s.groupId = groupId;
    },

    removeStudentFromGroup(state, action) {
      const { studentId } = action.payload;
      const s = state.students.find(s => s.id === studentId);
      if (s) s.groupId = null;
    },

    addCourseToGroup(state, action) {
      const { groupId, courseId } = action.payload;
      const g = state.groups.find(g => g.id === groupId);
      if (g && !g.courseIds.includes(courseId)) g.courseIds.push(courseId);
    },

    removeCourseFromGroup(state, action) {
      const { groupId, courseId } = action.payload;
      const g = state.groups.find(g => g.id === groupId);
      if (g) g.courseIds = g.courseIds.filter(id => id !== courseId);
    },
  },
});

export const {
  addStudent, updateStudent, deleteStudent,
  addGroup, updateGroup, deleteGroup,
  addStudentToGroup, removeStudentFromGroup,
  addCourseToGroup, removeCourseFromGroup,
} = studentsSlice.actions;

/* ── Selectors ── */
export const selectStudents     = (state) => state.students.students;
export const selectGroups       = (state) => state.students.groups;
export const selectGroupById    = (id) => (state) => state.students.groups.find(g => g.id === id);
export const selectStudentsByGroup = (groupId) => (state) =>
  state.students.students.filter(s => s.groupId === groupId);

export default studentsSlice.reducer;