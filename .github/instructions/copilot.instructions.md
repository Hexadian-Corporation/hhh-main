
<critical>Note: This is a living document and will be updated as we refine our processes. Always refer back to this for the latest guidelines. Update whenever necessary.</critical>

<critical>**Development Workflow:** All changes go through a branch + PR — no direct commits to `main` unless explicitly instructed. See `.github/instructions/development-workflow.instructions.md`.</critical>

<critical>**PR and Issue linkage:** When creating a pull request from an issue, always mention the issue number in the PR description using `Fixes #N`, `Closes #N`, or `Resolves #N`. This is required for GitHub to auto-close the issue on merge.</critical>

<critical>**Before starting implementation:** Read ALL instruction files in `.github/instructions/` of this repository. Also read the organization-level instructions from the `Hexadian-Corporation/.github` repository (`.github/instructions/` directory). These contain essential rules for workflow, bug history, domain models, and GitHub procedures that you MUST follow.</critical>

<critical>**PR title:** The PR title MUST be identical to the originating issue title. Set the final PR title (remove the `[WIP]` prefix) before beginning implementation, not after.</critical>

# Copilot Instructions — H³ Hexadian Hauling Helper

## Project Overview

**H³ (Hexadian Hauling Helper)** is a Star Citizen companion app for managing hauling contracts. The product is owned by **Hexadian Corporation** (GitHub org: `Hexadian-Corporation`).

The workspace at `hexadian-hauling-helper` is a monorepo with **git submodules** — one per service/frontend. Each submodule has its **own GitHub repository** under the org.

## Repository Map

| Submodule | Repo | Port | Stack | Purpose |
|-----------|------|------|-------|---------|
| `hhh-contracts-service` | `Hexadian-Corporation/hhh-contracts-service` | 8001 | Python · FastAPI · MongoDB | Hauling contract CRUD (catalog) |
| `hhh-ships-service` | `Hexadian-Corporation/hhh-ships-service` | 8002 | Python · FastAPI · MongoDB | Ship data management |
| `hhh-maps-service` | `Hexadian-Corporation/hhh-maps-service` | 8003 | Python · FastAPI · MongoDB | Location / map data (stations, cities, orbitals) |
| `hhh-graphs-service` | `Hexadian-Corporation/hhh-graphs-service` | 8004 | Python · FastAPI · MongoDB | Graph/analytics service |
| `hhh-routes-service` | `Hexadian-Corporation/hhh-routes-service` | 8005 | Python · FastAPI · MongoDB | Route calculation (depends on contracts, ships, maps, graphs) |
| `hhh-commodities-service` | `Hexadian-Corporation/hhh-commodities-service` | 8007 | Python · FastAPI · MongoDB | Commodity reference data (trade goods catalog) |
| `hhh-dataminer` | `Hexadian-Corporation/hhh-dataminer` | 8008 | Python · FastAPI · MongoDB | Game data import orchestration (multi-source merge) |
| `hhh-frontend` | `Hexadian-Corporation/hhh-frontend` | 3000 | React 19 · TypeScript · Vite 8 | Player-facing frontend |
| `hhh-backoffice-frontend` | `Hexadian-Corporation/hhh-backoffice-frontend` | 3001 | React 19 · TypeScript · Vite 8 | Admin backoffice |

**Standalone libraries (not submodules):**

| Library | Repo | Packages | Stack | Purpose |
|---------|------|----------|-------|---------|
| `hexadian-auth-client` | `Hexadian-Corporation/hexadian-auth-client` | `@hexadian-corporation/auth-core`, `auth-react`, `auth-node`, `auth-angular` | TypeScript · npm workspaces | Auth client SDK — OAuth flow, token storage, React hooks, Node.js middleware |

> **Standalone service (not a submodule):** `hexadian-auth-service` (`Hexadian-Corporation/hexadian-auth-service`) — port 8006, Python · FastAPI · MongoDB. Centralized identity platform: user auth, JWT, RBAC (Groups→Roles→Permissions), RSI verification, authorization code flow. Includes two frontends as subdirectories: `auth-portal` (port 3003) and `auth-backoffice` (port 3002). Runs independently with its own MongoDB instance and docker-compose.

