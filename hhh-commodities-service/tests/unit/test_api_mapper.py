from src.domain.models.commodity import Commodity
from src.infrastructure.adapters.inbound.api.dtos import CommodityCreateDTO, CommodityUpdateDTO
from src.infrastructure.adapters.inbound.api.mapper import CommodityApiMapper


class TestCommodityApiMapper:
    def test_to_dto(self) -> None:
        commodity = Commodity(id="abc", name="Laranite", code="LARA")
        dto = CommodityApiMapper.to_dto(commodity)
        assert dto.id == "abc"
        assert dto.name == "Laranite"
        assert dto.code == "LARA"

    def test_to_dto_none_id(self) -> None:
        commodity = Commodity(name="Laranite", code="LARA")
        dto = CommodityApiMapper.to_dto(commodity)
        assert dto.id == ""

    def test_to_domain_from_create(self) -> None:
        dto = CommodityCreateDTO(name="Laranite", code="LARA")
        commodity = CommodityApiMapper.to_domain_from_create(dto)
        assert commodity.id is None
        assert commodity.name == "Laranite"
        assert commodity.code == "LARA"

    def test_to_domain_from_update(self) -> None:
        dto = CommodityUpdateDTO(name="Updated")
        commodity = CommodityApiMapper.to_domain_from_update(dto)
        assert commodity.name == "Updated"
        assert commodity.code == ""

    def test_to_domain_from_update_all_fields(self) -> None:
        dto = CommodityUpdateDTO(name="Updated", code="UPD")
        commodity = CommodityApiMapper.to_domain_from_update(dto)
        assert commodity.name == "Updated"
        assert commodity.code == "UPD"
