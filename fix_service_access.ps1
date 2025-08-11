# PowerShell script to fix service accessibility issues

# Function to check if a port is in use
function Test-PortInUse {
    param(
        [int]$Port
    )
    
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return ($connections -ne $null)
}

# Function to check if a service is accessible
function Test-ServiceAccessible {
    param(
        [string]$Url,
        [int]$TimeoutSec = 5
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec $TimeoutSec -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Define the services and their ports
$services = @(
    @{name="Grafana"; port=32792; url="http://localhost:32792"},
    @{name="MLflow"; port=32793; url="http://localhost:32793"},
    @{name="Housing API"; port=32794; url="http://localhost:32794/health"},
    @{name="Retraining Service"; port=32795; url="http://localhost:32795/health"},
    @{name="Prometheus"; port=32796; url="http://localhost:32796/-/healthy"}
)

Write-Host "Checking service accessibility..." -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

$allServicesAccessible = $true

foreach ($service in $services) {
    Write-Host "Checking $($service.name) on port $($service.port)..." -NoNewline
    
    # Check if port is in use
    if (Test-PortInUse -Port $service.port) {
        # Check if service is accessible
        if (Test-ServiceAccessible -Url $service.url) {
            Write-Host "ACCESSIBLE" -ForegroundColor Green
        } else {
            Write-Host "PORT IN USE BUT SERVICE NOT ACCESSIBLE" -ForegroundColor Yellow
            $allServicesAccessible = $false
        }
    } else {
        Write-Host "PORT NOT IN USE" -ForegroundColor Red
        $allServicesAccessible = $false
    }
}

if (-not $allServicesAccessible) {
    Write-Host "`nSome services are not accessible. Attempting to fix..." -ForegroundColor Yellow
    
    # Check Docker status
    Write-Host "`nChecking Docker status..." -ForegroundColor Cyan
    try {
        $dockerStatus = docker info
        Write-Host "Docker is running." -ForegroundColor Green
    } catch {
        Write-Host "Docker is not running or not installed." -ForegroundColor Red
        Write-Host "Please start Docker and try again." -ForegroundColor Red
        exit
    }
    
    # Check if containers are running
    Write-Host "`nChecking Docker containers..." -ForegroundColor Cyan
    $containers = docker ps --format "{{.Names}}"
    
    if ($containers) {
        Write-Host "Running containers:" -ForegroundColor Green
        $containers | ForEach-Object { Write-Host "  - $_" }
    } else {
        Write-Host "No containers are running." -ForegroundColor Red
        
        # Try to start the containers
        Write-Host "`nAttempting to start containers with docker-compose..." -ForegroundColor Yellow
        try {
            docker-compose up -d
            Write-Host "Containers started. Please wait a moment for services to initialize." -ForegroundColor Green
        } catch {
            Write-Host "Failed to start containers with docker-compose." -ForegroundColor Red
            Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    # Provide instructions for manual fixes
    Write-Host "`nManual fix instructions:" -ForegroundColor Cyan
    Write-Host "1. Ensure Docker is running" -ForegroundColor White
    Write-Host "2. Navigate to the project directory in PowerShell" -ForegroundColor White
    Write-Host "3. Run: docker-compose down" -ForegroundColor White
    Write-Host "4. Run: docker-compose up -d" -ForegroundColor White
    Write-Host "5. Wait for services to initialize (may take a minute)" -ForegroundColor White
    Write-Host "6. Run this script again to check service accessibility" -ForegroundColor White
    
    # Provide browser URLs
    Write-Host "`nService URLs (after fixing):" -ForegroundColor Cyan
    Write-Host "Grafana:            http://localhost:32792" -ForegroundColor Yellow
    Write-Host "MLflow:             http://localhost:32793" -ForegroundColor Yellow
    Write-Host "Housing API:        http://localhost:32794" -ForegroundColor Yellow
    Write-Host "Housing API Docs:   http://localhost:32794/docs" -ForegroundColor Yellow
    Write-Host "Retraining Service: http://localhost:32795" -ForegroundColor Yellow
    Write-Host "Prometheus:         http://localhost:32796" -ForegroundColor Yellow
} else {
    Write-Host "`nAll services are accessible!" -ForegroundColor Green
    
    # Provide browser URLs
    Write-Host "`nService URLs:" -ForegroundColor Cyan
    Write-Host "Grafana:            http://localhost:32792" -ForegroundColor Yellow
    Write-Host "MLflow:             http://localhost:32793" -ForegroundColor Yellow
    Write-Host "Housing API:        http://localhost:32794" -ForegroundColor Yellow
    Write-Host "Housing API Docs:   http://localhost:32794/docs" -ForegroundColor Yellow
    Write-Host "Retraining Service: http://localhost:32795" -ForegroundColor Yellow
    Write-Host "Prometheus:         http://localhost:32796" -ForegroundColor Yellow
}