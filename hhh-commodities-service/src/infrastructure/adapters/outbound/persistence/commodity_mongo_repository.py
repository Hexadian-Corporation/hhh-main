from bson import ObjectId
from pymongo.collection import Collection

from src.application.ports.outbound.commodity_repository_port import CommodityRepositoryPort
from src.domain.models.commodity import Commodity
from src.infrastructure.adapters.outbound.persistence.mapper import CommodityPersistenceMapper


class CommodityMongoRepository(CommodityRepositoryPort):
    def __init__(self, collection: Collection) -> None:  # type: ignore[type-arg]
        self._collection = collection

    def save(self, commodity: Commodity) -> Commodity:
        doc = CommodityPersistenceMapper.to_document(commodity)
        result = self._collection.insert_one(doc)
        commodity.id = str(result.inserted_id)
        return commodity

    def find_by_id(self, commodity_id: str) -> Commodity | None:
        doc = self._collection.find_one({"_id": ObjectId(commodity_id)})
        if doc is None:
            return None
        return CommodityPersistenceMapper.to_domain(doc)

    def find_all(self) -> list[Commodity]:
        docs = self._collection.find()
        return [CommodityPersistenceMapper.to_domain(doc) for doc in docs]

    def search_by_name(self, query: str) -> list[Commodity]:
        docs = self._collection.find({"name": {"$regex": query, "$options": "i"}})
        return [CommodityPersistenceMapper.to_domain(doc) for doc in docs]

    def update(self, commodity_id: str, commodity: Commodity) -> Commodity | None:
        update_fields = {}
        if commodity.name:
            update_fields["name"] = commodity.name
        if commodity.code:
            update_fields["code"] = commodity.code

        if not update_fields:
            return self.find_by_id(commodity_id)

        result = self._collection.find_one_and_update(
            {"_id": ObjectId(commodity_id)},
            {"$set": update_fields},
            return_document=True,
        )
        if result is None:
            return None
        return CommodityPersistenceMapper.to_domain(result)

    def delete(self, commodity_id: str) -> bool:
        result = self._collection.delete_one({"_id": ObjectId(commodity_id)})
        return result.deleted_count > 0
