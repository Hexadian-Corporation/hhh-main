> **© 2026 Hexadian Corporation** — Licensed under [PolyForm Noncommercial 1.0.0 (Modified)](./LICENSE). No commercial use, no public deployment, no plagiarism. See [LICENSE](./LICENSE) for full terms.

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

All backend services must share the same JWT secret to validate tokens issued by the auth service. The `docker-compose.yml` reads `HEXADIAN_AUTH_JWT_SECRET` from the host environment (or `.env` file) and passes it directly to every service.

1. Copy the example env file:
   ```bash
   cp .env.example .env
   ```
2. Set a strong secret in `.env`:
   ```
   HEXADIAN_AUTH_JWT_SECRET=replace-with-a-secure-random-string
   ```

> **Note:** If `HEXADIAN_AUTH_JWT_SECRET` is not set, it defaults to `change-me-in-production`. Never use the default in production. The standalone `hexadian-auth-service` uses the same `HEXADIAN_AUTH_JWT_SECRET` variable, so a single value in `.env` configures all services.

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

All permissions are **namespaced** by application: `hhh:` for HHH services, `auth:` for auth service.

### Application Registration Flow

When a user registers from a frontend, the auth portal receives an `app_id` and `app_signature` (HMAC-SHA256) to auto-assign the user to the appropriate groups.

| Frontend | `app_id` | Signing secret env var |
|----------|----------|------------------------|
| hhh-frontend | `hhh-frontend` | `HEXADIAN_AUTH_APP_SIGNING_SECRET` |

> **Note:** Newly registered users are auto-assigned to the **Users** group (player frontend only). Backoffice access requires manual group assignment by an administrator.

### Roles (9 total)

#### Auth Roles

| Role | Permissions | Description |
|------|-------------|-------------|
| **Auth Admin** | `auth:users:read`, `auth:users:write`, `auth:users:admin`, `auth:rbac:manage` | Full auth administration |
| **Auth User Manager** | `auth:users:read`, `auth:users:write` | User account management |

#### HHH Roles

| Role | Permissions | Description |
|------|-------------|-------------|
| **HHH Contracts Manager** | `hhh:contracts:read/write/delete` | Full access to contracts |
| **HHH Locations Manager** | `hhh:locations:read/write/delete` | Full access to locations |
| **HHH Commodities Manager** | `hhh:commodities:read/write/delete` | Full access to commodities |
| **HHH Ships Manager** | `hhh:ships:read/write/delete` | Full access to ships |
| **HHH Graphs Manager** | `hhh:graphs:read/write/delete` | Full access to graphs |
| **HHH Routes Manager** | `hhh:routes:read/write/delete` | Full access to routes |
| **HHH Viewer** | All `hhh:*:read` (6 permissions) | Read-only access to all HHH resources |

### Groups (3 total)

| Group | Roles | Auto-assign apps | Description |
|-------|-------|------------------|-------------|
| **Users** | HHH Viewer, HHH Contracts Manager | `hhh-frontend` | Auto-assigned on registration. No backoffice access. |
| **Content Managers** | Auth User Manager, all HHH Managers (6) | _(none)_ | Full content management + user management |
| **Admins** | Auth Admin, all HHH Managers (6) | _(none)_ | Full system access including RBAC |

### All Permissions (22 total)

#### HHH Permissions (18)

| Resource | Read | Write | Delete |
|----------|------|-------|--------|
| Contracts | `hhh:contracts:read` | `hhh:contracts:write` | `hhh:contracts:delete` |
| Locations | `hhh:locations:read` | `hhh:locations:write` | `hhh:locations:delete` |
| Commodities | `hhh:commodities:read` | `hhh:commodities:write` | `hhh:commodities:delete` |
| Ships | `hhh:ships:read` | `hhh:ships:write` | `hhh:ships:delete` |
| Graphs | `hhh:graphs:read` | `hhh:graphs:write` | `hhh:graphs:delete` |
| Routes | `hhh:routes:read` | `hhh:routes:write` | `hhh:routes:delete` |

#### Auth Permissions (4)

| Permission | Purpose |
|------------|---------|
| `auth:users:read` | List users |
| `auth:users:write` | Create/update users |
| `auth:users:admin` | Delete users, reset passwords, assign groups |
| `auth:rbac:manage` | Manage permissions, roles, groups |

### Frontend Access Control

| Application | Gate requirement | Nav items filtered by |
|-------------|-----------------|----------------------|
| **hhh-frontend** | Any authenticated user | `hhh:*:read` per resource |
| **hhh-backoffice-frontend** | Any `hhh:*:write` (non-contracts) | `hhh:*:write` per section, `auth:users:read` for Users |
| **auth-backoffice** | Any `auth:*` permission | `auth:users:read/admin` for Users, `auth:rbac:manage` for RBAC |

### API Endpoints & Required Permissions

#### Contracts Service (`:8001`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/contracts` | `hhh:contracts:read` |
| GET | `/contracts/{id}` | `hhh:contracts:read` |
| POST | `/contracts` | `hhh:contracts:write` |
| PUT | `/contracts/{id}` | `hhh:contracts:write` |
| DELETE | `/contracts/{id}` | `hhh:contracts:delete` |

#### Ships Service (`:8002`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/ships` | `hhh:ships:read` |
| GET | `/ships/{id}` | `hhh:ships:read` |
| POST | `/ships` | `hhh:ships:write` |
| DELETE | `/ships/{id}` | `hhh:ships:delete` |

#### Maps Service (`:8003`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/locations` | `hhh:locations:read` |
| GET | `/locations/{id}` | `hhh:locations:read` |
| GET | `/locations/search?q=` | `hhh:locations:read` |
| POST | `/locations` | `hhh:locations:write` |
| PUT | `/locations/{id}` | `hhh:locations:write` |
| DELETE | `/locations/{id}` | `hhh:locations:delete` |

#### Graphs Service (`:8004`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/graphs` | `hhh:graphs:read` |
| GET | `/graphs/{id}` | `hhh:graphs:read` |
| POST | `/graphs` | `hhh:graphs:write` |
| DELETE | `/graphs/{id}` | `hhh:graphs:delete` |

#### Routes Service (`:8005`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/routes` | `hhh:routes:read` |
| GET | `/routes/{id}` | `hhh:routes:read` |
| POST | `/routes/optimize` | `hhh:routes:write` |
| DELETE | `/routes/{id}` | `hhh:routes:delete` |

#### Commodities Service (`:8007`)

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/commodities` | `hhh:commodities:read` |
| GET | `/commodities/{id}` | `hhh:commodities:read` |
| GET | `/commodities/search?q=` | `hhh:commodities:read` |
| POST | `/commodities` | `hhh:commodities:write` |
| PUT | `/commodities/{id}` | `hhh:commodities:write` |
| DELETE | `/commodities/{id}` | `hhh:commodities:delete` |

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
| GET | `/auth/users` | `auth:users:read` | |
| GET | `/auth/users/{id}` | _(self)_ or `auth:users:read` | Own profile always accessible |
| PUT | `/auth/users/{id}` | _(self)_ or `auth:users:admin` | Own profile always editable |
| DELETE | `/auth/users/{id}` | `auth:users:admin` | |
| POST | `/auth/users/{id}/password-reset` | `auth:users:admin` | |
| POST | `/auth/verify/start` | _(authenticated)_ | Own RSI verification |
| POST | `/auth/verify/confirm` | _(authenticated)_ | Own RSI verification |
| POST | `/auth/password/change` | _(authenticated)_ | Own password only |
| ALL | `/rbac/**` | `auth:rbac:manage` | Except user-group assignment: `auth:users:admin` |
