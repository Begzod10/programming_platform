# `POST /api/v1/auth/login`

Single login endpoint for all three account origins: native student_platform
accounts, Gennis-linked accounts, and Turon-linked accounts. The client
always sends the same body — there is no `system`/`source` field to pick.

- **Domain (production):** `https://tech.gennis.uz`
- **Full URL:** `https://tech.gennis.uz/api/v1/auth/login`
- **Method:** `POST`
- **Auth required:** none
- **Rate limit:** 20 requests / 60s per caller (`app/core/rate_limit.py`)
- **Route:** `app/api/v1/endpoints/auth.py:login`
- **Logic:** `app/services/auth_service.py:login`

## How it resolves the account (server-side, not visible on the wire)

1. Tries Gennis/Turon first — one call to gennis-v2's shared shim
   (`GennisService.login`, hits `https://v2.gennis.uz/api/v1/integrations/student-platform/login`).
   That shim checks the password against the shared `user` table and reports
   back `source: "gennis"` or `"turon"`.
2. On success, student_platform finds-or-creates its own local `Student` row
   (its own DB, a separate id space from the shared `user` table) and syncs
   groups/flow/debt into it.
3. If step 1 fails (not a gennis/turon account, or wrong password there),
   falls back to a native student_platform password check.
4. Issues its own JWT — `sub` is student_platform's **local** `Student.id`,
   not the shared management/gennis-v2 id.

## Request body

```json
{
  "username": "aliyev_shodlik",
  "password": "correct-horse-battery-staple"
}
```

| Field | Type | Notes |
|---|---|---|
| `username` | string | Gennis/turon login, or a native student_platform username/email |
| `password` | string | Plain password |

## Response — 200 OK

Same envelope for every case:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 4821,
    "username": "aliyev_shodlik",
    "email": "aliyev_shodlik@example.com",
    "full_name": "Shodlik Aliyev",
    "role": "student",
    "phone": "+998901234567",
    "current_level": "Beginner",
    "total_points": 0,
    "is_active": true,
    "balance": 0,
    "achievements": [],
    "created_at": "2026-08-20T09:14:03.000Z"
  }
}
```

### Example — Gennis student (first-time login, account auto-created)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQ4MjF9...",
  "token_type": "bearer",
  "user": {
    "id": 4821,
    "username": "gennis_13807",
    "email": "gennis_13807@gennis.uz",
    "full_name": "Shodlik Aliyev",
    "role": "student",
    "phone": "+998901234567",
    "current_level": "Beginner",
    "total_points": 0,
    "is_active": true,
    "balance": 0,
    "achievements": [],
    "created_at": "2026-08-20T09:14:03.000Z"
  }
}
```

### Example — Turon teacher

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjUwMTJ9...",
  "token_type": "bearer",
  "user": {
    "id": 5012,
    "username": "n.eshqobilova",
    "email": "n.eshqobilova@turon.uz",
    "full_name": "Nigora Eshqobilova",
    "role": "teacher",
    "phone": "+998901112233",
    "current_level": "Beginner",
    "total_points": 0,
    "is_active": true,
    "balance": 0,
    "achievements": [],
    "created_at": "2026-08-12T07:02:41.000Z"
  }
}
```

`UserRead` never exposes which upstream system the account came from
(`gennis_id`/`turon_id` are internal columns, not returned) — the two
examples above look identical in shape, only the values differ:

| Field | Gennis account | Turon account |
|---|---|---|
| `username` (teacher role) | their real gennis login | their real turon login |
| `username` (student role) | `gennis_<gennis_student_id>` | `turon_<shared user.id>` |
| `email` (if not set upstream) | `<username>@gennis.uz` | `<username>@turon.uz` |
| id stored on the local row (not returned) | `Student.gennis_id` | `Student.turon_id` |

## Error responses

**401 Unauthorized** — wrong username/password (checked after the
gennis/turon attempt and the local fallback both fail):

```json
{
  "detail": "parol yokida login xato"
}
```

**403 Forbidden** — account matched locally but is deactivated:

```json
{
  "detail": "Foydalanuvchi faol emas"
}
```
