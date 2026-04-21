# app/utils/constants.py

ALLOWED_EXTENSIONS = {".py", ".js", ".ts", ".html", ".css"}

MAX_FILE_SIZE = 10 * 1024 * 1024

UPLOAD_DIR = "./uploads"

POINTS_MAP = {
    "Easy":   (10,  30),
    "Medium": (30,  60),
    "Hard":   (60, 100),
}

GRADE_MULTIPLIERS = {
    "A": 1.00,
    "B": 0.85,
    "C": 0.70,
    "D": 0.50,
    "F": 0.00,
}