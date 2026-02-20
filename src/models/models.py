"""
SQLAlchemy ORM 모델
티츄 매니저의 모든 데이터베이스 테이블 정의
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, JSON, Boolean, ForeignKey
from datetime import datetime, date

from core.database import Base


class Player(Base):
    """플레이어 정보"""
    __tablename__ = "tichu_players"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, comment="플레이어 이름")
    code = Column(String(50), nullable=False, unique=True, comment="접속 코드 (공백 불가)")
    profile_url = Column(
        String(500),
        nullable=True,
        default="https://ui-avatars.com/api/?name=User&size=150&background=9ca3af&color=fff",
        comment="프로필 이미지 URL"
    )
    created_at = Column(DateTime, default=datetime.utcnow, comment="가입일")
    is_admin = Column(Boolean, default=False, comment="관리자 여부")

    def __repr__(self):
        return f"<Player(id={self.id}, name='{self.name}', code='{self.code}')>"


class Match(Base):
    """게임 매치 기록"""
    __tablename__ = "tichu_matches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    play_date = Column(Date, default=date.today, nullable=False, comment="게임 날짜")

    # 팀 구성 (JSON 배열로 플레이어 ID 저장)
    team_a_ids = Column(JSON, nullable=False, comment="팀 A 플레이어 ID 리스트 [id1, id2]")
    team_b_ids = Column(JSON, nullable=False, comment="팀 B 플레이어 ID 리스트 [id1, id2]")

    # 총점
    score_a = Column(Integer, default=0, nullable=False, comment="팀 A 총점")
    score_b = Column(Integer, default=0, nullable=False, comment="팀 B 총점")

    # 라운드별 상세 기록 (JSON)
    rounds = Column(JSON, default=list, comment="라운드별 점수 기록")
    # [{
    #   "round": 1,
    #   "team_a_base": 100,
    #   "team_b_base": 0,
    #   "events": [
    #     {"type": "tichu", "player_id": 1, "success": true},
    #     {"type": "grand", "player_id": 3, "success": false},
    #     {"type": "one_two", "team": "A"}
    #   ]
    # }]

    # 승자 및 상태
    winner_team = Column(
        String(1),
        nullable=True,
        comment="승리 팀 ('A' or 'B')"
    )
    status = Column(
        String(20),
        default="PLAYING",
        nullable=False,
        comment="게임 상태 (PLAYING/FINISHED)"
    )

    def __repr__(self):
        return f"<Match(id={self.id}, status='{self.status}', winner='{self.winner_team}')>"


class MatchStats(Base):
    """
    개인별 티츄/라지티츄 시도 및 성공 기록
    라운드별로 기록
    """
    __tablename__ = "tichu_match_stats"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    match_id = Column(
        Integer,
        ForeignKey("tichu_matches.id", ondelete="CASCADE"),
        nullable=False,
        comment="매치 ID"
    )
    player_id = Column(
        Integer,
        ForeignKey("tichu_players.id", ondelete="CASCADE"),
        nullable=False,
        comment="플레이어 ID"
    )

    # 라운드 번호
    round_number = Column(Integer, nullable=False, comment="라운드 번호")

    # 스몰 티츄
    is_tichu_try = Column(Boolean, default=False, comment="스몰 티츄 시도 여부")
    is_tichu_succ = Column(Boolean, default=False, comment="스몰 티츄 성공 여부")

    # 라지 티츄
    is_grand_try = Column(Boolean, default=False, comment="라지 티츄 시도 여부")
    is_grand_succ = Column(Boolean, default=False, comment="라지 티츄 성공 여부")

    def __repr__(self):
        return f"<MatchStats(match_id={self.match_id}, player_id={self.player_id}, round={self.round_number})>"