# hhh-events

Shared MongoDB Change Streams event infrastructure for H³ inter-service communication.

## Overview

Provides event publishing and subscribing utilities built on MongoDB Change Streams,
enabling async inter-service communication without additional infrastructure.

## Usage

```python
from src.hhh_events import EventPublisher, EventSubscriber, EventDocument, EventMode, ensure_events_indexes
```
