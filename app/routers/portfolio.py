from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.portfolio import CryptoHolding
from app.schemas.crypto import HoldingCreate, HoldingUpdate, HoldingResponse, PortfolioSummary, MarketAnalysis
from app.utils.auth import get_current_user, get_premium_user
from app.services.price_fetcher import price_fetcher
from app.services.analyzer import market_analyzer
from app.config import settings

router = APIRouter(prefix="/portfolio", tags=["포트폴리오"])


@router.get("/", response_model=PortfolioSummary)
async def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """포트폴리오 전체 조회 + 실시간 평가액 계산"""
    result = await db.execute(
        select(CryptoHolding).where(CryptoHolding.user_id == current_user.id)
    )
    holdings = result.scalars().all()

    if not holdings:
        return PortfolioSummary(
            holdings=[], total_invested=0, total_value=0,
            total_profit_loss=0, total_profit_loss_pct=0, holding_count=0
        )

    # 보유 심볼 목록으로 현재가 일괄 조회
    symbols = [h.symbol for h in holdings]
    prices = await price_fetcher.get_prices(symbols)

    holding_responses = []
    total_invested = 0.0
    total_value = 0.0

    for h in holdings:
        current_price = prices.get(h.symbol)
        invested = h.amount * h.avg_buy_price
        total_invested += invested

        if current_price:
            current_value = h.amount * current_price
            profit_loss = current_value - invested
            profit_loss_pct = (profit_loss / invested * 100) if invested > 0 else 0
            total_value += current_value
        else:
            current_value = profit_loss = profit_loss_pct = None

        holding_responses.append(HoldingResponse(
            id=h.id,
            symbol=h.symbol,
            name=h.name,
            amount=h.amount,
            avg_buy_price=h.avg_buy_price,
            current_price=current_price,
            current_value=current_value,
            profit_loss=profit_loss,
            profit_loss_pct=profit_loss_pct,
            created_at=h.created_at,
        ))

    total_profit_loss = total_value - total_invested
    total_profit_loss_pct = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0

    return PortfolioSummary(
        holdings=holding_responses,
        total_invested=round(total_invested, 2),
        total_value=round(total_value, 2),
        total_profit_loss=round(total_profit_loss, 2),
        total_profit_loss_pct=round(total_profit_loss_pct, 2),
        holding_count=len(holdings),
    )


@router.post("/holdings", response_model=HoldingResponse, status_code=201)
async def add_holding(
    holding_in: HoldingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """코인 보유 내역 추가 (무료: 5개 제한)"""
    # 무료 플랜 코인 수 제한 확인
    if not current_user.is_premium:
        count_result = await db.execute(
            select(func.count()).where(CryptoHolding.user_id == current_user.id)
        )
        count = count_result.scalar()
        if count >= settings.free_plan_coin_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"무료 플랜은 최대 {settings.free_plan_coin_limit}개 코인만 추적할 수 있습니다. 프리미엄으로 업그레이드하세요.",
            )

    holding = CryptoHolding(
        user_id=current_user.id,
        symbol=holding_in.symbol,
        name=holding_in.name,
        amount=holding_in.amount,
        avg_buy_price=holding_in.avg_buy_price,
    )
    db.add(holding)
    await db.flush()
    await db.refresh(holding)
    return HoldingResponse(
        id=holding.id,
        symbol=holding.symbol,
        name=holding.name,
        amount=holding.amount,
        avg_buy_price=holding.avg_buy_price,
        created_at=holding.created_at,
    )


@router.patch("/holdings/{holding_id}", response_model=HoldingResponse)
async def update_holding(
    holding_id: int,
    holding_in: HoldingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """코인 보유 내역 수정"""
    result = await db.execute(
        select(CryptoHolding).where(
            CryptoHolding.id == holding_id,
            CryptoHolding.user_id == current_user.id,
        )
    )
    holding = result.scalar_one_or_none()
    if not holding:
        raise HTTPException(status_code=404, detail="보유 내역을 찾을 수 없습니다.")

    if holding_in.amount is not None:
        holding.amount = holding_in.amount
    if holding_in.avg_buy_price is not None:
        holding.avg_buy_price = holding_in.avg_buy_price

    await db.flush()
    return HoldingResponse(
        id=holding.id, symbol=holding.symbol, name=holding.name,
        amount=holding.amount, avg_buy_price=holding.avg_buy_price,
        created_at=holding.created_at,
    )


@router.delete("/holdings/{holding_id}", status_code=204)
async def delete_holding(
    holding_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """코인 보유 내역 삭제"""
    result = await db.execute(
        select(CryptoHolding).where(
            CryptoHolding.id == holding_id,
            CryptoHolding.user_id == current_user.id,
        )
    )
    holding = result.scalar_one_or_none()
    if not holding:
        raise HTTPException(status_code=404, detail="보유 내역을 찾을 수 없습니다.")
    await db.delete(holding)


@router.get("/analyze/{symbol}", response_model=MarketAnalysis)
async def analyze_coin(
    symbol: str,
    current_user: User = Depends(get_premium_user),  # 프리미엄 전용
):
    """Gemini AI로 특정 코인 시장 분석 (프리미엄 전용)"""
    coin_info = await price_fetcher.get_coin_info(symbol)
    if not coin_info:
        raise HTTPException(status_code=404, detail=f"{symbol} 코인 정보를 찾을 수 없습니다.")

    fear_greed = await price_fetcher.get_fear_greed_index()
    analysis = await market_analyzer.analyze_market(symbol, coin_info, fear_greed)
    return analysis


@router.get("/search")
async def search_coins(
    q: str,
    current_user: User = Depends(get_current_user),
):
    """코인 검색 (이름 또는 심볼)"""
    results = await price_fetcher.search_coin(q)
    return {"results": results}
