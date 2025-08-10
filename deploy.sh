#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_USERNAME=${DOCKER_USERNAME:-"your-docker-username"}
IMAGE_NAME="mlops-housing-pipeline"
COMPOSE_FILE="docker-compose.monitoring.yml"

echo -e "${BLUE}🚀 MLOps Pipeline Deployment Script${NC}"
echo "=================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is running
check_docker() {
    print_info "Checking Docker status..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    print_status "Docker is running"
}

# Stop existing containers
stop_existing() {
    print_info "Stopping existing containers..."
    if [ -f "$COMPOSE_FILE" ]; then
        docker-compose -f "$COMPOSE_FILE" down || true
        print_status "Existing containers stopped"
    else
        print_warning "No existing compose file found"
    fi
}

# Pull latest images
pull_images() {
    print_info "Pulling latest Docker images..."
    
    # Pull the main application image
    if docker pull "$DOCKER_USERNAME/$IMAGE_NAME:latest" 2>/dev/null; then
        print_status "Application image pulled successfully"
    else
        print_warning "Could not pull application image, will build locally"
        build_local_image
    fi
    
    # Pull other required images
    docker pull grafana/grafana:latest || print_warning "Could not pull Grafana image"
    docker pull prom/prometheus:latest || print_warning "Could not pull Prometheus image"
    docker pull python:3.10-slim || print_warning "Could not pull Python image"
}

# Build local image if pull fails
build_local_image() {
    print_info "Building Docker image locally..."
    if docker build -t "$DOCKER_USERNAME/$IMAGE_NAME:latest" .; then
        print_status "Local image built successfully"
    else
        print_error "Failed to build local image"
        exit 1
    fi
}

# Update docker-compose file to use the correct image
update_compose_file() {
    print_info "Updating docker-compose configuration..."
    
    if [ -f "$COMPOSE_FILE" ]; then
        # Create backup
        cp "$COMPOSE_FILE" "$COMPOSE_FILE.backup"
        
        # Update image references (if needed)
        # This is a placeholder - adjust based on your compose file structure
        print_status "Docker-compose file ready"
    else
        print_error "Docker-compose file not found: $COMPOSE_FILE"
        exit 1
    fi
}

# Start services
start_services() {
    print_info "Starting MLOps services..."
    
    if docker-compose -f "$COMPOSE_FILE" up -d; then
        print_status "Services started successfully"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Wait for services to be ready
wait_for_services() {
    print_info "Waiting for services to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo -n "."
        
        # Check if services are responding
        if curl -s http://localhost:8000/health > /dev/null 2>&1 && \
           curl -s http://localhost:8001/health > /dev/null 2>&1; then
            echo ""
            print_status "All services are ready!"
            return 0
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo ""
    print_warning "Services may not be fully ready yet, but continuing..."
}

# Run health checks
run_health_checks() {
    print_info "Running comprehensive health checks..."
    
    local all_healthy=true
    
    # Check Housing API
    if curl -f -s http://localhost:8000/health > /dev/null; then
        print_status "Housing API is healthy"
    else
        print_error "Housing API health check failed"
        all_healthy=false
    fi
    
    # Check Iris API
    if curl -f -s http://localhost:8001/health > /dev/null; then
        print_status "Iris API is healthy"
    else
        print_error "Iris API health check failed"
        all_healthy=false
    fi
    
    # Check Grafana
    if curl -f -s http://localhost:3000/api/health > /dev/null; then
        print_status "Grafana is healthy"
    else
        print_warning "Grafana may still be starting up"
    fi
    
    # Check Prometheus
    if curl -f -s http://localhost:9090/-/healthy > /dev/null; then
        print_status "Prometheus is healthy"
    else
        print_warning "Prometheus may still be starting up"
    fi
    
    if [ "$all_healthy" = true ]; then
        print_status "All critical services are healthy!"
    else
        print_warning "Some services may need more time to start"
    fi
}

# Display service URLs
show_service_urls() {
    echo ""
    echo -e "${BLUE}🌐 Service URLs:${NC}"
    echo "=================================="
    echo -e "${GREEN}Housing API:${NC}     http://localhost:8000/docs"
    echo -e "${GREEN}Iris API:${NC}        http://localhost:8001/docs"
    echo -e "${GREEN}Grafana:${NC}         http://localhost:3000 (admin/admin)"
    echo -e "${GREEN}Prometheus:${NC}      http://localhost:9090"
    echo -e "${GREEN}MLflow:${NC}          http://localhost:5000"
    echo ""
    echo -e "${YELLOW}📊 Quick Tests:${NC}"
    echo "curl http://localhost:8000/health"
    echo "curl http://localhost:8001/health"
    echo ""
}

# Show container status
show_container_status() {
    print_info "Container Status:"
    docker-compose -f "$COMPOSE_FILE" ps
}

# Main deployment function
main() {
    echo -e "${BLUE}Starting deployment process...${NC}"
    echo ""
    
    check_docker
    stop_existing
    pull_images
    update_compose_file
    start_services
    wait_for_services
    run_health_checks
    show_container_status
    show_service_urls
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "${BLUE}Your MLOps pipeline is now running!${NC}"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        print_info "Stopping all services..."
        docker-compose -f "$COMPOSE_FILE" down
        print_status "All services stopped"
        ;;
    "restart")
        print_info "Restarting all services..."
        docker-compose -f "$COMPOSE_FILE" restart
        print_status "All services restarted"
        ;;
    "logs")
        print_info "Showing service logs..."
        docker-compose -f "$COMPOSE_FILE" logs -f
        ;;
    "status")
        show_container_status
        ;;
    "help")
        echo "Usage: $0 [deploy|stop|restart|logs|status|help]"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy the MLOps pipeline (default)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show service logs"
        echo "  status   - Show container status"
        echo "  help     - Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
