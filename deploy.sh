#!/bin/bash
set -e

echo "🚀 Starting MLOps Pipeline Deployment"

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.monitoring.yml down || true

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker pull ${DOCKER_USERNAME:-username}/mlops-housing-pipeline:latest

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Health checks
echo "🏥 Running health checks..."
curl -f http://localhost:8000/health || exit 1

echo "✅ Deployment completed successfully!"
echo "🌐 Services available at:"
echo "  - Housing API: http://localhost:8000/docs"
echo "  - Grafana: http://localhost:3000"
echo "  - MLflow: http://localhost:5000"