import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader
from pathlib import Path

_COURSE_TEMPLATE_BYTES = None

# ── Category ribbon theming ──────────────────────────────────────────────
# Colors mirror frontend/src/views/student/courses/Courses/StudentCourses.js's
# TECH_META exactly (kept here for reference/parity — per explicit request
# the ribbon's own background stays the template's default for every
# category, so "color" isn't drawn). Icons are each category's real brand
# logo rather than a generic glyph, sourced from devicon/simple-icons.
CATEGORY_THEME = {
    "html-css": {"color": "#e34c26"},
    "javascript": {"color": "#f0db4f"},
    "python": {"color": "#3776ab"},
    "react": {"color": "#61dafb"},
    "sql": {"color": "#336791"},
    "git": {"color": "#f05032"},
    "telegram-bot": {"color": "#2ca5e0"},
    "ai-integration": {"color": "#6c5ce7"},
}
_DEFAULT_CATEGORY_THEME = {"color": "#6c5ce7"}

# Where the icon sits in the template's default ribbon (the empty gap
# between the baked-in "COURSE CERTIFICATE" title and the GENNIS stamp),
# measured in the same "logical landscape" point space (LW=3475, LH=2450)
# the translate+rotate(90) block below draws in.
_RIBBON_ICON_CENTER_XY = (2555.1, 1859.6)
_RIBBON_ICON_SIZE = 200

# Pre-rasterized brand-logo PNGs (512×512, from each project's official SVG —
# devicon for html-css/javascript/python/react/sql/git, simple-icons for
# telegram-bot/ai-integration). One file per category slug, named to match;
# unrecognized slugs fall back to the ai-integration icon.
_ICON_DIR = Path("app/static/icons")
_icon_image_cache = {}


def _get_category_icon_image(category_slug: str):
    """Load a category's pre-rendered logo PNG as a cached ImageReader.
    Returns None if the asset is missing (caller degrades gracefully)."""
    key = category_slug if category_slug in CATEGORY_THEME else "ai-integration"
    if key in _icon_image_cache:
        return _icon_image_cache[key]

    try:
        path = (_ICON_DIR / f"{key}.png").resolve()
        if not path.exists():
            return None
        reader = ImageReader(str(path))
        _icon_image_cache[key] = reader
        return reader
    except Exception as e:
        print(f"❌ Icon yuklanmadi ({category_slug}): {e}")
        return None


def _draw_category_ribbon(can, category_slug: str):
    """Draws only the category icon on top of the template's ribbon — the
    ribbon's own background, "COURSE CERTIFICATE" title, and GENNIS stamp
    are left exactly as the template already renders them."""
    icon_img = _get_category_icon_image(category_slug)
    if icon_img is not None:
        cx, cy = _RIBBON_ICON_CENTER_XY
        half = _RIBBON_ICON_SIZE / 2
        can.drawImage(
            icon_img, cx - half, cy - half, width=_RIBBON_ICON_SIZE,
            height=_RIBBON_ICON_SIZE, mask="auto",
        )


# ── Origin logo (top-left corner) ────────────────────────────────────────
# The template's top-left corner has the GENNIS logo baked in, which is
# correct by default — students who registered through Gennis directly
# need nothing drawn. A student who came in through Turon should see the
# Turon International School logo there instead, so for that one case the
# GENNIS logo is patched over (filled with the template's own background
# tone, sampled off the template itself) and the Turon logo drawn on top.
# Measured the same way as the ribbon geometry: connected-component /
# pixel measurement on a rendered+rotated version of the template, in the
# same "logical landscape" point space (LW=3475, LH=2450).
_ORIGIN_LOGO_BG_COLOR = "#DEE5E3"
_ORIGIN_LOGO_PATCH_RECT = (273, 1765, 505, 513)  # x, y, width, height
_ORIGIN_LOGO_DRAW_RECT = (305.5, 1832.4, 440, 378.5)  # x, y, width, height — Turon logo's own 321:276 aspect
_ORIGIN_LOGO_PATHS = {
    "turon": Path("app/static/logos/turon.png"),
}
_origin_logo_image_cache = {}


def _hex_to_rgb01(hex_color: str):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _get_origin_logo_image(origin: str):
    path = _ORIGIN_LOGO_PATHS.get(origin)
    if path is None:
        return None
    if origin in _origin_logo_image_cache:
        return _origin_logo_image_cache[origin]
    try:
        abs_path = path.resolve()
        if not abs_path.exists():
            return None
        reader = ImageReader(str(abs_path))
        _origin_logo_image_cache[origin] = reader
        return reader
    except Exception as e:
        print(f"❌ Origin logo yuklanmadi ({origin}): {e}")
        return None


def _draw_origin_logo(can, origin: str):
    """No-op for "gennis" (or anything else unrecognized) — the template's
    default GENNIS logo is already correct. Only "turon" patches it."""
    if origin != "turon":
        return
    logo_img = _get_origin_logo_image(origin)
    if logo_img is None:
        return

    r, g, b = _hex_to_rgb01(_ORIGIN_LOGO_BG_COLOR)
    can.setFillColorRGB(r, g, b)
    can.rect(*_ORIGIN_LOGO_PATCH_RECT, fill=1, stroke=0)
    can.drawImage(logo_img, *_ORIGIN_LOGO_DRAW_RECT, mask="auto")


