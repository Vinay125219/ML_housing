"""
Startup script for the MLOps API
Ensures all required directories exist and starts the API server
"""

import os
import sys
import subprocess

def ensure_directories():
    """Create all required directories if they don't exist"""
    directories = [
        "data",
        "models", 
        "housinglogs",
        "irislogs",
        "mlruns"
    ]
    
    print("🔧 Creating required directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}/")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pandas
        import sklearn
        import mlflow
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_housing_api():
    """Start the housing prediction API"""
    print("\n🚀 Starting Housing Price Prediction API...")
    print("   API will be available at: http://localhost:8000")
    print("   Documentation at: http://localhost:8000/docs")
    print("   Press Ctrl+C to stop\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.housing_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 API stopped by user")

def start_iris_api():
    """Start the iris classification API"""
    print("\n🚀 Starting Iris Classification API...")
    print("   API will be available at: http://localhost:8000")
    print("   Documentation at: http://localhost:8000/docs")
    print("   Press Ctrl+C to stop\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 API stopped by user")

if __name__ == "__main__":
    print("🏗️  MLOps API Startup Script")
    print("=" * 40)
    
    # Ensure directories exist
    ensure_directories()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Ask user which API to start
    print("\nWhich API would you like to start?")
    print("1. Housing Price Prediction API")
    print("2. Iris Classification API")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        start_housing_api()
    elif choice == "2":
        start_iris_api()
    else:
        print("❌ Invalid choice. Please run the script again.")
