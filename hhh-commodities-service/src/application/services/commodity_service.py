from cachetools import TTLCache

from src.application.ports.inbound.commodity_service_port import CommodityServicePort
from src.application.ports.outbound.commodity_repository_port import CommodityRepositoryPort
from src.domain.exceptions.commodity_not_found_error import CommodityNotFoundError
from src.domain.models.commodity import Commodity


class CommodityService(CommodityServicePort):
    _cache: TTLCache[str, list[Commodity]] = TTLCache(maxsize=128, ttl=900)

    def __init__(self, repository: CommodityRepositoryPort) -> None:
        self._repository = repository

    def _invalidate_cache(self) -> None:
        self._cache.clear()

    def create(self, commodity: Commodity) -> Commodity:
        result = self._repository.save(commodity)
        self._invalidate_cache()
        return result

    def get(self, commodity_id: str) -> Commodity:
        commodity = self._repository.find_by_id(commodity_id)
        if commodity is None:
            raise CommodityNotFoundError(commodity_id)
        return commodity

    def list_all(self) -> list[Commodity]:
        cache_key = "__all__"
        if cache_key in self._cache:
            return self._cache[cache_key]
        result = self._repository.find_all()
        self._cache[cache_key] = result
        return result

    def search_by_name(self, query: str) -> list[Commodity]:
        cache_key = f"search:{query.lower()}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        result = self._repository.search_by_name(query)
        self._cache[cache_key] = result
        return result

    def update(self, commodity_id: str, commodity: Commodity) -> Commodity:
        result = self._repository.update(commodity_id, commodity)
        if result is None:
            raise CommodityNotFoundError(commodity_id)
        self._invalidate_cache()
        return result

    def delete(self, commodity_id: str) -> None:
        deleted = self._repository.delete(commodity_id)
        if not deleted:
            raise CommodityNotFoundError(commodity_id)
        self._invalidate_cache()
