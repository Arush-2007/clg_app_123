import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.core.config import get_settings
from src.core.database import Base, engine
from src.core.debug_log import debug_log
from src.core.logging import configure_logging
from src.core.middleware import (
    RateLimitMiddleware,
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
)
from src.routes.clubs_routes import router as clubs_router
from src.routes.events_routes import router as events_router
from src.routes.media_routes import router as media_router
from src.routes.positions_routes import router as positions_router
from src.routes.profile_routes import router as profile_router
from src.routes.system_routes import router as system_router
from src.routes.users_routes import router as users_router

settings = get_settings()
configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    debug_log(
        run_id="run1",
        hypothesis_id="H5",
        location="main.py:lifespan:startup",
        message="startup schema mode",
        data={"auto_create_schema": settings.auto_create_schema, "database_url_prefix": settings.database_url.split(':')[0]},
    )
    if settings.auto_create_schema:
        Base.metadata.create_all(bind=engine)
    yield
    # --- shutdown (nothing needed yet) ---


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.app_debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)
app.add_middleware(SecurityHeadersMiddleware)
app.include_router(system_router)
app.include_router(clubs_router, prefix=settings.api_prefix)
app.include_router(positions_router, prefix=settings.api_prefix)
app.include_router(events_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(profile_router, prefix=settings.api_prefix)
app.include_router(media_router, prefix=settings.api_prefix)

storage_provider = os.environ.get("STORAGE_PROVIDER", "local").lower()
if storage_provider == "local":
    uploads_dir = Path(settings.upload_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
