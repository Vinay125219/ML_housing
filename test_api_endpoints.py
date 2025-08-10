#!/usr/bin/env python3
"""
Test script to test API endpoints directly without starting a server.
"""

import sys
import json
from fastapi.testclient import TestClient

# Add the current directory to the path so we can import our API modules
sys.path.append('.')

def test_housing_api():
    """Test housing API endpoints."""
    print("🏠 Testing Housing API Endpoints...")
    
    try:
        from api.housing_api import app
        client = TestClient(app)
        
        # Test root endpoint
        print("  📍 Testing root endpoint...")
        response = client.get("/")
        assert response.status_code == 200
        print(f"     ✅ Root endpoint: {response.json()}")
        
        # Test valid prediction
        print("  ✅ Testing valid prediction...")
        valid_data = {
            "total_rooms": 5000.0,
            "total_bedrooms": 1200.0,
            "population": 3000.0,
            "households": 1000.0,
            "median_income": 5.5,
            "housing_median_age": 25.0,
            "latitude": 37.88,
            "longitude": -122.23
        }
        
        response = client.post("/predict", json=valid_data)
        assert response.status_code == 200
        result = response.json()
        print(f"     ✅ Valid prediction: ${result['predicted_price']:.2f} hundred thousands")
        assert "predicted_price" in result
        assert isinstance(result["predicted_price"], (int, float))
        
        # Test invalid prediction (negative income)
        print("  ❌ Testing invalid prediction...")
        invalid_data = valid_data.copy()
        invalid_data["median_income"] = -1.0
        
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422
        error = response.json()
        print(f"     ✅ Correctly rejected invalid input: {error['detail'][0]['msg']}")
        
        # Test metrics endpoint
        print("  📊 Testing metrics endpoint...")
        response = client.get("/app-metrics")
        assert response.status_code == 200
        metrics = response.json()
        print(f"     ✅ Metrics: {metrics}")
        
        print("  🎉 Housing API tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"  💥 Housing API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_iris_api():
    """Test iris API endpoints."""
    print("\n🌸 Testing Iris API Endpoints...")
    
    try:
        from api.main import app
        client = TestClient(app)
        
        # Test root endpoint
        print("  📍 Testing root endpoint...")
        response = client.get("/")
        assert response.status_code == 200
        print(f"     ✅ Root endpoint: {response.json()}")
        
        # Test valid prediction
        print("  ✅ Testing valid prediction...")
        valid_data = {
            "sepal_length": 5.8,
            "sepal_width": 3.0,
            "petal_length": 4.3,
            "petal_width": 1.3
        }
        
        response = client.post("/predict", json=valid_data)
        assert response.status_code == 200
        result = response.json()
        print(f"     ✅ Valid prediction: Class {result['predicted_class']} ({result['class_name']})")
        assert "predicted_class" in result
        assert "class_name" in result
        assert result["predicted_class"] in [0, 1, 2]
        assert result["class_name"] in ["setosa", "versicolor", "virginica"]
        
        # Test invalid prediction (negative sepal length)
        print("  ❌ Testing invalid prediction...")
        invalid_data = valid_data.copy()
        invalid_data["sepal_length"] = -1.0
        
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422
        error = response.json()
        print(f"     ✅ Correctly rejected invalid input: {error['detail'][0]['msg']}")
        
        # Test metrics endpoint
        print("  📊 Testing metrics endpoint...")
        response = client.get("/app-metrics")
        assert response.status_code == 200
        metrics = response.json()
        print(f"     ✅ Metrics: {metrics}")
        
        print("  🎉 Iris API tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"  💥 Iris API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("\n🔬 Testing Edge Cases...")
    
    try:
        from api.housing_api import app as housing_app
        from api.main import app as iris_app
        
        housing_client = TestClient(housing_app)
        iris_client = TestClient(iris_app)
        
        # Test housing edge cases
        print("  🏠 Testing housing edge cases...")
        
        # Boundary values for California
        boundary_data = {
            "total_rooms": 1.0,  # Minimum
            "total_bedrooms": 1.0,  # Minimum
            "population": 1.0,  # Minimum
            "households": 1.0,  # Minimum
            "median_income": 0.1,  # Near minimum
            "housing_median_age": 0.0,  # Minimum
            "latitude": 32.1,  # Near California boundary
            "longitude": -124.0  # Near California boundary
        }
        
        response = housing_client.post("/predict", json=boundary_data)
        if response.status_code == 200:
            print(f"     ✅ Boundary values accepted: ${response.json()['predicted_price']:.2f}")
        else:
            print(f"     ⚠️  Boundary values rejected: {response.status_code}")
        
        # Test iris edge cases
        print("  🌸 Testing iris edge cases...")
        
        # Boundary values for iris
        iris_boundary_data = {
            "sepal_length": 3.0,  # Minimum
            "sepal_width": 1.5,  # Minimum
            "petal_length": 0.5,  # Minimum
            "petal_width": 0.05  # Minimum
        }
        
        response = iris_client.post("/predict", json=iris_boundary_data)
        if response.status_code == 200:
            result = response.json()
            print(f"     ✅ Boundary values accepted: Class {result['predicted_class']} ({result['class_name']})")
        else:
            print(f"     ⚠️  Boundary values rejected: {response.status_code}")
        
        print("  🎉 Edge case tests completed!")
        return True
        
    except Exception as e:
        print(f"  💥 Edge case test failed: {e}")
        return False

def main():
    """Run all API endpoint tests."""
    print("🧪 Starting API Endpoint Tests")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(test_housing_api())
    results.append(test_iris_api())
    results.append(test_edge_cases())
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} test suites passed!")
        print("✅ API endpoints are working correctly with enhanced validation!")
    else:
        print(f"⚠️  {passed}/{total} test suites passed")
        print("❌ Some API tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
