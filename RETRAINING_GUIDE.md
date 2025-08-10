# 🔄 Complete Model Retraining Guide

This guide shows you all the ways to retrain your models with new datasets.

## 🎯 Retraining Options Overview

Your MLOps pipeline has **4 different ways** to retrain models:

1. **🤖 Automatic Retraining Service** - API-based retraining (Recommended)
2. **📅 Scheduled Retraining** - Runs automatically daily
3. **💻 Manual Script Execution** - Direct Python scripts
4. **🔧 Custom Dataset Integration** - Add your own data

---

## 🤖 Option 1: Automatic Retraining Service (Easiest)

### Access the Retraining API
The retraining service runs on **port 8002** with its own API interface.

**URL**: http://localhost:8002

### Available Endpoints:

#### 1. **Check Retraining Status**
```bash
curl http://localhost:8002/status
```

#### 2. **Trigger Manual Retraining**
```bash
# Retrain all models
curl -X POST "http://localhost:8002/retrain" \
  -H "Content-Type: application/json" \
  -d '{}'

# Retrain specific model
curl -X POST "http://localhost:8002/retrain" \
  -H "Content-Type: application/json" \
  -d '{"model_type": "housing"}'

# Force retraining (even if performance is good)
curl -X POST "http://localhost:8002/retrain" \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

#### 3. **View Retraining Results**
```bash
curl http://localhost:8002/results
```

#### 4. **Check Performance Metrics**
```bash
curl http://localhost:8002/performance
```

### Using the Web Interface
1. **Open**: http://localhost:8002/docs
2. **Try the interactive API** - just like the housing API
3. **Click** on `/retrain` endpoint
4. **Click** "Try it out"
5. **Modify** the JSON payload if needed
6. **Click** "Execute"

---

## 📅 Option 2: Scheduled Retraining

### How It Works
- **Automatic**: Runs every day at 2 AM
- **Performance Checks**: Every 6 hours
- **Smart**: Only retrains if performance drops

### Configure Schedule
Edit `src/retraining_scheduler.py`:
```python
# Change the schedule
schedule.every().day.at("02:00").do(self.run_scheduled_retraining)
schedule.every(6).hours.do(self.check_performance)

# Examples of other schedules:
schedule.every().hour.do(self.check_performance)           # Every hour
schedule.every().monday.at("09:00").do(self.run_scheduled_retraining)  # Weekly
schedule.every(30).minutes.do(self.check_performance)      # Every 30 min
```

---

## 💻 Option 3: Manual Script Execution

### Run Retraining Scripts Directly

#### Housing Model Retraining
```bash
# Navigate to your project directory
cd "c:\Users\vinay\OneDrive\Desktop\mlops-housing-pipeline (2) (1)\mlops-housing-pipeline"

# Run housing model retraining
python src/model_retraining.py
```

#### Individual Model Scripts
```bash
# Retrain housing model only
python src/train_and_track.py

# Retrain iris model only
python src/train_iris.py
```

---

## 🔧 Option 4: Custom Dataset Integration

### Adding New Housing Data

#### Step 1: Prepare Your Data
Your new dataset should have these columns:
```
MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Latitude, Longitude, MedHouseVal
```

#### Step 2: Replace the Dataset
```bash
# Backup original data
cp data/housing.csv data/housing_backup.csv

# Add your new data
cp /path/to/your/new_data.csv data/housing.csv
```

#### Step 3: Retrain with New Data
```bash
# Method 1: Use retraining API
curl -X POST "http://localhost:8002/retrain" \
  -H "Content-Type: application/json" \
  -d '{"force": true}'

# Method 2: Run script directly
python src/train_and_track.py
```

### Adding New Iris Data

#### Step 1: Prepare Your Data
Your iris dataset should have these columns:
```
sepal length (cm), sepal width (cm), petal length (cm), petal width (cm), target
```

#### Step 2: Modify the Training Script
Edit `src/train_iris.py` to load your custom data:
```python
# Replace this line:
data = load_iris(as_frame=True)

# With this:
import pandas as pd
df = pd.read_csv('data/your_iris_data.csv')
X = df.drop('target', axis=1)
y = df['target']
```

#### Step 3: Retrain
```bash
python src/train_iris.py
```

---

## 📊 Monitoring Retraining Progress

### View Training Logs
```bash
# Real-time logs
docker-compose -f docker-compose.monitoring.yml logs -f retraining-service

