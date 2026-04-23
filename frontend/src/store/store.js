import { configureStore } from '@reduxjs/toolkit';
import coursesReducer  from './coursesSlice';
import studentsReducer from './studentsSlice';

const store = configureStore({
  reducer: {
    courses:  coursesReducer,
    students: studentsReducer,
  },
});

export default store;