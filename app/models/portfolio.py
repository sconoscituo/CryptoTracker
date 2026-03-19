from datetime import datetime
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CryptoHolding(Base):
    """암호화폐 보유 내역 모델"""
    __tablename__ = "crypto_holdings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 사용자 연결
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 코인 정보
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)   # 예: "bitcoin", "ethereum"
    name: Mapped[str] = mapped_column(String(100), nullable=False)    # 예: "Bitcoin", "Ethereum"

    # 보유량 및 평균 매수가 (KRW 기준)
    amount: Mapped[float] = mapped_column(Float, nullable=False)           # 보유 수량
    avg_buy_price: Mapped[float] = mapped_column(Float, nullable=False)    # 평균 매수가 (USD)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="holdings")

    def __repr__(self) -> str:
        return f"<CryptoHolding id={self.id} symbol={self.symbol} amount={self.amount}>"
