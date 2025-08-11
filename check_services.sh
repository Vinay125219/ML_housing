#!/bin/bash

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== MLOps Services Health Check =====${NC}"

# Function to check if a port is open
check_port() {
    local host=$1
    local port=$2
    local service=$3
    
    # Try to connect to the port
    if nc -z -w 5 $host $port 2>/dev/null; then
        echo -e "${GREEN}✓ $service port $port is open${NC}"
        return 0
    else
        echo -e "${RED}✗ $service port $port is closed${NC}"
        return 1
    fi
}

# Function to check service health endpoint
check_health() {
    local url=$1
    local service=$2
    
    # Try to connect to the health endpoint
    response=$(curl -s -o /dev/null -w "%{http_code}" $url)
    
    if [ "$response" == "200" ]; then
        echo -e "${GREEN}✓ $service health check passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $service health check failed (HTTP $response)${NC}"
        return 1
    fi
}

# Get Docker container status
echo -e "\n${YELLOW}Checking Docker container status...${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep mlops

# Check if Docker containers are running
if ! docker ps | grep -q mlops; then
    echo -e "\n${RED}No MLOps containers are running. Start them with:${NC}"
    echo "docker-compose up -d"
    exit 1
 fi

# Get port mappings from Docker
echo -e "\n${YELLOW}Getting port mappings from Docker...${NC}"

# Extract port mappings for each service
GRAFANA_PORT=$(docker port mlops-grafana 3000/tcp | cut -d ':' -f 2)
MLFLOW_PORT=$(docker port mlops-mlflow 5000/tcp | cut -d ':' -f 2)
HOUSING_API_PORT=$(docker port mlops-housing-api 8000/tcp | cut -d ':' -f 2)
RETRAINING_PORT=$(docker port mlops-retraining 8002/tcp | cut -d ':' -f 2)
PROMETHEUS_PORT=$(docker port mlops-prometheus 9090/tcp | cut -d ':' -f 2)

echo "Grafana: localhost:$GRAFANA_PORT"
echo "MLflow: localhost:$MLFLOW_PORT"
echo "Housing API: localhost:$HOUSING_API_PORT"
echo "Retraining Service: localhost:$RETRAINING_PORT"
echo "Prometheus: localhost:$PROMETHEUS_PORT"

# Check if ports are open
echo -e "\n${YELLOW}Checking if ports are open...${NC}"
check_port localhost $GRAFANA_PORT "Grafana"
check_port localhost $MLFLOW_PORT "MLflow"
check_port localhost $HOUSING_API_PORT "Housing API"
check_port localhost $RETRAINING_PORT "Retraining Service"
check_port localhost $PROMETHEUS_PORT "Prometheus"

# Check health endpoints
echo -e "\n${YELLOW}Checking service health endpoints...${NC}"
check_health "http://localhost:$GRAFANA_PORT/api/health" "Grafana"
check_health "http://localhost:$MLFLOW_PORT" "MLflow"
check_health "http://localhost:$HOUSING_API_PORT/health" "Housing API"
check_health "http://localhost:$RETRAINING_PORT/health" "Retraining Service"
check_health "http://localhost:$PROMETHEUS_PORT/-/healthy" "Prometheus"

# Check Docker logs for errors
echo -e "\n${YELLOW}Checking for errors in Docker logs...${NC}"
for container in mlops-grafana mlops-mlflow mlops-housing-api mlops-retraining mlops-prometheus; do
    echo -e "\n${YELLOW}Last 10 log lines for $container:${NC}"
    docker logs --tail 10 $container
done

# Check Docker network
echo -e "\n${YELLOW}Checking Docker network...${NC}"
docker network inspect mlops-network

echo -e "\n${YELLOW}===== Diagnosis and Recommendations =====${NC}"
echo "1. If only the Housing API is accessible, check if other services started correctly."
echo "2. Verify that all services have proper health check configurations in docker-compose.yml."
echo "3. Check if there are any port conflicts on your host machine."
echo "4. Try restarting the services with: docker-compose restart <service-name>"
echo "5. For detailed logs, run: docker logs <container-name>"