from motor.motor_asyncio import AsyncIOMotorCollection

from hhh_events.schemas import EventDocument


class EventPublisher:
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self._collection = collection

    async def publish(self, event: EventDocument) -> None:
        await self._collection.insert_one(event.model_dump())
