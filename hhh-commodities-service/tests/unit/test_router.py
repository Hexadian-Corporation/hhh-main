from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.application.ports.inbound.commodity_service_port import CommodityServicePort
from src.domain.exceptions.commodity_not_found_error import CommodityNotFoundError
from src.domain.models.commodity import Commodity
from src.infrastructure.adapters.inbound.api import router as router_module
from src.infrastructure.adapters.inbound.api.router import init_router, router


@pytest.fixture
def mock_service() -> MagicMock:
    return MagicMock(spec=CommodityServicePort)


@pytest.fixture
def client(mock_service: MagicMock) -> TestClient:
    from fastapi import FastAPI

    app = FastAPI()
    init_router(mock_service)
    app.include_router(router)
    return TestClient(app)


@pytest.fixture(autouse=True)
def _reset_router() -> None:
    """Reset the module-level _service after each test."""
    yield
    router_module._service = None


class TestCommodityRouter:
    def test_create(self, client: TestClient, mock_service: MagicMock) -> None:
        mock_service.create.return_value = Commodity(id="1", name="Laranite", code="LARA")

        response = client.post("/commodities/", json={"name": "Laranite", "code": "LARA"})

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "1"
        assert data["name"] == "Laranite"
        assert data["code"] == "LARA"

    def test_get_commodity(self, client: TestClient, mock_service: MagicMock) -> None:
        mock_service.get.return_value = Commodity(id="1", name="Laranite", code="LARA")

        response = client.get("/commodities/1")

        assert response.status_code == 200
        assert response.json()["name"] == "Laranite"

    def test_get_commodity_not_found(self, client: TestClient, mock_service: MagicMock) -> None:
        mock_service.get.side_effect = CommodityNotFoundError("missing")

        response = client.get("/commodities/missing")

        assert response.status_code == 404

    def test_list_commodities(self, client: TestClient, mock_service: MagicMock) -> None:
        mock_service.list_all.return_value = [
            Commodity(id="1", name="Laranite", code="LARA"),
            Commodity(id="2", name="Quantainium", code="QUANT"),
        ]

        response = client.get("/commodities/")

        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.headers["cache-control"] == "max-age=900"

    def test_search_commodities(self, client: TestClient, mock_service: MagicMock) -> None:
        mock_service.search_by_name.return_value = [
            Commodity(id="1", name="Laranite", code="LARA"),
        ]

        response = client.get("/commodities/search?q=lar")

        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_service.search_by_name.assert_called_once_with("lar")
        assert response.headers["cache-control"] == "max-age=900"

    def test_update_commodity(self, client: TestClient, mock_service: MagicMock) -> None:
        mock_service.update.return_value = Commodity(id="1", name="Updated", code="UPD")

        response = client.put("/commodities/1", json={"name": "Updated", "code": "UPD"})

        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

    def test_update_commodity_not_found(self, client: TestClient, mock_service: MagicMock) -> None:
        mock_service.update.side_effect = CommodityNotFoundError("missing")

        response = client.put("/commodities/missing", json={"name": "X"})

        assert response.status_code == 404

    def test_delete_commodity(self, client: TestClient, mock_service: MagicMock) -> None:
        mock_service.delete.return_value = None

        response = client.delete("/commodities/1")

        assert response.status_code == 204

    def test_delete_commodity_not_found(self, client: TestClient, mock_service: MagicMock) -> None:
        mock_service.delete.side_effect = CommodityNotFoundError("missing")

        response = client.delete("/commodities/missing")

        assert response.status_code == 404

    def test_create_missing_fields(self, client: TestClient, mock_service: MagicMock) -> None:
        response = client.post("/commodities/", json={})

        assert response.status_code == 422
