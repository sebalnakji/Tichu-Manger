"""
DTO 모듈
Pydantic 요청/응답 스키마
"""
from dto.player import PlayerCreate, PlayerUpdate, PlayerResponse
from dto.match import MatchCreate, RoundScoreRequest, MatchResponse, TeamAssignment
from dto.stats import PlayerStats, TeamStats, LeaderboardResponse

__all__ = [
    # Player
    "PlayerCreate",
    "PlayerUpdate",
    "PlayerResponse",

    # Match
    "MatchCreate",
    "RoundScoreRequest",
    "MatchResponse",
    "TeamAssignment",

    # Stats
    "PlayerStats",
    "TeamStats",
    "LeaderboardResponse",
]