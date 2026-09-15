"""_student_origin() in achievements.py — picks which logo
(app/utils/certificate.py's origin param) a student's downloaded
certificate should show: Turon's logo for students who came in through
Turon, the template's own default GENNIS logo for everyone else."""
from types import SimpleNamespace

from app.api.v1.endpoints.achievements import _student_origin


def test_student_with_turon_id_gets_turon_origin():
    student = SimpleNamespace(turon_id=42, gennis_id=None)
    assert _student_origin(student) == "turon"


def test_student_with_gennis_id_only_gets_gennis_origin():
    student = SimpleNamespace(turon_id=None, gennis_id=7)
    assert _student_origin(student) == "gennis"


def test_student_with_neither_id_defaults_to_gennis_origin():
    """A directly-registered student (no synced turon_id/gennis_id at all)
    falls back to the platform's own default logo."""
    student = SimpleNamespace(turon_id=None, gennis_id=None)
    assert _student_origin(student) == "gennis"


def test_student_with_both_ids_prefers_turon_origin():
    student = SimpleNamespace(turon_id=42, gennis_id=7)
    assert _student_origin(student) == "turon"
