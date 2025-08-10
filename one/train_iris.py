import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
import mlflow
from mlflow.models.signature import infer_signature
from mlflow.tracking import MlflowClient
import joblib
import os
from pydantic import BaseModel, Field, validator
from typing import List, Union
import numpy as np

# Set up MLflow - use ../mlruns to create in project root
mlflow.set_tracking_uri("file:../mlruns")
mlflow.set_experiment("iris_classification")

class IrisDataValidator(BaseModel):
    """
    Validator for Iris dataset features.
    
    Ensures data quality before training by validating:
    - Feature ranges are within expected bounds
    - No missing values
    - Proper data types
    """
    sepal_length: float = Field(..., ge=4.0, le=8.0, description="Sepal length in cm")
    sepal_width: float = Field(..., ge=2.0, le=5.0, description="Sepal width in cm")
    petal_length: float = Field(..., ge=1.0, le=7.0, description="Petal length in cm")
    petal_width: float = Field(..., ge=0.1, le=3.0, description="Petal width in cm")
    target: int = Field(..., ge=0, le=2, description="Target class (0=Setosa, 1=Versicolor, 2=Virginica)")

    @validator('sepal_length')
    def validate_sepal_length(cls, v):
        if v < 4.0 or v > 8.0:
            raise ValueError(f'Sepal length {v} is outside valid range [4.0, 8.0] cm')
        return v

    @validator('sepal_width')
    def validate_sepal_width(cls, v):
        if v < 2.0 or v > 5.0:
            raise ValueError(f'Sepal width {v} is outside valid range [2.0, 5.0] cm')
        return v

    @validator('petal_length')
    def validate_petal_length(cls, v):
        if v < 1.0 or v > 7.0:
            raise ValueError(f'Petal length {v} is outside valid range [1.0, 7.0] cm')
        return v

    @validator('petal_width')
    def validate_petal_width(cls, v):
        if v < 0.1 or v > 3.0:
            raise ValueError(f'Petal width {v} is outside valid range [0.1, 3.0] cm')
        return v

    @validator('target')
    def validate_target(cls, v):
        if v not in [0, 1, 2]:
            raise ValueError(f'Target {v} must be 0, 1, or 2')
        return v

    class Config:
        schema_extra = {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
                "target": 0
            },
            "examples": {
                "valid_setosa": {
                    "summary": "Valid Setosa flower data",
                    "description": "Typical measurements for Iris Setosa",
                    "value": {
                        "sepal_length": 5.1,
                        "sepal_width": 3.5,
                        "petal_length": 1.4,
                        "petal_width": 0.2,
                        "target": 0
                    }
                },
                "valid_versicolor": {
                    "summary": "Valid Versicolor flower data",
                    "description": "Typical measurements for Iris Versicolor",
                    "value": {
                        "sepal_length": 6.4,
                        "sepal_width": 3.2,
                        "petal_length": 4.5,
                        "petal_width": 1.5,
                        "target": 1
                    }
                },
                "valid_virginica": {
                    "summary": "Valid Virginica flower data",
                    "description": "Typical measurements for Iris Virginica",
                    "value": {
                        "sepal_length": 6.3,
                        "sepal_width": 3.3,
                        "petal_length": 6.0,
                        "petal_width": 2.5,
                        "target": 2
                    }
                },
                "invalid_example_1": {
                    "summary": "Invalid: Out of range sepal length",
                    "description": "Shows validation error for sepal length > 8.0 cm",
                    "value": {
                        "sepal_length": 9.0,
                        "sepal_width": 3.5,
                        "petal_length": 1.4,
                        "petal_width": 0.2,
                        "target": 0
                    }
                },
                "invalid_example_2": {
                    "summary": "Invalid: Negative petal width",
                    "description": "Shows validation error for negative petal width",
                    "value": {
                        "sepal_length": 5.1,
                        "sepal_width": 3.5,
                        "petal_length": 1.4,
                        "petal_width": -0.5,
                        "target": 0
                    }
                },
                "invalid_example_3": {
                    "summary": "Invalid: Invalid target class",
                    "description": "Shows validation error for target class 5",
                    "value": {
                        "sepal_length": 5.1,
                        "sepal_width": 3.5,
                        "petal_length": 1.4,
                        "petal_width": 0.2,
                        "target": 5
                    }
                }
            }
        }

