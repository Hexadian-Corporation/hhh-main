from unittest.mock import AsyncMock

from hhh_events.indexes import _TTL_SECONDS, ensure_events_indexes


class TestEnsureEventsIndexes:
    async def test_creates_ttl_and_helper_indexes(self) -> None:
        collection = AsyncMock()
        await ensure_events_indexes(collection)

        calls = collection.create_index.await_args_list
        assert len(calls) == 3

        # TTL index on timestamp
        ttl_call = calls[0]
        assert ttl_call.args[0] == [("timestamp", 1)]
        assert ttl_call.kwargs["expireAfterSeconds"] == _TTL_SECONDS

        # Helper indexes
        assert calls[1].args[0] == [("type", 1)]
        assert calls[2].args[0] == [("source_service", 1)]

    def test_ttl_is_30_days(self) -> None:
        assert _TTL_SECONDS == 30 * 24 * 60 * 60
