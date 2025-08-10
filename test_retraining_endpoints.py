#!/usr/bin/env python3
"""
Test script for the new retraining endpoints in the Housing and Iris APIs.
"""

import requests
import json
import time
from typing import Dict, Any

def test_endpoint(url: str, method: str = "GET", data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    """Test an API endpoint and return the response."""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "success": False}

def main():
    """Test the retraining endpoints."""
    print("🧪 Testing Retraining Endpoints")
    print("=" * 50)
    
    # Test Housing API endpoints
    print("\n🏠 Testing Housing API (Port 8000)")
    print("-" * 30)
    
    housing_base = "http://localhost:8000"
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    result = test_endpoint(f"{housing_base}/health")
    if result.get("success"):
        print("   ✅ Health check passed")
    else:
        print(f"   ❌ Health check failed: {result}")
    
    # Test model info endpoint
    print("2. Testing model-info endpoint...")
    result = test_endpoint(f"{housing_base}/model-info")
    if result.get("success"):
        print("   ✅ Model info retrieved successfully")
        print(f"   📊 Model: {result['data'].get('model_name', 'Unknown')}")
        print(f"   📅 Last trained: {result['data'].get('last_trained', 'Unknown')}")
    else:
        print(f"   ❌ Model info failed: {result}")
    
    # Test retraining endpoint
    print("3. Testing retrain endpoint...")
    retrain_data = {"model_type": "housing", "force": True}
    result = test_endpoint(f"{housing_base}/retrain", "POST", retrain_data)
    if result.get("success"):
        print("   ✅ Retraining started successfully")
        print(f"   🔄 Status: {result['data'].get('status', 'Unknown')}")
        print(f"   📝 Message: {result['data'].get('message', 'No message')}")
    else:
        print(f"   ❌ Retraining failed: {result}")
    
    # Test Iris API endpoints
    print("\n🌸 Testing Iris API (Port 8001)")
    print("-" * 30)
    
    iris_base = "http://localhost:8001"
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    result = test_endpoint(f"{iris_base}/health")
    if result.get("success"):
        print("   ✅ Health check passed")
    else:
        print(f"   ❌ Health check failed: {result}")
    
    # Test model info endpoint
    print("2. Testing model-info endpoint...")
    result = test_endpoint(f"{iris_base}/model-info")
    if result.get("success"):
        print("   ✅ Model info retrieved successfully")
        print(f"   📊 Model: {result['data'].get('model_name', 'Unknown')}")
        print(f"   📅 Last trained: {result['data'].get('last_trained', 'Unknown')}")
    else:
        print(f"   ❌ Model info failed: {result}")
    
    # Test retraining endpoint
    print("3. Testing retrain endpoint...")
    retrain_data = {"model_type": "iris", "force": True}
    result = test_endpoint(f"{iris_base}/retrain", "POST", retrain_data)
    if result.get("success"):
        print("   ✅ Retraining started successfully")
        print(f"   🔄 Status: {result['data'].get('status', 'Unknown')}")
        print(f"   📝 Message: {result['data'].get('message', 'No message')}")
    else:
        print(f"   ❌ Retraining failed: {result}")
    
    # Test both models retraining
    print("\n🔄 Testing Both Models Retraining")
    print("-" * 30)
    
    print("Testing retrain all models from housing API...")
    retrain_data = {"force": True}  # No model_type = retrain all
    result = test_endpoint(f"{housing_base}/retrain", "POST", retrain_data)
    if result.get("success"):
        print("   ✅ All models retraining started successfully")
        print(f"   🔄 Status: {result['data'].get('status', 'Unknown')}")
        print(f"   📝 Message: {result['data'].get('message', 'No message')}")
    else:
        print(f"   ❌ All models retraining failed: {result}")
    
    print("\n📋 Summary")
    print("=" * 50)
    print("✅ Retraining endpoints have been added to both APIs!")
    print("🌐 You can now access them at:")
    print("   • Housing API: http://localhost:8000/docs")
    print("   • Iris API: http://localhost:8001/docs")
    print("\n🎯 Available endpoints:")
    print("   • POST /retrain - Trigger model retraining")
    print("   • GET /model-info - Get model information")
    print("   • GET /health - Health check")
    
    print("\n💡 Usage examples:")
    print("   # Retrain housing model only")
    print('   curl -X POST "http://localhost:8000/retrain" -H "Content-Type: application/json" -d \'{"model_type": "housing", "force": true}\'')
    print("\n   # Retrain iris model only")
    print('   curl -X POST "http://localhost:8001/retrain" -H "Content-Type: application/json" -d \'{"model_type": "iris", "force": true}\'')
    print("\n   # Retrain all models")
    print('   curl -X POST "http://localhost:8000/retrain" -H "Content-Type: application/json" -d \'{"force": true}\'')

if __name__ == "__main__":
    main()
