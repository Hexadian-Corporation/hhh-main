import asyncio

from motor.motor_asyncio import AsyncIOMotorCollection

from hhh_events.indexes import ensure_events_indexes
from hhh_events.publisher import EventPublisher
from hhh_events.schemas import EventDocument, EventMode
from hhh_events.subscriber import EventSubscriber


class TestPublishSubscribeRoundTrip:
    async def test_published_event_is_received_by_subscriber(
        self,
        events_collection: AsyncIOMotorCollection,
        token_collection: AsyncIOMotorCollection,
    ) -> None:
        await ensure_events_indexes(events_collection)

        publisher = EventPublisher(events_collection)
        subscriber = EventSubscriber(
            events_collection,
            token_collection,
            "test-round-trip",
        )

        event = EventDocument(
            type="ships.imported",
            source_service="dataminer",
            modified_ids=["s1", "s2"],
            mode=EventMode.FULL_SYNC,
            metadata={"batch": 1},
        )

        received: list[EventDocument] = []

        async def consume() -> None:
            async for evt in subscriber.stream():
                received.append(evt)
                break  # stop after first event

        consumer_task = asyncio.create_task(consume())
        await asyncio.sleep(0.5)  # let the watch() start listening
        await publisher.publish(event)
        await asyncio.wait_for(consumer_task, timeout=10.0)

        assert len(received) == 1
        assert received[0].type == "ships.imported"
        assert received[0].source_service == "dataminer"
        assert received[0].modified_ids == ["s1", "s2"]
        assert received[0].mode == EventMode.FULL_SYNC
        assert received[0].metadata == {"batch": 1}

    async def test_subscriber_filters_by_event_type(
        self,
        events_collection: AsyncIOMotorCollection,
        token_collection: AsyncIOMotorCollection,
    ) -> None:
        publisher = EventPublisher(events_collection)
        subscriber = EventSubscriber(
            events_collection,
            token_collection,
            "test-filter",
            event_types=["ships.imported"],
        )

        received: list[EventDocument] = []

        async def consume() -> None:
            async for evt in subscriber.stream():
                received.append(evt)
                break

        consumer_task = asyncio.create_task(consume())
        await asyncio.sleep(0.5)

        # Publish an event that should NOT match the filter
        await publisher.publish(
            EventDocument(
                type="maps.imported",
                source_service="dataminer",
                modified_ids=["m1"],
                mode=EventMode.FULL_SYNC,
            )
        )
        # Publish an event that SHOULD match the filter
        await publisher.publish(
            EventDocument(
                type="ships.imported",
                source_service="dataminer",
                modified_ids=["s1"],
                mode=EventMode.INCREMENTAL,
            )
        )

        await asyncio.wait_for(consumer_task, timeout=10.0)

        assert len(received) == 1
        assert received[0].type == "ships.imported"


class TestResumeTokenPersistence:
    async def test_subscriber_resumes_after_restart(
        self,
        events_collection: AsyncIOMotorCollection,
        token_collection: AsyncIOMotorCollection,
    ) -> None:
        publisher = EventPublisher(events_collection)
        subscriber_id = "test-resume"

        # First subscriber: consume one event and stop
        sub1 = EventSubscriber(events_collection, token_collection, subscriber_id)

        async def consume_one(sub: EventSubscriber) -> EventDocument:
            async for evt in sub.stream():
                return evt
            raise AssertionError("No events received")  # pragma: no cover

        task1 = asyncio.create_task(consume_one(sub1))
        await asyncio.sleep(0.5)

        await publisher.publish(
            EventDocument(
                type="event.first",
                source_service="svc",
                modified_ids=["1"],
                mode=EventMode.FULL_SYNC,
            )
        )

        first = await asyncio.wait_for(task1, timeout=10.0)
        assert first.type == "event.first"

        # Publish second event AFTER first subscriber stopped
        await publisher.publish(
            EventDocument(
                type="event.second",
                source_service="svc",
                modified_ids=["2"],
                mode=EventMode.INCREMENTAL,
            )
        )

        # New subscriber with same ID — should resume after the first event
        sub2 = EventSubscriber(events_collection, token_collection, subscriber_id)
        task2 = asyncio.create_task(consume_one(sub2))
        second = await asyncio.wait_for(task2, timeout=10.0)

        assert second.type == "event.second"
        assert second.modified_ids == ["2"]
