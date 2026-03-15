from abc import ABC, abstractmethod

from src.domain.models.commodity import Commodity


class CommodityServicePort(ABC):
    @abstractmethod
    def create(self, commodity: Commodity) -> Commodity: ...

    @abstractmethod
    def get(self, commodity_id: str) -> Commodity: ...

    @abstractmethod
    def list_all(self) -> list[Commodity]: ...

    @abstractmethod
    def search_by_name(self, query: str) -> list[Commodity]: ...

    @abstractmethod
    def update(self, commodity_id: str, commodity: Commodity) -> Commodity: ...

    @abstractmethod
    def delete(self, commodity_id: str) -> None: ...
