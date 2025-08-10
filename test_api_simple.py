#!/usr/bin/env python3
"""
Simple test to check if APIs can start without issues
"""

import sys
import os

def test_housing_api():
    """Test if housing API can be imported and started"""
    try:
        print("Testing housing API import...")
        
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        # Try importing the housing API
        from api.housing_api import app
        print("✅ Housing API imported successfully")
        
        # Check if the app has the expected endpoints
        routes = [route.path for route in app.routes]
        print(f"📍 Available routes: {routes}")
        
        # Check for retraining endpoint
        if "/retrain" in routes:
            print("✅ Retraining endpoint found")
        else:
            print("❌ Retraining endpoint NOT found")
            
        return True
        
    except Exception as e:
        print(f"❌ Housing API import failed: {e}")
        return False

def test_iris_api():
    """Test if iris API can be imported and started"""
    try:
        print("\nTesting iris API import...")
        
        # Try importing the iris API
        from api.main import app as iris_app
        print("✅ Iris API imported successfully")
        
        # Check if the app has the expected endpoints
        routes = [route.path for route in iris_app.routes]
        print(f"📍 Available routes: {routes}")
        
        # Check for retraining endpoint
        if "/retrain" in routes:
            print("✅ Retraining endpoint found")
        else:
            print("❌ Retraining endpoint NOT found")
            
        return True
        
    except Exception as e:
        print(f"❌ Iris API import failed: {e}")
        return False

def main():
    print("🧪 Testing API Imports")
    print("=" * 40)
    
    housing_ok = test_housing_api()
    iris_ok = test_iris_api()
    
    print("\n📊 Summary:")
    print(f"Housing API: {'✅ OK' if housing_ok else '❌ FAILED'}")
    print(f"Iris API: {'✅ OK' if iris_ok else '❌ FAILED'}")
    
    if housing_ok and iris_ok:
        print("\n🎉 Both APIs can be imported successfully!")
        print("You can now start them with:")
        print("  uvicorn api.housing_api:app --host 127.0.0.1 --port 8000")
        print("  uvicorn api.main:app --host 127.0.0.1 --port 8001")
    else:
        print("\n⚠️  Some APIs have import issues. Check the errors above.")

if __name__ == "__main__":
    main()
