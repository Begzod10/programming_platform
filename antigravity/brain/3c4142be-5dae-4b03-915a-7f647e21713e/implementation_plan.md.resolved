# Fixing Course Deletion Issues

The user is experiencing issues deleting courses. My investigation revealed that several database constraints were either missing or configured with `NO ACTION`, which prevents deletion if related records exist.

## Proposed Changes

### Backend Models

I will update the following models to include `ondelete="CASCADE"` in their foreign keys and `cascade="all, delete-orphan"` in their relationships.

#### [MODIFY] [submission.py](file:///c:/Users/sunna/.gemini/backend/app/models/submission.py)
- Update `project_id`, `student_id`, and `lesson_id` to include `ondelete="CASCADE"`.

#### [MODIFY] [student_degree.py](file:///c:/Users/sunna/.gemini/backend/app/models/student_degree.py) (Need to check this file first)
- Update `degree_id` and `student_id` to include `ondelete="CASCADE"`.

#### [MODIFY] [course.py](file:///c:/Users/sunna/.gemini/backend/app/models/course.py)
- Update `achievements` relationship to include `cascade="all, delete-orphan"`.

### Database Schema

I will create a fix script to apply these changes to the existing database using `ALTER TABLE`.

#### [NEW] [fix_db_deletion_final.py](file:///c:/Users/sunna/.gemini/backend/fix_db_deletion_final.py)
- A script to drop existing constraints and recreate them with `ON DELETE CASCADE`.

## Verification Plan

### Automated Tests
- Run `test_delete_course.py` to ensure a course can be deleted even if it has lessons, submissions, and achievements.

### Manual Verification
- Verify that deleting a course through the UI (or API) works without errors.
