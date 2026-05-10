# Filtering Students by Teacher

Currently, the teacher's student list endpoint returns all students in the system. We need to filter this list so that a teacher only sees students enrolled in their managed groups.

## Proposed Changes

### Backend Service

#### [MODIFY] [student_service.py](file:///c:/Users/sunna/.gemini/backend/app/services/student_service.py)
- Add `get_students_by_teacher` method that joins the `Student` model with `Group` and filters by `Group.teacher_id`.

### API Endpoint

#### [MODIFY] [students.py](file:///c:/Users/sunna/.gemini/backend/app/api/v1/endpoints/teacher/students.py)
- Update the `get_all_students` endpoint to use the new `get_students_by_teacher` method, passing the `current_teacher.id`.

## Verification Plan

### Automated Tests
- Test the `GET /api/v1/teacher/students/` endpoint with a teacher account and verify it only returns students from their groups.
