"""
Simple script to start both APIs
"""

import subprocess
import sys
import time
import os
from threading import Thread

def start_housing_api():
    """Start housing API"""
    print("🏠 Starting Housing API on port 8000...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.housing_api:app", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("🏠 Housing API stopped")

def start_iris_api():
    """Start iris API"""
    print("🌸 Starting Iris API on port 8001...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8001"
        ], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("🌸 Iris API stopped")

def main():
    print("🚀 Starting MLOps APIs")
    print("=" * 40)
    print("Housing API: http://127.0.0.1:8000/docs")
    print("Iris API: http://127.0.0.1:8001/docs")
    print("Press Ctrl+C to stop both APIs")
    print("=" * 40)
    
    # Start both APIs in separate threads
    housing_thread = Thread(target=start_housing_api, daemon=True)
    iris_thread = Thread(target=start_iris_api, daemon=True)
    
    housing_thread.start()
    time.sleep(2)  # Give housing API time to start
    iris_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping all APIs...")

if __name__ == "__main__":
    main()
