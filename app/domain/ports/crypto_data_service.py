from abc import abstractmethod
from typing import Any, Dict, List

from app.domain.ports.base_service import AbstractService


class AbstractCryptoDataService(AbstractService):
    """CryptoTracker 도메인 서비스 포트."""

    @abstractmethod
    async def fetch_prices(self, symbols: List[str], currency: str = "USD") -> Dict[str, Any]:
        """지정된 심볼 목록의 현재 가격 정보를 가져옵니다."""
        ...

    @abstractmethod
    async def analyze_market(self, symbol: str, timeframe: str = "24h") -> Dict[str, Any]:
        """특정 코인의 시장 동향을 AI로 분석합니다."""
        ...

    @abstractmethod
    async def set_alert(self, user_id: str, symbol: str, condition: Dict[str, Any]) -> Dict[str, Any]:
        """가격 조건 알림을 설정합니다."""
        ...

    @abstractmethod
    async def get_portfolio(self, user_id: str) -> Dict[str, Any]:
        """사용자의 포트폴리오 현황 및 손익을 반환합니다."""
        ...

    async def health_check(self) -> Dict[str, Any]:
        return {"service": "CryptoDataService", "status": "ok"}
