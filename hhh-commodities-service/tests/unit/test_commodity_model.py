from src.domain.models.commodity import Commodity


class TestCommodityModel:
    def test_default_values(self) -> None:
        commodity = Commodity()
        assert commodity.id is None
        assert commodity.name == ""
        assert commodity.code == ""

    def test_with_values(self) -> None:
        commodity = Commodity(id="abc123", name="Laranite", code="LARA")
        assert commodity.id == "abc123"
        assert commodity.name == "Laranite"
        assert commodity.code == "LARA"
