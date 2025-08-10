import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, Union
import pandas as pd
import joblib
import logging
from datetime import datetime
import sqlite3
import subprocess
import sys
from prometheus_fastapi_instrumentator import Instrumentator

# Ensure the log directory exists
os.makedirs("housinglogs", exist_ok=True)

# Load housing model
try:
    model = joblib.load("models/LinearRegression.pkl")
    print("✅ Loaded LinearRegression model successfully")
except Exception as e:
    print(f"⚠️ Could not load LinearRegression model: {e}")
    try:
        model = joblib.load("models/DecisionTree.pkl")
        print("✅ Loaded DecisionTree model successfully")
    except Exception as e2:
        print(f"❌ Could not load any existing housing models: {e2}")
        print("🔄 Please run the training scripts first:")
        print("   python src/train_and_track.py")
        # Create a dummy model for now
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        print("⚠️ Using dummy model - please train proper models first")

# Setup file logging
logging.basicConfig(
    filename='housinglogs/predictions.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# SQLite DB setup
conn = sqlite3.connect("housinglogs/predictions.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS housinglogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    inputs TEXT,
    prediction REAL
)
''')
conn.commit()

# FastAPI setup
app = FastAPI(
    title="MLOps Housing Price Prediction API",
    description="A comprehensive MLOps pipeline for housing price prediction with automated training, deployment, monitoring, and retraining capabilities.",
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

# Expected input features (based on housing.csv)
FEATURE_NAMES = [
    "MedInc", "HouseAge", "AveRooms", "AveBedrms", 
    "Population", "AveOccup", "Latitude", "Longitude"
]

class HousingRequest(BaseModel):
    """
    Housing features for price prediction.
    
    Supports both naming conventions:
    - Standard: MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Latitude, Longitude
    - Alternative: median_income, housing_median_age, total_rooms, total_bedrooms, population, households, latitude, longitude
    
    All features must be within realistic ranges for California housing data.
    """
    # Standard feature names
    MedInc: Optional[float] = Field(
        None, 
        gt=0, 
        ge=0.5, 
        le=15.0,
        description="Median income in block group (in $100,000s)",
        example=8.3252
    )
    HouseAge: Optional[float] = Field(
        None, 
        gt=0, 
        ge=1.0, 
        le=52.0,
        description="Median house age in block group (in years)",
        example=41.0
    )
    AveRooms: Optional[float] = Field(
        None, 
        gt=0, 
        ge=0.8, 
        le=8.0,
        description="Average number of rooms per household",
        example=6.984127
    )
    AveBedrms: Optional[float] = Field(
        None, 
        gt=0, 
        ge=0.5, 
        le=5.0,
        description="Average number of bedrooms per household",
        example=1.023810
    )
    Population: Optional[int] = Field(
        None, 
        gt=0, 
        ge=3, 
        le=35682,
        description="Block group population",
        example=322
    )
    AveOccup: Optional[float] = Field(
        None, 
        gt=0, 
        ge=1.0, 
        le=10.0,
        description="Average number of household members",
        example=2.555556
    )
    
    # Alternative feature names
    median_income: Optional[float] = Field(
        None,
        gt=0,
        ge=0.5,
        le=15.0,
        description="Median income in block group (in $100,000s) - alternative name",
        example=8.3252
    )
    housing_median_age: Optional[float] = Field(
        None,
        gt=0,
        ge=1.0,
        le=52.0,
        description="Median house age in block group (in years) - alternative name",
        example=41.0
    )
    total_rooms: Optional[float] = Field(
        None,
        gt=0,
        ge=0.8,
        le=8.0,
        description="Total number of rooms - alternative name",
        example=6.984127
    )
    total_bedrooms: Optional[float] = Field(
        None,
        gt=0,
        ge=0.5,
        le=5.0,
        description="Total number of bedrooms - alternative name",
        example=1.023810
    )
    households: Optional[float] = Field(
        None,
        gt=0,
        ge=1.0,
        le=10.0,
        description="Number of households - alternative name",
        example=2.555556
    )
    
    # Common features
    Latitude: Optional[float] = Field(
        None, 
        ge=32.54, 
        le=41.95,
        description="Block group latitude (California range)",
        example=37.88
    )
    Longitude: Optional[float] = Field(
        None, 
        ge=-124.35, 
        le=-114.31,
        description="Block group longitude (California range)",
        example=-122.23
    )
    latitude: Optional[float] = Field(
        None,
        ge=32.54,
        le=41.95,
        description="Block group latitude (California range) - alternative name",
        example=37.88
    )
    longitude: Optional[float] = Field(
        None,
        ge=-124.35,
        le=-114.31,
        description="Block group longitude (California range) - alternative name",
        example=-122.23
    )

    @validator('MedInc')
    def validate_med_inc(cls, v):
        if v is not None and (v < 0.5 or v > 15.0):
            raise ValueError(f'Median income {v} is outside valid range [0.5, 15.0] ($100,000s)')
        return v

    @validator('HouseAge')
    def validate_house_age(cls, v):
        if v is not None and (v < 1.0 or v > 52.0):
            raise ValueError(f'House age {v} is outside valid range [1.0, 52.0] years')
        return v

    @validator('AveRooms')
    def validate_ave_rooms(cls, v):
        if v is not None and (v < 0.8 or v > 8.0):
            raise ValueError(f'Average rooms {v} is outside valid range [0.8, 8.0]')
        return v

    @validator('AveBedrms')
    def validate_ave_bedrms(cls, v):
        if v is not None and (v < 0.5 or v > 5.0):
            raise ValueError(f'Average bedrooms {v} is outside valid range [0.5, 5.0]')
        return v

    @validator('Population')
    def validate_population(cls, v):
        if v is not None and (v < 3 or v > 35682):
            raise ValueError(f'Population {v} is outside valid range [3, 35682]')
        return v

    @validator('AveOccup')
    def validate_ave_occup(cls, v):
        if v is not None and (v < 1.0 or v > 10.0):
            raise ValueError(f'Average occupancy {v} is outside valid range [1.0, 10.0]')
        return v

    @validator('Latitude')
    def validate_latitude(cls, v):
        if v is not None and (v < 32.54 or v > 41.95):
            raise ValueError(f'Latitude {v} is outside California range [32.54, 41.95]')
        return v

    @validator('Longitude')
    def validate_longitude(cls, v):
        if v is not None and (v < -124.35 or v > -114.31):
            raise ValueError(f'Longitude {v} is outside California range [-124.35, -114.31]')
        return v

    @validator('median_income')
    def validate_median_income(cls, v):
        if v is not None and (v < 0.5 or v > 15.0):
            raise ValueError(f'Median income {v} is outside valid range [0.5, 15.0] ($100,000s)')
        return v

    @validator('housing_median_age')
    def validate_housing_median_age(cls, v):
        if v is not None and (v < 1.0 or v > 52.0):
            raise ValueError(f'Housing median age {v} is outside valid range [1.0, 52.0] years')
        return v

    @validator('total_rooms')
    def validate_total_rooms(cls, v):
        if v is not None and (v < 0.8 or v > 8.0):
            raise ValueError(f'Total rooms {v} is outside valid range [0.8, 8.0]')
        return v

    @validator('total_bedrooms')
    def validate_total_bedrooms(cls, v):
        if v is not None and (v < 0.5 or v > 5.0):
            raise ValueError(f'Total bedrooms {v} is outside valid range [0.5, 5.0]')
        return v

    @validator('households')
    def validate_households(cls, v):
        if v is not None and (v < 1.0 or v > 10.0):
            raise ValueError(f'Households {v} is outside valid range [1.0, 10.0]')
        return v

    @validator('latitude')
    def validate_latitude_alt(cls, v):
        if v is not None and (v < 32.54 or v > 41.95):
            raise ValueError(f'Latitude {v} is outside California range [32.54, 41.95]')
        return v

    @validator('longitude')
    def validate_longitude_alt(cls, v):
        if v is not None and (v < -124.35 or v > -114.31):
            raise ValueError(f'Longitude {v} is outside California range [-124.35, -114.31]')
        return v

    @validator('*')
    def validate_at_least_one_set(cls, v, values):
        """Ensure at least one set of features is provided"""
        # Check if we have at least one complete set of features
        standard_features = ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude']
        alternative_features = ['median_income', 'housing_median_age', 'total_rooms', 'total_bedrooms', 'population', 'households', 'latitude', 'longitude']
        
        standard_count = sum(1 for f in standard_features if values.get(f) is not None)
        alternative_count = sum(1 for f in alternative_features if values.get(f) is not None)
        
        if standard_count == 0 and alternative_count == 0:
            raise ValueError('At least one set of features must be provided')
        
        return v

    class Config:
        schema_extra = {
            "example": {
                "MedInc": 8.3252,
                "HouseAge": 41.0,
                "AveRooms": 6.984127,
                "AveBedrms": 1.023810,
                "Population": 322,
                "AveOccup": 2.555556,
                "Latitude": 37.88,
                "Longitude": -122.23
            },
            "examples": {
                "valid_high_value": {
                    "summary": "High-value housing area",
                    "description": "Typical measurements for expensive California housing",
                    "value": {
                        "MedInc": 12.5,
                        "HouseAge": 25.0,
                        "AveRooms": 7.5,
                        "AveBedrms": 3.2,
                        "Population": 1500,
                        "AveOccup": 2.8,
                        "Latitude": 37.88,
                        "Longitude": -122.23
                    }
                },
                "valid_affordable": {
                    "summary": "Affordable housing area",
                    "description": "Typical measurements for affordable California housing",
                    "value": {
                        "MedInc": 3.2,
                        "HouseAge": 35.0,
                        "AveRooms": 5.2,
                        "AveBedrms": 2.1,
                        "Population": 2500,
                        "AveOccup": 3.1,
                        "Latitude": 36.75,
                        "Longitude": -119.79
                    }
                },
                "invalid_example_1": {
                    "summary": "Invalid: Out of range median income",
                    "description": "Shows validation error for median income > 15.0",
                    "value": {
                        "MedInc": 20.0,
                        "HouseAge": 41.0,
                        "AveRooms": 6.984127,
                        "AveBedrms": 1.023810,
                        "Population": 322,
                        "AveOccup": 2.555556,
                        "Latitude": 37.88,
                        "Longitude": -122.23
                    }
                },
                "invalid_example_2": {
                    "summary": "Invalid: Out of California latitude range",
                    "description": "Shows validation error for latitude outside California",
                    "value": {
                        "MedInc": 8.3252,
                        "HouseAge": 41.0,
                        "AveRooms": 6.984127,
                        "AveBedrms": 1.023810,
                        "Population": 322,
                        "AveOccup": 2.555556,
                        "Latitude": 45.0,
                        "Longitude": -122.23
                    }
                }
            }
        }

class RetrainRequest(BaseModel):
    """
    Request model for triggering housing model retraining.
    """
    new_data_path: Optional[str] = Field(
        None,
        description="Path to new training data (optional, uses existing data if not provided)",
        example="data/new_housing_data.csv"
    )

    class Config:
        schema_extra = {
            "example": {
                "new_data_path": "data/new_housing_data.csv"
            }
        }

@app.get("/")
def root():
    return {"message": "Housing price prediction API is running."}

@app.post("/predict")
def predict(data: HousingRequest):
    # Create DataFrame - handle both naming conventions
    if data.MedInc is not None:
        # Standard naming convention
        input_dict = {
            "MedInc": data.MedInc,
            "HouseAge": data.HouseAge,
            "AveRooms": data.AveRooms,
            "AveBedrms": data.AveBedrms,
            "Population": data.Population,
            "AveOccup": data.AveOccup,
            "Latitude": data.Latitude,
            "Longitude": data.Longitude
        }
    else:
        # Alternative naming convention
        input_dict = {
            "MedInc": data.median_income,
            "HouseAge": data.housing_median_age,
            "AveRooms": data.total_rooms,
            "AveBedrms": data.total_bedrooms,
            "Population": data.population,
            "AveOccup": data.households,
            "Latitude": data.latitude or data.Latitude,
            "Longitude": data.longitude or data.Longitude
        }
    
    input_df = pd.DataFrame([input_dict])

    # Predict
    prediction = model.predict(input_df)
    predicted_price = float(prediction[0])

    # Log to file
    log_msg = f"Input: {input_dict} | Prediction: ${predicted_price:,.2f}"
    logging.info(log_msg)

    # Log to SQLite
    cursor.execute('''
        INSERT INTO housinglogs (timestamp, inputs, prediction)
        VALUES (?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        str(input_dict),
        predicted_price
    ))
    conn.commit()

    return {
        "predicted_price": predicted_price,
        "predicted_price_formatted": f"${predicted_price:,.2f}"
    }

