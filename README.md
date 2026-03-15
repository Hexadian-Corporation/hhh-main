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
| `hhh-auth-service` | 8006 | Authentication and user management |
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

## Quick Start (first use)

Two commands. On a fresh machine, all you need is (requires `git` and `uv` programs intalled):

```bash
git clone --recurse-submodules https://github.com/Hexadian-Corporation/hhh-main.git
cd hhh-main
uv run hhh up
```

This does everything automatically:
1. Initializes Git submodules
2. Builds a Docker image for each component
3. Starts **9 containers**: MongoDB + 6 backends + 2 frontends

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
| Auth API | http://localhost:8006/docs |

## CLI Reference

All operations go through `uv run hhh`:

| Command | Description |
|---|---|
| `uv run hhh up` | **First use**: submodules + build + start everything in Docker |
| `uv run hhh down` | Stop all containers |
| `uv run hhh restart <service>` | Rebuild + restart a single service container |
| `uv run hhh logs [service]` | Follow logs (all containers, or a single one) |
| `uv run hhh ps` | Show status of each container |
| `uv run hhh setup` | Local setup (submodules + uv sync + npm install) |
| `uv run hhh sync` | **Pull latest + update submodules + sync all deps** |
| `uv run hhh sync <service>` | Pull + sync deps + rebuild + restart a single service |
| `uv run hhh start` | Start backends locally (no Docker) |
| `uv run test` | Run tests for all services |
| `uv run lint` | Run linter for all services |
| `uv run hhh --help` | Show available commands |

**Service aliases** (used with `restart`, `sync`, `logs`):

`contracts` · `ships` · `maps` · `graphs` · `routes` · `auth` · `frontend` · `backoffice`

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
