import httpx
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.models.user import Student, UserRole
from app.models.group import Group, student_groups
from app.models.flow import Flow, student_flows

logger = logging.getLogger(__name__)

class GennisService:
    """Talks to management-v2's student_platform integration endpoint.

    Despite the name, this now serves BOTH gennis and turon accounts —
    management-v2 authenticates against one shared user account and, after
    that, resolves either a gennis or a turon teacher/student record, tagging
    its response with `"source"` so callers know which. Every sync method
    below takes a `system` ("gennis" | "turon") that says which id column
    (Student.gennis_id / Student.turon_id, Group.gennis_id / Group.turon_id)
    and which username/email prefix ("gennis_" / "turon_") to use — gennis and
    turon ids are independent, overlapping numeric spaces, so the two must
    never be written to the same column. See auth_service.login.

    No fallback to gennis-v2's own copy of this shim: if MGMT_INTEGRATION_URL
    is unreachable, `login()` returns None and the caller falls through to
    local auth, same as any other failure — it never retries a second URL.
    """
    BASE_URL = settings.MGMT_INTEGRATION_URL

    @classmethod
    async def login(cls, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Gennis/turon tizimiga login qilish (v2's shim resolves which one)"""
        # v2's shim mirrors old gennis's /base/login, including the request
        # field name, so the body below is unchanged from the old integration.
        url = f"{cls.BASE_URL}/login"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json={"username": username, "password": password})
                if resp.status_code == 200:
                    return resp.json()
                logger.error(f"Gennis login muvaffaqiyatsiz: {resp.status_code}")
        except Exception as e:
            logger.error(f"Gennis login xatosi: {e}")
        return None

    @classmethod
    async def fetch_flow_students(cls, flow_id: int, token: str) -> List[Dict[str, Any]]:
        """Flow-dagi barcha talabalarni Turon API dan tortib olish (faqat
        turon — gennis'da flow yo'q, shuning uchun `source` param yo'q, xuddi
        v2's /flow/{id}/students shim'i kabi)."""
        url = f"{cls.BASE_URL}/flow/{flow_id}/students"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("students", []) if isinstance(data, dict) else data
        except Exception as e:
            logger.error(f"Flow talabalarini olishda xato: {e}")
        return []

    @classmethod
    async def fetch_group_students(cls, group_id: int, token: str, system: str = "gennis") -> List[Dict[str, Any]]:
        """Guruhdagi barcha talabalarni Gennis/Turon API dan tortib olish"""
        # v2 keys this on the group id IN ITS OWN SYSTEM — the same id the
        # login response returns and the same one stored as Group.gennis_id /
        # Group.turon_id — but orders the path differently from old gennis's
        # /group/students/{id}. `system` disambiguates which id space it's in.
        url = f"{cls.BASE_URL}/group/{group_id}/students"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers, params={"source": system})
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("students", []) if isinstance(data, dict) else data
        except Exception as e:
            logger.error(f"Talabalarni olishda xato: {e}")
        return []

    @classmethod
    async def sync_teacher_data(cls, db: AsyncSession, teacher: Student, login_data: Dict[str, Any], system: str = "gennis"):
        """O'qituvchi va uning barcha guruh/talabalarni sinxronlash"""
        token = login_data.get("access_token")
        user_info = login_data.get("user", {})
        teacher_info = user_info.get("teacher", {})
        groups_data = teacher_info.get("group", [])
        # Turon-only, independent from group[] — see app/models/flow.py.
        # teacher_info.get("flow") is always [] for gennis, so the loop below
        # is a no-op there.
        flows_data = teacher_info.get("flow", [])

        # O'qituvchi profilini yangilash
        teacher.gennis_token = token
        teacher.full_name = f"{user_info.get('name', '')} {user_info.get('surname', '')}".strip()

        phones = user_info.get("phone", [])
        if phones:
            teacher.phone = str(phones[0].get("phone"))[:50]

        await db.flush()

        id_col = f"{system}_id"
        current_ext_ids = {g_data.get("id") for g_data in groups_data if g_data.get("id") is not None}

        for g_data in groups_data:
            group = await cls._sync_group(db, g_data, teacher.id, system=system)

            # Guruh talabalarini yangilash
            students_list = await cls.fetch_group_students(getattr(group, id_col), token, system=system)
            for s_data in students_list:
                await cls._sync_student(db, s_data, group.id, system=system)

            # Gennis/turon endi bu guruhda ko'rsatmayotgan talabalarni guruhdan chiqaramiz.
            # students_list bo'sh bo'lsa (API vaqtinchalik hech narsa qaytarmasa) hech
            # kimni o'chirmaymiz — bu holat ehtimol API xatosi, haqiqiy bo'shatish emas.
            current_student_ext_ids = {s.get("id") for s in students_list if s.get("id") is not None}
            if current_student_ext_ids:
                stale_members_result = await db.execute(
                    select(Student.id, Student.username)
                    .join(student_groups, student_groups.c.student_id == Student.id)
                    .where(
                        student_groups.c.group_id == group.id,
                        getattr(Student, id_col).isnot(None),
                        getattr(Student, id_col).notin_(current_student_ext_ids),
                    )
                )
                stale_members = stale_members_result.all()
                if stale_members:
                    stale_student_ids = [row[0] for row in stale_members]
                    for _, username in stale_members:
                        logger.info(
                            f"Talaba '{username}' endi guruh '{group.name}'da emas — chiqarilmoqda."
                        )
                    await db.execute(
                        delete(student_groups).where(
                            student_groups.c.group_id == group.id,
                            student_groups.c.student_id.in_(stale_student_ids),
                        )
                    )

        # Gennis/turon endi bu o'qituvchiga bermayotgan guruhlarni bo'shatamiz (teacher_id = NULL).
        #
        # groups_data bu yerga faqat login()dan MUVAFFAQIYATLI (200 OK) javob
        # kelgandagina yetib keladi — auth_service.login shim None qaytarsa,
        # sync_teacher_data umuman chaqirilmaydi. Demak bo'sh ro'yxat "API
        # vaqtinchalik xato berdi" degani emas, balki management-v2'ning
        # _groups_for_teacher_turon'i "bu o'qituvchida hozir faol/o'chirilmagan
        # guruh yo'q" deb aniq javob bergani. Ilgari bu yerda `if
        # current_ext_ids:` bo'sh ro'yxatda tozalashni butunlay o'tkazib
        # yuborardi — natijada oxirgi tayinlovi (masalan bitta timetable
        # yozuvi) o'chirilgan o'qituvchi eski guruhini (va uning talabalarini)
        # student_platform'da abadiy ko'rib turaverdi (rimefara_teach_turon /
        # "1-blue"da tasdiqlandi, 2026-09-03).
        stale_result = await db.execute(
            select(Group).where(
                Group.teacher_id == teacher.id,
                getattr(Group, id_col).isnot(None),
                getattr(Group, id_col).notin_(current_ext_ids),
            )
        )
        stale_groups = stale_result.scalars().all()
        for stale_group in stale_groups:
            logger.info(
                f"Guruh '{stale_group.name}' ({id_col}={getattr(stale_group, id_col)}) endi "
                f"o'qituvchi {teacher.username} da emas — bo'shatilmoqda."
            )
            stale_group.teacher_id = None

        # Flow tomoni — Guruh bilan bir xil pattern, lekin alohida konteyner
        # (student_flows, Flow.teacher_id). Faqat turon'da ma'no bor; gennis
        # uchun flows_data doim [] bo'ladi, shuning uchun bu blok no-op.
        current_flow_ext_ids = {f_data.get("id") for f_data in flows_data if f_data.get("id") is not None}

        for f_data in flows_data:
            flow = await cls._sync_flow(db, f_data, teacher.id)

            students_list = await cls.fetch_flow_students(flow.turon_id, token)
            for s_data in students_list:
                await cls._sync_flow_student(db, s_data, flow.id, system=system)

            current_student_ext_ids = {s.get("id") for s in students_list if s.get("id") is not None}
            if current_student_ext_ids:
                stale_members_result = await db.execute(
                    select(Student.id, Student.username)
                    .join(student_flows, student_flows.c.student_id == Student.id)
                    .where(
                        student_flows.c.flow_id == flow.id,
                        getattr(Student, id_col).isnot(None),
                        getattr(Student, id_col).notin_(current_student_ext_ids),
                    )
                )
                stale_members = stale_members_result.all()
                if stale_members:
                    stale_student_ids = [row[0] for row in stale_members]
                    for _, username in stale_members:
                        logger.info(
                            f"Talaba '{username}' endi flow '{flow.name}'da emas — chiqarilmoqda."
                        )
                    await db.execute(
                        delete(student_flows).where(
                            student_flows.c.flow_id == flow.id,
                            student_flows.c.student_id.in_(stale_student_ids),
                        )
                    )

        # Same reasoning as the group cleanup above — flows_data is only
        # ever a genuinely-empty *successful* answer here, never a stand-in
        # for a failed call, so it's trusted the same way.
        stale_flow_result = await db.execute(
            select(Flow).where(
                Flow.teacher_id == teacher.id,
                Flow.turon_id.isnot(None),
                Flow.turon_id.notin_(current_flow_ext_ids),
            )
        )
        stale_flows = stale_flow_result.scalars().all()
        for stale_flow in stale_flows:
            logger.info(
                f"Flow '{stale_flow.name}' (turon_id={stale_flow.turon_id}) endi "
                f"o'qituvchi {teacher.username} da emas — bo'shatilmoqda."
            )
            stale_flow.teacher_id = None

        await db.commit()
        logger.info(f"O'qituvchi {teacher.username} sinxronizatsiyasi yakunlandi.")

    @classmethod
    async def sync_student_data(cls, db: AsyncSession, student: Student, login_data: Dict[str, Any], system: str = "gennis"):
        """Talaba ma'lumotlarini va ism-familiyasini sinxronlash"""
        token = login_data.get("access_token")
        user_info = login_data.get("user", {})
        student_info = user_info.get("student", {})
        groups_data = student_info.get("group", [])
        # Turon-only, independent from group[] — see app/models/flow.py.
        # student_info.get("flow") is always [] for gennis, so this is a no-op there.
        flows_data = student_info.get("flow", [])

        # Ismlarni yangilash
        student.gennis_token = token
        student.full_name = f"{user_info.get('name', '')} {user_info.get('surname', '')}".strip()
        student.surname = user_info.get("surname", "")
        student.balance = user_info.get("balance", student_info.get("combined_debt", 0))

        phones = user_info.get("phone", [])
        if phones:
            student.phone = str(phones[0].get("phone"))[:50]

        await db.flush()

        # Talabani guruhlari bilan qayta yuklash
        result = await db.execute(
            select(Student).filter(Student.id == student.id).options(selectinload(Student.groups))
        )
        student = result.scalar_one()

        for g_data in groups_data:
            group = await cls._sync_group(db, g_data, system=system)

            # Xavfsiz bog'lash: ON CONFLICT DO NOTHING
            query = text("""
                INSERT INTO student_groups (student_id, group_id)
                VALUES (:s_id, :g_id)
                ON CONFLICT (student_id, group_id) DO NOTHING
            """)
            await db.execute(query, {"s_id": student.id, "g_id": group.id})
            student.group_id = group.id

        for f_data in flows_data:
            flow = await cls._sync_flow(db, f_data)

            query = text("""
                INSERT INTO student_flows (student_id, flow_id)
                VALUES (:s_id, :f_id)
                ON CONFLICT (student_id, flow_id) DO NOTHING
            """)
            await db.execute(query, {"s_id": student.id, "f_id": flow.id})

        await db.commit()
        logger.info(f"Talaba {student.username} ma'lumotlari yangilandi.")

    @classmethod
    async def _sync_flow(cls, db: AsyncSession, f_data: Dict[str, Any], teacher_id: Optional[int] = None) -> Flow:
        """Flow bazada yaratish yoki yangilash (faqat turon — group[] bilan mustaqil)."""
        f_id = f_data.get("id")
        result = await db.execute(select(Flow).where(Flow.turon_id == f_id))
        flow = result.scalar_one_or_none()

        if not flow:
            flow = Flow(name=f_data.get("name"), turon_id=f_id, teacher_id=teacher_id)
            db.add(flow)
        else:
            flow.name = f_data.get("name")
            if teacher_id:
                flow.teacher_id = teacher_id

        await db.flush()
        return flow

    @classmethod
    async def _sync_group(cls, db: AsyncSession, g_data: Dict[str, Any], teacher_id: Optional[int] = None, system: str = "gennis") -> Group:
        """Guruhni bazada yaratish yoki yangilash"""
        id_col = f"{system}_id"
        g_id = g_data.get("id")
        result = await db.execute(select(Group).where(getattr(Group, id_col) == g_id))
        group = result.scalar_one_or_none()

        if not group:
            group = Group(
                name=g_data.get("name"),
                price=g_data.get("price", 0),
                teacher_id=teacher_id,
                **{id_col: g_id},
            )
            db.add(group)
        else:
            group.name = g_data.get("name")
            group.price = g_data.get("price", 0)
            if teacher_id:
                group.teacher_id = teacher_id

        await db.flush()
        return group

    @staticmethod
    def _normalized_name(value: Optional[str]) -> str:
        """Case- and spacing-insensitive name form, used to re-link students."""
        return " ".join((value or "").split()).casefold()

    @classmethod
    async def _find_renumbered_student(
        cls, db: AsyncSession, s_data: Dict[str, Any], container_id: int, system: str = "gennis",
        member_table=student_groups, member_id_col: str = "group_id",
    ) -> Optional[Student]:
        """Find a current group/flow member who is this same person under an old id.

        Both GENNIS (during the v2 cutover) and TURON can re-issue a person's
        id, so an `{system}_{id}` lookup can miss for people already on the
        platform. Minting a fresh row in that case strands the student's entire
        history — points, projects, enrolments — on an abandoned account, so
        before creating we look for them among the container's existing
        members by name.

        Scoping the search to `container_id` (a Group id when
        member_table=student_groups, a Flow id when member_table=
        student_flows) is what makes this safe: a candidate must already be
        in the very container the source system places this student in, so
        two different people can't be collapsed into one.
        """
        full_name = cls._normalized_name(
            f"{s_data.get('name', '')} {s_data.get('surname', '')}"
        )
        if not full_name:
            return None

        id_col = f"{system}_id"
        result = await db.execute(
            select(Student)
            .join(member_table, member_table.c.student_id == Student.id)
            .where(
                getattr(member_table.c, member_id_col) == container_id,
                Student.role == UserRole.student,
                getattr(Student, id_col).isnot(None),
                getattr(Student, id_col) != s_data.get("id"),
            )
        )
        matches = [
            s for s in result.scalars().all()
            if cls._normalized_name(s.full_name) == full_name
        ]
        # Ambiguity means we can't tell which row is the right one — fall back
        # to creating a new student rather than guessing and merging a stranger.
        if len(matches) != 1:
            return None
        return matches[0]

    @classmethod
    async def _sync_student(cls, db: AsyncSession, s_data: Dict[str, Any], group_id: int, system: str = "gennis") -> Student:
        """Talabani ism-familiyasi bilan birga sinxronlash, Guruh a'zoligi
        orqali (O'qituvchi logini uchun). Bu ham Student.group_id — birlamchi
        guruh ko'rsatkichini — yangilaydi."""
        return await cls._sync_container_student(
            db, s_data, group_id, system=system,
            member_table=student_groups, member_id_col="group_id",
            insert_table="student_groups", insert_col="group_id",
            set_primary_group=True,
        )

    @classmethod
    async def _sync_flow_student(cls, db: AsyncSession, s_data: Dict[str, Any], flow_id: int, system: str = "turon") -> Student:
        """Talabani ism-familiyasi bilan birga sinxronlash, Flow a'zoligi
        orqali. Student.group_id ga TEGMAYDI — Flow Group'dan mustaqil,
        alohida konteyner (unrelated denormalized pointer)."""
        return await cls._sync_container_student(
            db, s_data, flow_id, system=system,
            member_table=student_flows, member_id_col="flow_id",
            insert_table="student_flows", insert_col="flow_id",
            set_primary_group=False,
        )

    @classmethod
    async def _sync_container_student(
        cls, db: AsyncSession, s_data: Dict[str, Any], container_id: int, system: str,
        *, member_table, member_id_col: str, insert_table: str, insert_col: str,
        set_primary_group: bool,
    ) -> Student:
        id_col = f"{system}_id"
        s_id = s_data.get("id")
        s_username = f"{system}_{s_id}"

        # Ismlarni tayyorlash
        first_name = s_data.get("name", "")
        last_name = s_data.get("surname", "")
        full_name = f"{first_name} {last_name}".strip()
        if not full_name:
            full_name = s_username # Agar ism kelmasa username qo'yiladi

        result = await db.execute(select(Student).where(Student.username == s_username))
        student = result.scalar_one_or_none()

        if not student:
            # No row under the current id — check whether the source system
            # renumbered someone we already have before assuming this is a new person.
            student = await cls._find_renumbered_student(
                db, s_data, container_id, system=system,
                member_table=member_table, member_id_col=member_id_col,
            )
            if student is not None:
                logger.warning(
                    "Talaba '%s' yangi %s id oldi: %s → %s. "
                    "Mavjud hisob qayta bog'landi (yangi hisob yaratilmadi).",
                    student.username, system, getattr(student, id_col), s_id,
                )
                # `s_username` is free — the lookup above found nothing.
                student.username = s_username
                student.email = f"{s_username}@{system}.uz"

        if not student:
            student = Student(
                username=s_username,
                email=f"{s_username}@{system}.uz",
                full_name=full_name,
                hashed_password="external_auth",
                role=UserRole.student,
                phone=str(s_data.get("phone"))[:50],
                balance=s_data.get("balance", 0),
                surname=last_name,
                group_id=container_id if set_primary_group else None,
                **{id_col: s_id},
            )
            db.add(student)
            await db.flush()
        else:
            student.full_name = full_name
            student.surname = last_name
            student.phone = str(s_data.get("phone"))[:50]
            student.balance = s_data.get("balance", 0)
            if set_primary_group:
                student.group_id = container_id
            setattr(student, id_col, s_id)

        # Bog'liqlikni bazada yangilash (Xato bermasligi uchun ON CONFLICT)
        query = text(f"""
            INSERT INTO {insert_table} (student_id, {insert_col})
            VALUES (:s_id, :c_id)
            ON CONFLICT (student_id, {insert_col}) DO NOTHING
        """)
        await db.execute(query, {"s_id": student.id, "c_id": container_id})

        await db.flush()
        return student
