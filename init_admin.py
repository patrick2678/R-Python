from pathlib import Path
import time

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles

from app.core.logger import logger
from app.core.metrics import record_request
from app.database import Base, engine, SessionLocal
from app.models import user, post, comment
from app.routes.auth import router as auth_router
from app.routes.posts import router as posts_router
from app.routes.comment import router as comments_router
from app.routes.users import router as users_router
from app.routes.dashboard import router as dashboard_router
from app.core.init_admin import create_admin_if_not_exists


Base.metadata.create_all(bind=engine)

db = SessionLocal()
create_admin_if_not_exists(db)
db.close()

app = FastAPI(
    title="Blog Management System",
    description="Backend API for blog management using FastAPI",
    version="1.0.0"
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    logger.info(f"Incoming request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
    except Exception:
        process_time_ms = (time.time() - start_time) * 1000
        record_request(
            request.method,
            request.url.path,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            process_time_ms,
        )
        logger.exception(
            f"Unhandled error: {request.method} {request.url.path} "
            f"Status: 500 Time: {process_time_ms:.2f}ms"
        )
        raise

    process_time_ms = (time.time() - start_time) * 1000

    record_request(request.method, request.url.path, response.status_code, process_time_ms)

    logger.info(
        f"Completed request: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {process_time_ms:.2f}ms"
    )

    return response


app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(users_router)
app.include_router(dashboard_router)

frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
if frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Blog Management System API is running successfully"}
