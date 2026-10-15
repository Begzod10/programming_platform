// The demo account (see backend app/core/demo.py): one course, its first two
// lessons, no project submission. The ids mirror the backend constants.
export const DEMO_COURSE_ID = 9;
export const DEMO_HOME = `/student/courses/${DEMO_COURSE_ID}`;
export const isDemoUser = (user) => !!user?.is_demo;
