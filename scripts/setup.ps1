Write-Host "=== H³ – Hexadian Hauling Helper – Setup ===" -ForegroundColor Cyan

Write-Host "Initializing and updating submodules..."
git submodule update --init --recursive

Write-Host ""
Write-Host "Installing Python services..."
$services = @("hhh-contracts-service","hhh-ships-service","hhh-maps-service","hhh-graphs-service","hhh-routes-service","hhh-auth-service")
foreach ($svc in $services) {
    Write-Host "  -> $svc" -ForegroundColor Green
    Push-Location $svc
    uv sync
    Pop-Location
}

Write-Host ""
Write-Host "Installing frontend dependencies..."
$frontends = @("hhh-frontend","hhh-backoffice-frontend")
foreach ($fe in $frontends) {
    Write-Host "  -> $fe" -ForegroundColor Green
    Push-Location $fe
    npm install
    Pop-Location
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Cyan
Write-Host "  - Start all services: docker compose up --build"
Write-Host "  - Or run individually: cd <service> && uv run uvicorn src.main:app --reload"
