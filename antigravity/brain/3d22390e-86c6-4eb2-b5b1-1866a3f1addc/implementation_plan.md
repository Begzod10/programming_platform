# Student Gennis Integration Plan

The goal is to implement automated login and data synchronization for students, similar to how it works for teachers. When a student logs in, the system should first authenticate with Gennis and then synchronize their local profile.

## Proposed Changes

### [MODIFY] [gennis_service.py](file:///c:/Users/sunna/.gemini/backend/app/services/gennis_service.py)
- Add `sync_student_data` method to handle student-specific synchronization.
- This method will:
    - Update student profile (phone, balance, surname).
    - Save Gennis token.
    - Synchronize groups associated with the student.

### [MODIFY] [auth_service.py](file:///c:/Users/sunna/.gemini/backend/app/services/auth_service.py)
- Update `login` function to prioritize Gennis authentication for both teachers and students.
- If Gennis login is successful:
    - If user doesn't exist locally, create a new record.
    - If user exists, update their record.
    - Call the appropriate sync method (`sync_teacher_data` or `sync_student_data`).
- If Gennis login fails, fallback to local authentication (for administrative users or if Gennis is down).

## Verification Plan

### Automated Tests
- Create a temporary script to mock Gennis responses and verify the synchronization logic in `auth_service.py`.

### Manual Verification
- Request the user to test with a real student account.
- Check the database to ensure `phone`, `balance`, and `surname` are updated correctly after login.