> **Shared library (not a submodule):** `hexadian-auth-common` (`Hexadian-Corporation/hexadian-auth-common`) — pure Python package. Shared JWT validation (`decode_access_token`), `UserContext` dataclass, FastAPI auth dependencies (`JWTAuthDependency`, `require_permission`, `require_any_permission`), and error types. Installed in all H³ backend services via `uv add hexadian-auth-common @ git+https://github.com/Hexadian-Corporation/hexadian-auth-common.git`.

> **Shared library (not a submodule):** `hexadian-auth-client` (`Hexadian-Corporation/hexadian-auth-client`) — TypeScript monorepo (npm workspaces). Auth client SDK for frontend and backend applications. Four packages: `@hexadian-corporation/auth-core` (pure TypeScript, zero framework deps — OAuth client, token storage, JWT decode, auth events), `@hexadian-corporation/auth-react` (React 18/19 integration — `AuthProvider`, `useAuth`, `usePermissions`, `ProtectedRoute`), `@hexadian-corporation/auth-node` (server-side JWT verification, Express middleware, NestJS guards — TypeScript equivalent of `hexadian-auth-common`), and `@hexadian-corporation/auth-angular` (Angular 17+ signals-based `AuthService`, functional guards, `HttpInterceptorFn`). Published to GitHub Packages (`@hexadian-corporation` scope). Both H³ frontends (`hhh-frontend`, `hhh-backoffice-frontend`) use `auth-core` + `auth-react` for all authentication — OAuth flow, token storage, and protected routes.


The root `hexadian-hauling-helper` repo (`Hexadian-Corporation/hexadian-hauling-helper`) contains:
- `docker-compose.yml` — orchestrates H³ services + MongoDB 3-node replica set (auth service runs standalone)
- `.github/` — labels, workflows, project board config
- `pyproject.toml` — workspace-level Python config

### hexadian-hauling-helper — Root Monorepo

```
hexadian-hauling-helper/
├── docker-compose.yml               # Full-stack orchestration (all services + MongoDB replica set)
├── pyproject.toml                    # Workspace-level Python config
├── .github/
│   ├── instructions/                # Copilot instruction files (VS Code local)
│   ├── labels.yml                   # Synced label definitions
│   ├── PROJECT_BOARD.md             # Project board reference
│   └── workflows/                   # Workflows: pr-title, sync-submodules, auto-unblock
├── docs/
│   └── brand-assets/               # Hexadian corporate brand images (logos, backgrounds)
├── hhh-contracts-service/           # Submodule → Hexadian-Corporation/hhh-contracts-service
├── hhh-ships-service/               # Submodule → Hexadian-Corporation/hhh-ships-service
├── hhh-maps-service/                # Submodule → Hexadian-Corporation/hhh-maps-service
├── hhh-graphs-service/              # Submodule → Hexadian-Corporation/hhh-graphs-service
├── hhh-routes-service/              # Submodule → Hexadian-Corporation/hhh-routes-service
├── hhh-commodities-service/         # Submodule → Hexadian-Corporation/hhh-commodities-service
├── hhh-dataminer/                   # Submodule → Hexadian-Corporation/hhh-dataminer
├── hhh-frontend/                    # Submodule → Hexadian-Corporation/hhh-frontend
└── hhh-backoffice-frontend/         # Submodule → Hexadian-Corporation/hhh-backoffice-frontend
```

**Workflows in hexadian-hauling-helper:**
- **`pr-title.yml`** — Validates PR title format: `<type>(main): description`
- **`sync-submodules.yml`** — Triggered by `repository_dispatch` (`submodule-updated`) from any submodule. Runs `git submodule update --remote --merge`, commits and pushes updated refs.
- **`auto-unblock.yml`** — Runs every 15 minutes + on `repository_dispatch` (`unblock-check`). Checks all "Blocked" items on the project board and moves them to "Ready" when all blocking issues are closed.

**hexadian-hauling-helper issue & PR title format:** `<type>(main): description` (e.g., `ci(main): add auto-unblock workflow`)

