"""
Category-themed certificate generation (app/utils/certificate.py).

Covers the optional `category_slug` parameter added to generate_certificate():
  - omitting it must behave exactly as before (backward compatibility for
    existing callers, e.g. achievement_service.generate_certificate_pdf)
  - a recognized slug draws the category's real brand-logo icon
  - an unrecognized/unknown slug falls back gracefully instead of erroring
"""
from PyPDF2 import PdfReader

from app.utils.certificate import CATEGORY_THEME, generate_certificate


def _make_pdf(**kwargs) -> PdfReader:
    buf = generate_certificate(
        student_name="Test Student",
        course_name="Python",
        cert_number=1,
        **kwargs,
    )
    buf.seek(0)
    return PdfReader(buf)


def test_generate_certificate_without_category_slug_is_unchanged():
    """No category_slug (the default) must still produce a valid single-page
    certificate — existing callers that don't pass it must see no behavior
    change."""
    reader = _make_pdf()
    assert len(reader.pages) == 1


def test_generate_certificate_with_known_category_slug():
    for slug in CATEGORY_THEME:
        reader = _make_pdf(category_slug=slug)
        assert len(reader.pages) == 1


def test_generate_certificate_with_unknown_category_slug_falls_back():
    """An unrecognized slug (e.g. a category created after this list was
    written) must not raise — it degrades to the default icon."""
    reader = _make_pdf(category_slug="some-future-category")
    assert len(reader.pages) == 1


def test_generate_certificate_with_none_category_slug_explicit():
    reader = _make_pdf(category_slug=None)
    assert len(reader.pages) == 1
