#!/bin/bash

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== MLOps Services Fix Script =====${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if containers are running
if ! docker ps | grep -q mlops; then
    echo -e "${RED}No MLOps containers are running. Starting them...${NC}"
    docker-compose up -d
    echo -e "${GREEN}Containers started. Waiting 30 seconds for initialization...${NC}"
    sleep 30
fi

# Function to check if a service is healthy
check_service() {
    local container=$1
    local port=$2
    local health_endpoint=$3
    
    echo -e "\n${YELLOW}Checking $container...${NC}"
    
    # Check if container is running
    if ! docker ps | grep -q $container; then
        echo -e "${RED}$container is not running. Starting it...${NC}"
        docker-compose up -d $container
        echo -e "${GREEN}$container started. Waiting 10 seconds...${NC}"
        sleep 10
    fi
    
    # Check if port is accessible
    if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:$port$health_endpoint | grep -q "200"; then
        echo -e "${RED}$container is not accessible on port $port. Restarting...${NC}"
        docker-compose restart $container
        echo -e "${GREEN}$container restarted. Waiting 10 seconds...${NC}"
        sleep 10
    else
        echo -e "${GREEN}$container is healthy.${NC}"
    fi
}

# Check and fix each service
check_service "mlops-grafana" "3000" "/api/health"
check_service "mlops-mlflow" "5000" "/"
check_service "mlops-housing-api" "8000" "/health"
check_service "mlops-retraining" "8002" "/health"
check_service "mlops-prometheus" "9090" "/-/healthy"

# Get port mappings
echo -e "\n${YELLOW}Current port mappings:${NC}"
GRAFANA_PORT=$(docker port mlops-grafana 3000/tcp | cut -d ':' -f 2)
MLFLOW_PORT=$(docker port mlops-mlflow 5000/tcp | cut -d ':' -f 2)
HOUSING_API_PORT=$(docker port mlops-housing-api 8000/tcp | cut -d ':' -f 2)
RETRAINING_PORT=$(docker port mlops-retraining 8002/tcp | cut -d ':' -f 2)
PROMETHEUS_PORT=$(docker port mlops-prometheus 9090/tcp | cut -d ':' -f 2)

echo "Grafana: http://localhost:$GRAFANA_PORT"
echo "MLflow: http://localhost:$MLFLOW_PORT"
echo "Housing API: http://localhost:$HOUSING_API_PORT"
echo "Housing API Docs: http://localhost:$HOUSING_API_PORT/docs"
echo "Retraining Service: http://localhost:$RETRAINING_PORT"
echo "Prometheus: http://localhost:$PROMETHEUS_PORT"

# Final check
echo -e "\n${YELLOW}Performing final health check...${NC}"
ALL_HEALTHY=true

if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:$GRAFANA_PORT/api/health | grep -q "200"; then
    echo -e "${RED}Grafana is still not accessible.${NC}"
    ALL_HEALTHY=false
fi

if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:$MLFLOW_PORT | grep -q "200"; then
    echo -e "${RED}MLflow is still not accessible.${NC}"
    ALL_HEALTHY=false
fi

if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:$HOUSING_API_PORT/health | grep -q "200"; then
    echo -e "${RED}Housing API is still not accessible.${NC}"
    ALL_HEALTHY=false
fi

if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:$RETRAINING_PORT/health | grep -q "200"; then
    echo -e "${RED}Retraining Service is still not accessible.${NC}"
    ALL_HEALTHY=false
fi

if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:$PROMETHEUS_PORT/-/healthy | grep -q "200"; then
    echo -e "${RED}Prometheus is still not accessible.${NC}"
    ALL_HEALTHY=false
fi

if $ALL_HEALTHY; then
    echo -e "\n${GREEN}All services are now healthy and accessible!${NC}"
else
    echo -e "\n${YELLOW}Some services are still not accessible. Try these additional steps:${NC}"
    echo "1. Check for port conflicts: netstat -tuln"
    echo "2. Check Docker logs: docker-compose logs"
    echo "3. Restart Docker completely"
    echo "4. Rebuild containers: docker-compose up -d --build"
fi