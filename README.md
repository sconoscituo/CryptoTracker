# CryptoTracker

암호화폐 포트폴리오 추적 + AI 시장 분석 + 텔레그램 알림 서비스

## 기능

### 무료 플랜
- 최대 5개 코인 포트폴리오 추적
- 실시간 가격 조회 (CoinGecko API)
- 기본 수익/손실 계산

### 프리미엄 플랜
- 무제한 코인 추적
- Gemini AI 시장 심리 분석 (공포/탐욕 지수 해석)
- 목표가 도달 시 텔레그램 알림
- 포트폴리오 상세 분석 리포트

## 기술 스택

- **백엔드**: FastAPI + SQLAlchemy (aiosqlite)
- **AI**: Google Gemini AI
- **가격 데이터**: CoinGecko API (무료)
- **알림**: python-telegram-bot
- **인증**: JWT (python-jose)

## 시작하기

```bash
# 1. 환경변수 설정
cp .env.example .env
# .env 파일 편집하여 API 키 입력

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 서버 실행
uvicorn app.main:app --reload
```

## Docker로 실행

```bash
docker-compose up -d
```

## API 문서

서버 실행 후 http://localhost:8000/docs 에서 Swagger UI 확인

## 환경변수

| 변수명 | 설명 |
|--------|------|
| `GEMINI_API_KEY` | Google Gemini AI API 키 |
| `DATABASE_URL` | 데이터베이스 URL |
| `SECRET_KEY` | JWT 서명용 시크릿 키 |
| `TELEGRAM_BOT_TOKEN` | 텔레그램 봇 토큰 |

## 수익 구조

- 무료: 5개 코인 제한
- 프리미엄: 월 $9.99 - 무제한 + AI 분석 + 텔레그램 알림
