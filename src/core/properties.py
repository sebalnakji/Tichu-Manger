"""
환경별 설정 관리
로컬 개발 환경과 운영 환경을 분리하여 관리
"""
import os
from enum import Enum
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Environment(Enum):
    """환경 구분"""
    LOCAL = "local"
    PROD = "prod"


class Config:
    """공통 설정"""
    APP_NAME: str = "Tichu Manager"
    APP_VERSION: str = "1.0.0"

    # Logging
    LOG_CONFIG_PATH: str = "logging.yaml"

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Auth
    ADMIN_CODE: str = os.getenv("ADMIN_CODE", "admin123")

    # Supabase (공통 설정으로 이동)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_BUCKET: str = os.getenv("SUPABASE_BUCKET", "tichu-profiles")
    ENABLE_CLEANUP_SCHEDULER: bool = os.getenv(
        "ENABLE_CLEANUP_SCHEDULER", "true"
    ).lower() in {"1", "true", "yes", "on"}


class LocalConfig(Config):
    """로컬 개발 환경 설정"""
    ENV: Environment = Environment.LOCAL
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///tichu.db")

    # Storage (로컬에서도 Supabase Storage 사용)
    STORAGE_TYPE: str = "supabase"
    UPLOAD_DIR: str = "./uploads"


class ProdConfig(Config):
    """운영 환경 설정"""
    ENV: Environment = Environment.PROD
    DEBUG: bool = False

    # Database (Supabase PostgreSQL)
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Storage (Supabase Storage)
    STORAGE_TYPE: str = "supabase"
    ENABLE_CLEANUP_SCHEDULER: bool = os.getenv(
        "ENABLE_CLEANUP_SCHEDULER", "false"
    ).lower() in {"1", "true", "yes", "on"}


def get_settings():
    """
    환경에 따라 적절한 설정 반환
    APP_ENV 환경변수로 제어
    """
    env = os.getenv("APP_ENV", "local").lower()

    if env == "prod":
        return ProdConfig()
    return LocalConfig()


# 전역 설정 객체
settings = get_settings()


def validate_required_settings() -> None:
    """Fail fast with variable names only; never include secret values."""
    if settings.ENV != Environment.PROD:
        return

    required = ("DATABASE_URL", "ADMIN_CODE", "SUPABASE_URL", "SUPABASE_KEY")
    missing = [name for name in required if not getattr(settings, name, None)]
    if missing:
        raise RuntimeError(
            "Missing required production environment variables: "
            + ", ".join(missing)
        )

    if settings.ADMIN_CODE.strip().lower() in {
        "admin",
        "admin123",
        "changeme",
        "change-me-in-production",
    }:
        raise RuntimeError(
            "ADMIN_CODE must be changed from the development default in production."
        )
