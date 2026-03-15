from src.domain.exceptions.commodity_not_found_error import CommodityNotFoundError


class TestCommodityNotFoundError:
    def test_message(self) -> None:
        error = CommodityNotFoundError("abc123")
        assert str(error) == "Commodity not found: abc123"
        assert error.commodity_id == "abc123"
