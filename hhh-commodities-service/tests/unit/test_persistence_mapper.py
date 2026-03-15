from src.domain.models.commodity import Commodity
from src.infrastructure.adapters.outbound.persistence.mapper import CommodityPersistenceMapper


class TestCommodityPersistenceMapper:
    def test_to_document(self) -> None:
        commodity = Commodity(id="abc", name="Laranite", code="LARA")
        doc = CommodityPersistenceMapper.to_document(commodity)
        assert doc == {"name": "Laranite", "code": "LARA"}
        assert "_id" not in doc

    def test_to_domain(self) -> None:
        doc = {"_id": "abc123", "name": "Laranite", "code": "LARA"}
        commodity = CommodityPersistenceMapper.to_domain(doc)
        assert commodity.id == "abc123"
        assert commodity.name == "Laranite"
        assert commodity.code == "LARA"
