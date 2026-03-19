from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── 사용자 스키마 ──────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    is_premium: bool
    telegram_chat_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── 포트폴리오 스키마 ──────────────────────────────────────────

class HoldingCreate(BaseModel):
    """코인 보유 내역 생성 요청"""
    symbol: str = Field(..., example="bitcoin", description="CoinGecko 코인 ID")
    name: str = Field(..., example="Bitcoin", description="코인 이름")
    amount: float = Field(..., gt=0, description="보유 수량")
    avg_buy_price: float = Field(..., gt=0, description="평균 매수가 (USD)")


class HoldingUpdate(BaseModel):
    """코인 보유 내역 수정 요청"""
    amount: Optional[float] = Field(None, gt=0)
    avg_buy_price: Optional[float] = Field(None, gt=0)


class HoldingResponse(BaseModel):
    """코인 보유 내역 응답"""
    id: int
    symbol: str
    name: str
    amount: float
    avg_buy_price: float
    # 현재가 및 수익률 (실시간 조회 시 포함)
    current_price: Optional[float] = None
    current_value: Optional[float] = None      # 현재 평가액 (USD)
    profit_loss: Optional[float] = None        # 수익/손실 (USD)
    profit_loss_pct: Optional[float] = None    # 수익률 (%)
    created_at: datetime

    model_config = {"from_attributes": True}


class PortfolioSummary(BaseModel):
    """포트폴리오 전체 요약"""
    holdings: list[HoldingResponse]
    total_invested: float      # 총 투자금액 (USD)
    total_value: float         # 총 평가액 (USD)
    total_profit_loss: float   # 총 수익/손실 (USD)
    total_profit_loss_pct: float  # 총 수익률 (%)
    holding_count: int


# ── 가격 알림 스키마 ──────────────────────────────────────────

class AlertCreate(BaseModel):
    """가격 알림 생성 요청"""
    symbol: str = Field(..., example="bitcoin")
    target_price: float = Field(..., gt=0, description="목표 가격 (USD)")
    direction: str = Field(..., pattern="^(above|below)$", description="above: 이상, below: 이하")


class AlertResponse(BaseModel):
    """가격 알림 응답"""
    id: int
    symbol: str
    target_price: float
    direction: str
    is_triggered: bool
    is_active: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── AI 분석 스키마 ──────────────────────────────────────────

class MarketAnalysis(BaseModel):
    """Gemini AI 시장 분석 결과"""
    symbol: str
    current_price: float
    fear_greed_interpretation: str    # 공포/탐욕 지수 해석
    market_sentiment: str             # 시장 심리 요약
    trend_analysis: str               # 트렌드 분석
    recommendation: str               # AI 추천 (매수/홀드/매도)
    analysis_text: str                # 전체 분석 텍스트
    analyzed_at: datetime
