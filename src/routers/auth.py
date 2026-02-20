"""
Auth Router
인증 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.database import get_db
from core.properties import settings
from models.models import Player
from utils.hangul_converter import convert_hangul_to_english

router = APIRouter(prefix="/api/auth", tags=["Auth"])


class AuthRequest(BaseModel):
    """인증 요청"""
    code: str


class AuthResponse(BaseModel):
    """인증 응답"""
    role: str
    player_id: int = None
    player_name: str = None


@router.post("/verify", response_model=AuthResponse)
def verify_code(auth: AuthRequest, db: Session = Depends(get_db)):
    """
    코드 인증
    - 관리자 코드 확인
    - 플레이어 코드 확인
    """
    # 입력받은 코드를 영문 자판으로 변환
    english_code = convert_hangul_to_english(auth.code)

    # 1. 관리자 코드 확인
    if english_code == settings.ADMIN_CODE:
        return AuthResponse(role="admin")

    # 2. 플레이어 코드 확인 (변환된 코드로 비교)
    player = db.query(Player).filter(Player.code == english_code).first()
    if player:
        return AuthResponse(
            role="player",
            player_id=player.id,
            player_name=player.name
        )

    # 3. 일치하는 코드 없음
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="코드가 일치하지 않습니다."
    )