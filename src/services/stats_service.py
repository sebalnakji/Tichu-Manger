"""
Stats Service
통계 계산 및 랭킹 로직
"""
from typing import List, Optional
from sqlalchemy import func, extract, or_
from sqlalchemy.orm import Session
from itertools import combinations

from models.models import Player, Match, MatchStats
from dto.stats import PlayerStats, TeamStats


class StatsService:
    """통계 계산 서비스"""

    @staticmethod
    def get_player_stats(
        player_id: int,
        db: Session,
        year: Optional[int] = None
    ) -> Optional[PlayerStats]:
        """
        개인 전적 통계 조회

        Args:
            player_id: 플레이어 ID
            db: 데이터베이스 세션
            year: 연도 필터 (None이면 전체)

        Returns:
            PlayerStats: 플레이어 통계 또는 None
        """
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return None

        # 연도 필터링 쿼리
        query = db.query(Match).filter(Match.status == "FINISHED")
        if year:
            query = query.filter(extract('year', Match.play_date) == year)

        matches = query.all()

        # 전체 전적 계산
        total_games = 0
        wins = 0
        losses = 0

        for match in matches:
            if player_id in match.team_a_ids:
                total_games += 1
                if match.winner_team == "A":
                    wins += 1
                else:
                    losses += 1
            elif player_id in match.team_b_ids:
                total_games += 1
                if match.winner_team == "B":
                    wins += 1
                else:
                    losses += 1

        # 최근 10판 전적 계산
        recent_query = db.query(Match).filter(Match.status == "FINISHED")
        if year:
            recent_query = recent_query.filter(extract('year', Match.play_date) == year)

        recent_matches = recent_query.order_by(Match.play_date.desc()).limit(20).all()

        recent_games = 0
        recent_wins = 0

        for match in recent_matches:
            if recent_games >= 10:
                break

            if player_id in match.team_a_ids:
                recent_games += 1
                if match.winner_team == "A":
                    recent_wins += 1
            elif player_id in match.team_b_ids:
                recent_games += 1
                if match.winner_team == "B":
                    recent_wins += 1

        # 티츄 통계 계산
        stats_query = db.query(MatchStats).filter(MatchStats.player_id == player_id)
        if year:
            stats_query = stats_query.join(Match).filter(
                extract('year', Match.play_date) == year
            )

        tichu_stats = stats_query.all()

        tichu_try = sum(1 for s in tichu_stats if s.is_tichu_try)
        tichu_success = sum(1 for s in tichu_stats if s.is_tichu_succ)
        grand_try = sum(1 for s in tichu_stats if s.is_grand_try)
        grand_success = sum(1 for s in tichu_stats if s.is_grand_succ)

        # 비율 계산
        win_rate = (wins / total_games * 100) if total_games > 0 else 0.0
        recent_win_rate = (recent_wins / recent_games * 100) if recent_games > 0 else 0.0
        tichu_success_rate = (tichu_success / tichu_try * 100) if tichu_try > 0 else 0.0
        grand_success_rate = (grand_success / grand_try * 100) if grand_try > 0 else 0.0

        return PlayerStats(
            player_id=player.id,
            player_name=player.name,
            profile_url=player.profile_url,
            total_games=total_games,
            wins=wins,
            losses=losses,
            win_rate=round(win_rate, 1),
            recent_games=recent_games,
            recent_wins=recent_wins,
            recent_win_rate=round(recent_win_rate, 1),
            tichu_try=tichu_try,
            tichu_success=tichu_success,
            tichu_success_rate=round(tichu_success_rate, 2),
            grand_try=grand_try,
            grand_success=grand_success,
            grand_success_rate=round(grand_success_rate, 2),
        )

    @staticmethod
    def get_team_stats(
        player1_id: int,
        player2_id: int,
        db: Session,
        year: Optional[int] = None
    ) -> Optional[TeamStats]:
        """
        팀 전적 통계 조회 (순서 무관)

        Args:
            player1_id: 플레이어 1 ID
            player2_id: 플레이어 2 ID
            db: 데이터베이스 세션
            year: 연도 필터

        Returns:
            TeamStats: 팀 통계 또는 None
        """
        # 플레이어 정보 조회
        player1 = db.query(Player).filter(Player.id == player1_id).first()
        player2 = db.query(Player).filter(Player.id == player2_id).first()

        if not player1 or not player2:
            return None

        # 팀 이름 생성 (가나다순)
        names = sorted([player1.name, player2.name])
        team_name = f"{names[0]}/{names[1]} 팀"

        # 연도 필터링
        query = db.query(Match).filter(Match.status == "FINISHED")
        if year:
            query = query.filter(extract('year', Match.play_date) == year)

        matches = query.all()

        # 두 사람이 같은 팀이었던 매치 찾기 (순서 무관)
        total_games = 0
        wins = 0
        losses = 0
        match_ids = []

        for match in matches:
            # team_a에 두 사람이 모두 있는지 확인
            if player1_id in match.team_a_ids and player2_id in match.team_a_ids:
                total_games += 1
                match_ids.append(match.id)
                if match.winner_team == "A":
                    wins += 1
                else:
                    losses += 1
            # team_b에 두 사람이 모두 있는지 확인
            elif player1_id in match.team_b_ids and player2_id in match.team_b_ids:
                total_games += 1
                match_ids.append(match.id)
                if match.winner_team == "B":
                    wins += 1
                else:
                    losses += 1

        # 티츄 통계 (두 사람 합산)
        if match_ids:
            stats_query = db.query(MatchStats).filter(
                MatchStats.match_id.in_(match_ids),
                or_(MatchStats.player_id == player1_id, MatchStats.player_id == player2_id)
            )

            tichu_stats = stats_query.all()

            tichu_try = sum(1 for s in tichu_stats if s.is_tichu_try)
            tichu_success = sum(1 for s in tichu_stats if s.is_tichu_succ)
            grand_try = sum(1 for s in tichu_stats if s.is_grand_try)
            grand_success = sum(1 for s in tichu_stats if s.is_grand_succ)
        else:
            tichu_try = tichu_success = grand_try = grand_success = 0

        # 비율 계산
        win_rate = (wins / total_games * 100) if total_games > 0 else 0.0
        tichu_success_rate = (tichu_success / tichu_try * 100) if tichu_try > 0 else 0.0
        grand_success_rate = (grand_success / grand_try * 100) if grand_try > 0 else 0.0

        # ID 순서를 정규화 (작은 ID가 player1)
        if player1_id > player2_id:
            player1_id, player2_id = player2_id, player1_id
            player1, player2 = player2, player1

        return TeamStats(
            player1_id=player1.id,
            player2_id=player2.id,
            player1_name=player1.name,
            player2_name=player2.name,
            team_name=team_name,
            total_games=total_games,
            wins=wins,
            losses=losses,
            win_rate=round(win_rate, 1),
            tichu_try=tichu_try,  # 추가
            tichu_success=tichu_success,  # 추가
            tichu_success_rate=round(tichu_success_rate, 1),
            grand_try=grand_try,  # 추가
            grand_success=grand_success,  # 추가
            grand_success_rate=round(grand_success_rate, 1),
        )

    @staticmethod
    def get_team_leaderboard(
        db: Session,
        year: Optional[int] = None
    ) -> List[TeamStats]:
        """
        팀 랭킹 조회
        정렬 우선순위: 승수 > 승률

        Args:
            db: 데이터베이스 세션
            year: 연도 필터

        Returns:
            List[TeamStats]: 정렬된 팀 통계 리스트
        """
        # 모든 플레이어 조합 찾기
        players = db.query(Player).all()

        # 2명씩 조합 생성
        team_combinations = list(combinations(players, 2))

        stats_list = []
        for player1, player2 in team_combinations:
            stats = StatsService.get_team_stats(player1.id, player2.id, db, year)
            if stats and stats.total_games > 0:  # 함께 게임한 기록이 있는 팀만
                stats_list.append(stats)

        # 정렬: 승수 > 승률
        stats_list.sort(
            key=lambda x: (
                -x.wins,  # 승수 내림차순
                -x.win_rate,  # 승률 내림차순
            )
        )

        return stats_list

    @staticmethod
    def get_leaderboard(
        db: Session,
        year: Optional[int] = None
    ) -> List[PlayerStats]:
        """
        전체 플레이어 랭킹 조회
        정렬 우선순위: 승수 > 승률 > 티츄 성공률 > 라지티츄 성공률

        Args:
            db: 데이터베이스 세션
            year: 연도 필터

        Returns:
            List[PlayerStats]: 정렬된 플레이어 통계 리스트
        """
        players = db.query(Player).all()
        stats_list = []

        for player in players:
            stats = StatsService.get_player_stats(player.id, db, year)
            if stats and stats.total_games > 0:  # 게임 기록이 있는 플레이어만
                stats_list.append(stats)

        # 정렬: 승수 > 승률 > 티츄 성공률 > 라지티츄 성공률
        stats_list.sort(
            key=lambda x: (
                -x.wins,  # 승수 내림차순
                -x.win_rate,  # 승률 내림차순
                -x.tichu_success_rate,  # 티츄 성공률 내림차순
                -x.grand_success_rate,  # 라지티츄 성공률 내림차순
            )
        )

        return stats_list