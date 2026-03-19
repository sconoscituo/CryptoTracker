from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 앱 기본 설정
    app_name: str = "CryptoTracker"
    debug: bool = False

    # 데이터베이스
    database_url: str = "sqlite+aiosqlite:///./cryptotracker.db"

    # JWT 인증
    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7일

    # Google Gemini AI
    gemini_api_key: str = ""

    # 텔레그램 봇
    telegram_bot_token: str = ""

    # CoinGecko API (무료 플랜)
    coingecko_api_url: str = "https://api.coingecko.com/api/v3"

    # 무료 플랜 코인 제한
    free_plan_coin_limit: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()
