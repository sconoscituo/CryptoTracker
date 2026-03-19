from abc import ABC, abstractmethod
from typing import Any, Dict


class AbstractService(ABC):
    """헥사고날 아키텍처 - 추상 서비스 포트."""

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """서비스 상태를 확인합니다."""
        ...
