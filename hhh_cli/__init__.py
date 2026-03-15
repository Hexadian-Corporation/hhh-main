"""H³ – Hexadian Hauling Helper – CLI orchestration.

Single entry point for setup, run, test, and lint of the entire platform.
All commands are invoked via `uv run hhh <command>`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SERVICES = [
    ("hhh-contracts-service", 8001),
    ("hhh-ships-service", 8002),
    ("hhh-maps-service", 8003),
    ("hhh-graphs-service", 8004),
    ("hhh-routes-service", 8005),
    ("hhh-auth-service", 8006),
]

FRONTENDS = [
    ("hhh-frontend", 3000),
    ("hhh-backoffice-frontend", 3001),
]

ROOT = Path(__file__).resolve().parent.parent


# ── helpers ──────────────────────────────────────────────────────────

def _run(args: list[str], *, cwd: Path | None = None, shell: bool = False) -> int:
    return subprocess.run(args, cwd=cwd, shell=shell).returncode


def _sync_service(svc_dir: Path) -> bool:
    return _run(["uv", "sync"], cwd=svc_dir) == 0


def _ensure_synced(svc_dir: Path) -> None:
    if not (svc_dir / ".venv").exists():
        _sync_service(svc_dir)


# ── commands ─────────────────────────────────────────────────────────

def setup() -> None:
    """Full setup: init submodules + sync all services + install frontends."""
    print("=== H³ – Full project setup ===\n")

    # 1. Git submodules
    print("[1/3] Initializing git submodules...")
    if _run(["git", "submodule", "update", "--init", "--recursive"], cwd=ROOT) != 0:
        print("WARNING: git submodule update failed (not a git repo or no submodules)")

    # 2. Python services
    print("\n[2/3] Syncing Python services...")
    failed: list[str] = []
    for svc_name, _ in SERVICES:
        svc_dir = ROOT / svc_name
        if not svc_dir.exists():
            continue
        print(f"  -> {svc_name}")
        if not _sync_service(svc_dir):
            failed.append(svc_name)
    if failed:
        print(f"\nFailed to sync: {', '.join(failed)}")
        sys.exit(1)

    # 3. Frontends (npm)
    print("\n[3/3] Installing frontend dependencies...")
    for fe_name, _ in FRONTENDS:
        fe_dir = ROOT / fe_name
        if not fe_dir.exists():
            continue
        print(f"  -> {fe_name}")
        _run(["npm", "install"], cwd=fe_dir, shell=True)

    print("\n=== Setup complete! ===")
    print("  Run services:  uv run hhh start")
    print("  Run with Docker: uv run hhh up")
    print("  Run tests:     uv run test")


def sync() -> None:
    """Pull latest changes, update submodules, and sync dependencies."""
    print("=== H³ – Syncing everything ===")

    # 1. Pull latest main repo + submodule refs
    print("\n── Git pull (with submodules) ──")
    _run(["git", "pull", "--recurse-submodules"], cwd=ROOT)

    # 2. Update submodules to latest remote main
    print("\n── Updating submodules to latest main ──")
    _run(["git", "submodule", "update", "--remote", "--merge"], cwd=ROOT)

    # 3. Sync Python dependencies
    print("\n── Syncing Python dependencies ──")
    failed: list[str] = []
    for svc_name, _ in SERVICES:
        svc_dir = ROOT / svc_name
        if not svc_dir.exists():
            continue
        print(f"  -> {svc_name}")
        if not _sync_service(svc_dir):
            failed.append(svc_name)

    # 4. Install frontend dependencies
    print("\n── Syncing frontend dependencies ──")
    for fe_name, _ in FRONTENDS:
        fe_dir = ROOT / fe_name
        if not fe_dir.exists():
            continue
        print(f"  -> {fe_name}")
        if _run(["npm", "install"], cwd=fe_dir, shell=True) != 0:
            print("    (failed — is npm installed?")

    if failed:
        print(f"\nFailed to sync: {', '.join(failed)}")
        sys.exit(1)

    # 5. Commit lockfile changes in submodules
    print("\n── Committing lockfile updates ──")
    all_modules = [(n, None) for n, _ in SERVICES] + [(n, None) for n, _ in FRONTENDS]
    for mod_name, _ in all_modules:
        mod_dir = ROOT / mod_name
        if not mod_dir.exists():
            continue
        # Check if there are lockfile changes to commit
        rc = subprocess.run(
            ["git", "diff", "--quiet"], cwd=mod_dir,
        ).returncode
        if rc != 0:
            print(f"  -> {mod_name}: committing lockfile updates")
            _run(["git", "add", "-A"], cwd=mod_dir)
            _run(["git", "commit", "-m", "chore: update lockfile"], cwd=mod_dir)
            _run(["git", "push"], cwd=mod_dir)
        else:
            print(f"  -> {mod_name}: up to date")

    # 6. Update submodule refs in hhh-main
    print("\n── Updating submodule refs in hhh-main ──")
    rc = subprocess.run(["git", "diff", "--quiet"], cwd=ROOT).returncode
    if rc != 0:
        _run(["git", "add", "-A"], cwd=ROOT)
        _run(["git", "commit", "-m", "chore: sync submodule refs"], cwd=ROOT)
        _run(["git", "push"], cwd=ROOT)
        print("  -> refs updated and pushed")
    else:
        print("  -> refs already up to date")

    print("\nAll synced!")


def start() -> None:
    """Start all services locally (auto-syncs if needed)."""
    print("=== H³ – Starting all services ===")
    processes: list[tuple[str, subprocess.Popen]] = []
    for svc_name, port in SERVICES:
        svc_dir = ROOT / svc_name
        if not svc_dir.exists():
            continue
        _ensure_synced(svc_dir)
        print(f"  -> {svc_name} on port {port}")
        p = subprocess.Popen(
            ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", f"--port={port}", "--reload"],
            cwd=svc_dir,
        )
        processes.append((svc_name, p))

    print(f"\n{len(processes)} services started. Press Ctrl+C to stop.\n")
    try:
        for _, p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        for _, p in processes:
            p.terminate()
        for _, p in processes:
            p.wait()


def up() -> None:
    """One-command first use: init submodules + build and start all containers.

    After cloning the repo, this is the only command needed:
        uv run hhh up

    Result: MongoDB + 6 backend services + 2 frontends running in Docker.
    - Frontend:           http://localhost:3000
    - Backoffice:         http://localhost:3001
    - Contracts API:      http://localhost:8001
    - Ships API:          http://localhost:8002
    - Maps API:           http://localhost:8003
    - Graphs API:         http://localhost:8004
    - Routes API:         http://localhost:8005
    - Auth API:           http://localhost:8006
    """
    print("=== H³ – First-use setup & launch ===\n")

    # 1. Git submodules
    print("[1/2] Initializing git submodules...")
    _run(["git", "submodule", "update", "--init", "--recursive"], cwd=ROOT)

    # 2. Docker compose build + up (each component in its own container)
    print("\n[2/2] Building and starting all containers...")
    print("       (MongoDB + 6 services + 2 frontends)\n")
    code = _run(["docker", "compose", "up", "--build", "-d"], cwd=ROOT)
    if code != 0:
        sys.exit(code)

    print("\n=== H³ is running! ===")
    print()
    print("  Frontend:           http://localhost:3000")
    print("  Backoffice:         http://localhost:3001")
    print()
    print("  Contracts API:      http://localhost:8001/docs")
    print("  Ships API:          http://localhost:8002/docs")
    print("  Maps API:           http://localhost:8003/docs")
    print("  Graphs API:         http://localhost:8004/docs")
    print("  Routes API:         http://localhost:8005/docs")
    print("  Auth API:           http://localhost:8006/docs")
    print()
    print("  Stop:  uv run hhh down")
    print("  Logs:  uv run hhh logs")


def down() -> None:
    """Stop all containers and clean up."""
    print("=== H³ – Stopping all containers ===")
    sys.exit(_run(["docker", "compose", "down"], cwd=ROOT))


def logs() -> None:
    """Follow logs from all containers."""
    sys.exit(_run(["docker", "compose", "logs", "-f"], cwd=ROOT))


def ps() -> None:
    """Show status of all containers."""
    sys.exit(_run(["docker", "compose", "ps"], cwd=ROOT))


def run_tests() -> None:
    """Run pytest across all services (auto-syncs if needed)."""
    print("=== H³ – Running tests ===")
    extra_args = sys.argv[2:] if len(sys.argv) > 2 else sys.argv[1:]
    failed: list[str] = []
    for svc_name, _ in SERVICES:
        svc_dir = ROOT / svc_name
        if not svc_dir.exists():
            continue
        _ensure_synced(svc_dir)
        print(f"\n--- {svc_name} ---")
        if _run(["uv", "run", "pytest", *extra_args], cwd=svc_dir) != 0:
            failed.append(svc_name)

    print("\n=== Results ===")
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        sys.exit(1)
    print("All tests passed!")


def run_lint() -> None:
    """Run ruff across all services (auto-syncs if needed)."""
    print("=== H³ – Running linter ===")
    failed: list[str] = []
    for svc_name, _ in SERVICES:
        svc_dir = ROOT / svc_name
        if not svc_dir.exists():
            continue
        _ensure_synced(svc_dir)
        print(f"\n--- {svc_name} ---")
        if _run(["uv", "run", "ruff", "check", "."], cwd=svc_dir) != 0:
            failed.append(svc_name)

    print("\n=== Results ===")
    if failed:
        print(f"Issues in: {', '.join(failed)}")
        sys.exit(1)
    print("All clean!")


# ── entry points ─────────────────────────────────────────────────────

COMMANDS = {
    "up": (up, "First-use: submodules + build + start everything in Docker"),
    "down": (down, "Stop all containers"),
    "logs": (logs, "Follow logs from all containers"),
    "ps": (ps, "Show status of all containers"),
    "setup": (setup, "Full local setup (submodules + deps + frontends)"),
    "sync": (sync, "Sync Python service dependencies"),
    "start": (start, "Start backend services locally (no Docker)"),
    "test": (run_tests, "Run tests for all services"),
    "lint": (run_lint, "Run linter for all services"),
}


def main() -> None:
    """CLI entry point: `uv run hhh [command]`."""
    args = sys.argv[1:]
    cmd = args[0] if args else "up"

    if cmd in ("--help", "-h"):
        print("Usage: hhh [command]\n")
        print("Commands:")
        for name, (_, desc) in COMMANDS.items():
            print(f"  {name:<14} {desc}")
        sys.exit(0)

    entry = COMMANDS.get(cmd)
    if entry is None:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS)}")
        sys.exit(1)
    entry[0]()
