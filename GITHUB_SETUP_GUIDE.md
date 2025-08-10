# 🚀 Complete GitHub CI/CD Setup Guide

This guide will help you set up the complete CI/CD pipeline with GitHub Actions, Docker Hub integration, and automated deployment.

## 📋 Prerequisites

1. ✅ **GitHub Repository** - Your code is in a GitHub repo
2. ✅ **Docker Hub Account** - For storing Docker images
3. ✅ **Local Docker Desktop** - For testing deployments

## 🔧 Step 1: Set Up Docker Hub

### Create Docker Hub Repository
1. **Go to** [Docker Hub](https://hub.docker.com/)
2. **Sign in** to your account
3. **Click** "Create Repository"
4. **Repository name**: `mlops-housing-pipeline`
5. **Visibility**: Public (or Private if you prefer)
6. **Click** "Create"

### Get Docker Hub Credentials
1. **Username**: Your Docker Hub username
2. **Password**: Your Docker Hub password (or access token - recommended)

**To create an access token (recommended)**:
1. Go to **Account Settings** → **Security**
2. Click **"New Access Token"**
3. **Description**: "GitHub Actions CI/CD"
4. **Permissions**: Read, Write, Delete
5. **Copy the token** (you won't see it again!)

## 🔐 Step 2: Configure GitHub Secrets

### Add Secrets to Your GitHub Repository
1. **Go to your GitHub repository**
2. **Click** "Settings" tab
3. **Click** "Secrets and variables" → "Actions"
4. **Click** "New repository secret"

### Required Secrets:
Add these secrets one by one:

#### 1. DOCKER_USERNAME
- **Name**: `DOCKER_USERNAME`
- **Value**: Your Docker Hub username
- **Click** "Add secret"

#### 2. DOCKER_PASSWORD
- **Name**: `DOCKER_PASSWORD`
- **Value**: Your Docker Hub password or access token
- **Click** "Add secret"

### Verify Secrets
You should now see:
- ✅ `DOCKER_USERNAME`
- ✅ `DOCKER_PASSWORD`

## 📁 Step 3: Prepare Your Repository

### Required Files Checklist
Make sure your repository has these files:

```
mlops-housing-pipeline/
├── .github/workflows/ci-cd.yml     ✅ (Updated with CI/CD pipeline)
├── api/
│   ├── housing_api.py              ✅ (With retraining endpoints)
│   └── main.py                     ✅ (With retraining endpoints)
├── src/                            ✅ (All source code)
├── models/                         ✅ (Model files)
├── data/                           ✅ (Data files)
├── Dockerfile                      ✅ (Updated)
├── docker-compose.monitoring.yml   ✅ (Complete monitoring stack)
├── requirements.txt                ✅ (All dependencies)
├── deploy.sh                       ✅ (Deployment script)
└── README.md                       ✅ (Documentation)
```

### Update requirements.txt
Make sure your `requirements.txt` includes all dependencies:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pandas==2.1.3
scikit-learn==1.3.2
numpy==1.25.2
pydantic==2.5.0
python-multipart==0.0.6
mlflow==2.8.1
prometheus-client==0.19.0
prometheus-fastapi-instrumentator==6.1.0
joblib==1.3.2
requests==2.31.0
```

## 🚀 Step 4: Test the CI/CD Pipeline

### Push to GitHub
```bash
# Add all files
git add .

# Commit changes
git commit -m "feat: Complete CI/CD pipeline with Docker Hub integration"

# Push to main branch
git push origin main
```

### Monitor the Pipeline
1. **Go to your GitHub repository**
2. **Click** "Actions" tab
3. **You should see** the workflow running with these jobs:
   - ✅ **Code Quality & Linting** - Checks code quality
   - ✅ **Validation Testing** - Tests APIs and validation
   - ✅ **Docker Build & Push** - Builds and pushes to Docker Hub
   - ✅ **Security Scanning** - Scans for vulnerabilities
   - ✅ **Deploy Application** - Creates deployment artifacts

### Expected Pipeline Flow
```
Push to main → Code Quality → Testing → Docker Build → Security Scan → Deploy
     ↓              ↓           ↓           ↓              ↓           ↓
   Lint code    Run tests   Build image   Scan image   Create deploy
   Format       Validate    Push to Hub   Check vulns   artifacts
```

## 🐳 Step 5: Verify Docker Hub Integration

### Check Docker Hub
1. **Go to** [Docker Hub](https://hub.docker.com/)
2. **Navigate** to your `mlops-housing-pipeline` repository
3. **You should see** a new image with tags like:
   - `latest`
   - `main-<commit-sha>`

### Test Local Pull
```bash
# Pull your image from Docker Hub
docker pull your-username/mlops-housing-pipeline:latest

# Verify it works
docker run -p 8000:8000 your-username/mlops-housing-pipeline:latest
```

## 🚀 Step 6: Deploy Locally

### Using the Deployment Script
```bash
# Make script executable
chmod +x deploy.sh

# Set your Docker username
export DOCKER_USERNAME="your-docker-username"

# Deploy the pipeline
./deploy.sh

# Other commands:
./deploy.sh stop      # Stop all services
./deploy.sh restart   # Restart services
./deploy.sh logs      # View logs
./deploy.sh status    # Check status
```

### Manual Deployment
```bash
# Pull latest image
docker pull your-username/mlops-housing-pipeline:latest

# Start the monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Check services
curl http://localhost:8000/health
curl http://localhost:8001/health
```

## 📊 Step 7: Verify Complete Setup

### Test All Components
1. **APIs**: http://localhost:8000/docs and http://localhost:8001/docs
2. **Retraining**: Use the `/retrain` endpoints
3. **Monitoring**: http://localhost:3000 (Grafana)
4. **Metrics**: http://localhost:9090 (Prometheus)
5. **Experiments**: http://localhost:5000 (MLflow)

### Test CI/CD Features
```bash
# Make a small change
echo "# Updated" >> README.md

# Commit and push
git add README.md
git commit -m "test: Trigger CI/CD pipeline"
git push origin main

# Watch the pipeline run in GitHub Actions
```

## 🎯 Step 8: Advanced Features

### Automated Daily Retraining
The pipeline includes a scheduled job that runs daily at 2 AM UTC to retrain models automatically.

### Branch Protection
Consider setting up branch protection rules:
1. **Go to** Settings → Branches
2. **Add rule** for `main` branch
3. **Require** status checks to pass
4. **Require** pull request reviews

### Notifications
Set up notifications for pipeline failures:
1. **Go to** Settings → Notifications
2. **Configure** email or Slack notifications
3. **Set up** for failed workflows

## 🔍 Troubleshooting

### Common Issues

#### 1. Docker Hub Authentication Failed
- **Check** your Docker Hub credentials
- **Verify** secrets are set correctly in GitHub
- **Try** using an access token instead of password

#### 2. Pipeline Fails on Tests
- **Check** the test logs in GitHub Actions
- **Ensure** all dependencies are in requirements.txt
- **Verify** model files exist

#### 3. Deployment Script Fails
- **Check** Docker is running locally
- **Verify** ports 8000, 8001, 3000, 9090, 5000 are available
- **Check** docker-compose.monitoring.yml exists

#### 4. Services Not Starting
- **Check** container logs: `docker-compose logs`
- **Verify** image was built correctly
- **Check** port conflicts

### Getting Help
- **Check** GitHub Actions logs for detailed error messages
- **Review** Docker container logs
- **Verify** all required files are present
- **Test** locally before pushing to GitHub

## ✅ Success Checklist

- [ ] GitHub repository created and configured
- [ ] Docker Hub repository created
- [ ] GitHub secrets configured (DOCKER_USERNAME, DOCKER_PASSWORD)
- [ ] All required files in repository
- [ ] CI/CD pipeline runs successfully
- [ ] Docker image builds and pushes to Docker Hub
- [ ] Local deployment works with deploy.sh
- [ ] All APIs accessible and functional
- [ ] Monitoring dashboard working
- [ ] Retraining endpoints available

## 🎉 Congratulations!

You now have a complete MLOps CI/CD pipeline with:
- ✅ **Automated testing** on every push
- ✅ **Docker image building** and pushing to Docker Hub
- ✅ **Security scanning** with Trivy
- ✅ **Automated deployment** scripts
- ✅ **Comprehensive monitoring** with Grafana and Prometheus
- ✅ **Model retraining** capabilities
- ✅ **Daily scheduled** model updates

Your MLOps pipeline is production-ready! 🚀
