from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class PriceAlert(Base):
    """가격 알림 모델"""
    __tablename__ = "price_alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 사용자 연결
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 알림 설정
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)        # 예: "bitcoin"
    target_price: Mapped[float] = mapped_column(Float, nullable=False)     # 목표 가격 (USD)

    # 방향: "above" = 목표가 이상일 때, "below" = 목표가 이하일 때 알림
    direction: Mapped[str] = mapped_column(String(10), nullable=False)

    # 알림 상태
    is_triggered: Mapped[bool] = mapped_column(Boolean, default=False)     # 알림 발송 완료 여부
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)         # 알림 활성 여부

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<PriceAlert id={self.id} symbol={self.symbol} target={self.target_price} dir={self.direction}>"
