from datetime import UTC, datetime

from hhh_events.schemas import EventDocument, EventMode


class TestEventMode:
    def test_values(self) -> None:
        assert EventMode.FULL_SYNC == "full_sync"
        assert EventMode.INCREMENTAL == "incremental"
        assert EventMode.DELETE == "delete"


class TestEventDocument:
    def test_create_with_defaults(self) -> None:
        event = EventDocument(
            type="commodities.imported",
            source_service="dataminer",
            modified_ids=["id1", "id2"],
            mode=EventMode.FULL_SYNC,
        )
        assert event.type == "commodities.imported"
        assert event.source_service == "dataminer"
        assert event.modified_ids == ["id1", "id2"]
        assert event.mode == EventMode.FULL_SYNC
        assert isinstance(event.timestamp, datetime)
        assert event.metadata == {}

    def test_create_with_explicit_fields(self) -> None:
        ts = datetime(2026, 3, 22, 12, 0, 0, tzinfo=UTC)
        event = EventDocument(
            type="ships.imported",
            source_service="dataminer",
            modified_ids=["s1"],
            mode=EventMode.INCREMENTAL,
            timestamp=ts,
            metadata={"batch_size": 42},
        )
        assert event.timestamp == ts
        assert event.metadata == {"batch_size": 42}

    def test_model_dump(self) -> None:
        ts = datetime(2026, 1, 1, tzinfo=UTC)
        event = EventDocument(
            type="maps.imported",
            source_service="dataminer",
            modified_ids=[],
            mode=EventMode.DELETE,
            timestamp=ts,
        )
        data = event.model_dump()
        assert data == {
            "type": "maps.imported",
            "source_service": "dataminer",
            "modified_ids": [],
            "mode": "delete",
            "timestamp": ts,
            "metadata": {},
        }

    def test_empty_modified_ids(self) -> None:
        event = EventDocument(
            type="test",
            source_service="svc",
            modified_ids=[],
            mode=EventMode.FULL_SYNC,
        )
        assert event.modified_ids == []
