"""
Routers 모듈
FastAPI API 엔드포인트
"""
from routers.players import router as players_router
from routers.matches import router as matches_router
from routers.stats import router as stats_router
from routers.auth import router as auth_router
from routers.admin import router as admin_router

__all__ = [
    "players_router",
    "matches_router",
    "stats_router",
    "auth_router",
    "admin_router",
]