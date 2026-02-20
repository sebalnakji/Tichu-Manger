"""
Player DTO
플레이어 관련 요청/응답 스키마
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class PlayerCreate(BaseModel):
    """플레이어 생성 요청"""
    name: str = Field(..., min_length=1, max_length=50, description="플레이어 이름")
    code: str = Field(..., min_length=1, max_length=50, description="접속 코드 (공백 불가)")
    profile_url: Optional[str] = Field(None, description="프로필 이미지 URL")

    @field_validator('code')
    @classmethod
    def validate_no_space(cls, v: str) -> str:
        """공백 검증: 스페이스, 탭 등 모든 공백 문자 불허"""
        if re.search(r'\s', v):
            raise ValueError('코드에는 공백(띄어쓰기, 탭 등)을 포함할 수 없습니다.')
        return v


class PlayerUpdate(BaseModel):
    """플레이어 수정 요청"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    profile_url: Optional[str] = None

    @field_validator('code')
    @classmethod
    def validate_no_space(cls, v: Optional[str]) -> Optional[str]:
        """공백 검증"""
        if v is not None and re.search(r'\s', v):
            raise ValueError('코드에는 공백(띄어쓰기, 탭 등)을 포함할 수 없습니다.')
        return v


class PlayerResponse(BaseModel):
    """플레이어 응답"""
    id: int
    name: str
    code: str
    profile_url: Optional[str]
    created_at: datetime
    is_admin: bool

    class Config:
        from_attributes = True