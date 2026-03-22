from collections.abc import AsyncGenerator
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from hhh_events.schemas import EventDocument


class EventSubscriber:
    def __init__(
        self,
        events_collection: AsyncIOMotorCollection,
        token_collection: AsyncIOMotorCollection,
        subscriber_id: str,
        event_types: list[str] | None = None,
    ) -> None:
        self._events_collection = events_collection
        self._token_collection = token_collection
        self._subscriber_id = subscriber_id
        self._event_types = event_types

    async def _load_token(self) -> dict[str, Any] | None:
        doc = await self._token_collection.find_one({"_id": self._subscriber_id})
        if doc is not None:
            return doc["resume_token"]
        return None

    async def _save_token(self, token: dict[str, Any]) -> None:
        await self._token_collection.update_one(
            {"_id": self._subscriber_id},
            {"$set": {"resume_token": token}},
            upsert=True,
        )

    async def stream(self) -> AsyncGenerator[EventDocument, None]:
        pipeline: list[dict[str, Any]] = [{"$match": {"operationType": "insert"}}]
        if self._event_types:
            pipeline.append({"$match": {"fullDocument.type": {"$in": self._event_types}}})

        resume_token = await self._load_token()
        kwargs: dict[str, Any] = {"pipeline": pipeline}
        if resume_token is not None:
            kwargs["resume_after"] = resume_token

        async with self._events_collection.watch(**kwargs) as change_stream:
            async for change in change_stream:
                await self._save_token(change["_id"])
                doc = change["fullDocument"]
                doc.pop("_id", None)
                yield EventDocument(**doc)
