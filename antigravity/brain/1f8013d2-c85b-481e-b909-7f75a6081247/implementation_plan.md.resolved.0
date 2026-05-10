# Automating Gennis Token Retrieval and Student Sync

The goal is to eliminate the manual step of fetching a Gennis token via PowerShell and pasting it. The system will automatically log in to Gennis when a teacher logs into the platform, retrieve a token, and synchronize students and groups.

## User Review Required

> [!IMPORTANT]
> This plan assumes that the teacher's credentials (username and password) on this platform are the same as their credentials on `admin.gennis.uz`. If they are different, we will need to add a way for teachers to link their Gennis accounts.

> [!NOTE]
> Synchronizing data from Gennis will overwrite local data for those students/groups.

## Proposed Changes

### Database & Models

#### [MODIFY] [user.py](file:///c:/Users/sunna/.gemini/backend/app/models/user.py)
- Add `gennis_token: Mapped[Optional[str]]` to store the session token.
- Add `phone: Mapped[Optional[str]]` and `surname: Mapped[Optional[str]]` to match Gennis data structure.
- Add `balance: Mapped[int]` (default 0).

#### [MODIFY] [group.py](file:///c:/Users/sunna/.gemini/backend/app/models/group.py)
- Add `price: Mapped[int]` (default 0).
- Add `gennis_id: Mapped[Optional[int]]` to map local groups to Gennis groups.

---

### Backend Services

#### [NEW] [gennis_service.py](file:///c:/Users/sunna/.gemini/backend/app/services/gennis_service.py)
- `login(username, password)`: POST to `https://tech.gennis.uz/api/v1/auth/login`.
- `fetch_groups(token)`: GET groups from Gennis API.
- `sync_teacher_data(db, teacher, token)`: 
    - Fetch all groups for the teacher.
    - For each group, fetch students.
    - Upsert groups and students into local database.

#### [MODIFY] [auth_service.py](file:///c:/Users/sunna/.gemini/backend/app/services/auth_service.py)
- In the `login` function:
    - If user is a teacher:
        - Call `GennisService.login(username, password)`.
        - If successful, save token to `user.gennis_token`.
        - Trigger `GennisService.sync_teacher_data` as a background task.

#### [MODIFY] [classroom.py](file:///c:/Users/sunna/.gemini/backend/app/api/v1/endpoints/classroom.py)
- Update `sync_classroom` endpoint to:
    - Check if teacher has a `gennis_token`.
    - Use `GennisService.sync_teacher_data` to perform the actual sync.

---

### Configuration

#### [MODIFY] [config.py](file:///c:/Users/sunna/.gemini/backend/app/config.py)
- Add `GENNIS_API_URL: str = "https://tech.gennis.uz/api/v1"`

## Verification Plan

### Automated Tests
1. **Mock Gennis API**: Create a mock server to test login and data fetching logic.
2. **Unit Test for Sync**: Test `sync_teacher_data` with sample JSON responses from Gennis.

### Manual Verification
1. Log in as a teacher with valid Gennis credentials.
2. Verify that the `gennis_token` is saved in the database.
3. Check if students and groups are automatically populated in the "My Students" view.
4. Click the "Sync" button in the frontend and verify it works without manual token input.
