from src.domain.models.commodity import Commodity
from src.infrastructure.adapters.inbound.api.dtos import CommodityCreateDTO, CommodityDTO, CommodityUpdateDTO


class CommodityApiMapper:
    @staticmethod
    def to_dto(commodity: Commodity) -> CommodityDTO:
        return CommodityDTO(
            id=commodity.id or "",
            name=commodity.name,
            code=commodity.code,
        )

    @staticmethod
    def to_domain_from_create(dto: CommodityCreateDTO) -> Commodity:
        return Commodity(name=dto.name, code=dto.code)

    @staticmethod
    def to_domain_from_update(dto: CommodityUpdateDTO) -> Commodity:
        return Commodity(
            name=dto.name or "",
            code=dto.code or "",
        )