# Or check log files
tail -f retraining.log
```

### MLflow Experiment Tracking
1. **Open**: http://localhost:5000
2. **View experiments**: See all training runs
3. **Compare models**: Check which performs better
4. **Download models**: Get trained model files

### Check Model Performance
```bash
# Get current performance metrics
curl http://localhost:8002/performance

# Example response:
{
  "housing": {
    "r2_score": 0.65,
    "mse": 0.45,
    "needs_retraining": false
  },
  "iris": {
    "accuracy": 0.92,
    "f1_score": 0.91,
    "needs_retraining": false
  }
}
```

---

## 🎯 Step-by-Step: Retrain with New Data

### Complete Example: Housing Model

#### Step 1: Start Services
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

#### Step 2: Check Current Performance
```bash
curl http://localhost:8002/performance
```

#### Step 3: Add Your New Data
```bash
# Replace with your data file
cp your_new_housing_data.csv data/housing.csv
```

#### Step 4: Trigger Retraining
```bash
curl -X POST "http://localhost:8002/retrain" \
  -H "Content-Type: application/json" \
  -d '{"model_type": "housing", "force": true}'
```

#### Step 5: Monitor Progress
```bash
# Check status
curl http://localhost:8002/status

# View results when complete
curl http://localhost:8002/results
```

#### Step 6: Test New Model
```bash
# Make a prediction to test
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
```

---

## 🔍 Troubleshooting Retraining

### Common Issues

#### 1. **Retraining Service Not Running**
```bash
# Check if service is up
curl http://localhost:8002/health

# If not, start it
docker-compose -f docker-compose.monitoring.yml restart retraining-service
```

#### 2. **Data Format Issues**
- **Check column names**: Must match expected format
- **Check data types**: Numeric columns should be numbers
- **Check missing values**: Remove or impute missing data

#### 3. **Memory Issues**
```bash
# Check Docker memory limits
docker stats

# Increase memory if needed in docker-compose.monitoring.yml
```

#### 4. **Permission Issues**
```bash
# Fix file permissions
chmod 644 data/*.csv
chmod 755 src/*.py
```

---

## 📈 Advanced Retraining Features

### Custom Performance Thresholds
Edit `src/model_retraining.py`:
```python
self.performance_thresholds = {
    'housing': {
        'min_r2': 0.6,      # Increase from 0.5
        'max_mse': 0.8,     # Decrease from 1.0
        'min_predictions': 50  # Decrease from 100
    },
    'iris': {
        'min_accuracy': 0.90,  # Increase from 0.85
        'min_f1': 0.90,        # Increase from 0.85
        'min_predictions': 25   # Decrease from 50
    }
}
```

### A/B Testing Models
```python
# Train multiple models and compare
models = {
    'RandomForest': RandomForestRegressor(n_estimators=100),
    'GradientBoosting': GradientBoostingRegressor(),
    'XGBoost': XGBRegressor()
}
```

### Data Validation Before Training
```python
# Add data quality checks
def validate_data(df):
    assert df.shape[0] > 100, "Need at least 100 samples"
    assert df.isnull().sum().sum() == 0, "No missing values allowed"
    assert df.dtypes.apply(lambda x: x.kind in 'biufc').all(), "All numeric columns"
```

---

## 🎉 Quick Start Commands

```bash
# 1. Check retraining service
curl http://localhost:8002/docs

# 2. Trigger immediate retraining
curl -X POST "http://localhost:8002/retrain" -H "Content-Type: application/json" -d '{"force": true}'

# 3. Check results
curl http://localhost:8002/results

# 4. View in MLflow
# Open: http://localhost:5000
```

---

## 📞 Need Help?

### Documentation
- **Full API docs**: http://localhost:8002/docs
- **MLflow UI**: http://localhost:5000
- **Grafana monitoring**: http://localhost:3000

### Log Files
- **Retraining logs**: `retraining.log`
- **Service logs**: `docker-compose logs retraining-service`
- **MLflow logs**: Check MLflow UI

### Support Commands
```bash
# Health check all services
curl http://localhost:8000/health  # Housing API
curl http://localhost:8001/health  # Iris API
curl http://localhost:8002/health  # Retraining Service

# Restart everything
docker-compose -f docker-compose.monitoring.yml restart
```

Your models can now be retrained automatically or on-demand with new datasets! 🚀
