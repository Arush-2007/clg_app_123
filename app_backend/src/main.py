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
_BASE_DIR = Path(__file__).resolve().parents[1]
_UPLOAD_DIR = _BASE_DIR / settings.upload_dir

app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.app_debug)

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


@app.on_event("startup")
def on_startup() -> None:
    # region agent log
    debug_log(
        run_id="run1",
        hypothesis_id="H5",
        location="main.py:on_startup",
        message="startup schema mode",
        data={"auto_create_schema": settings.auto_create_schema, "database_url_prefix": settings.database_url.split(':')[0]},
    )
    # endregion
    if settings.auto_create_schema:
        Base.metadata.create_all(bind=engine)


app.include_router(system_router)
app.include_router(clubs_router, prefix=settings.api_prefix)
app.include_router(positions_router, prefix=settings.api_prefix)
app.include_router(events_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(profile_router, prefix=settings.api_prefix)
app.include_router(media_router, prefix=settings.api_prefix)
app.mount("/uploads", StaticFiles(directory=str(_UPLOAD_DIR), check_dir=False), name="uploads")
