import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.v1.router import api_router
from app.db.database import init_db
from app.core.exceptions import register_exception_handlers
from app.scheduler import start_scheduler, scheduler
from app.utils import certificate as cert_utils
from app.db import base  # noqa: F401  ensures all models register on Base.metadata

UPLOAD_ROOT = Path(settings.UPLOAD_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Student Programming Platform started!")
    await init_db()
    start_scheduler()

    # Shablon faylni xotiraga olish
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "static", "web_certificate.pdf")
    abs_path = os.path.abspath(path)
    print(f"File path: {abs_path}")
    print(f"Exists: {os.path.exists(abs_path)}")
    try:
        with open(abs_path, "rb") as f:
            cert_utils._COURSE_TEMPLATE_BYTES = f.read()
            print(f"Template loaded: {len(cert_utils._COURSE_TEMPLATE_BYTES)} bytes")
    except Exception as e:
        print(f"Template not loaded: {e}")

    yield

    # Shutdown
    scheduler.shutdown()
    print("Student Programming Platform suspended...")


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


async def security_headers_middleware(request, call_next):
    response = await call_next(request)
    for key, value in SECURITY_HEADERS.items():
        response.headers.setdefault(key, value)
    return response


def create_application() -> FastAPI:
    # Anchor upload dirs to settings.UPLOAD_DIR (absolute, derived from this
    # file). Relative paths break depending on uvicorn CWD.
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    (UPLOAD_ROOT / "courses").mkdir(parents=True, exist_ok=True)
    (UPLOAD_ROOT / "projects").mkdir(parents=True, exist_ok=True)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if settings.DEBUG else None,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
        swagger_ui_parameters={"docExpansion": "none"},
    )

    # Explicit origins required when allow_credentials=True; the CORS spec
    # forbids "*" + credentials and browsers will reject it anyway.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(security_headers_middleware)

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_ROOT)), name="uploads")
    register_exception_handlers(app)

    return app


app = create_application()


@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Student Platform API ishlayapti!",
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
