# ML Housing Project - Docker & CI/CD Guide

## Overview

This document provides instructions for working with the Docker containers and CI/CD automation for the ML Housing project.

## Docker Compose Stack

The project uses Docker Compose to manage multiple services:

- **Housing API**: Main prediction service
- **Model Training**: Service for training ML models
- **Data Loader**: Service for loading and preprocessing data
- **Retraining Service**: Automated model retraining
- **MLflow**: Model tracking and versioning
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and monitoring

## Local Development

### Running the Stack

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Service URLs

- Housing API: http://localhost:8000/docs
- MLflow: http://localhost:5000
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- Retraining Service: http://localhost:8002

## CI/CD Automation

The project includes GitHub Actions workflows for CI/CD automation in `.github/workflows/ci-cd.yml`.

### Workflow Steps

1. **Code Quality**: Linting and type checking
2. **Validation Testing**: Data validation and API testing
3. **Docker Build & Push**: Building and pushing Docker images
4. **Security Scanning**: Vulnerability scanning with Trivy
5. **Deployment**: Automated deployment script generation

### Deployment

For deployment, use the provided scripts:

#### Linux/macOS
```bash
# Set Docker Hub username
export DOCKER_USERNAME=your_username

# Run deployment script
./deploy.sh
```

#### Windows
```powershell
# Set Docker Hub username
$env:DOCKER_USERNAME="your_username"

# Run deployment script
.\deploy.ps1
```

## Monitoring

The project includes comprehensive monitoring:

- **Grafana Dashboards**: Pre-configured dashboards for model performance and system metrics
- **Prometheus Metrics**: Custom metrics for model accuracy, prediction latency, and system health
- **Health Checks**: All services include health check endpoints

## Troubleshooting

### Common Issues

1. **Services not starting**: Check Docker logs with `docker-compose logs [service_name]`
2. **Port conflicts**: Ensure ports 8000, 5000, 9090, and 3000 are available
3. **Missing data**: Verify data volumes are properly mounted

### Health Check

Run the health check script to verify all services:

```bash
# Linux/macOS
./check_services.sh

# Windows
.\check_services.ps1
```