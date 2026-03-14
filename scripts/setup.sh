#!/usr/bin/env bash
set -e

echo "=== H³ – Hexadian Hauling Helper – Setup ==="

echo "Initializing and updating submodules..."
git submodule update --init --recursive

echo ""
echo "Installing Python services..."
for svc in hhh-contracts-service hhh-ships-service hhh-maps-service hhh-graphs-service hhh-routes-service hhh-auth-service; do
    echo "  -> $svc"
    (cd "$svc" && uv sync)
done

echo ""
echo "Installing frontend dependencies..."
for fe in hhh-frontend hhh-backoffice-frontend; do
    echo "  -> $fe"
    (cd "$fe" && npm install)
done

echo ""
echo "Setup complete!"
echo "  - Start all services: docker compose up --build"
echo "  - Or run individually: cd <service> && uv run uvicorn src.main:app --reload"
