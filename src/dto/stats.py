"""
Stats DTO
통계 관련 데이터 전송 객체
"""
from pydantic import BaseModel
from typing import Optional


class PlayerStats(BaseModel):
    """개인 통계"""
    player_id: int
    player_name: str
    profile_url: str
    total_games: int
    wins: int
    losses: int
    win_rate: float
    recent_games: int
    recent_wins: int
    recent_win_rate: float
    tichu_try: int
    tichu_success: int
    tichu_success_rate: float
    grand_try: int
    grand_success: int
    grand_success_rate: float


class TeamStats(BaseModel):
    """팀 통계"""
    player1_id: int
    player2_id: int
    player1_name: str
    player2_name: str
    team_name: str
    total_games: int
    wins: int
    losses: int
    win_rate: float
    tichu_try: int  # 추가
    tichu_success: int  # 추가
    tichu_success_rate: float
    grand_try: int  # 추가
    grand_success: int  # 추가
    grand_success_rate: float


class LeaderboardResponse(BaseModel):
    """개인 랭킹 응답"""
    rank: int
    stats: PlayerStats


class TeamLeaderboardResponse(BaseModel):
    """팀 랭킹 응답"""
    rank: int
    stats: TeamStats