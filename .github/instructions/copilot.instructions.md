
<critical>Note: This is a living document and will be updated as we refine our processes. Always refer back to this for the latest guidelines. Update whenever necessary.</critical>

# Copilot Instructions — H³ Hexadian Hauling Helper

## Project Overview

**H³ (Hexadian Hauling Helper)** is a Star Citizen companion app for managing hauling contracts. The product is owned by **Hexadian Corporation** (GitHub org: `Hexadian-Corporation`).

The workspace at `hhh-main` is a monorepo with **git submodules** — one per service/frontend. Each submodule has its **own GitHub repository** under the org.

## Repository Map

| Submodule | Repo | Port | Stack | Purpose |
|-----------|------|------|-------|---------|
| `hhh-contracts-service` | `Hexadian-Corporation/hhh-contracts-service` | 8001 | Python · FastAPI · MongoDB | Hauling contract CRUD (catalog) |
| `hhh-ships-service` | `Hexadian-Corporation/hhh-ships-service` | 8002 | Python · FastAPI · MongoDB | Ship data management |
| `hhh-maps-service` | `Hexadian-Corporation/hhh-maps-service` | 8003 | Python · FastAPI · MongoDB | Location / map data (stations, cities, orbitals) |
| `hhh-graphs-service` | `Hexadian-Corporation/hhh-graphs-service` | 8004 | Python · FastAPI · MongoDB | Graph/analytics service |
| `hhh-routes-service` | `Hexadian-Corporation/hhh-routes-service` | 8005 | Python · FastAPI · MongoDB | Route calculation (depends on contracts, ships, maps, graphs) |
| `hhh-auth-service` | `Hexadian-Corporation/hhh-auth-service` | 8006 | Python · FastAPI · MongoDB | User auth (register, login, JWT, RSI verification) |
| `hhh-frontend` | `Hexadian-Corporation/hhh-frontend` | 3000 | React 19 · TypeScript · Vite 8 | Player-facing frontend |
| `hhh-backoffice-frontend` | `Hexadian-Corporation/hhh-backoffice-frontend` | 3001 | React 19 · TypeScript · Vite 8 | Admin backoffice |

The root `hhh-main` repo (`Hexadian-Corporation/hhh-main`) contains:
- `docker-compose.yml` — orchestrates all services + MongoDB 3-node replica set
- `.github/` — labels, workflows, project board config
- `pyproject.toml` — workspace-level Python config

### hhh-main — Root Monorepo

```
hhh-main/
├── docker-compose.yml               # Full-stack orchestration (all services + MongoDB replica set)
├── pyproject.toml                    # Workspace-level Python config
├── .github/
│   ├── instructions/                # Copilot instruction files (VS Code local)
│   ├── labels.yml                   # Synced label definitions
│   ├── PROJECT_BOARD.md             # Project board reference
│   └── workflows/                   # Workflows: pr-title, sync-submodules, auto-unblock
├── hhh-contracts-service/           # Submodule → Hexadian-Corporation/hhh-contracts-service
├── hhh-ships-service/               # Submodule → Hexadian-Corporation/hhh-ships-service
├── hhh-maps-service/                # Submodule → Hexadian-Corporation/hhh-maps-service
├── hhh-graphs-service/              # Submodule → Hexadian-Corporation/hhh-graphs-service
├── hhh-routes-service/              # Submodule → Hexadian-Corporation/hhh-routes-service
├── hhh-auth-service/                # Submodule → Hexadian-Corporation/hhh-auth-service
├── hhh-frontend/                    # Submodule → Hexadian-Corporation/hhh-frontend
└── hhh-backoffice-frontend/         # Submodule → Hexadian-Corporation/hhh-backoffice-frontend
```

**Workflows in hhh-main:**
- **`pr-title.yml`** — Validates PR title format: `<type>(main): description`
- **`sync-submodules.yml`** — Triggered by `repository_dispatch` (`submodule-updated`) from any submodule. Runs `git submodule update --remote --merge`, commits and pushes updated refs.
- **`auto-unblock.yml`** — Runs every 15 minutes + on `repository_dispatch` (`unblock-check`). Checks all "Blocked" items on the project board and moves them to "Ready" when all blocking issues are closed.

**hhh-main issue & PR title format:** `<type>(main): description` (e.g., `ci(main): add auto-unblock workflow`)

**hhh-main quality standards:** CI only runs `Validate PR Title`. No lint/test jobs (no application code in this repo). Squash merge only.

## Architecture

### Backend Services — Hexagonal Architecture

Every Python backend follows the same **Hexagonal (Ports & Adapters)** layout:

