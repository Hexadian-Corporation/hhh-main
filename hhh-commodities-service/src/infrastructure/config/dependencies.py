from opyoid import Module, SingletonScope
from pymongo import MongoClient
from pymongo.collation import Collation
from pymongo.collection import Collection

from src.application.ports.inbound.commodity_service_port import CommodityServicePort
from src.application.ports.outbound.commodity_repository_port import CommodityRepositoryPort
from src.application.services.commodity_service import CommodityService
from src.infrastructure.adapters.outbound.persistence.commodity_mongo_repository import CommodityMongoRepository
from src.infrastructure.config.settings import Settings


class AppModule(Module):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def configure(self) -> None:
        client = MongoClient(self._settings.mongo_uri)
        db = client[self._settings.mongo_db]
        collection = db["commodities"]

        collection.create_index("code", unique=True)
        collection.create_index(
            "name",
            collation=Collation(locale="en", strength=2),
        )

        self.bind(Collection, to_instance=collection)  # type: ignore[type-arg]
        self.bind(CommodityRepositoryPort, to_class=CommodityMongoRepository, scope=SingletonScope)
        self.bind(CommodityServicePort, to_class=CommodityService, scope=SingletonScope)
