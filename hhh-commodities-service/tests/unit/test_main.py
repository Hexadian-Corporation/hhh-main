import importlib
import sys
from unittest.mock import MagicMock, patch


class TestCreateApp:
    def _reload_main(self) -> MagicMock:
        """Reload src.main with MongoDB mocked out, returns the mock collection."""
        # Remove cached module so reload is fresh
        sys.modules.pop("src.main", None)

        with patch("src.infrastructure.config.dependencies.MongoClient") as mock_mongo:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_mongo.return_value.__getitem__ = MagicMock(return_value=mock_db)
            mock_db.__getitem__ = MagicMock(return_value=mock_collection)

            import src.main as main_module

            importlib.reload(main_module)
            self._main = main_module
        return mock_collection

    def test_health_endpoint(self) -> None:
        self._reload_main()

        from fastapi.testclient import TestClient

        client = TestClient(self._main.app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "hhh-commodities-service"

    def test_cors_headers(self) -> None:
        self._reload_main()

        from fastapi.testclient import TestClient

        client = TestClient(self._main.app)
        response = client.options(
            "/commodities/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_cors_rejects_unknown_origin(self) -> None:
        self._reload_main()

        from fastapi.testclient import TestClient

        client = TestClient(self._main.app)
        response = client.options(
            "/commodities/",
            headers={
                "Origin": "http://evil.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" not in response.headers
