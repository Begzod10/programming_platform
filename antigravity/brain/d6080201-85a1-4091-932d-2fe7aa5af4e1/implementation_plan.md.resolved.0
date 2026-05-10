# Implementation Plan - Fixing Course and Lesson Image/Status Functionality

The goal is to resolve issues where course and lesson images, as well as their published status, are not being saved or updated correctly. This is primarily due to missing fields in backend models and Pydantic schemas.

## Proposed Changes

### Backend Models

#### [MODIFY] [course.py](file:///c:/Users/sunna/.gemini/backend/app/models/course.py)
- Add `is_published` field (Boolean, default False).

#### [MODIFY] [lesson.py](file:///c:/Users/sunna/.gemini/backend/app/models/lesson.py)
- Add `is_published` field (Boolean, default False).
- Add `chapter` field (String, nullable).

### Backend Schemas

#### [MODIFY] [course.py](file:///c:/Users/sunna/.gemini/backend/app/schemas/course.py)
- Update `CourseUpdate` to include:
    - `image_url`
    - `is_published`
    - `thumbnail_url`
    - `video_intro_url`
    - `syllabus_url`
- Update `CourseRead` to include `is_published`.

#### [MODIFY] [lesson.py](file:///c:/Users/sunna/.gemini/backend/app/schemas/lesson.py)
- Update `LessonBase` to include `is_published` and `chapter`.
- Update `LessonUpdate` to include `is_published` and `chapter`.

### Backend Services

#### [MODIFY] [course_service.py](file:///c:/Users/sunna/.gemini/backend/app/services/course_service.py)
- Update `build_dto` to include `is_published` in the returned dictionary.

## Verification Plan

### Automated Tests
- I will use the browser tool to verify if images can be saved and displayed on the teacher dashboard.
- I will check the API responses to ensure `is_published` and `image_url` are correctly returned.

### Manual Verification
- Verify that a teacher can set a course image URL and it persists after refresh.
- Verify that toggling the "Published" status persists after refresh.
