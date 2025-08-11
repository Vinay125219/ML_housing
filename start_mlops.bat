@echo off
echo ========================================
echo      MLOps Housing Pipeline Startup
echo ========================================
echo.

:: Check if Docker is running
echo [1/5] Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running or not installed
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)
echo ✅ Docker is running

:: Check if docker-compose is available
echo [2/5] Checking docker-compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: docker-compose is not available
    pause
    exit /b 1
)
echo ✅ docker-compose is available

:: Stop any existing containers
echo [3/5] Stopping existing containers...
docker-compose down >nul 2>&1
echo ✅ Cleaned up existing containers

:: Start all services
echo [4/5] Starting MLOps services...
echo This may take a few minutes on first run...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ERROR: Failed to start services
    echo Check the error messages above
    pause
    exit /b 1
)

echo ✅ Services started successfully

:: Wait a moment for services to initialize
echo [5/5] Waiting for services to initialize...
timeout /t 10 /nobreak >nul

:: Open browser with services
echo Opening services in browser...
python open_browser.py

echo.
echo ========================================
echo   MLOps Pipeline is now running! 🚀
echo ========================================
echo.
echo Service URLs:
echo   • Streamlit Dashboard: http://localhost:8501
echo   • Housing API:         http://localhost:8000/docs
echo   • MLflow Tracking:     http://localhost:5000
echo   • Grafana Dashboard:   http://localhost:3001 (admin/admin)
echo   • Prometheus:          http://localhost:9090
echo   • Retraining API:      http://localhost:8002
echo.
echo To stop all services, run: docker-compose down
echo.
pause