@app.get("/app-metrics")
def metrics():
    cursor.execute("SELECT COUNT(*) FROM housinglogs")
    total_requests = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(prediction) FROM housinglogs")
    avg_prediction = cursor.fetchone()[0] or 0

    return {
        "total_predictions": total_requests,
        "average_predicted_price": avg_prediction,
        "last_updated": datetime.now().isoformat()
    }

@app.post("/retrain")
def retrain_model(data: RetrainRequest):
    """
    Trigger housing model retraining with optional new data
    """
    try:
        if data.new_data_path:
            # Import and call the retrain function directly
            sys.path.append('src')
            from retrain_housing import retrain_housing_model
            result = retrain_housing_model(data.new_data_path)
        else:
            # Import and call the retrain function directly
            sys.path.append('src')
            from retrain_housing import retrain_housing_model
            result = retrain_housing_model()
        
        # Reload the model after retraining
        global model
        try:
            model = joblib.load("models/LinearRegression.pkl")
        except:
            model = joblib.load("models/DecisionTree.pkl")
        
        return {
            "message": "Housing model retraining completed successfully",
            "results": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")

@app.get("/model-info")
def get_model_info():
    """
    Get information about the current housing model
    """
    try:
        # Try to load retraining results
        if os.path.exists("../retrain_results.json"):
            import json
            with open("../retrain_results.json", "r") as f:
                retrain_info = json.load(f)
        else:
            retrain_info = {"message": "No retraining history available"}
        
        cursor.execute("SELECT COUNT(*) FROM housinglogs")
        total_requests = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(prediction) FROM housinglogs")
        avg_prediction = cursor.fetchone()[0] or 0
        
        return {
            "current_model": "LinearRegression.pkl",
            "model_path": "models/LinearRegression.pkl",
            "last_retraining": retrain_info,
            "total_predictions": total_requests,
            "average_predicted_price": avg_prediction
        }
    except Exception as e:
        return {"error": f"Could not retrieve model info: {str(e)}"}

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring
    """
    try:
        # Test model prediction with sample data
        sample_data = pd.DataFrame([{
            "MedInc": 8.3252,
            "HouseAge": 41.0,
            "AveRooms": 6.984127,
            "AveBedrms": 1.023810,
            "Population": 322,
            "AveOccup": 2.555556,
            "Latitude": 37.88,
            "Longitude": -122.23
        }])
        
        prediction = model.predict(sample_data)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "model_loaded": True,
            "prediction_test": float(prediction[0]),
            "database_connection": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
