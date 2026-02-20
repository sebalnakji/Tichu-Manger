"""
Core 모듈
환경 설정, 데이터베이스, 로깅 초기화
"""
from core.properties import settings
from core.database import get_db, init_db
from core.logging_config import setup_logging, get_logger

__all__ = [
    "settings",
    "get_db",
    "init_db",
    "setup_logging",
    "get_logger",
]