# hhh-commodities-service

Commodity data management microservice for **H³ – Hexadian Hauling Helper**.

## Domain

Manages commodity information used in hauling contracts — types, prices, and trade data.

## Stack

- Python 3.11+ / FastAPI
- MongoDB (database: `hhh_commodities`)
- opyoid (dependency injection)
- Hexagonal architecture (Ports & Adapters)

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- MongoDB running on localhost:27017

## Setup

```bash
uv sync
```

## Run

```bash
uv run uvicorn src.main:app --reload --port 8007
```

## Test

```bash
uv run pytest
```

## Lint

```bash
uv run ruff check .
```

## Format

```bash
uv run ruff format .
```

## Run in Docker (full stack)

From the monorepo root (`hhh-main`):

```bash
uv run hhh up
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `HHH_COMMODITIES_MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `HHH_COMMODITIES_MONGO_DB` | `hhh_commodities` | Database name |
| `HHH_COMMODITIES_PORT` | `8007` | Service port |

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
