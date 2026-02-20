"""
데이터베이스 연결 및 세션 관리
SQLAlchemy를 사용하여 SQLite/PostgreSQL 추상화
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from core.properties import settings

# SQLAlchemy Engine 생성
# check_same_thread=False: SQLite에서 멀티스레드 사용 허용
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG  # DEBUG 모드에서 SQL 쿼리 로그 출력
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Class for Models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션 의존성 주입용 함수
    FastAPI의 Depends()에서 사용

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    데이터베이스 초기화
    모든 테이블 생성 (애플리케이션 시작 시 호출)
    """
    from models.models import Player, Match, MatchStats  # 순환 import 방지
    Base.metadata.create_all(bind=engine)