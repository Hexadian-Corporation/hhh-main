from unittest.mock import AsyncMock, MagicMock

from hhh_events.schemas import EventMode
from hhh_events.subscriber import EventSubscriber


class TestEventSubscriberTokenPersistence:
    async def test_load_token_returns_none_when_not_found(self) -> None:
        events_col = AsyncMock()
        token_col = AsyncMock()
        token_col.find_one.return_value = None

        sub = EventSubscriber(events_col, token_col, "test-sub")
        token = await sub._load_token()

        assert token is None
        token_col.find_one.assert_awaited_once_with({"_id": "test-sub"})

    async def test_load_token_returns_stored_token(self) -> None:
        events_col = AsyncMock()
        token_col = AsyncMock()
        token_col.find_one.return_value = {"_id": "test-sub", "resume_token": {"_data": "abc123"}}

        sub = EventSubscriber(events_col, token_col, "test-sub")
        token = await sub._load_token()

        assert token == {"_data": "abc123"}

    async def test_save_token_upserts(self) -> None:
        events_col = AsyncMock()
        token_col = AsyncMock()

        sub = EventSubscriber(events_col, token_col, "my-subscriber")
        await sub._save_token({"_data": "xyz"})

        token_col.update_one.assert_awaited_once_with(
            {"_id": "my-subscriber"},
            {"$set": {"resume_token": {"_data": "xyz"}}},
            upsert=True,
        )


class TestEventSubscriberPipeline:
    def test_pipeline_without_event_types(self) -> None:
        sub = EventSubscriber(AsyncMock(), AsyncMock(), "sub1")
        assert sub._event_types is None

    def test_pipeline_with_event_types(self) -> None:
        sub = EventSubscriber(
            AsyncMock(),
            AsyncMock(),
            "sub1",
            event_types=["ships.imported", "maps.imported"],
        )
        assert sub._event_types == ["ships.imported", "maps.imported"]


class TestEventSubscriberStream:
    async def test_stream_yields_events(self) -> None:
        events_col = AsyncMock()
        token_col = AsyncMock()
        token_col.find_one.return_value = None

        change_doc = {
            "_id": {"_data": "resume123"},
            "operationType": "insert",
            "fullDocument": {
                "_id": "objectid_here",
                "type": "ships.imported",
                "source_service": "dataminer",
                "modified_ids": ["s1"],
                "mode": "full_sync",
                "timestamp": "2026-03-22T00:00:00+00:00",
                "metadata": {},
            },
        }

        # Motor's watch() returns a ChangeStream directly (not a coroutine)
        mock_stream = MagicMock()
        mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_stream.__aexit__ = AsyncMock(return_value=False)

        async def _async_iter():
            yield change_doc

        mock_stream.__aiter__ = lambda self: _async_iter()

        # watch() is NOT a coroutine in Motor — it returns the stream object directly
        events_col.watch = MagicMock(return_value=mock_stream)

        sub = EventSubscriber(events_col, token_col, "test-sub")
        events = []
        async for event in sub.stream():
            events.append(event)

        assert len(events) == 1
        assert events[0].type == "ships.imported"
        assert events[0].mode == EventMode.FULL_SYNC
        assert events[0].modified_ids == ["s1"]

        # Verify resume token was saved
        token_col.update_one.assert_awaited_once_with(
            {"_id": "test-sub"},
            {"$set": {"resume_token": {"_data": "resume123"}}},
            upsert=True,
        )
