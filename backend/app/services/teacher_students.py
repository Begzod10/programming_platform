from sqlalchemy import select, union
from sqlalchemy.sql import Subquery

from app.models.group import Group, student_groups
from app.models.flow import Flow, student_flows


def teacher_student_ids_subquery(teacher_id: int) -> Subquery:
    """Student ids reachable by a teacher via either a Group they own or a
    Flow they own — turon's two independent containers (gennis only ever
    populates the Group half). A subject teacher who is scheduled to teach a
    Flow rather than a Group (see gennis_service.sync_teacher_data) is
    otherwise invisible everywhere "this teacher's students" gets resolved —
    My Students, progress, ranking, achievements, the student-delete guard —
    so every one of those call sites should filter through this, not
    `Group.teacher_id` alone.

    Plain UNION (not UNION ALL) so a student in two of the teacher's
    containers still appears once; callers don't need their own DISTINCT.
    """
    from_groups = (
        select(student_groups.c.student_id)
        .join(Group, Group.id == student_groups.c.group_id)
        .where(Group.teacher_id == teacher_id)
    )
    from_flows = (
        select(student_flows.c.student_id)
        .join(Flow, Flow.id == student_flows.c.flow_id)
        .where(Flow.teacher_id == teacher_id)
    )
    return union(from_groups, from_flows).subquery()


def student_teacher_ids_subquery(student_id: int) -> Subquery:
    """Inverse of teacher_student_ids_subquery: the teacher ids a student is
    reachable BY, via either container. Used to scope a course-less game
    session's visibility to only the teacher who actually owns this student
    (via a Group or Flow) — without this, any teacher's course-less game
    (gennis or turon) was visible to every student platform-wide, including
    a different teacher's turon students who'd never even met that teacher."""
    from_groups = (
        select(Group.teacher_id)
        .join(student_groups, student_groups.c.group_id == Group.id)
        .where(student_groups.c.student_id == student_id, Group.teacher_id.isnot(None))
    )
    from_flows = (
        select(Flow.teacher_id)
        .join(student_flows, student_flows.c.flow_id == Flow.id)
        .where(student_flows.c.student_id == student_id, Flow.teacher_id.isnot(None))
    )
    return union(from_groups, from_flows).subquery()
