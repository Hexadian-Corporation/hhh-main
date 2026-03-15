from typing import Any

from src.domain.models.commodity import Commodity


class CommodityPersistenceMapper:
    @staticmethod
    def to_document(commodity: Commodity) -> dict[str, Any]:
        doc: dict[str, Any] = {
            "name": commodity.name,
            "code": commodity.code,
        }
        return doc

    @staticmethod
    def to_domain(document: dict[str, Any]) -> Commodity:
        return Commodity(
            id=str(document["_id"]),
            name=document["name"],
            code=document["code"],
        )
