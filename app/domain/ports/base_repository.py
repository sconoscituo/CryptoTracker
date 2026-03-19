from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class AbstractRepository(ABC, Generic[T, ID]):
    """헥사고날 아키텍처 - Generic 추상 레포지토리 포트."""

    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        """ID로 단일 엔티티를 조회합니다."""
        ...

    @abstractmethod
    async def get_all(self) -> List[T]:
        """모든 엔티티를 조회합니다."""
        ...

    @abstractmethod
    async def save(self, entity: T) -> T:
        """엔티티를 저장(생성 또는 수정)합니다."""
        ...

    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """ID에 해당하는 엔티티를 삭제합니다."""
        ...
