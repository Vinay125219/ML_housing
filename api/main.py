import sys
import time
from fastapi import FastAPI, HTTPException, Response, BackgroundTasks
from pydantic import BaseModel, Field, validator, ValidationError
from typing import Optional, Dict, Any
import pandas as pd

# import mlflow.pyfunc  # Uncomment if using MLflow
import joblib
import logging
from datetime import datetime
import sqlite3
import os
from prometheus_fastapi_instrumentator import Instrumentator

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from prometheus_metrics import mlops_metrics, get_metrics_handler

# Ensure the log directory exists
os.makedirs("irislogs", exist_ok=True)

# Load MLflow model
# model_uri = "runs:/70968cdab4644053835a226c51eec164/model"
# model = mlflow.pyfunc.load_model(model_uri)

# OR load local model:
model = joblib.load("models/RandomForest.pkl")

# Setup file logging
logging.basicConfig(
    filename="irislogs/predictions.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# SQLite DB setup
conn = sqlite3.connect("irislogs/predictions.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS irislogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    inputs TEXT,
    prediction TEXT
)
"""
)
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
Instrumentator().instrument(app).expose(
    app, include_in_schema=False, endpoint="/metrics"
)


# Add custom metrics endpoint
@app.get("/mlops-metrics")
async def get_mlops_metrics():
    """Get enhanced MLOps metrics."""
    metrics_data = get_metrics_handler()
    return Response(content=metrics_data, media_type="text/plain")


# Expected input features
FEATURE_NAMES = [
    "sepal length (cm)",
    "sepal width (cm)",
    "petal length (cm)",
    "petal width (cm)",
]


class IrisRequest(BaseModel):
    """
    Enhanced Iris Classification Request with comprehensive validation.

    Based on Iris Dataset characteristics:
    - Sepal Length: 4.3-7.9 cm
    - Sepal Width: 2.0-4.4 cm
    - Petal Length: 1.0-6.9 cm
    - Petal Width: 0.1-2.5 cm
    """

    sepal_length: float = Field(
        ...,
        ge=3.0,
        le=10.0,
        description="Sepal length in centimeters. Must be between 3.0 and 10.0 cm (reasonable biological range).",
    )

    sepal_width: float = Field(
        ...,
        ge=1.5,
        le=5.0,
        description="Sepal width in centimeters. Must be between 1.5 and 5.0 cm (reasonable biological range).",
    )

    petal_length: float = Field(
        ...,
        ge=0.5,
        le=8.0,
        description="Petal length in centimeters. Must be between 0.5 and 8.0 cm (reasonable biological range).",
    )

    petal_width: float = Field(
        ...,
        ge=0.05,
        le=3.0,
        description="Petal width in centimeters. Must be between 0.05 and 3.0 cm (reasonable biological range).",
    )

    @validator("petal_width")
    def validate_petal_proportions(cls, v, values):
        """Ensure petal width is reasonable compared to petal length."""
        if "petal_length" in values:
            # Petal width should generally be less than petal length
            if v > values["petal_length"]:
                raise ValueError("Petal width cannot be greater than petal length")
            # Aspect ratio should be reasonable (width/length ratio between 0.01 and 1.0)
            ratio = v / values["petal_length"]
            if ratio < 0.01 or ratio > 1.0:
                raise ValueError(
                    f"Petal width/length ratio ({ratio:.3f}) is unrealistic. Should be between 0.01 and 1.0."
                )
        return v

    @validator("sepal_width")
    def validate_sepal_proportions(cls, v, values):
        """Ensure sepal width is reasonable compared to sepal length."""
        if "sepal_length" in values:
            # Sepal width should generally be less than sepal length
            if v > values["sepal_length"]:
                raise ValueError("Sepal width cannot be greater than sepal length")
            # Aspect ratio should be reasonable (width/length ratio between 0.2 and 1.0)
            ratio = v / values["sepal_length"]
            if ratio < 0.2 or ratio > 1.0:
                raise ValueError(
                    f"Sepal width/length ratio ({ratio:.3f}) is unrealistic. Should be between 0.2 and 1.0."
                )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "sepal_length": 5.8,
                "sepal_width": 3.0,
                "petal_length": 4.3,
                "petal_width": 1.3,
            }
        }


class IrisResponse(BaseModel):
    """Response model for iris classification predictions."""

    predicted_class: int = Field(
        ...,
        ge=0,
        le=2,
        description="Predicted iris class: 0=setosa, 1=versicolor, 2=virginica",
    )
    class_name: str = Field(..., description="Human-readable class name")
    input_validation_passed: bool = Field(
        default=True, description="Whether input validation passed successfully"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "predicted_class": 1,
                "class_name": "versicolor",
                "input_validation_passed": True,
            }
        }


class ValidationErrorResponse(BaseModel):
    """Response model for validation errors."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
    details: Optional[dict] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Input validation failed",
                "details": {
                    "field": "sepal_length",
                    "value": -1.0,
                    "constraint": "must be greater than or equal to 3.0",
                },
            }
        }