def validate_iris_dataframe(df: pd.DataFrame) -> bool:
    """
    Validate the entire iris dataframe before training.
    
    Args:
        df: DataFrame containing iris data
        
    Returns:
        bool: True if validation passes, raises ValueError otherwise
        
    Raises:
        ValueError: If validation fails with specific error details
    """
    print("🔍 Validating iris dataset...")
    
    # Check for missing values
    if df.isnull().any().any():
        missing_cols = df.columns[df.isnull().any()].tolist()
        raise ValueError(f"Missing values found in columns: {missing_cols}")
    
    # Check data types
    expected_dtypes = {
        'sepal_length': 'float64',
        'sepal_width': 'float64', 
        'petal_length': 'float64',
        'petal_width': 'float64',
        'target': 'int64'
    }
    
    for col, expected_type in expected_dtypes.items():
        if col in df.columns:
            if str(df[col].dtype) != expected_type:
                raise ValueError(f"Column {col} has type {df[col].dtype}, expected {expected_type}")
    
    # Check feature ranges
    feature_ranges = {
        'sepal_length': (4.0, 8.0),
        'sepal_width': (2.0, 5.0),
        'petal_length': (1.0, 7.0),
        'petal_width': (0.1, 3.0)
    }
    
    for feature, (min_val, max_val) in feature_ranges.items():
        if feature in df.columns:
            if df[feature].min() < min_val or df[feature].max() > max_val:
                raise ValueError(f"Feature {feature} has values outside range [{min_val}, {max_val}]")
    
    # Check target values
    if 'target' in df.columns:
        valid_targets = [0, 1, 2]
        invalid_targets = df[~df['target'].isin(valid_targets)]['target'].unique()
        if len(invalid_targets) > 0:
            raise ValueError(f"Invalid target values found: {invalid_targets}")
    
    # Check for reasonable data distribution
    if 'target' in df.columns:
        target_counts = df['target'].value_counts()
        if len(target_counts) < 2:
            raise ValueError("Dataset must contain at least 2 classes for classification")
        
        min_samples_per_class = target_counts.min()
        if min_samples_per_class < 10:
            print(f"⚠️ Warning: Some classes have very few samples (minimum: {min_samples_per_class})")
    
    print("✅ Iris dataset validation passed!")
    return True

def validate_single_iris_sample(sample_data: dict) -> dict:
    """
    Validate a single iris sample using Pydantic.
    
    Args:
        sample_data: Dictionary containing iris measurements
        
    Returns:
        dict: Validated data
        
    Raises:
        ValueError: If validation fails
    """
    try:
        validated = IrisDataValidator(**sample_data)
        return validated.dict()
    except Exception as e:
        raise ValueError(f"Sample validation failed: {str(e)}")

# Load and validate data
print("📊 Loading iris dataset...")
data = load_iris(as_frame=True)
df = data.frame

# Validate the dataset
try:
    validate_iris_dataframe(df)
except ValueError as e:
    print(f"❌ Dataset validation failed: {e}")
    exit(1)

X = df.drop("target", axis=1)
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.5, random_state=42
)

# Create models directory if not exists (in project root)
os.makedirs("../models", exist_ok=True)

# Store model performance for comparison
model_performance = {}

def train_and_log_model(model, model_name):
    with mlflow.start_run(run_name=model_name) as run:
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="weighted")

        mlflow.log_param("model_name", model_name)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)

        signature = infer_signature(X_test, preds)
        input_example = X_test.head(2)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            input_example=input_example,
            signature=signature
        )

        # Save locally - use ../models to save in project root
        joblib.dump(model, f"../models/{model_name}.pkl")

        print(f"✅ {model_name} | Accuracy: {acc:.3f} | F1 Score: {f1:.3f} | Saved to ../models/{model_name}.pkl")
        
        # Store performance for comparison
        model_performance[model_name] = {
            'accuracy': acc,
            'f1': f1,
            'run_id': run.info.run_id
        }

# Train models
train_and_log_model(LogisticRegression(max_iter=200), "LogisticRegression")
train_and_log_model(RandomForestClassifier(n_estimators=100), "RandomForest")

# Register the best model based on performance
print("\n📊 Model Performance Comparison:")
print("=" * 40)
for model_name, metrics in model_performance.items():
    print(f"{model_name}: Accuracy={metrics['accuracy']:.3f}, F1={metrics['f1']:.3f}")

# Find the best model (higher accuracy and F1)
best_model_name = max(model_performance.keys(), key=lambda x: (model_performance[x]['accuracy'], model_performance[x]['f1']))
best_metrics = model_performance[best_model_name]

print(f"\n🏆 Best Model: {best_model_name}")
print(f"   Accuracy: {best_metrics['accuracy']:.3f}")
print(f"   F1 Score: {best_metrics['f1']:.3f}")

# Register the best model
try:
    registered_model = mlflow.register_model(
        model_uri=f"runs:/{best_metrics['run_id']}/model",
        name="IrisClassifier"
    )
    print(f"✅ Successfully registered 'IrisClassifier' model (version {registered_model.version})")
except Exception as e:
    print(f"⚠️  IrisClassifier already registered or error: {e}")

# Example usage of validation functions
if __name__ == "__main__":
    print("\n🧪 Testing validation functions...")
    
    # Test valid sample
    valid_sample = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
        "target": 0
    }
    
    try:
        validated = validate_single_iris_sample(valid_sample)
        print(f"✅ Valid sample validation passed: {validated}")
    except ValueError as e:
        print(f"❌ Valid sample validation failed: {e}")
    
    # Test invalid sample
    invalid_sample = {
        "sepal_length": 9.0,  # Out of range
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
        "target": 0
    }
    
    try:
        validated = validate_single_iris_sample(invalid_sample)
        print(f"✅ Invalid sample validation passed (unexpected): {validated}")
    except ValueError as e:
        print(f"✅ Invalid sample validation correctly failed: {e}")
    
    print("\n🎯 Validation testing completed!")
