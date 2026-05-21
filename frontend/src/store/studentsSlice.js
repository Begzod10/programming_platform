import { createSlice } from '@reduxjs/toolkit';

// Real data is loaded from the API. Initial slice state is empty so no
// placeholder data (and no mock passwords) ship in the production bundle.
const initialStudents = [];
const initialGroups = [];

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