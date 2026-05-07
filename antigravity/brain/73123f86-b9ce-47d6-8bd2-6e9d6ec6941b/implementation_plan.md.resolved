# Fixing Achievement Progress and Certificate Logic

The user reported that certificates show "100% completed" but remain locked, even when courses haven't been taken. This is due to a fallback in the progress calculation that defaults to student's total points for unhandled or misconfigured achievement types.

## Proposed Changes

### [Backend] Achievement Service

#### [MODIFY] [achievement_service.py](file:///c:/Users/sunna/.gemini/backend/app/services/achievement_service.py)

- Update `get_achievement_progress` to calculate progress correctly based on `criteria_type`.
- Prevent fallback to `total_points` for `course_completion` achievements when `course_id` is missing.
- Use `CourseService.calc_progress` (or equivalent logic) to show actual percentage progress for courses instead of a simple 0/1 (binary) status.
- Ensure that if `criteria_type` is unknown, progress defaults to 0.

### [Backend] Ranking Service (Verification)

- Check if points are being added incorrectly during synchronization or other processes. (Investigation only for now).

## Verification Plan

### Automated Tests
- Create a test script to verify `get_achievement_progress` with different achievement configurations (points-based vs course-based).
- Verify that a student with 0 progress in a course shows 0% progress for the corresponding certificate.

### Manual Verification
- Ask the user to check the "Мои Сертификаты" page after the fix to see if the "100% completed" label for locked certificates has disappeared or changed to actual progress.
