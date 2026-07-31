# Tichu-Manager

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Jinja2](https://img.shields.io/badge/Jinja2-B41717?logo=jinja&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?logo=supabase&logoColor=white)

친목 모임용 카드 게임 **티츄(Tichu)** 점수 관리 웹앱입니다.

모바일 환경에 최적화되어 있으며, 게임 진행 중 실시간 점수 기록과 랭킹 관리를 지원합니다.

## 주요 기능

- **게임 관리** — 2v2 랜덤 팀 배정, 라운드별 점수 입력, 1000점 승리 판정
- **특수 이벤트** — 스몰 티츄 / 라지 티츄 / 원투 기록 및 보너스 계산
- **랭킹** — 개인 / 팀 랭킹, 시즌별 승률 및 티츄 성공률 통계
- **프로필** — 프로필 사진 업로드, 닉네임/코드 관리
- **관리자** — 유저 관리, 기록 수정, 테이블별/시즌별 데이터 초기화

## 기술 스택

| 구분 | 기술 |
|---|---|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, Jinja2 |
| **Frontend** | Vanilla JS, Tailwind CSS (CDN) |
| **Storage** | Supabase Storage (메타데이터 + 프로필 이미지) |
| **Scheduler** | APScheduler (미완료 게임 자동 정리) |

### 환경별 구성

- **개발 환경** — SQLite
- **운영 환경** — Koyeb Washington + Supabase US + UptimeRobot

## 실행 방법

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

cd src
python main.py
```

`http://localhost:8000`에서 확인할 수 있습니다.

## 성능 테스트

2026-07-31 서울에서 각 엔드포인트를 10회 워밍업한 뒤 30회씩 순차 측정했습니다.
아래 값은 응답 시간 중앙값(p50)이며 모든 요청이 성공했습니다.

| 엔드포인트 | Koyeb(US) + Supabase(US) | Render(SG) + Supabase(KR) | 더 빠른 환경 |
|---|---:|---:|---|
| `/health` | 209.01ms | **132.99ms** | Render |
| `/` | 208.30ms | **120.64ms** | Render |
| `/api/players/` | **231.81ms** | 338.68ms | Koyeb |
| `/api/matches/finished` | **310.94ms** | 477.25ms | Koyeb |
| `/api/stats/leaderboard` | **302.32ms** | 688.39ms | Koyeb |
| `/api/players/{id}` | **228.97ms** | 334.62ms | Koyeb |

| 요약 | Koyeb(US) + Supabase(US) | Render(SG) + Supabase(KR) |
|---|---:|---:|
| 전체 평균 p50 | **248.56ms** | 348.76ms |
| DB 기능 평균 p50 | **268.51ms** | 459.74ms |
| 실패 | 0/180 | 0/180 |

Render는 단순 응답이 빠르지만, 실제 게임에서 사용하는 DB 중심 기능은 Koyeb가 더 빠릅니다.

**최종 운영 환경은 Koyeb(US) + Supabase(US)입니다.**
