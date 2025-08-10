"""
Fix API issues and start both APIs properly
"""

import os
import sys
import subprocess
import time
import signal
from threading import Thread

def create_required_directories():
    """Create all required directories"""
    directories = [
        "data", "models", "housinglogs", "irislogs", 
        "mlruns", "logs", "grafana/dashboards", "grafana/datasources"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_required_files():
    """Check if required model files exist"""
    required_files = [
        "models/DecisionTree.pkl",
        "models/iris_model.pkl"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("⚠️  Missing model files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("   Run model training first: python src/train_and_track.py")
        return False
    
    print("✅ All required model files exist")
    return True

def start_housing_api():
    """Start housing API"""
    print("🏠 Starting Housing API on port 8000...")
    try:
        # Use subprocess.Popen for better control
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "api.housing_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], cwd=os.getcwd())
        
        return process
    except Exception as e:
        print(f"❌ Failed to start Housing API: {e}")
        return None

def start_iris_api():
    """Start iris API"""
    print("🌸 Starting Iris API on port 8001...")
    try:
        # Use subprocess.Popen for better control
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8001",
            "--reload"
        ], cwd=os.getcwd())
        
        return process
    except Exception as e:
        print(f"❌ Failed to start Iris API: {e}")
        return None

def wait_for_api(url, name, timeout=30):
    """Wait for API to be ready"""
    import requests
    
    print(f"⏳ Waiting for {name} to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ {name} is ready!")
                return True
        except:
            pass
        time.sleep(1)
    
    print(f"⚠️  {name} may not be ready yet")
    return False

def test_apis():
    """Test both APIs"""
    import requests
    
    print("\n🧪 Testing APIs...")
    
    # Test Housing API
    try:
        housing_data = {
            "total_rooms": 5000.0,
            "total_bedrooms": 1200.0,
            "population": 3000.0,
            "households": 1000.0,
            "median_income": 5.5,
            "housing_median_age": 25.0,
            "latitude": 37.88,
            "longitude": -122.23
        }
        
        response = requests.post("http://localhost:8000/predict", json=housing_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Housing API test successful! Predicted price: ${result.get('predicted_price', 0) * 100000:,.0f}")
        else:
            print(f"⚠️  Housing API test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Housing API test error: {e}")
    
    # Test Iris API
    try:
        iris_data = {
            "sepal_length": 5.8,
            "sepal_width": 3.0,
            "petal_length": 4.3,
            "petal_width": 1.3
        }
        
        response = requests.post("http://localhost:8001/predict", json=iris_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Iris API test successful! Predicted class: {result.get('class_name', 'Unknown')}")
        else:
            print(f"⚠️  Iris API test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Iris API test error: {e}")

def test_retraining_endpoints():
    """Test retraining endpoints"""
    import requests
    
    print("\n🔄 Testing retraining endpoints...")
    
    # Test Housing API retraining endpoint
    try:
        response = requests.get("http://localhost:8000/model-info", timeout=10)
        if response.status_code == 200:
            print("✅ Housing model-info endpoint working")
        else:
            print(f"⚠️  Housing model-info endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Housing model-info test error: {e}")
    
    # Test Iris API retraining endpoint
    try:
        response = requests.get("http://localhost:8001/model-info", timeout=10)
        if response.status_code == 200:
            print("✅ Iris model-info endpoint working")
        else:
            print(f"⚠️  Iris model-info endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Iris model-info test error: {e}")

def main():
    print("🔧 MLOps API Fixer and Starter")
    print("=" * 40)
    
    # Setup
    create_required_directories()
    
    # Check model files
    if not check_required_files():
        print("\n⚠️  Some model files are missing. Training models first...")
        try:
            subprocess.run([sys.executable, "src/train_and_track.py"], check=True)
            subprocess.run([sys.executable, "src/train_iris.py"], check=True)
            print("✅ Models trained successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Model training failed: {e}")
            print("   You may need to train models manually")
    
    # Start APIs
    print("\n🚀 Starting APIs...")
    housing_process = start_housing_api()
    time.sleep(3)  # Give housing API time to start
    iris_process = start_iris_api()
    
    if not housing_process or not iris_process:
        print("❌ Failed to start one or both APIs")
        return
    
    # Wait for APIs to be ready
    time.sleep(5)
    housing_ready = wait_for_api("http://localhost:8000", "Housing API")
    iris_ready = wait_for_api("http://localhost:8001", "Iris API")
    
    if housing_ready and iris_ready:
        print("\n🎉 Both APIs are running successfully!")
        print("\n🌐 Access your APIs:")
        print("  Housing API: http://localhost:8000/docs")
        print("  Iris API: http://localhost:8001/docs")
        
        # Test APIs
        test_apis()
        test_retraining_endpoints()
        
        print("\n📊 Open your simple dashboard:")
        print("  File: simple_dashboard.html")
        print("  Or run: python -m http.server 8080")
        
        print("\n⏹️  Press Ctrl+C to stop both APIs")
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping APIs...")
            housing_process.terminate()
            iris_process.terminate()
            housing_process.wait()
            iris_process.wait()
            print("✅ APIs stopped successfully")
    else:
        print("❌ APIs failed to start properly")
        if housing_process:
            housing_process.terminate()
        if iris_process:
            iris_process.terminate()

if __name__ == "__main__":
    main()
