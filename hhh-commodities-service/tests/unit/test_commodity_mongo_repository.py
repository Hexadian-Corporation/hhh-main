from unittest.mock import MagicMock

from bson import ObjectId

from src.domain.models.commodity import Commodity
from src.infrastructure.adapters.outbound.persistence.commodity_mongo_repository import CommodityMongoRepository


class TestCommodityMongoRepository:
    def setup_method(self) -> None:
        self.mock_collection = MagicMock()
        self.repo = CommodityMongoRepository(self.mock_collection)

    def test_save(self) -> None:
        commodity = Commodity(name="Laranite", code="LARA")
        inserted_id = ObjectId()
        self.mock_collection.insert_one.return_value = MagicMock(inserted_id=inserted_id)

        result = self.repo.save(commodity)

        self.mock_collection.insert_one.assert_called_once_with({"name": "Laranite", "code": "LARA"})
        assert result.id == str(inserted_id)

    def test_find_by_id_found(self) -> None:
        oid = ObjectId()
        self.mock_collection.find_one.return_value = {"_id": oid, "name": "Laranite", "code": "LARA"}

        result = self.repo.find_by_id(str(oid))

        assert result is not None
        assert result.name == "Laranite"
        self.mock_collection.find_one.assert_called_once_with({"_id": oid})

    def test_find_by_id_not_found(self) -> None:
        oid = ObjectId()
        self.mock_collection.find_one.return_value = None

        result = self.repo.find_by_id(str(oid))

        assert result is None

    def test_find_all(self) -> None:
        self.mock_collection.find.return_value = [
            {"_id": ObjectId(), "name": "Laranite", "code": "LARA"},
            {"_id": ObjectId(), "name": "Quantainium", "code": "QUANT"},
        ]

        result = self.repo.find_all()

        assert len(result) == 2
        self.mock_collection.find.assert_called_once()

    def test_search_by_name(self) -> None:
        self.mock_collection.find.return_value = [
            {"_id": ObjectId(), "name": "Laranite", "code": "LARA"},
        ]

        result = self.repo.search_by_name("lar")

        assert len(result) == 1
        self.mock_collection.find.assert_called_once_with({"name": {"$regex": "lar", "$options": "i"}})

    def test_update_found(self) -> None:
        oid = ObjectId()
        self.mock_collection.find_one_and_update.return_value = {
            "_id": oid,
            "name": "Updated",
            "code": "UPD",
        }

        result = self.repo.update(str(oid), Commodity(name="Updated", code="UPD"))

        assert result is not None
        assert result.name == "Updated"

    def test_update_not_found(self) -> None:
        oid = ObjectId()
        self.mock_collection.find_one_and_update.return_value = None

        result = self.repo.update(str(oid), Commodity(name="Updated", code="UPD"))

        assert result is None

    def test_update_no_fields(self) -> None:
        oid = ObjectId()
        self.mock_collection.find_one.return_value = {"_id": oid, "name": "Existing", "code": "EX"}

        result = self.repo.update(str(oid), Commodity())

        assert result is not None
        assert result.name == "Existing"
        self.mock_collection.find_one_and_update.assert_not_called()

    def test_delete_found(self) -> None:
        oid = ObjectId()
        self.mock_collection.delete_one.return_value = MagicMock(deleted_count=1)

        result = self.repo.delete(str(oid))

        assert result is True

    def test_delete_not_found(self) -> None:
        oid = ObjectId()
        self.mock_collection.delete_one.return_value = MagicMock(deleted_count=0)

        result = self.repo.delete(str(oid))

        assert result is False

    def test_update_partial_name_only(self) -> None:
        oid = ObjectId()
        self.mock_collection.find_one_and_update.return_value = {
            "_id": oid,
            "name": "NewName",
            "code": "OLD",
        }

        result = self.repo.update(str(oid), Commodity(name="NewName"))

        assert result is not None
        self.mock_collection.find_one_and_update.assert_called_once()
        call_args = self.mock_collection.find_one_and_update.call_args
        assert call_args[0][1] == {"$set": {"name": "NewName"}}

    def test_update_partial_code_only(self) -> None:
        oid = ObjectId()
        self.mock_collection.find_one_and_update.return_value = {
            "_id": oid,
            "name": "Old",
            "code": "NEW",
        }

        result = self.repo.update(str(oid), Commodity(code="NEW"))

        assert result is not None
        call_args = self.mock_collection.find_one_and_update.call_args
        assert call_args[0][1] == {"$set": {"code": "NEW"}}
