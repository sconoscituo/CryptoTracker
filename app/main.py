from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import settings
from app.database import init_db, AsyncSessionLocal
from app.routers import portfolio, alerts, users
from app.middleware.security_headers import SecurityHeadersMiddleware


# APScheduler - 주기적 가격 알림 체크
scheduler = AsyncIOScheduler()


async def check_price_alerts():
    """5분마다 가격 알림 조건 체크 (스케줄러 작업)"""
    from app.services.price_fetcher import price_fetcher
    from app.services.notifier import notifier

    async with AsyncSessionLocal() as db:
        count = await notifier.check_and_notify_alerts(db, price_fetcher)
        if count > 0:
            print(f"[알림] {count}개의 가격 알림을 발송했습니다.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 라이프사이클 핸들러"""
    # 시작: DB 초기화 + 스케줄러 시작
    await init_db()
    scheduler.add_job(check_price_alerts, "interval", minutes=5, id="price_alert_checker")
    scheduler.start()
    print("CryptoTracker API 서버 시작됨")
    yield
    # 종료: 스케줄러 정지
    scheduler.shutdown()
    print("CryptoTracker API 서버 종료됨")


app = FastAPI(
    title="CryptoTracker API",
    description="암호화폐 포트폴리오 추적 + AI 시장 분석 + 텔레그램 알림",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 설정 (프론트엔드 연동 시 origins 수정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)

# 라우터 등록
app.include_router(users.router)
app.include_router(portfolio.router)
app.include_router(alerts.router)


@app.get("/", tags=["헬스체크"])
async def root():
    """API 서버 상태 확인"""
    return {
        "service": "CryptoTracker",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["헬스체크"])
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy"}
