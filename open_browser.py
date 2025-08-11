#!/usr/bin/env python3
"""
Browser auto-open script for Streamlit MLOps dashboard
"""

import time
import webbrowser
import requests
import sys
import os

def wait_for_service(url, max_attempts=30, delay=2):
    """Wait for a service to become available"""
    print(f"Waiting for {url} to become available...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} is now available!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"Attempt {attempt + 1}/{max_attempts} - Service not ready yet, waiting...")
        time.sleep(delay)
    
    print(f"❌ {url} did not become available within {max_attempts * delay} seconds")
    return False

def open_all_services():
    """Open all MLOps services in browser"""
    
    services = {
        "Streamlit Dashboard": "http://localhost:8501",
        "Housing API Docs": "http://localhost:8000/docs", 
        "MLflow Tracking": "http://localhost:5000",
        "Grafana Dashboard": "http://localhost:3001",
        "Prometheus": "http://localhost:9090"
    }
    
    print("🚀 Opening MLOps Pipeline Services...")
    print("=" * 50)
    
    # Wait for key services first
    key_services = [
        "http://localhost:8501",  # Streamlit
        "http://localhost:8000/health",  # Housing API
    ]
    
    for service_url in key_services:
        if not wait_for_service(service_url):
            print(f"⚠️  Warning: {service_url} is not responding")
    
    # Open all services in browser
    time.sleep(2)  # Give services a moment to fully initialize
    
    for service_name, url in services.items():
        try:
            print(f"🌐 Opening {service_name}: {url}")
            webbrowser.open(url)
            time.sleep(1)  # Stagger browser openings
        except Exception as e:
            print(f"❌ Could not open {service_name}: {e}")
    
    print("\n✅ All services should now be open in your browser!")
    print("\n📝 Default credentials:")
    print("   Grafana: admin / admin")
    print("\n🔗 Service URLs:")
    for service_name, url in services.items():
        print(f"   {service_name}: {url}")

if __name__ == "__main__":
    try:
        open_all_services()
    except KeyboardInterrupt:
        print("\n\n❌ Browser opening cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error opening services: {e}")
        sys.exit(1)
