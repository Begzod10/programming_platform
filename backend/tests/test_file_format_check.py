"""Content-vs-extension warnings: detection is strict, nothing is ever blocked, the score is never touched."""
import io
import zipfile

from app.services.file_format_check import (
    apply_to_review, detect_language, format_warnings, snapshot_format_warnings, zip_format_warnings,
)

PYTHON = """# app/ranking.py
import os
from flask import Flask

def find_rank(points, target):
    for i in range(len(points)):
        if points[i] == target:
            return i
    return -1

class Cache:
    def __init__(self):
        self.items = {}
"""
HTML = """<!DOCTYPE html>
<html><head><title>t</title><link rel="stylesheet" href="s.css"></head>
<body><div class="card"><h2>Salom</h2><p>matn</p><a href="#">havola</a><img src="a.png" alt="x"></div></body></html>"""
CSS = ".card { color: red; }\n#header { background: blue; }\np { margin: 0; }\n.btn { padding: 4px; }\n"
JS = "const el = document.getElementById('a');\nfunction go() { console.log(1); }\nel.addEventListener('click', () => go());\nlet n = 1;\n"


def test_detects_the_dominant_language():
    assert detect_language(PYTHON) == "python"
    assert detect_language(HTML) == "html"
    assert detect_language(CSS) == "css"
    assert detect_language(JS) == "js"
    assert detect_language("") is None and detect_language("salom dunyo") is None


def test_python_saved_as_html_is_the_case_that_started_this():
    [w] = format_warnings([("youtube qoyib beraymi.html", PYTHON)])
    assert (w["extension"], w["detected"], w["suggested"]) == (".html", "python", ".py")
    assert "Python kodi" in w["message"] and ".py" in w["message"] and "Python" in w["message_ru"]


def test_html_in_a_css_or_js_file_is_flagged():
    got = {w["file"]: w["suggested"] for w in format_warnings([("style.css", HTML), ("app.js", HTML)])}
    assert got == {"style.css": ".html", "app.js": ".html"}


def test_a_correct_file_and_the_normal_mixes_are_not_flagged():
    assert format_warnings([("index.html", HTML), ("style.css", CSS), ("app.js", JS), ("main.py", PYTHON)]) == []
    page_with_script = HTML.replace("</body>", "<script>" + JS + "</script></body>")
    assert format_warnings([("page.html", page_with_script)]) == []
    template_in_python = PYTHON + "\nTEMPLATE = '<div><p>x</p></div>'\n"
    assert format_warnings([("app.py", template_in_python)]) == []             # .py is never checked


def test_dependency_folders_and_other_extensions_are_skipped():
    assert format_warnings([("venv/lib/site-packages/x/page.html", PYTHON), ("node_modules/a/b.css", HTML),
                            ("notes.txt", PYTHON), ("data.json", PYTHON)]) == []


def make_zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, text in files.items():
            zf.writestr(name, text)
    return buf.getvalue()


def test_zip_and_snapshot_helpers_find_the_same_thing():
    warnings = zip_format_warnings(make_zip({"OK.html": PYTHON, "index.html": HTML}))
    assert [w["file"] for w in warnings] == ["OK.html"]
    snapshot = {"content_text": f"### OK.html\n```\n{PYTHON}\n```\n\n### index.html\n```\n{HTML}\n```"}
    assert [w["file"] for w in snapshot_format_warnings(snapshot)] == ["OK.html"]
    assert zip_format_warnings(b"not a zip") == [] and snapshot_format_warnings(None) == []


def test_review_gets_the_warning_without_a_score_change():
    review = {"grade": "B", "points": 80, "feedback": "Yaxshi.", "improvements": ["x"]}
    apply_to_review(review, format_warnings([("OK.html", PYTHON)]))
    assert review["points"] == 80 and review["grade"] == "B"
    assert review["feedback"].startswith("Yaxshi.") and "⚠️ Fayl formati" in review["feedback"] and "OK.html" in review["feedback"]
    assert review["improvements"][0] == "x" and len(review["improvements"]) == 2 and review["format_warnings"]


def test_a_review_without_warnings_is_untouched():
    review = {"feedback": "Yaxshi.", "improvements": []}
    apply_to_review(review, [])
    assert review == {"feedback": "Yaxshi.", "improvements": []}


def test_the_grader_prompt_names_the_files_and_forbids_a_score_drop():
    from app.services.grok_review import _build_review_prompt
    text = _build_review_prompt(
        title="T", description="d", github_url="(ZIP)", technologies=["HTML5"], difficulty_level="Easy", previous_points=0,
        repo_content="x", repo_summary="1", lesson_context=None, format_warnings=format_warnings([("OK.html", PYTHON)]))
    assert "FAYL FORMATI OGOHLANTIRISHI" in text and "OK.html" in text and "PASAYTIRMA" in text
    assert "FAYL FORMATI" not in _build_review_prompt(
        title="T", description="d", github_url="(ZIP)", technologies=[], difficulty_level="Easy", previous_points=0,
        repo_content="x", repo_summary="1")
