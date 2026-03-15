<critical>Note: This is a living document and will be updated as we refine our processes. Always refer back to this for the latest guidelines. Update whenever necessary.</critical>

# Copilot Instructions — hhh-commodities-service

## Project Context

**H³ (Hexadian Hauling Helper)** is a Star Citizen companion app for managing hauling contracts, owned by **Hexadian Corporation** (GitHub org: `Hexadian-Corporation`).

This service manages **commodity reference data** — the trade goods available in Star Citizen that are referenced by hauling contracts.

- **Repo:** `Hexadian-Corporation/hhh-commodities-service`
- **Port:** 8007
- **Stack:** Python · FastAPI · MongoDB · pymongo · opyoid (DI) · pydantic-settings · cachetools

## Architecture — Hexagonal (Ports & Adapters)

```
src/
├── main.py                          # FastAPI app factory + uvicorn
├── domain/
│   ├── models/                      # Pure dataclasses (no framework deps)
│   └── exceptions/                  # Domain-specific exceptions
├── application/
│   ├── ports/
│   │   ├── inbound/                 # Service interfaces (ABC)
│   │   └── outbound/               # Repository interfaces (ABC)
│   └── services/                    # Implementations of inbound ports
└── infrastructure/
    ├── config/
    │   ├── settings.py              # pydantic-settings (env prefix: HHH_COMMODITIES_)
    │   └── dependencies.py          # opyoid DI Module
    └── adapters/
        ├── inbound/api/             # FastAPI router, DTOs (Pydantic), API mappers
        └── outbound/persistence/    # MongoDB repository, persistence mappers
```

**Key conventions:**
- Domain models are **pure Python dataclasses** — no Pydantic, no ORM
- DTOs at the API boundary are **Pydantic BaseModel** subclasses
- Mappers are **static classes** (`to_domain`, `to_dto`, `to_document`)
- DI uses **opyoid** (`Module`, `Injector`, `SingletonScope`)
- Repositories use **pymongo** directly (no ODM)
- Router pattern: **`init_router(service)` + module-level `router`** (standard pattern)

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

> **Note:** CRUD endpoints will be added as part of COMM-2.

## Issue & PR Title Format

**Format:** `<type>(commodities): description`

- Example: `feat(commodities): add commodity domain model`
- Example: `fix(commodities): resolve search query bug`

**Allowed types:** `chore`, `fix`, `ci`, `docs`, `feat`, `refactor`, `test`, `build`, `perf`, `style`, `revert`

The issue title and PR title must be **identical**. PR body must include `Fixes #N`.

## Quality Standards

- `ruff check .` + `ruff format --check .` must pass
- `pytest --cov=src` with ≥90% coverage on changed lines (`diff-cover`)
- Type hints on all functions
- Squash merge only — PR title becomes the commit message

## Tooling

| Action | Command |
|--------|---------|
| Setup | `uv sync` |
| Run (dev) | `uv run uvicorn src.main:app --reload --port 8007` |
| Run in Docker | `uv run hhh up` (from monorepo root) |
| Test | `uv run pytest` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |

## Maintenance Rules

- **Keep the README up to date.** When you add, remove, or change commands, environment variables, API endpoints, domain models, or architecture — update `README.md`. The README is the source of truth for developers.
- **Keep the monorepo CLI service registry up to date.** When adding or removing a service, update `SERVICES`, `FRONTENDS`, `COMPOSE_SERVICE_MAP`, and `SERVICE_ALIASES` in `hhh-main/hhh_cli/__init__.py`, plus the `docker-compose.yml` entry.
