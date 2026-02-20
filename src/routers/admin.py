"""
Admin Router
관리자 전용 API 엔드포인트
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from core.database import get_db
from core.properties import settings
from core.logging_config import get_logger
from models.models import Player, Match, MatchStats
from dto.player import PlayerResponse

router = APIRouter(prefix="/api/admin", tags=["Admin"])
logger = get_logger(__name__)


def verify_admin(authorization: str = Header(None)):
    """
    관리자 권한 확인 미들웨어
    Authorization 헤더에 관리자 코드가 있는지 확인
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다."
        )

    # "Bearer admin123" 형식 또는 "admin123" 직접 전달
    code = authorization.replace("Bearer ", "").strip()

    if code != settings.ADMIN_CODE:
        logger.warning(f"관리자 권한 확인 실패")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 없습니다."
        )

    return True


@router.get("/users", response_model=List[PlayerResponse])
def get_all_users(
        db: Session = Depends(get_db),
        _: bool = Depends(verify_admin)
):
    """
    전체 유저 목록 조회 (관리자 전용)
    코드 포함하여 반환
    """
    players = db.query(Player).order_by(Player.created_at.desc()).all()
    logger.info(f"관리자: 전체 유저 목록 조회 ({len(players)}명)")
    return players


@router.delete("/users/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_admin(
        player_id: int,
        db: Session = Depends(get_db),
        _: bool = Depends(verify_admin)
):
    """
    유저 삭제 (관리자 전용)
    """
    player = db.query(Player).filter(Player.id == player_id).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"플레이어 ID {player_id}를 찾을 수 없습니다."
        )

    player_name = player.name
    db.delete(player)
    db.commit()

    logger.info(f"관리자: 유저 삭제 - {player_name} (ID: {player_id})")
    return None


@router.delete("/reset-all", status_code=status.HTTP_204_NO_CONTENT)
def reset_all_data(
        db: Session = Depends(get_db),
        _: bool = Depends(verify_admin)
):
    """
    전체 데이터 초기화 (관리자 전용)
    경고: 모든 플레이어, 매치, 통계 데이터 삭제
    """
    try:
        # 통계 삭제
        stats_count = db.query(MatchStats).delete()

        # 매치 삭제
        matches_count = db.query(Match).delete()

        # 플레이어 삭제
        players_count = db.query(Player).delete()

        db.commit()

        logger.warning(
            f"관리자: 전체 데이터 초기화 완료 - "
            f"플레이어 {players_count}명, 매치 {matches_count}개, 통계 {stats_count}개 삭제"
        )

        return None
    except Exception as e:
        db.rollback()
        logger.error(f"데이터 초기화 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="데이터 초기화 중 오류가 발생했습니다."
        )


@router.get("/matches/recent")
def get_recent_matches(
        limit: int = 10,
        db: Session = Depends(get_db),
        _: bool = Depends(verify_admin)
):
    """
    최근 매치 기록 조회 (관리자 전용)
    """
    matches = db.query(Match).order_by(Match.play_date.desc()).limit(limit).all()

    result = []
    for match in matches:
        result.append({
            "id": match.id,
            "play_date": match.play_date.isoformat(),
            "team_a_ids": match.team_a_ids,
            "team_b_ids": match.team_b_ids,
            "score_a": match.score_a,
            "score_b": match.score_b,
            "winner_team": match.winner_team,
            "status": match.status
        })

    logger.info(f"관리자: 최근 매치 {len(result)}개 조회")
    return result


@router.delete("/matches/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match_by_admin(
        match_id: int,
        db: Session = Depends(get_db),
        _: bool = Depends(verify_admin)
):
    """
    특정 매치 삭제 (관리자 전용)
    잘못된 기록 수정용
    """
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"매치 ID {match_id}를 찾을 수 없습니다."
        )

    db.delete(match)
    db.commit()

    logger.info(f"관리자: 매치 삭제 - ID {match_id}")
    return None