def _load_template_bytes(template_path: str):
    try:
        abs_path = Path(template_path).resolve()
        if abs_path.exists():
            with open(str(abs_path), "rb") as f:
                data = f.read()
            return data if len(data) > 0 else None
    except Exception as e:
        print(f"❌ Shablon yuklanmadi: {e}")
    return None


def _get_course_template():
    global _COURSE_TEMPLATE_BYTES
    if _COURSE_TEMPLATE_BYTES is None:
        _COURSE_TEMPLATE_BYTES = _load_template_bytes("app/static/web_certificate.pdf")
    return _COURSE_TEMPLATE_BYTES


def generate_certificate(
        student_name: str,
        course_name: str,
        cert_number: int,
        teacher_name: str = "Begzod Jumaniyozov",
        template_path: str = "app/static/web_certificate.pdf",
        category_slug: str = None,
        origin: str = "gennis",
) -> io.BytesIO:
    W_orig, H_orig = 2450, 3475
    LW, LH = H_orig, W_orig  # 3475 x 2450
    fs = W_orig / 595  # ≈ 4.12

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(W_orig, H_orig))

    can.saveState()
    can.translate(W_orig, 0)
    can.rotate(90)

    if category_slug:
        _draw_category_ribbon(can, category_slug)
    _draw_origin_logo(can, origin)

    # Talaba ismi
    can.setFillColorRGB(0, 0, 0)
    can.setFont("Times-Bold", int(20 * fs))
    can.drawString(310, LH * 0.595, student_name)

    # Kurs nomi
    can.setFillColorRGB(0, 0, 0)
    can.setFont("Times-Roman", int(20 * fs))
    can.drawString(310, LH * 0.505, course_name.upper() + " Course")

    # ID raqam
    can.setFillColorRGB(0, 0, 0)
    can.setFont("Times-Roman", int(15 * fs))
    id_font_size = int(17 * fs)
    id_offset = stringWidth("ID number:  AA ", "Times-Roman", id_font_size)
    can.drawString(260 + id_offset, LH * 0.458, f"{cert_number:07d}")

    # O'qituvchi ismi
    can.setFillColorRGB(0, 0, 0)
    can.setFont("Times-Roman", int(20 * fs))
    can.drawString(320, LH * 0.170, teacher_name)

    can.restoreState()
    can.save()
    packet.seek(0)

    try:
        new_pdf = PdfReader(packet)
        with open(template_path, "rb") as f:
            existing_pdf = PdfReader(f)
            output = PdfWriter()
            page = existing_pdf.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)
            result_buffer = io.BytesIO()
            output.write(result_buffer)
            result_buffer.seek(0)
            return result_buffer
    except Exception as e:
        print(f"❌ PDF xato: {e}")
        packet.seek(0)
        return packet


def generate_badge_certificate(
        student_name: str,
        achievement_name: str,
        achievement_description: str,
        cert_number: int,
        template_path: str = None,
) -> io.BytesIO:
    packet = io.BytesIO()
    W, H = 842, 595
    can = canvas.Canvas(packet, pagesize=(W, H))

    can.setFillColorRGB(1, 1, 1)
    can.rect(0, 0, W, H, fill=1, stroke=0)
    can.setStrokeColorRGB(0.4, 0.4, 0.8)
    can.setLineWidth(3)
    can.rect(20, 20, W - 40, H - 40, fill=0, stroke=1)

    can.setFillColorRGB(0.2, 0.2, 0.6)
    can.setFont("Times-Bold", 36)
    can.drawCentredString(W / 2, H - 100, "ACHIEVEMENT CERTIFICATE")

    can.setFillColorRGB(0, 0, 0)
    can.setFont("Times-Roman", 14)
    can.drawCentredString(W / 2, H - 150, "This certifies that")

    can.setFont("Times-Bold", 28)
    can.setFillColorRGB(0.1, 0.1, 0.5)
    can.drawCentredString(W / 2, H - 200, student_name)

    can.setFont("Times-Roman", 14)
    can.setFillColorRGB(0, 0, 0)
    can.drawCentredString(W / 2, H - 250, "has earned the achievement")

    can.setFont("Times-Bold", 22)
    can.setFillColorRGB(0.2, 0.5, 0.2)
    can.drawCentredString(W / 2, H - 290, achievement_name)

    can.setFont("Times-Roman", 12)
    can.setFillColorRGB(0.3, 0.3, 0.3)
    can.drawCentredString(W / 2, H - 330, achievement_description[:80])

    can.setFont("Times-Roman", 11)
    can.setFillColorRGB(0.5, 0.5, 0.5)
    can.drawCentredString(W / 2, 60, f"Certificate ID: BA{cert_number:07d}")

    can.setFont("Times-Bold", 14)
    can.setFillColorRGB(0.2, 0.2, 0.6)
    can.drawCentredString(W / 2, 40, "Gennis Innovative School")

    can.save()
    packet.seek(0)
    return packet