**hexadian-hauling-helper quality standards:** CI only runs `Validate PR Title` + `Secret Scan`. No lint/test jobs (no application code in this repo). Squash merge only.

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
- Settings use `pydantic-settings` with env prefix `HHH_{SERVICE_NAME}_` (except auth: `HEXADIAN_AUTH_`)
- Repositories use **motor** (async MongoDB driver, no ODM)

**Router patterns (two in use):**

| Pattern | Used by | Description |
|---------|---------|-------------|
| `init_router(service)` + module-level `router` | maps, auth, ships, graphs, routes, commodities | Module-level `_service: Service \| None = None` initialized via `init_router()`. Router is a module-level `APIRouter`. `main.py` uses `create_app()` factory + `uvicorn.run()`. |
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
- **`@hexadian-corporation/auth-core`** — OAuth authorization code flow, token storage, JWT decode, auth events
- **`@hexadian-corporation/auth-react`** — `AuthProvider`, `useAuth`, `usePermissions`, `ProtectedRoute` (wraps `auth-core` for React 19)

Auth is managed entirely via the `hexadian-auth-client` SDK. Do not implement inline OAuth logic or manual token handling in the frontends — use the SDK hooks and components instead.

### Auth Client SDK — npm Packages

`hexadian-auth-client` (`Hexadian-Corporation/hexadian-auth-client`) is an npm workspaces monorepo published to GitHub Packages under the `@hexadian-corporation` scope.

| Package | Purpose | Used by H³ |
|---------|---------|-----------|
| `@hexadian-corporation/auth-core` | Pure TypeScript OAuth client — authorization code flow, PKCE, token storage, JWT decode, auth event bus | ✅ Both frontends |
| `@hexadian-corporation/auth-react` | React 18/19 integration — `AuthProvider`, `useAuth`, `usePermissions`, `ProtectedRoute` | ✅ Both frontends |
| `@hexadian-corporation/auth-node` | Server-side JWT verification — Express middleware, NestJS guards (TypeScript equivalent of `hexadian-auth-common`) | ❌ Not used (Python backends use `hexadian-auth-common`) |
| `@hexadian-corporation/auth-angular` | Angular 17+ integration — signals-based `AuthService`, functional guards, `HttpInterceptorFn` | ❌ Not applicable |

**Installation in H³ frontends:**
```bash
npm install @hexadian-corporation/auth-core @hexadian-corporation/auth-react
```

### Infrastructure

- **MongoDB 7** — 3-node replica set (`rs0`) via docker-compose
- **Database-per-service** pattern — each service has its own DB (e.g., `hhh_contracts`, `hhh_maps`, `hexadian_auth`)
- Docker images use `mirror.gcr.io/library/` prefix for base images

### Docker Compose

**Compose project names:**
- `hexadian-hauling-helper` — main stack (set via `name:` in `docker-compose.yml`)
- `hexadian-auth-service` — standalone auth stack

**3-tier network architecture:**

| Network | Compose alias | `name:` | Members | Purpose |
|---------|--------------|---------|---------|--------|
| `hhh-inner-net` | — | `hexadian-hauling-helper-inner-net` | mongo1/2/3, mongo-init, all backends | DB isolation (`internal: true`) |
| `hhh-outer-net` | — | `hexadian-hauling-helper-outer-net` | all backends, both frontends | Frontends → backends (no DB access) |
| `hexadian-net` | — | `hexadian-shared-net` | all backends, both frontends | Cross-project (auth-service ↔ H³ stack) |

Auth service has its own DB isolation: `auth-inner-net` (`hexadian-auth-inner-net`, `internal: true`) for auth-mongo, and connects to `hexadian-shared-net` for cross-project communication.

## Domain Context

### Contracts Service — Hauling Contracts (Catalog)

A `Contract` represents an **available contract** in the catalog (not an accepted one).

- **Contract** — `id`, `title`, `description`, `status` (draft/active/expired/cancelled), `faction`, `reward_uec`, `collateral_uec`, `deadline`, `hauling_orders` (list), `requirements`, `created_at`, `updated_at`
- **HaulingOrder** — `commodity_id`, `scu_min`, `scu_max`, `max_container_scu`, `pickup_location_id`, `delivery_location_id`
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

### Commodities Service — Trade Goods Catalog

- **Commodity** — `id`, `name`, `code`

