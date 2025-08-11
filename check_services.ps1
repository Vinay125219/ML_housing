# PowerShell script to check the health of all services

$services = @(
    @{name="Grafana"; url="http://localhost:32792/api/health"; expected="ok"},
    @{name="MLflow"; url="http://localhost:32793"; expected=""}, # MLflow doesn't have a specific health endpoint
    @{name="Housing API"; url="http://localhost:32794/health"; expected="healthy"},
    @{name="Retraining Service"; url="http://localhost:32795/health"; expected="healthy"},
    @{name="Prometheus"; url="http://localhost:32796/-/healthy"; expected=""} # Prometheus returns 200 OK
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
Write-Host "Grafana:            http://localhost:32792" -ForegroundColor Yellow
Write-Host "MLflow:             http://localhost:32793" -ForegroundColor Yellow
Write-Host "Housing API:        http://localhost:32794" -ForegroundColor Yellow
Write-Host "Housing API Docs:   http://localhost:32794/docs" -ForegroundColor Yellow
Write-Host "Retraining Service: http://localhost:32795" -ForegroundColor Yellow
Write-Host "Prometheus:         http://localhost:32796" -ForegroundColor Yellow