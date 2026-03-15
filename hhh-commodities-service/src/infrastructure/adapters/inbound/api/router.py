from fastapi import APIRouter, HTTPException, Response

from src.application.ports.inbound.commodity_service_port import CommodityServicePort
from src.domain.exceptions.commodity_not_found_error import CommodityNotFoundError
from src.infrastructure.adapters.inbound.api.dtos import CommodityCreateDTO, CommodityDTO, CommodityUpdateDTO
from src.infrastructure.adapters.inbound.api.mapper import CommodityApiMapper

router = APIRouter(prefix="/commodities", tags=["commodities"])

_service: CommodityServicePort | None = None


def init_router(service: CommodityServicePort) -> None:
    global _service  # noqa: PLW0603
    _service = service


def _get_service() -> CommodityServicePort:
    assert _service is not None, "Router not initialized. Call init_router() first."
    return _service


@router.post("/", response_model=CommodityDTO, status_code=201)
def create_commodity(dto: CommodityCreateDTO) -> CommodityDTO:
    service = _get_service()
    commodity = CommodityApiMapper.to_domain_from_create(dto)
    created = service.create(commodity)
    return CommodityApiMapper.to_dto(created)


@router.get("/", response_model=list[CommodityDTO])
def list_commodities(response: Response) -> list[CommodityDTO]:
    service = _get_service()
    commodities = service.list_all()
    response.headers["Cache-Control"] = "max-age=900"
    return [CommodityApiMapper.to_dto(c) for c in commodities]


@router.get("/search", response_model=list[CommodityDTO])
def search_commodities(q: str, response: Response) -> list[CommodityDTO]:
    service = _get_service()
    commodities = service.search_by_name(q)
    response.headers["Cache-Control"] = "max-age=900"
    return [CommodityApiMapper.to_dto(c) for c in commodities]


@router.get("/{commodity_id}", response_model=CommodityDTO)
def get_commodity(commodity_id: str) -> CommodityDTO:
    service = _get_service()
    try:
        commodity = service.get(commodity_id)
    except CommodityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return CommodityApiMapper.to_dto(commodity)


@router.put("/{commodity_id}", response_model=CommodityDTO)
def update_commodity(commodity_id: str, dto: CommodityUpdateDTO) -> CommodityDTO:
    service = _get_service()
    commodity = CommodityApiMapper.to_domain_from_update(dto)
    try:
        updated = service.update(commodity_id, commodity)
    except CommodityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return CommodityApiMapper.to_dto(updated)


@router.delete("/{commodity_id}", status_code=204)
def delete_commodity(commodity_id: str) -> None:
    service = _get_service()
    try:
        service.delete(commodity_id)
    except CommodityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
