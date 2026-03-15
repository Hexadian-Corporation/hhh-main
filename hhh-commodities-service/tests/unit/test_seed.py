from unittest.mock import MagicMock

import pytest
from pymongo.errors import DuplicateKeyError

from src.application.ports.inbound.commodity_service_port import CommodityServicePort
from src.domain.models.commodity import Commodity
from src.seed import DEFAULT_COMMODITIES, seed_commodities


@pytest.fixture
def mock_service() -> MagicMock:
    return MagicMock(spec=CommodityServicePort)


class TestDefaultCommodities:
    def test_has_at_least_15_commodities(self) -> None:
        assert len(DEFAULT_COMMODITIES) >= 15

    def test_all_have_name_and_code(self) -> None:
        for commodity in DEFAULT_COMMODITIES:
            assert commodity.name, f"Commodity with code {commodity.code!r} has no name"
            assert commodity.code, f"Commodity with name {commodity.name!r} has no code"

    def test_codes_are_unique(self) -> None:
        codes = [c.code for c in DEFAULT_COMMODITIES]
        assert len(codes) == len(set(codes))

    def test_names_are_unique(self) -> None:
        names = [c.name for c in DEFAULT_COMMODITIES]
        assert len(names) == len(set(names))

    def test_ids_are_none(self) -> None:
        for commodity in DEFAULT_COMMODITIES:
            assert commodity.id is None

    def test_expected_commodities_present(self) -> None:
        codes = {c.code for c in DEFAULT_COMMODITIES}
        expected = {
            "LARA",
            "QUANT",
            "TITAN",
            "AGRI",
            "GOLD",
            "DIAM",
            "MEDSUP",
            "STIMS",
            "PFOOD",
            "HYDRO",
            "ALUM",
            "TUNG",
            "COPP",
            "FLUOR",
            "SCRAP",
        }
        assert expected == codes


class TestSeedCommodities:
    def test_creates_all_when_empty(self, mock_service: MagicMock) -> None:
        mock_service.list_all.return_value = []
        mock_service.create.side_effect = lambda c: Commodity(id="generated", name=c.name, code=c.code)

        result = seed_commodities(mock_service)

        assert len(result) == len(DEFAULT_COMMODITIES)
        assert mock_service.create.call_count == len(DEFAULT_COMMODITIES)

    def test_skips_existing_commodities(self, mock_service: MagicMock) -> None:
        existing = [Commodity(id="1", name="Laranite", code="LARA")]
        mock_service.list_all.return_value = existing
        mock_service.create.side_effect = lambda c: Commodity(id="generated", name=c.name, code=c.code)

        result = seed_commodities(mock_service)

        assert len(result) == len(DEFAULT_COMMODITIES) - 1
        created_codes = [c.args[0].code for c in mock_service.create.call_args_list]
        assert "LARA" not in created_codes

    def test_skips_all_when_fully_seeded(self, mock_service: MagicMock) -> None:
        mock_service.list_all.return_value = [
            Commodity(id=str(i), name=c.name, code=c.code) for i, c in enumerate(DEFAULT_COMMODITIES)
        ]

        result = seed_commodities(mock_service)

        assert len(result) == 0
        mock_service.create.assert_not_called()

    def test_handles_duplicate_key_error(self, mock_service: MagicMock) -> None:
        mock_service.list_all.return_value = []
        mock_service.create.side_effect = DuplicateKeyError("duplicate")

        result = seed_commodities(mock_service)

        assert len(result) == 0
        assert mock_service.create.call_count == len(DEFAULT_COMMODITIES)

    def test_returns_created_commodities(self, mock_service: MagicMock) -> None:
        mock_service.list_all.return_value = []
        mock_service.create.side_effect = lambda c: Commodity(id="new", name=c.name, code=c.code)

        result = seed_commodities(mock_service)

        for commodity in result:
            assert commodity.id == "new"
            assert commodity.name
            assert commodity.code

    def test_is_idempotent(self, mock_service: MagicMock) -> None:
        """Running seed twice with same state produces no new creates."""
        mock_service.list_all.return_value = [
            Commodity(id=str(i), name=c.name, code=c.code) for i, c in enumerate(DEFAULT_COMMODITIES)
        ]

        first_result = seed_commodities(mock_service)
        second_result = seed_commodities(mock_service)

        assert first_result == []
        assert second_result == []
