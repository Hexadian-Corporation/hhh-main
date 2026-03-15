class CommodityNotFoundError(Exception):
    def __init__(self, commodity_id: str) -> None:
        self.commodity_id = commodity_id
        super().__init__(f"Commodity not found: {commodity_id}")