Unique index on `code`. Case-insensitive index on `name`. TTL application cache (`cachetools.TTLCache`, maxsize=128, ttl=900s) for `list_all()` and `get()`. `Cache-Control: max-age=900` on GET endpoints.

### Auth Service — Centralized Identity Platform

**User model:** `id`, `username`, `hashed_password`, `group_ids` (list[str]), `is_active`, `rsi_handle`, `rsi_verified`, `rsi_verification_code`

> **Note:** `email` field was removed (M12). `rsi_handle` is required on registration. `group_ids` replaces the old `roles` list.

**RBAC model (3-level hierarchy):**
- **Permission** — `id`, `code` (e.g., `hhh:contracts:read`, `auth:rbac:manage`), `description`
- **Role** — `id`, `name`, `description`, `permission_ids` (list[str])
- **Group** — `id`, `name`, `description`, `role_ids` (list[str])
- **User** → Groups → Roles → Permissions (resolved at JWT refresh time)

**Token architecture:**
- **Access token** — JWT (HS256), 15 min TTL. Claims: `sub`, `username`, `groups`, `roles`, `permissions`, `rsi_handle`, `rsi_verified`, `iat`, `exp`
- **Refresh token** — opaque UUID, 7 days TTL, stored in `refresh_tokens` collection with TTL index. Revocable. On refresh, permissions are re-resolved from DB.

**Authorization code flow (redirect auth):**
1. App redirects to `auth-portal/login?redirect_uri=<callback>&state=<random>`
2. User authenticates on auth-portal
3. Auth-portal generates single-use auth code (60s TTL), redirects to `redirect_uri?code=<code>&state=<state>`
4. App calls `POST /auth/token/exchange {code, redirect_uri}` → `{access_token, refresh_token}`

**Auth frontends (inside hexadian-auth-service repo):**
- **auth-portal** (port 3003) — login, registration, RSI verification, password change
- **auth-backoffice** (port 3002) — user management CRUD, RBAC management (permissions, roles, groups)

**RSI verification flow (implemented — AUTH-1):**
1. `POST /auth/verify/start?user_id={id}` — body: `{"rsi_handle": "..."}`. Generates verification string, stores in `rsi_verification_code`.
2. User pastes string into RSI profile bio.
3. `POST /auth/verify/confirm?user_id={id}` — scrapes RSI profile, checks bio contains the string. Sets `rsi_verified = true`.

**Bio HTML parsing:** Extracts bio from `<div class="entry bio"><div class="value">...</div></div>`. Fragile — see BUG-009.

Handle validation: `^[A-Za-z0-9_-]{3,30}$` (strict, to prevent SSRF).

**JWT protection:** All H³ backend endpoints (except `/health`) require a valid JWT via `hexadian-auth-common` middleware. Both H³ frontends handle the full auth lifecycle — redirect flow, token exchange, storage, and refresh — via the `hexadian-auth-client` SDK (`@hexadian-corporation/auth-core` + `@hexadian-corporation/auth-react`).

## UI Styling

See `hexadian-ui-style.instructions.md` (in each frontend repo) for the canonical Hexadian corporate style guide (color palette, layout, typography, components, Tailwind classes). Canonical source: `hexadian-auth-service/.github/instructions/hexadian-ui-style.instructions.md`.

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

<critical>
**Every issue MUST be:** (1) added to this project board, (2) have Status set (`Ready` or `Blocked`), (3) have Priority set, and (4) have blocking relationships defined via native GitHub issue relationships (GraphQL `addBlockedBy`). See `gh-workflow.instructions.md` for the full mandatory checklist, field IDs, and bulk operation patterns.
</critical>

### Milestones