class RetrainRequest(BaseModel):
    """Request model for model retraining."""

    model_type: Optional[str] = Field(
        None,
        description="Type of model to retrain: 'housing', 'iris', or None for both",
    )
    force: bool = Field(
        False, description="Force retraining even if performance is acceptable"
    )
    new_data_path: Optional[str] = Field(
        None,
        description="Path to new dataset for retraining (e.g., 'data/new_iris_data.csv'). If not provided, uses built-in iris dataset.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "model_type": "iris",
                "force": True,
                "new_data_path": "data/new_iris_data.csv",
            }
        }


class RetrainResponse(BaseModel):
    """Response model for retraining requests."""

    status: str = Field(..., description="Status of the retraining request")
    message: str = Field(..., description="Detailed message about the retraining")
    task_id: Optional[str] = Field(None, description="Background task ID if applicable")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "started",
                "message": "Model retraining started in background",
                "task_id": "retrain_iris_20231201_143022",
            }
        }


class ModelInfoResponse(BaseModel):
    """Response model for model information."""

    model_name: str = Field(..., description="Name of the model")
    model_type: str = Field(..., description="Type of model (housing/iris)")
    last_trained: Optional[str] = Field(None, description="Last training timestamp")
    performance_metrics: Optional[dict] = Field(
        None, description="Current performance metrics"
    )
    model_path: str = Field(..., description="Path to the model file")

    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "RandomForest",
                "model_type": "iris",
                "last_trained": "2023-12-01T14:30:22",
                "performance_metrics": {"accuracy": 0.95, "f1_score": 0.94},
                "model_path": "models/iris_model.pkl",
            }
        }


@app.get("/")
def root():
    return {"message": "Iris prediction API is running."}


@app.post(
    "/predict",
    response_model=IrisResponse,
    responses={422: {"model": ValidationErrorResponse}},
)
def predict(data: IrisRequest):
    """
    Predict iris species with enhanced input validation.

    This endpoint validates all input parameters according to iris dataset
    characteristics and returns detailed error messages for invalid inputs.
    """
    start_time = time.time()

    try:
        # Create DataFrame
        input_dict = {
            "sepal length (cm)": data.sepal_length,
            "sepal width (cm)": data.sepal_width,
            "petal length (cm)": data.petal_length,
            "petal width (cm)": data.petal_width,
        }
        input_df = pd.DataFrame([input_dict])

        # Additional biological validation
        # Check if measurements are consistent with known iris characteristics
        if data.petal_length < 1.0 and data.petal_width > 0.5:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "ValidationError",
                    "message": "Biological validation failed",
                    "details": {
                        "field": "petal_measurements",
                        "constraint": "Very short petals (< 1.0 cm) typically have narrow width (< 0.5 cm)",
                    },
                },
            )

        # Predict
        prediction = model.predict(input_df)
        predicted_class = int(prediction[0])

        # Validate prediction is within expected range
        if predicted_class < 0 or predicted_class > 2:
            logging.warning(f"Unusual prediction value: {predicted_class}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "PredictionError",
                    "message": "Model returned unexpected class value",
                    "details": {"predicted_class": predicted_class},
                },
            )

        # Map class number to name
        class_names = {0: "setosa", 1: "versicolor", 2: "virginica"}
        class_name = class_names.get(predicted_class, "unknown")

        # Log to file
        log_msg = f"Input: {input_dict} | Prediction: {predicted_class} ({class_name})"
        logging.info(log_msg)

        # Log to SQLite
        cursor.execute(
            """
            INSERT INTO irislogs (timestamp, inputs, prediction)
            VALUES (?, ?, ?)
        """,
            (datetime.now().isoformat(), str(input_dict), str(predicted_class)),
        )
        conn.commit()

        # Record metrics
        prediction_latency = time.time() - start_time
        mlops_metrics.record_prediction(
            model_type="iris",
            model_name="RandomForest",
            prediction_value=float(predicted_class),
            latency=prediction_latency,
        )

        return IrisResponse(predicted_class=predicted_class, class_name=class_name)

    except ValidationError as e:
        logging.error(f"Validation error: {e}")
        mlops_metrics.record_validation_error("iris", "ValidationError")
        raise HTTPException(
            status_code=422,
            detail={
                "error": "ValidationError",
                "message": "Input validation failed",
                "details": str(e),
            },
        )
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        mlops_metrics.record_model_error("iris", "PredictionError")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PredictionError",
                "message": "An error occurred during prediction",
                "details": str(e),
            },
        )


# Renamed to avoid conflict with Prometheus /metrics
@app.get("/app-metrics")
def metrics():
    cursor.execute("SELECT COUNT(*) FROM irislogs")
    total_requests = cursor.fetchone()[0]

    return {
        "total_predictions": total_requests,
        "last_updated": datetime.now().isoformat(),
    }


