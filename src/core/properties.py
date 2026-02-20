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