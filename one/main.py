from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional
import pandas as pd
# import mlflow.pyfunc  # Uncomment if using MLflow
import joblib
import logging
from datetime import datetime
import sqlite3
import os
from prometheus_fastapi_instrumentator import Instrumentator
import subprocess
import sys

# Ensure the log directory exists
os.makedirs("irislogs", exist_ok=True)

# Load MLflow model
# model_uri = "runs:/70968cdab4644053835a226c51eec164/model"
# model = mlflow.pyfunc.load_model(model_uri)

# OR load local model:
try:
    model = joblib.load("models/RandomForest.pkl")
    print("✅ Loaded RandomForest model successfully")
except Exception as e:
    print(f"⚠️ Could not load RandomForest model: {e}")
    try:
        model = joblib.load("models/LogisticRegression.pkl")
        print("✅ Loaded LogisticRegression model successfully")
    except Exception as e2:
        print(f"❌ Could not load any existing models: {e2}")
        print("🔄 Please run the training scripts first:")
        print("   python src/train_iris.py")
        # Create a dummy model for now
        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression()
        print("⚠️ Using dummy model - please train proper models first")

# Setup file logging
logging.basicConfig(
    filename='irislogs/predictions.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# SQLite DB setup
conn = sqlite3.connect("irislogs/predictions.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS irislogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    inputs TEXT,
    prediction TEXT
)
''')
conn.commit()

# FastAPI setup
app = FastAPI(
    title="MLOps Iris Classification API",
    description="A comprehensive MLOps pipeline for iris flower classification with automated training, deployment, monitoring, and retraining capabilities.",
    version="1.0.0",
    contact={
        "name": "MLOps Team",
        "email": "mlops@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Expose Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app, include_in_schema=False, endpoint="/metrics")

# Expected input features
FEATURE_NAMES = [
    "sepal length (cm)",
    "sepal width (cm)",
    "petal length (cm)",
    "petal width (cm)"
]

class IrisRequest(BaseModel):
    """
    Iris flower measurements for classification.
    
    All measurements must be positive numbers within realistic ranges for iris flowers.
    """
    sepal_length: float = Field(
        ..., 
        gt=0, 
        ge=4.0, 
        le=8.0,
        description="Sepal length in centimeters",
        example=5.1
    )
    sepal_width: float = Field(
        ..., 
        gt=0, 
        ge=2.0, 
        le=5.0,
        description="Sepal width in centimeters",
        example=3.5
    )
    petal_length: float = Field(
        ..., 
        gt=0, 
        ge=1.0, 
        le=7.0,
        description="Petal length in centimeters",
        example=1.4
    )
    petal_width: float = Field(
        ..., 
        gt=0, 
        ge=0.1, 
        le=3.0,
        description="Petal width in centimeters",
        example=0.2
    )

    @validator('sepal_length')
    def validate_sepal_length(cls, v):
        if v < 4.0 or v > 8.0:
            raise ValueError(f'Sepal length {v} cm is outside valid range [4.0, 8.0] cm')
        return v

    @validator('sepal_width')
    def validate_sepal_width(cls, v):
        if v < 2.0 or v > 5.0:
            raise ValueError(f'Sepal width {v} cm is outside valid range [2.0, 5.0] cm')
        return v

    @validator('petal_length')
    def validate_petal_length(cls, v):
        if v < 1.0 or v > 7.0:
            raise ValueError(f'Petal length {v} cm is outside valid range [1.0, 7.0] cm')
        return v

    @validator('petal_width')
    def validate_petal_width(cls, v):
        if v < 0.1 or v > 3.0:
            raise ValueError(f'Petal width {v} cm is outside valid range [0.1, 3.0] cm')
        return v

    @validator('*')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError(f'All measurements must be positive numbers, got {v}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2
            },
            "examples": {
                "valid_setosa": {
                    "summary": "Valid Setosa flower measurements",
                    "description": "Typical measurements for Iris Setosa (small petals)",
                    "value": {
                        "sepal_length": 5.1,
                        "sepal_width": 3.5,
                        "petal_length": 1.4,
                        "petal_width": 0.2
                    }
                },
                "valid_versicolor": {
                    "summary": "Valid Versicolor flower measurements",
                    "description": "Typical measurements for Iris Versicolor (medium petals)",
                    "value": {
                        "sepal_length": 6.4,
                        "sepal_width": 3.2,
                        "petal_length": 4.5,
                        "petal_width": 1.5
                    }
                },
                "valid_virginica": {
                    "summary": "Valid Virginica flower measurements",
                    "description": "Typical measurements for Iris Virginica (large petals)",
                    "value": {
                        "sepal_length": 6.3,
                        "sepal_width": 3.3,
                        "petal_length": 6.0,
                        "petal_width": 2.5
                    }
                },
                "invalid_example_1": {
                    "summary": "Invalid: Out of range sepal length",
                    "description": "Shows validation error for sepal length > 8.0 cm",
                    "value": {
                        "sepal_length": 9.0,
                        "sepal_width": 3.5,
                        "petal_length": 1.4,
                        "petal_width": 0.2
                    }
                },
                "invalid_example_2": {
                    "summary": "Invalid: Negative petal width",
                    "description": "Shows validation error for negative petal width",
                    "value": {
                        "sepal_length": 5.1,
                        "sepal_width": 3.5,
                        "petal_length": 1.4,
                        "petal_width": -0.5
                    }
                },
                "invalid_example_3": {
                    "summary": "Invalid: Zero sepal length",
                    "description": "Shows validation error for zero sepal length",
                    "value": {
                        "sepal_length": 0.0,
                        "sepal_width": 3.5,
                        "petal_length": 1.4,
                        "petal_width": 0.2
                    }
                },
                "invalid_example_4": {
                    "summary": "Invalid: Unrealistic petal length",
                    "description": "Shows validation error for petal length < 1.0 cm",
                    "value": {
                        "sepal_length": 5.1,
                        "sepal_width": 3.5,
                        "petal_length": 0.5,
                        "petal_width": 0.2
                    }
                }
            }
        }

class RetrainRequest(BaseModel):
    """
    Request model for triggering iris model retraining.
    """
    new_data_path: Optional[str] = Field(
        None,
        description="Path to new training data (optional, uses existing data if not provided)",
        example="data/new_iris_data.csv"
    )

    class Config:
        schema_extra = {
            "example": {
                "new_data_path": "data/new_iris_data.csv"
            }
        }

@app.get("/")
def root():
    return {"message": "Iris prediction API is running."}

@app.post("/predict")
def predict(data: IrisRequest):
    # Create DataFrame
    input_dict = {
        "sepal length (cm)": data.sepal_length,
        "sepal width (cm)": data.sepal_width,
        "petal length (cm)": data.petal_length,
        "petal width (cm)": data.petal_width
    }
    input_df = pd.DataFrame([input_dict])

    # Predict
    prediction = model.predict(input_df)
    predicted_class = int(prediction[0])

    # Log to file
    log_msg = f"Input: {input_dict} | Prediction: {predicted_class}"
    logging.info(log_msg)

    # Log to SQLite
    cursor.execute('''
        INSERT INTO irislogs (timestamp, inputs, prediction)
        VALUES (?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        str(input_dict),
        str(predicted_class)
    ))
    conn.commit()

    return {"predicted_class": predicted_class}