| Milestone | Repo(s) | Description |
|-----------|---------|-------------|
| M0: Project Setup | hexadian-hauling-helper, hhh-maps-service, hhh-commodities-service | Board config, seed locations, seed commodities |
| M1: Hauling Contracts — Domain & API | hhh-contracts-service | Enrich domain, DTOs, mappers, PUT endpoint, CORS, MongoDB, tests |
| M2: Backoffice — Contract Management | hhh-backoffice-frontend | Setup, types/API client, list page, edit page (3-tab form) |
| M3: Frontend — Contract Creation | hhh-frontend | Setup, types/API client, landing page, create form (3-tab) |
| M4: Auth — RSI Account Verification | hexadian-auth-service | Verify endpoint (code generation + RSI profile scraping) |
| M5: Maps — CRUD Enhancements | hhh-maps-service | Search endpoint, location hierarchy, CRUD improvements |
| M6: Commodities — Service & API | hhh-commodities-service, hexadian-hauling-helper | Domain model, full CRUD stack, indexes, cache, submodule integration |
| M7: Backoffice — Location & Commodity Management | hhh-backoffice-frontend | Location and commodity CRUD pages in backoffice |
| M8: Contract Forms — Entity Reference Autocomplete | hhh-contracts-service, hhh-frontend, hhh-backoffice-frontend | Location and commodity autocomplete in contract forms |
| M9: Database Indexes & Caching | all backend services | MongoDB indexes + TTL application cache per service |
| M10: Dashboards & Browsing | hhh-frontend, hhh-backoffice-frontend | Dashboard pages and browsing views |
| M11: Corporate Branding & Visual Identity | hhh-frontend, hhh-backoffice-frontend | Hexadian brand assets, typography, color palette |
| M12: Auth - Centralized Identity Platform | hexadian-auth-service, hexadian-auth-common, all H³ services + frontends | JWT, RBAC, auth portal, auth backoffice, JWT protection for all services |
| M5: Auth React SDK | hexadian-auth-client, hhh-frontend, hhh-backoffice-frontend, hexadian-auth-service, hexadian-hauling-helper | Extract auth integration into reusable `@hexadian-corporation/auth-core` and `@hexadian-corporation/auth-react` packages. Migrate existing frontends. |
| M6: Auth Node Library | hexadian-auth-client | Server-side JWT verification for Node.js backends: `@hexadian-corporation/auth-node` with Express middleware, NestJS guards, and optional token introspection. TypeScript equivalent of `hexadian-auth-common`. |
| M7: Auth Angular Library | hexadian-auth-client | Angular 17+ integration: `@hexadian-corporation/auth-angular` with signals-based `AuthService`, functional route guards, `HttpInterceptorFn`, and OAuth callback component. |
| M13: Auth - Cross-Language & Token Introspection | hexadian-auth-common, hexadian-auth-service | JWT contract doc, token introspection endpoint |

### Labels

Custom labels synced across repos: `domain`, `api`, `persistence`, `backend`, `frontend`, `setup`, `testing`, `feature`, `enhancement`, `backoffice`, `priority:high`, `priority:medium`, `priority:low`, `project-management`

## Quality Standards

All code contributions must:
1. **Be formatted** — Python: `ruff format .` / TypeScript: Prettier via ESLint
2. **Pass linting** — Python: `ruff check .` / TypeScript: `npm run lint`
3. **Have ≥90% test coverage on changed lines** — enforced via `diff-cover` on PR diffs (not whole-repo thresholds)
4. **Type-check cleanly** — Python: type hints / TypeScript: `tsc --noEmit`
5. **Pass CI** — All checks (`Lint & Format`/`Lint & Type Check` + `Tests & Coverage` + `Validate PR Title` + `Secret Scan`) must pass before merge
6. **Branch up to date** — PR branch must be up to date with `main` (strict mode enabled)
7. **PR title format** — Must match `<type>(<scope>): description` (e.g., `feat(contracts): add domain models`). Issue title = PR title — use the same format for both.
8. **No review required** — approving review count set to 0 (Copilot agent PRs can merge without external reviewer)

## Tooling

| Tool | Purpose |
|------|---------|
| `uv` | Python package manager + project CLI |
| `uv run hhh` | Monorepo CLI: `up`, `down`, `restart`, `logs`, `sync`, `setup`, `start` |
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

# Sync + rebuild + restart a single service
uv run hhh sync contracts

# Rebuild + restart a single service (no pull)
uv run hhh restart contracts

# Auto-CD: detect changed submodules + sync + redeploy only affected containers
uv run hhh hotdeploy

