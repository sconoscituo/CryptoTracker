from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.alert import PriceAlert
from app.schemas.crypto import AlertCreate, AlertResponse
from app.utils.auth import get_current_user, get_premium_user

router = APIRouter(prefix="/alerts", tags=["가격 알림"])


@router.get("/", response_model=list[AlertResponse])
async def get_alerts(
    current_user: User = Depends(get_premium_user),  # 프리미엄 전용
    db: AsyncSession = Depends(get_db),
):
    """내 가격 알림 목록 조회 (프리미엄 전용)"""
    result = await db.execute(
        select(PriceAlert).where(PriceAlert.user_id == current_user.id)
        .order_by(PriceAlert.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(
    alert_in: AlertCreate,
    current_user: User = Depends(get_premium_user),  # 프리미엄 전용
    db: AsyncSession = Depends(get_db),
):
    """가격 알림 생성 (프리미엄 전용)"""
    if not current_user.telegram_chat_id:
        raise HTTPException(
            status_code=400,
            detail="텔레그램 알림을 받으려면 먼저 /users/me/telegram 에서 chat_id를 등록하세요.",
        )

    alert = PriceAlert(
        user_id=current_user.id,
        symbol=alert_in.symbol,
        target_price=alert_in.target_price,
        direction=alert_in.direction,
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_premium_user),
    db: AsyncSession = Depends(get_db),
):
    """가격 알림 삭제 (프리미엄 전용)"""
    result = await db.execute(
        select(PriceAlert).where(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == current_user.id,
        )
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다.")
    await db.delete(alert)


@router.patch("/{alert_id}/toggle", response_model=AlertResponse)
async def toggle_alert(
    alert_id: int,
    current_user: User = Depends(get_premium_user),
    db: AsyncSession = Depends(get_db),
):
    """가격 알림 활성/비활성 토글 (프리미엄 전용)"""
    result = await db.execute(
        select(PriceAlert).where(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == current_user.id,
        )
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다.")

    alert.is_active = not alert.is_active
    await db.flush()
    return alert
