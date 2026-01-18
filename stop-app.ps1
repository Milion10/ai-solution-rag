#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Arrête tous les services de l'application AI Solution
.DESCRIPTION
    Script d'arrêt qui stoppe Docker (PostgreSQL, Redis, MinIO)
.EXAMPLE
    .\stop-app.ps1
#>

Write-Host "🛑 Arrêt de AI Solution..." -ForegroundColor Cyan
Write-Host ""

$DockerPath = Join-Path $PSScriptRoot "docker"

# Arrêter les services Docker
Write-Host "🐳 Arrêt des services Docker..." -ForegroundColor Yellow
Push-Location $DockerPath
try {
    docker-compose down
    Write-Host "✅ Services Docker arrêtés" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors de l'arrêt de Docker" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host ""
Write-Host "✨ Application arrêtée avec succès !" -ForegroundColor Green
Write-Host "💡 N'oubliez pas de fermer les terminaux Backend et Frontend" -ForegroundColor Yellow
Write-Host ""
