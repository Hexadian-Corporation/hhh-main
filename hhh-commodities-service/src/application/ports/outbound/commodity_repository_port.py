from abc import ABC, abstractmethod

from src.domain.models.commodity import Commodity


class CommodityRepositoryPort(ABC):
    @abstractmethod
    def save(self, commodity: Commodity) -> Commodity: ...

    @abstractmethod
    def find_by_id(self, commodity_id: str) -> Commodity | None: ...

    @abstractmethod
    def find_all(self) -> list[Commodity]: ...

    @abstractmethod
    def search_by_name(self, query: str) -> list[Commodity]: ...

    @abstractmethod
    def update(self, commodity_id: str, commodity: Commodity) -> Commodity | None: ...

    @abstractmethod
    def delete(self, commodity_id: str) -> bool: ...
