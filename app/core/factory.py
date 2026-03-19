from typing import Any, Dict, Type, TypeVar

T = TypeVar("T")


class ServiceFactory:
    """싱글톤 서비스 팩토리 - 서비스 인스턴스를 생성하고 캐싱합니다."""

    _instance: "ServiceFactory | None" = None
    _registry: Dict[str, Any] = {}

    def __new__(cls) -> "ServiceFactory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._registry = {}
        return cls._instance

    def register(self, name: str, instance: Any) -> None:
        """서비스 인스턴스를 이름으로 등록합니다."""
        self._registry[name] = instance

    def get(self, name: str) -> Any:
        """등록된 서비스 인스턴스를 반환합니다."""
        if name not in self._registry:
            raise KeyError(f"Service '{name}' not registered in ServiceFactory.")
        return self._registry[name]

    def get_or_create(self, name: str, cls: Type[T], *args: Any, **kwargs: Any) -> T:
        """등록된 서비스가 없으면 생성 후 등록하고 반환합니다."""
        if name not in self._registry:
            self._registry[name] = cls(*args, **kwargs)
        return self._registry[name]

    def clear(self) -> None:
        """등록된 모든 서비스를 제거합니다 (테스트용)."""
        self._registry.clear()


# 전역 팩토리 인스턴스
service_factory = ServiceFactory()
