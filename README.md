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

### 테스트 조건

| 항목 | 조건 |
|---|---|
| 테스트 위치 | 대한민국 서울 |
| 테스트 날짜 | 2026-07-31 |
| 비교 환경 | Koyeb(US) + Supabase(US) / Render(SG) + Supabase(KR) |
| 워밍업 | 환경·엔드포인트별 10회 |
| 측정 | 환경·엔드포인트별 30회 |
| 동시성 | 1 |
| 타임아웃 | 30초 |
| 실행 방식 | 각 환경을 독립적으로 순차 실행 |
| 기준 코드 | 쿼리 최적화 커밋 `fd96b59` |

### 최종 측정 결과

단위는 ms이며, 워밍업 이후 측정값입니다.

| 엔드포인트 | 환경 | 평균 | 중앙값 | 최소 | 최대 | p95 | 실패율 |
|---|---|---:|---:|---:|---:|---:|---:|
| `/health` | Koyeb(US) + Supabase(US) | 233.43 | 209.01 | 204.41 | 288.31 | 287.34 | 0.00% |
| `/health` | Render(SG) + Supabase(KR) | 138.47 | 132.99 | 119.22 | 192.69 | 159.20 | 0.00% |
| `/` | Koyeb(US) + Supabase(US) | 231.71 | 208.30 | 203.65 | 299.56 | 283.39 | 0.00% |
| `/` | Render(SG) + Supabase(KR) | 121.99 | 120.64 | 112.14 | 136.25 | 130.96 | 0.00% |
| `/api/players/` | Koyeb(US) + Supabase(US) | 251.43 | 231.81 | 216.75 | 316.84 | 313.13 | 0.00% |
| `/api/players/` | Render(SG) + Supabase(KR) | 341.37 | 338.68 | 330.32 | 382.36 | 358.10 | 0.00% |
| `/api/matches/finished` | Koyeb(US) + Supabase(US) | 309.92 | 310.94 | 230.23 | 858.81 | 316.92 | 0.00% |
| `/api/matches/finished` | Render(SG) + Supabase(KR) | 489.94 | 477.25 | 470.16 | 826.02 | 487.46 | 0.00% |
| `/api/stats/leaderboard` | Koyeb(US) + Supabase(US) | 359.77 | 302.32 | 268.49 | 956.89 | 681.68 | 0.00% |
| `/api/stats/leaderboard` | Render(SG) + Supabase(KR) | 712.79 | 688.39 | 681.68 | 1079.16 | 888.62 | 0.00% |
| `/api/players/{id}` | Koyeb(US) + Supabase(US) | 251.11 | 228.97 | 224.11 | 303.03 | 301.07 | 0.00% |
| `/api/players/{id}` | Render(SG) + Supabase(KR) | 337.44 | 334.62 | 325.48 | 376.32 | 354.98 | 0.00% |

### 종합 비교

| 항목 | Koyeb(US) + Supabase(US) | Render(SG) + Supabase(KR) | 우세 환경 |
|---|---:|---:|---|
| 전체 엔드포인트 평균 p50 | 248.56ms | 348.76ms | Koyeb |
| DB 엔드포인트 평균 p50 | 268.51ms | 459.74ms | Koyeb |
| 전체 실패 | 0/180 | 0/180 | 동일 |
| 단순 응답(`/health`, `/`) | 상대적으로 느림 | 상대적으로 빠름 | Render |
| DB 중심 인게임 기능 | 상대적으로 빠름 | 상대적으로 느림 | Koyeb |

**최종 운영 환경: Koyeb(US) + Supabase(US)**
