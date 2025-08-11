# PowerShell deployment script for ML Housing project

Write-Host "🚀 Starting MLOps Pipeline Deployment" -ForegroundColor Cyan

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.monitoring.yml down

# Set Docker username from environment or use default
$DockerUsername = if ($env:DOCKER_USERNAME) { $env:DOCKER_USERNAME } else { "username" }

# Pull latest images
Write-Host "📥 Pulling latest Docker images..." -ForegroundColor Yellow
docker pull ${DockerUsername}/mlops-housing-pipeline:latest

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Green
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Health checks
Write-Host "🏥 Running health checks..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -ErrorAction Stop
    Write-Host "✅ Health check passed!" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host "🌐 Services available at:" -ForegroundColor Cyan
Write-Host "  - Housing API: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Grafana: http://localhost:3000" -ForegroundColor White
Write-Host "  - MLflow: http://localhost:5000" -ForegroundColor White