```
src/
├── main.py                          # FastAPI app factory + uvicorn
├── domain/
│   ├── models/                      # Pure dataclasses (no framework deps)
│   └── exceptions/                  # Domain-specific exceptions
├── application/
│   ├── ports/
│   │   ├── inbound/                 # Service interfaces (ABC)
│   │   └── outbound/               # Repository / external service interfaces (ABC)
│   └── services/                    # Implementations of inbound ports
└── infrastructure/
    ├── config/
    │   ├── settings.py              # pydantic-settings (env prefix: HHH_{SERVICE}_)
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
- Settings use `pydantic-settings` with env prefix `HHH_{SERVICE_NAME}_`
- Repositories use **pymongo** directly (no ODM)

**Router patterns (two in use):**

| Pattern | Used by | Description |
|---------|---------|-------------|
| `init_router(service)` + module-level `router` | maps, auth, ships, graphs, routes | Module-level `_service: Service \| None = None` initialized via `init_router()`. Router is a module-level `APIRouter`. `main.py` uses `create_app()` factory + `uvicorn.run()`. |
| `create_X_router(service) -> APIRouter` | contracts | Factory function that creates and returns a configured `APIRouter`. `main.py` uses a flat module-level `app` without `create_app()`. |

> **Note:** The `init_router()` pattern is the standard. The contracts-service factory pattern is legacy and will be migrated.

### Frontend — React + TypeScript

Both frontends share the intended stack (being set up):
- **React 19** + **TypeScript 5.9** + **Vite 8**
- **React Router v7** for routing
- **Tailwind CSS v4** (via Vite plugin) for styling
- **shadcn/ui** for component library
- **lucide-react** for icons
- API client modules using `fetch` with configurable base URL via `VITE_{SERVICE}_API_URL`

### Infrastructure

- **MongoDB 7** — 3-node replica set (`rs0`) via docker-compose
- **Database-per-service** pattern — each service has its own DB (e.g., `hhh_contracts`, `hhh_maps`, `hhh_auth`)
- Docker images use `mirror.gcr.io/library/` prefix for base images

## Domain Context

### Contracts Service — Hauling Contracts (Catalog)

A `Contract` represents an **available contract** in the catalog (not an accepted one).

- **Contract** — `id`, `title`, `description`, `status` (draft/active/expired/cancelled), `faction`, `reward_uec`, `collateral_uec`, `deadline`, `hauling_orders` (list), `requirements`, `created_at`, `updated_at`
- **HaulingOrder** — `commodity`, `scu_min`, `scu_max`, `max_container_scu`, `pickup_location_id`, `delivery_location_id`
- **Requirements** — `min_reputation` (0–5 int), `required_ship_tags` (list[str]), `max_crew_size` (int)

**Status values:** `draft` | `active` | `expired` | `cancelled`

**Future:** `AcceptedContract` entity will reference `Contract.id` + `User.id` — NOT implemented yet.

### Maps Service — Location Hierarchy

Locations use `parent_id` to form a tree:

- **Location** — `id`, `name`, `location_type`, `parent_id`, `coordinates` (x/y/z), `has_trade_terminal`, `has_landing_pad`, `landing_pad_size`
- **Coordinates** — `x`, `y`, `z` (all floats)

**`location_type` values:** `system` | `planet` | `moon` | `station` | `city` | `outpost`

**Hierarchy:** System → Planet/Moon → Station/City/Outpost. Top-level systems have `parent_id = None`.

Each `HaulingOrder.pickup_location_id` and `delivery_location_id` reference a Location ID.

### Ships Service — Ship Data

- **Ship** — `id`, `name`, `manufacturer`, `cargo_holds` (list), `total_scu`, `scm_speed`, `quantum_speed`, `landing_time_seconds`, `loading_time_per_scu_seconds`
- **CargoHold** — `name`, `volume_scu`, `max_box_size_scu`

### Graphs Service — Navigation Graph

- **Graph** — `id`, `name`, `nodes` (list), `edges` (list)
- **Node** — `location_id`, `label`
- **Edge** — `source_id`, `target_id`, `distance`, `travel_type` (quantum/scm/on_foot), `travel_time_seconds`

### Routes Service — Route Optimization

- **Route** — `id`, `params`, `stops` (list), `legs` (list), `total_distance`, `total_time_seconds`, `total_reward`, `contracts_fulfilled`
- **RouteStop** — `location_id`, `location_name`, `action` (pickup/delivery), `contract_id`, `cargo_name`, `cargo_scu`
- **RouteLeg** — `from_location_id`, `to_location_id`, `distance`, `travel_time_seconds`, `travel_type`
- **OptimizationParams** — `ship_id`, `contract_ids`, `strategy` (max_profit/min_time/min_distance), `max_route_time_seconds`

### Auth Service — User & RSI Verification

**User model:** `id`, `username`, `email`, `hashed_password`, `roles` (default: `["user"]`), `is_active`

**RSI verification flow (not yet implemented — AUTH-1):**
1. `POST /auth/verify/start` — generates a unique code, user puts it in their RSI profile bio
2. `POST /auth/verify/confirm` — service fetches `robertsspaceindustries.com/citizens/{handle}`, checks for the code
3. `User.rsi_verified` is set to `true` on success

Handle validation: `^[A-Za-z0-9_-]{3,30}$` (strict, to prevent SSRF).

## UI Design — Hexadian Branding

### Color Palette (CSS Custom Properties)

```css
:root {
  --color-bg: #0a0e17;         /* Dark space background */
  --color-surface: #111827;     /* Card / panel surface */
  --color-border: #1f2937;      /* Subtle borders */
  --color-accent: #06b6d4;      /* Cyan accent (primary actions) */
  --color-success: #10b981;     /* Green */
  --color-warning: #f59e0b;     /* Amber */
  --color-danger: #ef4444;      /* Red */
  --color-text: #e5e7eb;        /* Primary text */
  --color-text-muted: #9ca3af;  /* Secondary text */
}
```

### Status Badge Colors

| Status | Color |
|--------|-------|
| draft | Gray |
| active | Cyan (`--color-accent`) |
| expired | Amber (`--color-warning`) |
| cancelled | Red (`--color-danger`) |

## Project Management

### GitHub Project Board

URL: <https://github.com/orgs/Hexadian-Corporation/projects/1>

**Columns (Status field):**
- **Backlog** (gray) — Not yet prioritized
- **Ready** (blue) — Ready to pick up
- **Blocked** (red) — Waiting on dependencies
- **In Progress** (yellow) — Actively being worked on
- **In Review** (purple) — PR open, awaiting review
- **Done** (green) — Merged and closed

**Priority field:** High (red), Medium (yellow), Low (green)

### Milestones

| Milestone | Repo(s) | Description |
|-----------|---------|-------------|
| M0: Project Setup | hhh-main, hhh-maps-service | Board config, seed locations |
| M1: Hauling Contracts — Domain & API | hhh-contracts-service | Enrich domain, DTOs, mappers, PUT endpoint, CORS, MongoDB, tests |
| M2: Backoffice — Contract Management | hhh-backoffice-frontend | Setup, types/API client, list page, edit page (3-tab form) |
| M3: Frontend — Contract Creation | hhh-frontend | Setup, types/API client, landing page, create form (3-tab) |
| M4: Auth — RSI Account Verification | hhh-auth-service | Verify endpoint (code generation + RSI profile scraping) |

### Labels

Custom labels synced across repos: `domain`, `api`, `persistence`, `backend`, `frontend`, `setup`, `testing`, `feature`, `enhancement`, `backoffice`, `priority:high`, `priority:medium`, `project-management`

## Quality Standards

All code contributions must:
1. **Be formatted** — Python: `ruff format .` / TypeScript: Prettier via ESLint
2. **Pass linting** — Python: `ruff check .` / TypeScript: `npm run lint`
3. **Have ≥90% test coverage on changed lines** — enforced via `diff-cover` on PR diffs (not whole-repo thresholds)
4. **Type-check cleanly** — Python: type hints / TypeScript: `tsc --noEmit`
5. **Pass CI** — All checks (`Lint & Format`/`Lint & Type Check` + `Tests & Coverage` + `Validate PR Title`) must pass before merge
6. **Branch up to date** — PR branch must be up to date with `main` (strict mode enabled)
7. **PR title format** — Must match `<type>(<scope>): description` (e.g., `feat(contracts): add domain models`). Issue title = PR title — use the same format for both.
8. **No review required** — approving review count set to 0 (Copilot agent PRs can merge without external reviewer)

## Tooling

| Tool | Purpose |
|------|---------|
| `uv` | Python package manager + project CLI |
| `uv run hhh` | Monorepo CLI: `up`, `down`, `logs`, `setup`, `sync`, `start` |
| `ruff` | Python linter + formatter |
| `pytest` | Python test runner |
| `diff-cover` | PR-only coverage enforcement (changed lines only) |
| `vite` | Frontend dev server + bundler |
| `docker compose` | Full-stack orchestration (wrapped by `uv run hhh up`) |
| `gh` CLI | GitHub issue/PR/project management |

## Common Commands

```bash
# Start all services (Docker)
uv run hhh up

# Stop all services
uv run hhh down

# Local setup (first time: submodules + deps)
uv run hhh setup

# Run a backend with hot-reload
cd hhh-contracts-service && uv run uvicorn src.main:app --reload --port 8001

# Run Python tests in a service
cd hhh-contracts-service && uv run pytest

# Run Python linter
cd hhh-contracts-service && uv run ruff check .

# Run frontend dev server
cd hhh-frontend && npm run dev
```
