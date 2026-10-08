"""Write a student's own profile edits back to the system they come from.

A gennis/turon student's name and phone live in management (the DB gennis-v2 and
turon-v2 both read for identity); student_platform only keeps a synced copy. When
the student edits them here, the source must change first — otherwise the next
login would overwrite the edit with the old value, and the other systems would
keep showing the old one.

The call is service-to-service (a shared secret, see management-v2's
`PUT /student-profile`): student_platform has already authenticated the student.
"""
from __future__ import annotations

import logging
import re
from typing import Optional

import httpx
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)

UNREACHABLE = "Ma'lumotlar asosiy tizimga saqlanmadi. Birozdan keyin qayta urinib ko'ring."
NOT_FOUND = "Hisobingiz asosiy tizimda topilmadi. Administratorga murojaat qiling."
BAD_PHONE = "Telefon raqami noto'g'ri. 9 xonali raqam kiriting (masalan: 90 123 45 67)."
BAD_NAME = "Ism va familiya bo'sh bo'lmasligi va 255 belgidan oshmasligi kerak."


def clean_phone(value: Optional[str]) -> str:
    """Digits only, 9 of them (998 prefix dropped) — how gennis/turon store it."""
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 12 and digits.startswith("998"):
        digits = digits[3:]
    if len(digits) != 9:
        raise HTTPException(status_code=400, detail=BAD_PHONE)
    return digits


def clean_full_name(value: Optional[str]) -> str:
    name = " ".join((value or "").split())
    if not name or len(name) > 255:
        raise HTTPException(status_code=400, detail=BAD_NAME)
    return name


def split_full_name(full_name: str, current_surname: Optional[str]) -> tuple[str, str]:
    """"Name Surname" -> (name, surname). Keeps the stored surname when the new
    text still ends with it (so "Muhammad Ali Saparov" stays name="Muhammad Ali"
    for surname "Saparov"); otherwise the last word is the surname."""
    surname = (current_surname or "").strip()
    if surname and full_name.casefold().endswith(surname.casefold()) and len(full_name) > len(surname):
        return full_name[: -len(surname)].strip(), full_name[-len(surname):]
    parts = full_name.split()
    if len(parts) == 1:
        return parts[0], surname
    return " ".join(parts[:-1]), parts[-1]


def external_identities(student) -> list[tuple[str, int]]:
    """(source, id) pairs this student has in the outside systems."""
    out = []
    if student.gennis_id:
        out.append(("gennis", int(student.gennis_id)))
    if student.turon_id:
        out.append(("turon", int(student.turon_id)))
    return out


async def push_profile(student, *, name: Optional[str], surname: Optional[str], phone: Optional[str]) -> bool:
    """Write the changed fields to management. Returns False when the write-back
    is not configured (nothing was sent), True when every system accepted it;
    raises HTTPException (502) when one refused or could not be reached."""
    if not settings.STUDENT_PLATFORM_SERVICE_SECRET:
        logger.warning("profile write-back skipped: STUDENT_PLATFORM_SERVICE_SECRET is not set")
        return False

    payload_fields = {k: v for k, v in (("name", name), ("surname", surname), ("phone", phone)) if v is not None}
    url = f"{settings.MGMT_INTEGRATION_URL}/student-profile"
    headers = {"X-Student-Platform-Secret": settings.STUDENT_PLATFORM_SERVICE_SECRET}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for source, ext_id in external_identities(student):
                resp = await client.put(url, headers=headers, json={"source": source, "id": ext_id, **payload_fields})
                if resp.status_code == 404:
                    raise HTTPException(status_code=502, detail=NOT_FOUND)
                if resp.status_code == 422:
                    raise HTTPException(status_code=400, detail=BAD_PHONE if "phone" in payload_fields else BAD_NAME)
                if resp.status_code >= 300:
                    logger.error("profile write-back refused: %s %s", resp.status_code, resp.text[:200])
                    raise HTTPException(status_code=502, detail=UNREACHABLE)
    except httpx.HTTPError as e:
        logger.error("profile write-back failed: %s", e)
        raise HTTPException(status_code=502, detail=UNREACHABLE)
    return True
