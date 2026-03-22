from fastapi import APIRouter

from src.routes.clubs_routes import router as clubs_router
from src.routes.events_routes import router as events_router
from src.routes.media_routes import router as media_router
from src.routes.positions_routes import router as positions_router
from src.routes.profile_routes import router as profile_router
from src.routes.system_routes import router as system_router
from src.routes.users_routes import router as users_router

api_routes = APIRouter()
api_routes.include_router(system_router)
api_routes.include_router(clubs_router, prefix="/api/v1")
api_routes.include_router(positions_router, prefix="/api/v1")
api_routes.include_router(events_router, prefix="/api/v1")
api_routes.include_router(users_router, prefix="/api/v1")
api_routes.include_router(profile_router, prefix="/api/v1")
api_routes.include_router(media_router, prefix="/api/v1")

__all__ = ["api_routes"]
