"""
Team Service
팀 배정 알고리즘 및 관련 로직
"""
import random
from typing import List
from sqlalchemy.orm import Session

from models.models import Player
from dto.match import TeamAssignment


class TeamService:
    """팀 배정 서비스"""

    @staticmethod
    def assign_teams(player_ids: List[int], db: Session) -> TeamAssignment:
        """
        4명의 플레이어를 2:2로 랜덤 배정

        Args:
            player_ids: 선택된 플레이어 ID 리스트 (4명)
            db: 데이터베이스 세션

        Returns:
            TeamAssignment: 팀 A, 팀 B 배정 결과

        Raises:
            ValueError: 플레이어 수가 4명이 아닌 경우
        """
        if len(player_ids) != 4:
            raise ValueError("정확히 4명의 플레이어를 선택해야 합니다.")

        # 플레이어 존재 여부 확인
        players = db.query(Player).filter(Player.id.in_(player_ids)).all()
        if len(players) != 4:
            raise ValueError("선택한 플레이어 중 존재하지 않는 플레이어가 있습니다.")

        # 랜덤 셔플
        shuffled_ids = player_ids.copy()
        random.shuffle(shuffled_ids)

        # 2:2 배정
        team_a = shuffled_ids[:2]
        team_b = shuffled_ids[2:]

        return TeamAssignment(team_a=team_a, team_b=team_b)

    @staticmethod
    def validate_teams(team_a_ids: List[int], team_b_ids: List[int]) -> bool:
        """
        팀 구성 유효성 검증
        - 각 팀 2명씩
        - 중복 플레이어 없음

        Args:
            team_a_ids: 팀 A 플레이어 ID
            team_b_ids: 팀 B 플레이어 ID

        Returns:
            bool: 유효 여부
        """
        if len(team_a_ids) != 2 or len(team_b_ids) != 2:
            return False

        all_ids = team_a_ids + team_b_ids
        if len(set(all_ids)) != 4:  # 중복 체크
            return False

        return True