# Global variable to track retraining status
retraining_status = {"is_running": False, "last_run": None, "last_result": None}


def run_model_retraining(
    model_type: Optional[str] = None,
    force: bool = False,
    new_data_path: Optional[str] = None,
):
    """Background task to run model retraining."""
    global retraining_status

    try:
        retraining_status["is_running"] = True
        start_time = datetime.now()

        # Import retraining functionality
        sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
        from model_retraining import ModelRetrainer, ModelPerformanceMonitor

        # Initialize components
        monitor = ModelPerformanceMonitor()
        retrainer = ModelRetrainer()

        results = {
            "start_time": start_time.isoformat(),
            "model_type": model_type,
            "force": force,
            "results": {},
        }

        # Determine which models to retrain
        models_to_retrain = []
        if model_type == "housing":
            models_to_retrain = ["housing"]
        elif model_type == "iris":
            models_to_retrain = ["iris"]
        else:
            models_to_retrain = ["housing", "iris"]

        # Retrain models
        for model_name in models_to_retrain:
            try:
                if model_name == "iris":
                    # Check if retraining is needed
                    if not force:
                        performance = monitor.evaluate_model_performance("iris")
                        if not performance.get("needs_retraining", False):
                            results["results"]["iris"] = {
                                "status": "skipped",
                                "reason": "performance_acceptable",
                                "performance": performance,
                            }
                            continue

                    # Retrain iris model
                    retrain_result = retrainer.retrain_iris_model(
                        data_path=new_data_path
                    )
                    results["results"]["iris"] = retrain_result

                    # Reload the model in the API
                    global model
                    model = joblib.load("models/iris_model.pkl")

                elif model_name == "housing":
                    # Check if retraining is needed
                    if not force:
                        performance = monitor.evaluate_model_performance("housing")
                        if not performance.get("needs_retraining", False):
                            results["results"]["housing"] = {
                                "status": "skipped",
                                "reason": "performance_acceptable",
                                "performance": performance,
                            }
                            continue

                    # Retrain housing model
                    retrain_result = retrainer.retrain_housing_model()
                    results["results"]["housing"] = retrain_result

            except Exception as e:
                results["results"][model_name] = {"status": "failed", "error": str(e)}

        results["end_time"] = datetime.now().isoformat()
        results["status"] = "completed"

        # Update global status
        retraining_status["last_run"] = start_time.isoformat()
        retraining_status["last_result"] = results

        logging.info(f"Retraining completed: {results}")

    except Exception as e:
        error_result = {
            "status": "failed",
            "error": str(e),
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
        }
        retraining_status["last_result"] = error_result
        logging.error(f"Retraining failed: {e}")

    finally:
        retraining_status["is_running"] = False


@app.post("/retrain", response_model=RetrainResponse)
def retrain_model(request: RetrainRequest, background_tasks: BackgroundTasks):
    """
    Retrain Model

    Trigger model retraining for housing and/or iris models.
    This endpoint starts retraining in the background and returns immediately.
    """
    global retraining_status

    # Check if retraining is already running
    if retraining_status["is_running"]:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "RetrainingInProgress",
                "message": "Model retraining is already in progress",
                "details": {"current_status": retraining_status},
            },
        )

    # Generate task ID
    task_id = f"retrain_{request.model_type or 'all'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Start retraining in background
    background_tasks.add_task(
        run_model_retraining,
        model_type=request.model_type,
        force=request.force,
        new_data_path=request.new_data_path,
    )

    # Log the retraining request
    logging.info(
        f"Retraining requested: model_type={request.model_type}, force={request.force}"
    )

    return RetrainResponse(
        status="started",
        message=f"Model retraining started in background for {request.model_type or 'all models'}",
        task_id=task_id,
    )


@app.get("/model-info", response_model=ModelInfoResponse)
def get_model_info():
    """
    Get Model Info

    Get information about the currently loaded model including performance metrics
    and last training time.
    """
    try:
        # Get model file stats
        model_path = "models/iris_model.pkl"
        model_stats = os.stat(model_path) if os.path.exists(model_path) else None

        # Get performance metrics if available
        performance_metrics = None
        try:
            if os.path.exists("retraining_results.json"):
                import json

                with open("retraining_results.json", "r") as f:
                    results = json.load(f)
                    if "iris" in results and "results" in results["iris"]:
                        performance_metrics = results["iris"]["results"]
        except:
            pass

        return ModelInfoResponse(
            model_name="RandomForest",
            model_type="iris",
            last_trained=(
                datetime.fromtimestamp(model_stats.st_mtime).isoformat()
                if model_stats
                else None
            ),
            performance_metrics=performance_metrics,
            model_path=model_path,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ModelInfoError",
                "message": "Could not retrieve model information",
                "details": str(e),
            },
        )
