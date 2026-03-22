from datetime import UTC, datetime
from unittest.mock import AsyncMock

from hhh_events.publisher import EventPublisher
from hhh_events.schemas import EventDocument, EventMode


class TestEventPublisher:
    async def test_publish_inserts_document(self) -> None:
        collection = AsyncMock()
        publisher = EventPublisher(collection)
        ts = datetime(2026, 3, 22, tzinfo=UTC)
        event = EventDocument(
            type="ships.imported",
            source_service="dataminer",
            modified_ids=["s1", "s2"],
            mode=EventMode.FULL_SYNC,
            timestamp=ts,
            metadata={"source": "uex"},
        )

        await publisher.publish(event)

        collection.insert_one.assert_awaited_once_with(
            {
                "type": "ships.imported",
                "source_service": "dataminer",
                "modified_ids": ["s1", "s2"],
                "mode": "full_sync",
                "timestamp": ts,
                "metadata": {"source": "uex"},
            }
        )

    async def test_publish_multiple_events(self) -> None:
        collection = AsyncMock()
        publisher = EventPublisher(collection)
        for i in range(3):
            event = EventDocument(
                type=f"test.event.{i}",
                source_service="svc",
                modified_ids=[str(i)],
                mode=EventMode.INCREMENTAL,
            )
            await publisher.publish(event)

        assert collection.insert_one.await_count == 3
