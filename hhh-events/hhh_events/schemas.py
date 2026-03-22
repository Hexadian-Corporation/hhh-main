from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class EventMode(StrEnum):
    FULL_SYNC = "full_sync"
    INCREMENTAL = "incremental"
    DELETE = "delete"


class EventDocument(BaseModel):
    type: str
    source_service: str
    modified_ids: list[str]
    mode: EventMode
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)
