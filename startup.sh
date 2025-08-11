#!/bin/bash

# Ensure data directory exists
mkdir -p data

# Ensure models directory exists
mkdir -p models

# Ensure logs directory exists
mkdir -p logs housinglogs

# Ensure MLflow directory exists
mkdir -p mlruns

# Check if data file exists, if not generate it
if [ ! -f "data/housing.csv" ]; then
    echo "Generating housing dataset..."
    python src/load_data.py
fi

# Check if model file exists, if not train it
if [ ! -f "models/DecisionTree.pkl" ]; then
    echo "Training model..."
    python src/train_and_track.py
fi

# Start the API service
echo "Starting API service..."
# Make sure to bind to all interfaces and use the port that's exposed in the container
exec uvicorn api.housing_api:app --host 0.0.0.0 --port 8000 --reload