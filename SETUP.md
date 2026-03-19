# CryptoTracker 설정 가이드

## 프로젝트 소개

실시간 암호화폐 시세 추적 및 포트폴리오 관리 서비스입니다. CoinGecko 무료 API로 시세를 조회하고, Gemini AI로 시장 분석을 제공하며, 텔레그램 봇을 통해 가격 알림을 전송하는 FastAPI 백엔드 애플리케이션입니다.

---

## 1. 필요한 API 키 / 환경변수

| 변수명 | 설명 | 발급 URL |
|--------|------|----------|
| `GEMINI_API_KEY` | Google Gemini AI API 키 (시장 분석용) | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `TELEGRAM_BOT_TOKEN` | 텔레그램 가격 알림 봇 토큰 | [@BotFather](https://t.me/BotFather) |
| `SECRET_KEY` | JWT 서명용 시크릿 키 | 직접 임의 문자열 생성 (32자 이상 권장) |
| `DATABASE_URL` | 데이터베이스 연결 URL | 기본값: `sqlite+aiosqlite:///./cryptotracker.db` |
| `DEBUG` | 디버그 모드 (True/False) | 기본값: `True` |

> **참고**: CoinGecko API는 별도 키 없이 무료 플랜(공개 엔드포인트)을 사용합니다. 고속/대용량 요청이 필요하면 [CoinGecko Pro](https://www.coingecko.com/en/api/pricing)에서 유료 키를 발급하세요.

---

## 2. API 키 발급 방법

### GEMINI_API_KEY

1. [Google AI Studio](https://aistudio.google.com/app/apikey) 접속
2. Google 계정으로 로그인
3. **"Create API key"** 클릭
4. 발급된 키 복사

### TELEGRAM_BOT_TOKEN

1. 텔레그램 앱에서 **`@BotFather`** 검색 후 접속
2. `/newbot` 명령어 입력
3. 봇 이름 및 사용자명 설정 (사용자명은 `bot`으로 끝나야 함)
4. 발급된 **HTTP API Token** 복사

자세한 봇 생성 절차는 [TeleBot SETUP.md](../[TeleBot]/SETUP.md)의 "TELEGRAM_BOT_TOKEN 발급" 섹션을 참고하세요.

### SECRET_KEY

터미널에서 아래 명령어로 생성:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 3. GitHub Secrets 설정

GitHub 레포지토리 → **Settings → Secrets and variables → Actions → New repository secret**

| Secret 이름 | 값 |
|------------|-----|
| `GEMINI_API_KEY` | Google AI Studio API 키 |
| `TELEGRAM_BOT_TOKEN` | BotFather에서 발급받은 토큰 |
| `SECRET_KEY` | JWT 서명 시크릿 키 |

---

## 4. 로컬 개발 환경 설정

### 사전 요구사항

- Python 3.11 이상
- pip
- (선택) Docker, Docker Compose

### 설치 순서

```bash
# 1. 저장소 클론
git clone https://github.com/sconoscituo/CryptoTracker.git
cd CryptoTracker

# 2. 가상환경 생성 및 활성화
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경변수 파일 생성
cp .env.example .env
```

### .env 파일 편집

```env
GEMINI_API_KEY=AIzaSy...
DATABASE_URL=sqlite+aiosqlite:///./cryptotracker.db
SECRET_KEY=여기에_32자_이상의_임의_문자열_입력
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
DEBUG=True
```

---

## 5. 실행 방법

### 로컬 직접 실행

```bash
# 가상환경 활성화 후
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버 주소: `http://localhost:8000`
API 문서: `http://localhost:8000/docs`

### Docker로 실행

```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

---

## 6. 주요 기능 사용법

### 회원가입 / 로그인

```bash
# 회원가입
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# 로그인 (JWT 토큰 발급)
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 실시간 시세 조회

```bash
# 특정 코인 시세 조회 (CoinGecko ID 사용)
curl http://localhost:8000/api/crypto/price/bitcoin \
  -H "Authorization: Bearer <JWT_TOKEN>"

# 다중 코인 시세 일괄 조회
curl "http://localhost:8000/api/crypto/prices?coins=bitcoin,ethereum,solana" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 포트폴리오 관리

```bash
# 포트폴리오에 코인 추가
curl -X POST http://localhost:8000/api/portfolio \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"coin_id": "bitcoin", "amount": 0.5, "purchase_price": 60000}'

# 포트폴리오 전체 조회 (수익률 포함)
curl http://localhost:8000/api/portfolio \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 가격 알림 설정

```bash
# 가격 알림 등록 (BTC가 10만 달러 도달 시 텔레그램 알림)
curl -X POST http://localhost:8000/api/alerts \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"coin_id": "bitcoin", "target_price": 100000, "direction": "above"}'

# 알림 목록 조회
curl http://localhost:8000/api/alerts \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### AI 시장 분석

```bash
# Gemini AI 기반 시장 분석 요청
curl http://localhost:8000/api/crypto/analysis/bitcoin \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 무료 플랜 제한

- 포트폴리오 코인 추가: 최대 5개

### API 문서 (Swagger UI)

브라우저에서 `http://localhost:8000/docs` 접속 시 전체 API를 시각적으로 확인하고 테스트할 수 있습니다.
