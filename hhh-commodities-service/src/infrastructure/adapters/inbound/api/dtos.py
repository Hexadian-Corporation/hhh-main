from pydantic import BaseModel


class CommodityDTO(BaseModel):
    id: str
    name: str
    code: str


class CommodityCreateDTO(BaseModel):
    name: str
    code: str


class CommodityUpdateDTO(BaseModel):
    name: str | None = None
    code: str | None = None
