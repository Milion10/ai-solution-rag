# Script de demarrage de AI Solution
# Lance Docker, Backend et Frontend automatiquement

Write-Host "Demarrage de AI Solution..." -ForegroundColor Cyan
Write-Host ""

# Chemins
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendPath = Join-Path $PSScriptRoot "backend"
$FrontendPath = Join-Path $PSScriptRoot "frontend"
$DockerPath = Join-Path $PSScriptRoot "docker"

# 1. Verifier Docker
Write-Host "Verification de Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "Docker est installe" -ForegroundColor Green
} catch {
    Write-Host "Docker n'est pas installe ou pas demarre" -ForegroundColor Red
    Write-Host "   Veuillez installer Docker Desktop et le demarrer" -ForegroundColor Red
    exit 1
}

# 2. Lancer les services Docker
Write-Host ""
Write-Host "Demarrage des services Docker (PostgreSQL, Redis, MinIO)..." -ForegroundColor Yellow
Push-Location $DockerPath
try {
    docker-compose up -d
    Write-Host "Services Docker demarres" -ForegroundColor Green
} catch {
    Write-Host "Erreur lors du demarrage de Docker" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# Attendre que PostgreSQL soit pret
Write-Host ""
Write-Host "Attente du demarrage de PostgreSQL..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host "PostgreSQL devrait etre pret" -ForegroundColor Green

# 3. Lancer le Backend
Write-Host ""
Write-Host "Demarrage du Backend FastAPI..." -ForegroundColor Yellow
Push-Location $BackendPath

# Utiliser le venv global du projet (pas celui du backend)
$VenvPath = Join-Path $ProjectRoot ".venv"

# Verifier si le venv existe
if (-not (Test-Path "$VenvPath\Scripts\python.exe")) {
    Write-Host "Environnement virtuel non trouve dans $VenvPath" -ForegroundColor Red
    Write-Host "   Veuillez creer un venv: python -m venv .venv" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Lancer le backend dans un nouveau terminal
$backendCmd = @"
`$env:PYTHONPATH='$BackendPath'; Set-Location '$BackendPath'; & '$VenvPath\Scripts\Activate.ps1'; Write-Host 'Backend FastAPI demarre sur http://127.0.0.1:8000' -ForegroundColor Green; python -m uvicorn main:app --reload --port 8000
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
Write-Host "Backend lance dans un nouveau terminal" -ForegroundColor Green
Pop-Location

# 4. Lancer le Frontend
Write-Host ""
Write-Host "Demarrage du Frontend Next.js..." -ForegroundColor Yellow
Push-Location $FrontendPath

# Verifier si node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "node_modules non trouve, installation des dependances..." -ForegroundColor Yellow
    npm install
}

# Lancer le frontend dans un nouveau terminal
$frontendCmd = @"
Set-Location '$FrontendPath'; Write-Host 'Frontend Next.js demarre sur http://localhost:3000' -ForegroundColor Green; npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd
Write-Host "Frontend lance dans un nouveau terminal" -ForegroundColor Green
Pop-Location

# 5. Attendre et ouvrir le navigateur
Write-Host ""
Write-Host "Attente du demarrage complet (10 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Ouverture du navigateur..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Application demarree avec succes !" -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   MinIO:    http://localhost:9001 (minioadmin/minioadmin)" -ForegroundColor White
Write-Host ""
Write-Host "Pour arreter l'application, fermez les terminaux et executez:" -ForegroundColor Yellow
Write-Host "   .\stop-app.ps1" -ForegroundColor White
Write-Host ""
