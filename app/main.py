import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.v1.router import api_router
from app.db.database import init_db
from app.core.exceptions import register_exception_handlers
from app.scheduler import start_scheduler, scheduler


# Bu yerdagi ortiqcha app = FastAPI(...) qismini o'chirib tashlang,
# chunki pastda create_application funksiyasi yangi app yaratadi.

@asynccontextmanager
async def lifespan(app: FastAPI):

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    print(" Student Programming Platform started!")
    await init_db()

    # Scheduler ishga tushirish
    start_scheduler()

    yield

    # Shutdown
    scheduler.shutdown()
    print(" Student Programming Platform suspended...")


def create_application() -> FastAPI:
    # SHU YERGA QO'SHAMIZ:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        # Mana bu parametr hammasini yopib qo'yadi:
        swagger_ui_parameters={"docExpansion": "none"}
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    register_exception_handlers(app)

    return app


# Endi bu app obyekti hamma sozlamalarni o'z ichiga oladi
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
