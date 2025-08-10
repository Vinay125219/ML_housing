# Enhanced MLOps Features Guide

This document describes the enhanced features added to the MLOps Housing Pipeline project, including automated model retraining, comprehensive monitoring, and testing capabilities.

## 🚀 New Features Overview

### 1. **Enhanced Input Validation with Pydantic**
- Comprehensive validation for both Housing and Iris APIs
- Range validation based on dataset characteristics
- Custom validators for logical consistency
- Detailed error messages with field-specific feedback

### 2. **Automated Model Retraining**
- Performance monitoring and drift detection
- Scheduled retraining pipeline
- MLflow integration for experiment tracking
- API endpoints for manual retraining triggers

### 3. **Advanced Prometheus Metrics**
- Model performance metrics (accuracy, MSE, R²)
- API metrics (request rate, latency, errors)
- Data quality metrics (drift detection, feature stats)
- Business metrics (daily predictions, confidence scores)

### 4. **Grafana Monitoring Dashboard**
- Real-time visualization of all metrics
- Model performance tracking
- System health monitoring
- Alert configuration capabilities

### 5. **Comprehensive Testing Suite**
- Validation testing with edge cases
- API endpoint testing
- Sample data for user testing
- Automated test execution

## 📋 Quick Start Guide

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p models data housinglogs irislogs mlruns
```

### 1. Start the Enhanced APIs

#### Housing Price Prediction API
```bash
uvicorn api.housing_api:app --host 0.0.0.0 --port 8000
```

#### Iris Classification API
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8001
```

#### Model Retraining Service
```bash
python src/retraining_scheduler.py
```

### 2. Start Monitoring Stack
```bash
# Start all services with Docker Compose
docker-compose -f docker-compose.monitoring.yml up -d

# Access services:
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
# - Housing API: http://localhost:8000
# - Iris API: http://localhost:8001
# - MLflow: http://localhost:5000
```

### 3. Test the APIs
```bash
# Run comprehensive API tests
python test_api_samples.py

# Test with custom URLs
python test_api_samples.py --housing-url http://localhost:8000 --iris-url http://localhost:8001

# Skip invalid sample testing
python test_api_samples.py --skip-invalid

# Save results to file
python test_api_samples.py --save-results
```

## 🧪 Testing Samples

### Valid Housing API Samples
```json
{
  "total_rooms": 5000.0,
  "total_bedrooms": 1200.0,
  "population": 3000.0,
  "households": 1000.0,
  "median_income": 5.5,
  "housing_median_age": 25.0,
  "latitude": 37.88,
  "longitude": -122.23
}
```

### Valid Iris API Samples
```json
{
  "sepal_length": 5.8,
  "sepal_width": 3.0,
  "petal_length": 4.3,
  "petal_width": 1.3
}
```

### Testing with cURL
```bash
# Test Housing API
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "total_rooms": 5000.0,
    "total_bedrooms": 1200.0,
    "population": 3000.0,
    "households": 1000.0,
    "median_income": 5.5,
    "housing_median_age": 25.0,
    "latitude": 37.88,
    "longitude": -122.23
  }'

# Test Iris API
curl -X POST "http://localhost:8001/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.8,
    "sepal_width": 3.0,
    "petal_length": 4.3,
    "petal_width": 1.3
  }'
```

## 📊 Monitoring & Metrics

### API Endpoints
- **Housing API Docs**: http://localhost:8000/docs
- **Iris API Docs**: http://localhost:8001/docs
- **Prometheus Metrics**: http://localhost:8000/mlops-metrics
- **Retraining Service**: http://localhost:8002/status

### Key Metrics Available
- `mlops_api_requests_total` - Total API requests
- `mlops_model_predictions_total` - Total predictions made
- `mlops_model_accuracy` - Current model accuracy
- `mlops_api_validation_errors_total` - Validation errors
- `mlops_daily_predictions` - Daily prediction counts
- `mlops_model_prediction_latency_seconds` - Prediction latency

### Grafana Dashboard
1. Access Grafana at http://localhost:3000
2. Login with admin/admin
3. Navigate to "MLOps Monitoring Dashboard"
4. View real-time metrics and performance data

## 🔄 Model Retraining

### Automatic Retraining
- Runs daily at 2 AM (configurable)
- Performance checks every 6 hours
- Triggers retraining when performance degrades

### Manual Retraining
```bash
# Trigger retraining via API
curl -X POST "http://localhost:8002/retrain" \
  -H "Content-Type: application/json" \
  -d '{"force": true}'

# Check retraining status
curl "http://localhost:8002/status"

# View retraining results
curl "http://localhost:8002/results"
```

### Performance Thresholds
- **Housing Model**: R² > 0.5, MSE < 1.0
- **Iris Model**: Accuracy > 0.85, F1 > 0.85

## 🐳 Docker Deployment

### Single Service
```bash
# Build image
docker build -t mlops-housing-pipeline .

# Run housing API
docker run -p 8000:8000 mlops-housing-pipeline

# Run iris API
docker run -p 8001:8001 mlops-housing-pipeline \
  uvicorn api.main:app --host 0.0.0.0 --port 8001
```

### Full Stack
```bash
# Start complete monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f

# Stop all services
docker-compose -f docker-compose.monitoring.yml down
```

## 🔧 Configuration

### Environment Variables
```bash
export PYTHONPATH=/app
export MLFLOW_TRACKING_URI=http://localhost:5000
export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc_dir
```

### Customizing Validation Rules
Edit the Pydantic models in:
- `api/housing_api.py` - Housing validation rules
- `api/main.py` - Iris validation rules

### Customizing Retraining Schedule
Edit `src/retraining_scheduler.py`:
```python
# Change schedule
schedule.every().day.at("02:00").do(self.run_scheduled_retraining)
schedule.every(6).hours.do(self.check_performance)
```

## 📈 Performance Monitoring

### Health Checks
- **Housing API**: http://localhost:8000/health
- **Iris API**: http://localhost:8001/health
- **Retraining Service**: http://localhost:8002/health

### Logs
- Application logs: `*.log` files
- Prediction logs: SQLite databases in `housinglogs/` and `irislogs/`
- MLflow experiments: `mlruns/` directory

## 🚨 Troubleshooting

### Common Issues
1. **Model Loading Errors**: Retrain models with `python src/train_and_track.py`
2. **Database Errors**: Check directory permissions for `housinglogs/` and `irislogs/`
3. **Prometheus Metrics**: Ensure `/mlops-metrics` endpoint is accessible
4. **Docker Issues**: Check port conflicts and container logs

### Debug Mode
```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
python -m uvicorn api.housing_api:app --reload --log-level debug
```

## 📚 Additional Resources

- **API Documentation**: Available at `/docs` endpoint for each service
- **Prometheus Metrics**: Available at `/mlops-metrics` endpoint
- **MLflow UI**: http://localhost:5000 for experiment tracking
- **Test Results**: Generated in `test_results_*.json` files

For more detailed information, see the individual component documentation in the `src/` directory.