# Follow logs of a single service
uv run hhh logs contracts
```

## Security & Access Control

### Repository Visibility & Access Policy

All repositories are **public** (visible and cloneable by anyone), but protected by the following access controls:

| Control | Configuration |
|---------|---|
| **Visibility** | Public (view + clone allowed) |
| **Push permissions** | Restricted to 3 authorized users only |
| **PR requirements** | All changes must go through PR + CODEOWNERS review |
| **Direct commits** | Disabled for all users except authorized 3 |

### Authorized Users

Only these **3 GitHub users** can push directly to the `main` branch or approve PRs:

- **@Arkaivos**
- **@christianlc00**
- **@naldwax**

### Branch Protection Rules

All 12 public repositories have identical branch protection on `main`:

| Rule | Status |
|------|--------|
| `CODEOWNERS` file | ✅ Exists in all repos |
| `CODEOWNERS` reviews required | ✅ Yes (1+ approval from the 3 users) |
| Push restricted to | Arkaivos, christianlc00, naldwax |
| Force push allowed | ❌ No |
| Allow deletions | ❌ No |
| Required status checks | ✅ Yes (Lint, Tests, PR Title, Secret Scan) — all with `app_id: 15368` |
| Dismiss stale PR reviews | ❌ No |
| Enforce up-to-date branches | ✅ Yes (strict mode) |
| Enforce on admins | ❌ No (admins bypass, but use CODEOWNERS) |

**PR Merge Requirements (strictly enforced):**
- ✅ 1+ approval from CODEOWNERS (@Arkaivos, @christianlc00, or @naldwax)
- ✅ All required status checks passing (Lint, Tests, PR Title, Secret Scan)
- ✅ Branch up to date with `main` (strict mode)
- ❌ **Nobody else can merge** — only CODEOWNERS can approve and merge PRs

### CODEOWNERS

Every public repository contains a `CODEOWNERS` file at the root with:

```
* @Arkaivos @christianlc00 @naldwax
```

This requires that **any change to any file** must be approved by at least one of these 3 users before merge.

### Effect

- ✅ **Anyone** can fork, clone, and open PRs
- ✅ **Only CODEOWNERS** can merge PRs to `main` (1+ approval required)
- ✅ All changes must pass **CI checks** (Lint, Tests, PR Title, Secret Scan)
- ❌ **Nobody else** can push directly to `main` (push restrictions to 3 users)
- ❌ **No force pushes** allowed, even by admins
- ❌ **No PR merges without CODEOWNER approval** — fully enforced

### How to Apply to New Repositories

When adding a new repository to the organization:

1. **Ensure it's Public** — Visibility = Public (visible to everyone)
2. **Create CODEOWNERS file:**
   ```bash
   echo "* @Arkaivos @christianlc00 @naldwax" > CODEOWNERS
   ```
3. **Enable branch protection:**
   ```bash
   gh api repos/Hexadian-Corporation/<repo>/branches/main/protection \
     --method PATCH \
     -f 'restrictions[users][0]=Arkaivos' \
     -f 'restrictions[users][1]=christianlc00' \
     -f 'restrictions[users][2]=naldwax'
   ```
4. **Set required status checks with explicit `app_id: 15368`** — see `gh-workflow.instructions.md` for the full configuration patterns. Never use `app_id: null`.

---

## Maintenance Rules

- **Keep READMEs up to date.** When you add, remove, or change commands, environment variables, API endpoints, or architecture — update the README of the affected repo. The README is the source of truth for developers.
- **Keep the CLI service registry up to date.** When adding or removing a service/submodule, update `SERVICES`, `FRONTENDS`, `COMPOSE_SERVICE_MAP`, and `SERVICE_ALIASES` in `hhh_cli/__init__.py`, plus the `docker-compose.yml` entry.
- **Enforce security policies on new repos.** When creating a new repository, ensure it follows the Security & Access Control rules (public visibility, CODEOWNERS, branch protection, push restrictions).

## Organization Profile Maintenance

- **Keep the org profile README up to date.** When repositories, ports, architecture, workflows, security policy, or ownership change, update Hexadian-Corporation/.github/profile/README.md in the public .github repo.
- **Treat the org profile as canonical org summary.** Ensure descriptions in this repo remain consistent with the organization profile README.

Remember, before finishing: resolve any merge conflict and merge source (PR origin and destination) branch into current one.