"""
Score Service
점수 계산 및 라운드 관리 로직
"""
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from models.models import Match, MatchStats
from core.logging_config import get_logger

logger = get_logger(__name__)


class ScoreService:
    """점수 계산 서비스"""

    @staticmethod
    def calculate_round_score(
        team_a_base: int,
        team_b_base: int,
        events: List[dict],
        team_a_ids: List[int],
        team_b_ids: List[int]
    ) -> Dict:
        """
        라운드 최종 점수 계산

        Args:
            team_a_base: 팀 A 기본 점수
            team_b_base: 팀 B 기본 점수
            events: 이벤트 리스트 (티츄/라티/원투)
            team_a_ids: 팀 A 플레이어 ID 리스트
            team_b_ids: 팀 B 플레이어 ID 리스트

        Returns:
            {
                "team_a_total": int,
                "team_b_total": int,
                "team_a_bonus": int,
                "team_b_bonus": int
            }
        """
        # 원투 확인
        one_two_event = next((e for e in events if e["type"] == "one_two"), None)

        if one_two_event:
            # 원투 발생 시 기본 점수 무시
            if one_two_event.get("team") == "A":
                team_a_total = 200
                team_b_total = 0
            else:
                team_a_total = 0
                team_b_total = 200

            # 티츄/라티 보너스는 계산
            team_a_bonus = 0
            team_b_bonus = 0

            for event in events:
                if event["type"] == "tichu":
                    bonus = 100 if event.get("success") else -100
                    if event["player_id"] in team_a_ids:
                        team_a_bonus += bonus
                    else:
                        team_b_bonus += bonus

                elif event["type"] == "grand":
                    bonus = 200 if event.get("success") else -200
                    if event["player_id"] in team_a_ids:
                        team_a_bonus += bonus
                    else:
                        team_b_bonus += bonus

            team_a_total += team_a_bonus
            team_b_total += team_b_bonus

            return {
                "team_a_total": team_a_total,
                "team_b_total": team_b_total,
                "team_a_bonus": team_a_total - (200 if one_two_event.get("team") == "A" else 0),
                "team_b_bonus": team_b_total - (200 if one_two_event.get("team") == "B" else 0)
            }

        else:
            # 원투 없을 때는 기존 로직
            team_a_bonus = 0
            team_b_bonus = 0

            for event in events:
                if event["type"] == "tichu":
                    bonus = 100 if event.get("success") else -100
                    if event["player_id"] in team_a_ids:
                        team_a_bonus += bonus
                    else:
                        team_b_bonus += bonus

                elif event["type"] == "grand":
                    bonus = 200 if event.get("success") else -200
                    if event["player_id"] in team_a_ids:
                        team_a_bonus += bonus
                    else:
                        team_b_bonus += bonus

            return {
                "team_a_total": team_a_base + team_a_bonus,
                "team_b_total": team_b_base + team_b_bonus,
                "team_a_bonus": team_a_bonus,
                "team_b_bonus": team_b_bonus
            }


    @staticmethod
    def save_round_stats(
        match_id: int,
        round_number: int,
        events: List[dict],
        db: Session
    ):
        """
        라운드 이벤트를 MatchStats에 저장

        Args:
            match_id: 매치 ID
            round_number: 라운드 번호
            events: 이벤트 리스트
            db: 데이터베이스 세션
        """
        # 기존 해당 라운드 통계 삭제 (수정 시)
        db.query(MatchStats).filter(
            MatchStats.match_id == match_id,
            MatchStats.round_number == round_number
        ).delete()

        # 새 통계 저장
        for event in events:
            if event["type"] in ["tichu", "grand"]:
                stats = MatchStats(
                    match_id=match_id,
                    player_id=event["player_id"],
                    round_number=round_number,
                    is_tichu_try=(event["type"] == "tichu"),
                    is_tichu_succ=(event["type"] == "tichu" and event.get("success", False)),
                    is_grand_try=(event["type"] == "grand"),
                    is_grand_succ=(event["type"] == "grand" and event.get("success", False))
                )
                db.add(stats)

        db.commit()
        logger.info(f"라운드 {round_number} 통계 저장 완료 (매치 ID: {match_id})")


    @staticmethod
    def update_match_total_score(match_id: int, db: Session):
        """
        매치의 총점 계산 및 업데이트
        모든 라운드 점수를 합산

        Args:
            match_id: 매치 ID
            db: 데이터베이스 세션
        """
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            return

        total_a = 0
        total_b = 0

        for round_data in match.rounds:
            result = ScoreService.calculate_round_score(
                round_data.get("team_a_base", 0),
                round_data.get("team_b_base", 0),
                round_data.get("events", []),
                match.team_a_ids,
                match.team_b_ids
            )
            total_a += result["team_a_total"]
            total_b += result["team_b_total"]

        match.score_a = total_a
        match.score_b = total_b

        # 1000점 도달 확인
        if total_a >= 1000 or total_b >= 1000:
            match.status = "FINISHED"
            match.winner_team = "A" if total_a > total_b else "B"
        else:
            # 점수 수정으로 1000점 미만이 된 경우 → 게임 재개
            if match.status == "FINISHED":
                match.status = "PLAYING"
                match.winner_team = None

        db.commit()
        logger.info(f"총점 업데이트: 매치 ID {match_id}, A={total_a}, B={total_b}")