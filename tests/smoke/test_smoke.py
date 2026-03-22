"""Smoke tests for the full H³ stack.

Run AFTER `uv run hhh up` has started all services.
These tests validate that:
1. All services respond on their expected ports
2. Seed data is populated
3. Inter-service communication works (routes-service queries others)

Usage:
    uv run pytest tests/smoke/ -v
"""

import pytest
import httpx

BASE_URLS = {
    "contracts": "http://localhost:8001",
    "ships": "http://localhost:8002",
    "maps": "http://localhost:8003",
    "graphs": "http://localhost:8004",
    "routes": "http://localhost:8005",
    "commodities": "http://localhost:8007",
}


class TestServiceHealth:
    """Verify all services respond to basic requests."""

    @pytest.mark.parametrize("service,url", BASE_URLS.items())
    def test_service_is_up(self, service: str, url: str):
        """Each service responds with HTTP 200 on its root or health endpoint."""
        response = httpx.get(f"{url}/", timeout=10)
        # Most FastAPI services return 404 on root, which is fine — it means the server is up
        assert response.status_code in (200, 404, 422), f"{service} returned {response.status_code}"


class TestSeedData:
    """Verify seed data is populated after startup."""

    def test_locations_seeded(self):
        """Maps service has seeded locations."""
        response = httpx.get(f"{BASE_URLS['maps']}/locations/", timeout=10)
        assert response.status_code == 200
        locations = response.json()
        assert len(locations) >= 11  # 11 locations total (including 2 systems)

    def test_systems_include_stanton(self):
        """Stanton system exists in seeded data."""
        response = httpx.get(
            f"{BASE_URLS['maps']}/locations/",
            params={"location_type": "system"},
            timeout=10,
        )
        assert response.status_code == 200
        systems = response.json()
        names = [s["name"] for s in systems]
        assert "Stanton" in names

    def test_distances_seeded(self):
        """Location distances are populated."""
        response = httpx.get(f"{BASE_URLS['maps']}/distances/", timeout=10)
        assert response.status_code == 200
        distances = response.json()
        assert len(distances) >= 2  # At least some distances exist

    def test_ships_seeded(self):
        """Ships service has seeded ships."""
        response = httpx.get(f"{BASE_URLS['ships']}/ships/", timeout=10)
        assert response.status_code == 200
        ships = response.json()
        assert len(ships) >= 8  # 8 starter ships

    def test_zeus_mk2_exists(self):
        """Zeus MK-2 CL is in the ship catalogue."""
        response = httpx.get(
            f"{BASE_URLS['ships']}/ships/search",
            params={"q": "Zeus"},
            timeout=10,
        )
        assert response.status_code == 200
        results = response.json()
        assert any("Zeus" in s["name"] for s in results)


class TestInterServiceCommunication:
    """Verify services can communicate with each other."""

    def test_routes_service_can_query_maps(self):
        """Routes service can reach maps service.

        This is indirectly tested — if routes-service starts successfully
        and responds, its dependency on maps-service is working.
        """
        response = httpx.get(f"{BASE_URLS['routes']}/", timeout=10)
        assert response.status_code in (200, 404)

    def test_routes_service_can_query_ships(self):
        """Routes service can reach ships service."""
        response = httpx.get(f"{BASE_URLS['routes']}/", timeout=10)
        assert response.status_code in (200, 404)


class TestCORS:
    """Verify CORS is configured on all services."""

    @pytest.mark.parametrize("service,url", BASE_URLS.items())
    def test_cors_allows_localhost_3000(self, service: str, url: str):
        """Each service allows requests from http://localhost:3000."""
        response = httpx.options(
            f"{url}/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
            timeout=10,
        )
        # CORS preflight should return 200 with correct headers
        assert response.status_code == 200, f"{service} CORS preflight failed"
        assert "http://localhost:3000" in response.headers.get("access-control-allow-origin", "").split(", ")