# Renamed to avoid conflict with Prometheus /metrics
@app.get("/app-metrics")
def metrics():
    cursor.execute("SELECT COUNT(*) FROM irislogs")
    total_requests = cursor.fetchone()[0]

    return {
        "total_predictions": total_requests,
        "last_updated": datetime.now().isoformat()
    }

@app.post("/retrain")
def retrain_model(data: RetrainRequest):
    """
    Trigger model retraining with optional new data
    """
    try:
        if data.new_data_path:
            # Import and call the retrain function directly
            sys.path.append('src')
            from retrain_iris import retrain_iris_model
            result = retrain_iris_model(data.new_data_path)
        else:
            # Import and call the retrain function directly
            sys.path.append('src')
            from retrain_iris import retrain_iris_model
            result = retrain_iris_model()
        
        # Reload the model after retraining
        global model
        try:
            model = joblib.load("models/RandomForest.pkl")
        except:
            model = joblib.load("models/LogisticRegression.pkl")
        
        return {
            "message": "Model retraining completed successfully",
            "results": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")

@app.get("/model-info")
def get_model_info():
    """
    Get information about the current model
    """
    try:
        # Try to load retraining results
        if os.path.exists("iris_retrain_results.json"):
            import json
            with open("iris_retrain_results.json", "r") as f:
                retrain_info = json.load(f)
        else:
            retrain_info = {"message": "No retraining history available"}
        
        cursor.execute("SELECT COUNT(*) FROM irislogs")
        total_requests = cursor.fetchone()[0]
        
        return {
            "current_model": "RandomForest.pkl",
            "model_path": "models/RandomForest.pkl",
            "last_retraining": retrain_info,
            "total_predictions": total_requests
        }
    except Exception as e:
        return {"error": f"Could not retrieve model info: {str(e)}"}
