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
- **Infrastructure**: Docker, docker-compose, uv

## Quick Start

### Clone with submodules

```bash
git clone --recurse-submodules https://github.com/Hexadian-Corporation/hhh-main.git
cd hhh-main
```

### Setup (installs all dependencies)

```bash
# Linux / macOS
./scripts/setup.sh

# Windows (PowerShell)
.\scripts\setup.ps1
```

### Run with Docker

```bash
docker compose up --build
```

### Run individually

```bash
cd hhh-contracts-service
uv sync
uv run uvicorn src.main:app --reload --port 8001
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
