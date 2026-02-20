"""
Players Router
플레이어 관리 관련 API 엔드포인트
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session

from core.database import get_db
from core.logging_config import get_logger
from models.models import Player
from dto.player import PlayerCreate, PlayerUpdate, PlayerResponse
from utils.hangul_converter import convert_hangul_to_english
from services.storage_service import storage_service

router = APIRouter(prefix="/api/players", tags=["Players"])
logger = get_logger(__name__)


@router.post("/", response_model=PlayerResponse)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    """
    새 플레이어 생성
    """
    # 코드를 영문 자판으로 변환
    english_code = convert_hangul_to_english(player.code)

    # 중복 확인 (변환된 코드로)
    existing = db.query(Player).filter(Player.code == english_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 코드입니다."
        )

    # ⭐ 플레이어 이름으로 UI Avatars 생성
    default_profile = f"https://ui-avatars.com/api/?name={player.name}&size=150&background=9ca3af&color=fff"

    new_player = Player(
        name=player.name,
        code=english_code,  # 변환된 코드 저장
        profile_url=player.profile_url or default_profile  # ⭐ 플레이어별 기본 이미지
    )

    db.add(new_player)
    db.commit()
    db.refresh(new_player)

    logger.info(f"플레이어 생성: {new_player.name} (코드: {english_code})")
    return new_player


@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(
    player_id: int,
    player: PlayerUpdate,
    db: Session = Depends(get_db)
):
    """
    플레이어 정보 수정
    """
    existing_player = db.query(Player).filter(Player.id == player_id).first()
    if not existing_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"플레이어 ID {player_id}를 찾을 수 없습니다."
        )

    # 이름 수정
    if player.name is not None:
        existing_player.name = player.name

    # 코드 수정
    if player.code is not None:
        # 코드를 영문 자판으로 변환
        english_code = convert_hangul_to_english(player.code)

        # 중복 확인 (자기 자신 제외)
        duplicate = db.query(Player).filter(
            Player.code == english_code,
            Player.id != player_id
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 코드입니다."
            )

        existing_player.code = english_code
        logger.info(f"플레이어 코드 변경: {existing_player.name} → {english_code}")

    # 프로필 이미지 수정
    if player.profile_url is not None:
        existing_player.profile_url = player.profile_url

    db.commit()
    db.refresh(existing_player)

    logger.info(f"플레이어 수정: ID {player_id}")
    return existing_player


@router.post("/{player_id}/upload-profile")
async def upload_profile_image(
    player_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    프로필 이미지 업로드

    Args:
        player_id: 플레이어 ID
        file: 업로드할 이미지 파일

    Returns:
        dict: 업로드된 이미지 URL
    """
    # 플레이어 존재 확인
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"플레이어 ID {player_id}를 찾을 수 없습니다."
        )

    # 파일 타입 검증
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지 파일만 업로드 가능합니다."
        )

    # 파일 크기 검증 (5MB 제한)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="파일 크기는 5MB를 초과할 수 없습니다."
        )

    # 파일 확장자 추출
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="jpg, jpeg, png, webp 파일만 업로드 가능합니다."
        )

    # Supabase Storage에 업로드
    public_url = storage_service.upload_profile_image(
        player_id=player_id,
        file_content=file_content,
        file_extension=file_extension
    )

    if not public_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="이미지 업로드에 실패했습니다."
        )

    # ⭐ 기존 프로필 이미지 삭제 (Supabase Storage만)
    if player.profile_url and "supabase" in player.profile_url:
        storage_service.delete_profile_image(player.profile_url)

    # DB에 새 이미지 URL 저장
    player.profile_url = public_url
    db.commit()
    db.refresh(player)

    logger.info(f"프로필 이미지 업로드 완료: {player.name} → {public_url}")

    return {
        "message": "프로필 이미지가 업로드되었습니다.",
        "profile_url": public_url
    }


@router.post("/{player_id}/reset-profile")
async def reset_profile_image(
    player_id: int,
    db: Session = Depends(get_db)
):
    """
    프로필 이미지를 기본 이미지로 초기화

    Args:
        player_id: 플레이어 ID

    Returns:
        dict: 기본 이미지 URL
    """
    # 플레이어 존재 확인
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"플레이어 ID {player_id}를 찾을 수 없습니다."
        )

    # ⭐ 기존 프로필 이미지 삭제 (Supabase Storage만)
    if player.profile_url and "supabase" in player.profile_url:
        storage_service.delete_profile_image(player.profile_url)

    # ⭐ UI Avatars로 기본 이미지 생성
    default_url = f"https://ui-avatars.com/api/?name={player.name}&size=150&background=9ca3af&color=fff"
    player.profile_url = default_url
    db.commit()
    db.refresh(player)

    logger.info(f"프로필 이미지 초기화: {player.name} → 기본 이미지")

    return {
        "message": "프로필 이미지가 기본 이미지로 변경되었습니다.",
        "profile_url": default_url
    }


@router.get("/", response_model=List[PlayerResponse])
def get_all_players(db: Session = Depends(get_db)):
    """
    전체 플레이어 목록 조회
    """
    players = db.query(Player).all()
    return players


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    """
    특정 플레이어 조회
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"플레이어 ID {player_id}를 찾을 수 없습니다."
        )
    return player


@router.delete("/{player_id}")
def delete_player(player_id: int, db: Session = Depends(get_db)):
    """
    플레이어 삭제
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"플레이어 ID {player_id}를 찾을 수 없습니다."
        )

    # ⭐ 프로필 이미지 삭제 (Supabase Storage만)
    if player.profile_url and "supabase" in player.profile_url:
        storage_service.delete_profile_image(player.profile_url)

    db.delete(player)
    db.commit()

    logger.info(f"플레이어 삭제: ID {player_id} ({player.name})")
    return {"message": f"플레이어 {player.name}이(가) 삭제되었습니다."}