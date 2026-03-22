from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING

_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 days


async def ensure_events_indexes(collection: AsyncIOMotorCollection) -> None:
    await collection.create_index(
        [("timestamp", ASCENDING)],
        expireAfterSeconds=_TTL_SECONDS,
    )
    await collection.create_index([("type", ASCENDING)])
    await collection.create_index([("source_service", ASCENDING)])
