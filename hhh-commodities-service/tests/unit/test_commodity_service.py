from unittest.mock import MagicMock

import pytest

from src.application.ports.outbound.commodity_repository_port import CommodityRepositoryPort
from src.application.services.commodity_service import CommodityService
from src.domain.exceptions.commodity_not_found_error import CommodityNotFoundError
from src.domain.models.commodity import Commodity


@pytest.fixture
def mock_repository() -> MagicMock:
    return MagicMock(spec=CommodityRepositoryPort)


@pytest.fixture
def service(mock_repository: MagicMock) -> CommodityService:
    svc = CommodityService(mock_repository)
    svc._cache.clear()
    return svc


class TestCommodityService:
    def test_create(self, service: CommodityService, mock_repository: MagicMock) -> None:
        commodity = Commodity(name="Laranite", code="LARA")
        mock_repository.save.return_value = Commodity(id="1", name="Laranite", code="LARA")

        result = service.create(commodity)

        mock_repository.save.assert_called_once_with(commodity)
        assert result.id == "1"
        assert result.name == "Laranite"

    def test_get_found(self, service: CommodityService, mock_repository: MagicMock) -> None:
        mock_repository.find_by_id.return_value = Commodity(id="1", name="Laranite", code="LARA")

        result = service.get("1")

        assert result.id == "1"
        mock_repository.find_by_id.assert_called_once_with("1")

    def test_get_not_found(self, service: CommodityService, mock_repository: MagicMock) -> None:
        mock_repository.find_by_id.return_value = None

        with pytest.raises(CommodityNotFoundError):
            service.get("missing")

    def test_list_all(self, service: CommodityService, mock_repository: MagicMock) -> None:
        commodities = [
            Commodity(id="1", name="Laranite", code="LARA"),
            Commodity(id="2", name="Quantainium", code="QUANT"),
        ]
        mock_repository.find_all.return_value = commodities

        result = service.list_all()

        assert len(result) == 2
        mock_repository.find_all.assert_called_once()

    def test_list_all_cached(self, service: CommodityService, mock_repository: MagicMock) -> None:
        commodities = [Commodity(id="1", name="Laranite", code="LARA")]
        mock_repository.find_all.return_value = commodities

        service.list_all()
        service.list_all()

        mock_repository.find_all.assert_called_once()

    def test_search_by_name(self, service: CommodityService, mock_repository: MagicMock) -> None:
        commodities = [Commodity(id="1", name="Laranite", code="LARA")]
        mock_repository.search_by_name.return_value = commodities

        result = service.search_by_name("lar")

        assert len(result) == 1
        mock_repository.search_by_name.assert_called_once_with("lar")

    def test_search_by_name_cached(self, service: CommodityService, mock_repository: MagicMock) -> None:
        mock_repository.search_by_name.return_value = []

        service.search_by_name("lar")
        service.search_by_name("lar")

        mock_repository.search_by_name.assert_called_once()

    def test_update_found(self, service: CommodityService, mock_repository: MagicMock) -> None:
        updated = Commodity(id="1", name="Updated", code="UPD")
        mock_repository.update.return_value = updated

        result = service.update("1", Commodity(name="Updated", code="UPD"))

        assert result.name == "Updated"

    def test_update_not_found(self, service: CommodityService, mock_repository: MagicMock) -> None:
        mock_repository.update.return_value = None

        with pytest.raises(CommodityNotFoundError):
            service.update("missing", Commodity(name="X", code="Y"))

    def test_delete_found(self, service: CommodityService, mock_repository: MagicMock) -> None:
        mock_repository.delete.return_value = True

        service.delete("1")

        mock_repository.delete.assert_called_once_with("1")

    def test_delete_not_found(self, service: CommodityService, mock_repository: MagicMock) -> None:
        mock_repository.delete.return_value = False

        with pytest.raises(CommodityNotFoundError):
            service.delete("missing")

    def test_create_invalidates_cache(self, service: CommodityService, mock_repository: MagicMock) -> None:
        mock_repository.find_all.return_value = []
        mock_repository.save.return_value = Commodity(id="1", name="New", code="NEW")

        service.list_all()
        service.create(Commodity(name="New", code="NEW"))
        service.list_all()

        assert mock_repository.find_all.call_count == 2

    def test_update_invalidates_cache(self, service: CommodityService, mock_repository: MagicMock) -> None:
        mock_repository.find_all.return_value = []
        mock_repository.update.return_value = Commodity(id="1", name="Up", code="UP")

        service.list_all()
        service.update("1", Commodity(name="Up", code="UP"))
        service.list_all()

        assert mock_repository.find_all.call_count == 2

    def test_delete_invalidates_cache(self, service: CommodityService, mock_repository: MagicMock) -> None:
        mock_repository.find_all.return_value = []
        mock_repository.delete.return_value = True

        service.list_all()
        service.delete("1")
        service.list_all()

        assert mock_repository.find_all.call_count == 2
