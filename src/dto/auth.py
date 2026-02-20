"""
Auth DTO
인증 관련 요청/응답 스키마
"""
from pydantic import BaseModel, Field, field_validator
from typing import Literal
import re


class AuthRequest(BaseModel):
    """코드 검증 요청"""
    code: str = Field(..., min_length=1, max_length=50, description="접속 코드")

    @field_validator('code')
    @classmethod
    def validate_no_space(cls, v: str) -> str:
        """공백 검증"""
        if re.search(r'\s', v):
            raise ValueError('코드에는 공백을 포함할 수 없습니다.')
        return v


class AuthResponse(BaseModel):
    """코드 검증 응답"""
    role: Literal["admin", "user"]
    player_id: int = None
    player_name: str = None
    message: str = "인증 성공"