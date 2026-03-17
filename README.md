# H³ – Hexadian Hauling Helper

Main orchestration repository for **H³ (Hexadian Hauling Helper)** — a hauling route optimization application for Star Citizen.

## Architecture

Microservices with hexagonal architecture (Ports & Adapters), each service in its own repository and included here as Git submodules.

| Service | Port | Description |
|---|---|---|
| `hhh-contracts-service` | 8001 | Hauling contract management |
| `hhh-ships-service` | 8002 | Ship specifications and cargo capacity |
| `hhh-maps-service` | 8003 | Universe locations and map data |
| `hhh-graphs-service` | 8004 | Travel graph and connectivity |
| `hhh-routes-service` | 8005 | Route optimization engine |
| `hhh-commodities-service` | 8007 | Commodity data management |
| `hhh-frontend` | 3000 | Main web application (React) |
| `hhh-backoffice-frontend` | 3001 | Admin panel (React) |

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, opyoid, pymongo, pydantic
- **Frontend**: React 19, TypeScript, Vite 8
- **Database**: MongoDB (database-per-service)
- **Tooling**: uv, Docker, docker-compose

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package & project manager)
- [Docker](https://www.docker.com/) (for containerized deployment)

## Configuration

### JWT Secret

All backend services must share the same JWT secret to validate tokens issued by the auth service. The `docker-compose.yml` reads a single `JWT_SECRET` variable from the host environment (or `.env` file) and maps it into each service's prefixed env var (e.g. `HHH_CONTRACTS_JWT_SECRET`).

1. Copy the example env file:
   ```bash
   cp .env.example .env
   ```
2. Set a strong secret in `.env`:
   ```
   JWT_SECRET=replace-with-a-secure-random-string
   ```

> **Note:** If `JWT_SECRET` is not set, it defaults to `dev-secret-change-me`. Never use the default in production. The standalone `hexadian-auth-service` must be configured with the **same** secret via `HEXADIAN_AUTH_JWT_SECRET` in its own `docker-compose.yml` / `.env` file for token validation to work across all services.

## Quick Start (first use)

Two commands. On a fresh machine, all you need is (requires `git` and `uv` programs intalled):

```bash
git clone --recurse-submodules https://github.com/Hexadian-Corporation/hexadian-hauling-helper.git
cd hexadian-hauling-helper
uv run hhh up
```

This does everything automatically:
1. Initializes Git submodules
2. Starts the auth service (standalone, with its own MongoDB)
3. Builds and starts all H³ containers

> The auth service (`hexadian-auth-service`) is auto-started by the CLI from `../hexadian-auth-service/`. Clone it with:
> ```bash
> git clone git@github.com:Hexadian-Corporation/hexadian-auth-service.git ../hexadian-auth-service
> ```

Result:

| Component | URL |
|---|---|
| **Frontend** | http://localhost:3000 |
| **Backoffice** | http://localhost:3001 |
| Contracts API | http://localhost:8001/docs |
| Ships API | http://localhost:8002/docs |
| Maps API | http://localhost:8003/docs |
| Graphs API | http://localhost:8004/docs |
| Routes API | http://localhost:8005/docs |
| Commodities API | http://localhost:8007/docs |
| Auth API (standalone) | http://localhost:8006/docs |

## CLI Reference

All operations go through `uv run hhh`:

| Command | Description |
|---|---|
| `uv run hhh up` | **First use**: submodules + auth + build + start everything in Docker |
| `uv run hhh down` | Stop all containers (including standalone auth) |
| `uv run hhh restart <service>` | Rebuild + restart a single service container |
| `uv run hhh logs [service]` | Follow logs (all containers, or a single one) |
| `uv run hhh ps` | Show status of each container |
| `uv run hhh setup` | Local setup (submodules + uv sync + npm install) |
| `uv run hhh sync` | **Pull latest + update submodules + sync all deps** |
| `uv run hhh sync <service>` | Pull + sync deps + rebuild + restart a single service |
| `uv run hhh hotdeploy` | **Auto-CD**: detect changed submodules, sync + redeploy only affected containers |
| `uv run hhh start` | Start backends locally (no Docker) |
| `uv run test` | Run tests for all services |
| `uv run lint` | Run linter for all services |
| `uv run hhh --help` | Show available commands |

**Service aliases** (used with `restart`, `sync`, `logs`):

`contracts` · `ships` · `maps` · `graphs` · `routes` · `commodities` · `frontend` · `backoffice`

Example: `uv run hhh restart contracts` rebuilds and restarts only the contracts-service container.

## Local Development (no Docker)

For development with hot-reload on an individual service:

```bash
uv run hhh setup       # first time only
cd hhh-contracts-service
uv run uvicorn src.main:app --reload --port 8001
```

Or to start all backends locally at once:

```bash
uv run hhh start
```

## Submodule Management

```bash
# Update all submodules to latest
git submodule update --remote --merge

# Add a new submodule
git submodule add https://github.com/Hexadian-Corporation/<repo>.git

# Status
git submodule status
```

## Organization

GitHub Organization: [Hexadian-Corporation](https://github.com/Hexadian-Corporation)

---

## Authentication & Authorization

All services are protected by JWT-based authentication via `hexadian-auth-common`. Permissions are embedded in the JWT token and enforced per-endpoint using `require_permission()` / `require_any_permission()` FastAPI dependencies.

### Application Registration Flow

When a user registers from a frontend, the auth portal receives an `app_id` and `app_signature` (HMAC-SHA256) to auto-assign the user to the appropriate groups.

| Frontend | `app_id` | Signing secret env var |
|----------|----------|------------------------|
| hhh-frontend | `hhh-frontend` | `HEXADIAN_AUTH_APP_SIGNING_SECRET` |
| hhh-backoffice-frontend | `hhh-backoffice` | `HEXADIAN_AUTH_APP_SIGNING_SECRET` |

The auth service looks for groups with `auto_assign_apps` containing the provided `app_id`. Currently, the **Users** group auto-assigns for both `hhh-frontend` and `hhh-backoffice`.

### Roles & Groups (seed data)

| Role | Permissions | Description |
|------|-------------|-------------|
| **Member** | 8 — `contracts:read`, `contracts:write`, `locations:read`, `commodities:read`, `ships:read`, `graphs:read`, `routes:read`, `users:read` | Default for new users |
| **Content Manager** | 18 — all `read`/`write`/`delete` on 6 content resources | Full content management |
| **Super Admin** | 22 — all permissions | Full system access |

| Group | Role(s) | Auto-assign apps | Description |
|-------|---------|------------------|-------------|
| **Users** | Member | `hhh-frontend`, `hhh-backoffice` | Auto-assigned on registration |
| **Admins** | Super Admin | _(none)_ | Manually assigned |

### All Permissions (22 total)

#### Content permissions (18)

| Resource | Read | Write | Delete |
|----------|------|-------|--------|
| Contracts | `contracts:read` | `contracts:write` | `contracts:delete` |
| Locations | `locations:read` | `locations:write` | `locations:delete` |
| Commodities | `commodities:read` | `commodities:write` | `commodities:delete` |
| Ships | `ships:read` | `ships:write` | `ships:delete` |
| Graphs | `graphs:read` | `graphs:write` | `graphs:delete` |
| Routes | `routes:read` | `routes:write` | `routes:delete` |

#### Admin permissions (4)

| Permission | Purpose |
|------------|---------|
| `users:read` | List users |
| `users:write` | Create/update users |
| `users:admin` | Delete users, reset passwords, assign groups |
| `rbac:manage` | Manage permissions, roles, groups |

### API Endpoints & Required Permissions

#### Contracts Service (`:8001`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/contracts` | `contracts:read` |
| GET | `/contracts/{id}` | `contracts:read` |
| POST | `/contracts` | `contracts:write` |
| PUT | `/contracts/{id}` | `contracts:write` |
| DELETE | `/contracts/{id}` | `contracts:delete` |

#### Ships Service (`:8002`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/ships` | `ships:read` |
| GET | `/ships/{id}` | `ships:read` |
| POST | `/ships` | `ships:write` |
| DELETE | `/ships/{id}` | `ships:delete` |

#### Maps Service (`:8003`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/locations` | `locations:read` |
| GET | `/locations/{id}` | `locations:read` |
| GET | `/locations/search?q=` | `locations:read` |
| POST | `/locations` | `locations:write` |
| PUT | `/locations/{id}` | `locations:write` |
| DELETE | `/locations/{id}` | `locations:delete` |

#### Graphs Service (`:8004`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/graphs` | `graphs:read` |
| GET | `/graphs/{id}` | `graphs:read` |
| POST | `/graphs` | `graphs:write` |
| DELETE | `/graphs/{id}` | `graphs:delete` |

#### Routes Service (`:8005`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/routes` | `routes:read` |
| GET | `/routes/{id}` | `routes:read` |
| POST | `/routes/optimize` | `routes:write` |
| DELETE | `/routes/{id}` | `routes:delete` |

#### Commodities Service (`:8007`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/commodities` | `commodities:read` |
| GET | `/commodities/{id}` | `commodities:read` |
| GET | `/commodities/search?q=` | `commodities:read` |
| POST | `/commodities` | `commodities:write` |
| PUT | `/commodities/{id}` | `commodities:write` |
| DELETE | `/commodities/{id}` | `commodities:delete` |

#### Auth Service (`:8006`)

| Method | Endpoint | Permission | Notes |
|--------|----------|------------|-------|
| POST | `/auth/register` | _(public)_ | |
| POST | `/auth/login` | _(public)_ | |
| POST | `/auth/token/refresh` | _(public)_ | |
| POST | `/auth/token/revoke` | _(public)_ | |
| POST | `/auth/authorize` | _(public)_ | |
| POST | `/auth/token/exchange` | _(public)_ | |
| POST | `/auth/password/forgot` | _(public)_ | |
| GET | `/auth/users` | `users:read` | |
| GET | `/auth/users/{id}` | _(self)_ or `users:read` | Own profile always accessible |
| PUT | `/auth/users/{id}` | _(self)_ or `users:admin` | Own profile always editable |
| DELETE | `/auth/users/{id}` | `users:admin` | |
| POST | `/auth/users/{id}/password-reset` | `users:admin` | |
| POST | `/auth/verify/start` | _(authenticated)_ | Own RSI verification |
| POST | `/auth/verify/confirm` | _(authenticated)_ | Own RSI verification |
| POST | `/auth/password/change` | _(authenticated)_ | Own password only |
| ALL | `/rbac/**` | `rbac:manage` | Except user-group assignment: `users:admin` |
