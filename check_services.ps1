# PowerShell script to check the health of all services

$services = @(
    @{name="Grafana"; url="http://localhost:3001/api/health"; expected="ok"},
    @{name="MLflow"; url="http://localhost:5000"; expected=""}, # MLflow doesn't have a specific health endpoint
    @{name="Housing API"; url="http://localhost:8000/health"; expected="healthy"},
    @{name="Retraining Service"; url="http://localhost:8002/health"; expected="healthy"},
    @{name="Prometheus"; url="http://localhost:9090/-/healthy"; expected=""} # Prometheus returns 200 OK
)

Write-Host "Checking service health..." -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

foreach ($service in $services) {
    Write-Host "Checking $($service.name)..." -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $service.url -Method Get -TimeoutSec 5 -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            if ($service.expected -ne "") {
                $content = $response.Content | ConvertFrom-Json
                if ($content.status -eq $service.expected) {
                    Write-Host "OK" -ForegroundColor Green
                } else {
                    Write-Host "UNHEALTHY" -ForegroundColor Red
                    Write-Host "  Expected status: $($service.expected)" -ForegroundColor Red
                    Write-Host "  Actual status: $($content.status)" -ForegroundColor Red
                }
            } else {
                Write-Host "OK" -ForegroundColor Green
            }
        } else {
            Write-Host "FAILED" -ForegroundColor Red
            Write-Host "  Status code: $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "UNREACHABLE" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "\nService URLs:" -ForegroundColor Cyan
Write-Host "=============" -ForegroundColor Cyan
Write-Host "Grafana:            http://localhost:3001" -ForegroundColor Yellow
Write-Host "MLflow:             http://localhost:5000" -ForegroundColor Yellow
Write-Host "Housing API:        http://localhost:8000" -ForegroundColor Yellow
Write-Host "Housing API Docs:   http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Retraining Service: http://localhost:8002" -ForegroundColor Yellow
Write-Host "Prometheus:         http://localhost:9090" -ForegroundColor Yellow