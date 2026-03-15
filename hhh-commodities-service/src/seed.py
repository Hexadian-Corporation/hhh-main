import contextlib

from pymongo.errors import DuplicateKeyError

from src.application.ports.inbound.commodity_service_port import CommodityServicePort
from src.domain.models.commodity import Commodity

DEFAULT_COMMODITIES: list[Commodity] = [
    Commodity(name="Laranite", code="LARA"),
    Commodity(name="Quantanium", code="QUANT"),
    Commodity(name="Titanium", code="TITAN"),
    Commodity(name="Agricium", code="AGRI"),
    Commodity(name="Gold", code="GOLD"),
    Commodity(name="Diamond", code="DIAM"),
    Commodity(name="Medical Supplies", code="MEDSUP"),
    Commodity(name="Stims", code="STIMS"),
    Commodity(name="Processed Food", code="PFOOD"),
    Commodity(name="Hydrogen", code="HYDRO"),
    Commodity(name="Aluminum", code="ALUM"),
    Commodity(name="Tungsten", code="TUNG"),
    Commodity(name="Copper", code="COPP"),
    Commodity(name="Fluorine", code="FLUOR"),
    Commodity(name="Scrap", code="SCRAP"),
]


def seed_commodities(service: CommodityServicePort) -> list[Commodity]:
    """Seed default commodities. Skips commodities that already exist (by code).

    Returns the list of newly created commodities.
    """
    created: list[Commodity] = []
    existing_codes = {c.code for c in service.list_all()}

    for commodity in DEFAULT_COMMODITIES:
        if commodity.code in existing_codes:
            continue
        with contextlib.suppress(DuplicateKeyError):
            created.append(service.create(commodity))

    return created


if __name__ == "__main__":
    from opyoid import Injector

    from src.infrastructure.config.dependencies import AppModule
    from src.infrastructure.config.settings import Settings

    settings = Settings()
    injector = Injector([AppModule(settings)])
    svc = injector.inject(CommodityServicePort)

    result = seed_commodities(svc)
    print(f"Seeded {len(result)} commodities.")
