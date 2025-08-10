#!/usr/bin/env python3
"""
Quick Start Script for MLOps Monitoring
This script helps you get your monitoring stack up and running quickly.
"""

import os
import sys
import time
import subprocess
import requests
from typing import Dict, List
import json

class MonitoringStarter:
    """Helper class to start and verify the monitoring stack."""
    
    def __init__(self):
        self.services = {
            'grafana': {'url': 'http://localhost:3000', 'name': 'Grafana Dashboard'},
            'prometheus': {'url': 'http://localhost:9090', 'name': 'Prometheus Metrics'},
            'housing-api': {'url': 'http://localhost:8000', 'name': 'Housing Price API'},
            'iris-api': {'url': 'http://localhost:8001', 'name': 'Iris Classification API'},
            'retraining': {'url': 'http://localhost:8002', 'name': 'Model Retraining Service'},
            'mlflow': {'url': 'http://localhost:5000', 'name': 'MLflow Tracking'}
        }
    
    def print_banner(self):
        """Print welcome banner."""
        print("=" * 60)
        print("🚀 MLOps Monitoring Stack Quick Start")
        print("=" * 60)
        print("This script will help you:")
        print("✅ Start all monitoring services")
        print("✅ Verify everything is working")
        print("✅ Generate sample data")
        print("✅ Open your dashboard")
        print("=" * 60)
    
    def check_docker(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Docker is available")
                return True
            else:
                print("❌ Docker is not available")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Docker is not installed or not in PATH")
            return False
    
    def start_services(self) -> bool:
        """Start all services using docker-compose."""
        print("\n📦 Starting monitoring services...")
        
        try:
            # Check if docker-compose file exists
            if not os.path.exists('docker-compose.monitoring.yml'):
                print("❌ docker-compose.monitoring.yml not found")
                print("   Make sure you're in the project root directory")
                return False
            
            # Start services
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.monitoring.yml', 
                'up', '-d'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Services started successfully")
                return True
            else:
                print(f"❌ Failed to start services: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout starting services (this can take a while)")
            return False
        except FileNotFoundError:
            print("❌ docker-compose not found. Please install Docker Compose")
            return False
    
    def wait_for_services(self, timeout: int = 120) -> Dict[str, bool]:
        """Wait for services to be ready."""
        print("\n⏳ Waiting for services to be ready...")
        
        start_time = time.time()
        service_status = {name: False for name in self.services.keys()}
        
        while time.time() - start_time < timeout:
            all_ready = True
            
            for service_name, service_info in self.services.items():
                if service_status[service_name]:
                    continue  # Already ready
                
                try:
                    # Special handling for different services
                    if service_name == 'grafana':
                        response = requests.get(f"{service_info['url']}/api/health", timeout=5)
                    elif service_name == 'prometheus':
                        response = requests.get(f"{service_info['url']}/-/healthy", timeout=5)
                    else:
                        response = requests.get(f"{service_info['url']}/health", timeout=5)
                    
                    if response.status_code == 200:
                        service_status[service_name] = True
                        print(f"✅ {service_info['name']} is ready")
                    else:
                        all_ready = False
                        
                except requests.exceptions.RequestException:
                    all_ready = False
            
            if all_ready:
                break
            
            time.sleep(5)
            print(".", end="", flush=True)
        
        print()  # New line
        return service_status
    
    def generate_sample_data(self) -> bool:
        """Generate sample data for the dashboard."""
        print("\n📊 Generating sample data...")
        
        try:
            # Check if test script exists
            if os.path.exists('test_api_samples.py'):
                result = subprocess.run([sys.executable, 'test_api_samples.py'], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print("✅ Sample data generated successfully")
                    return True
                else:
                    print(f"⚠️  Test script had issues: {result.stderr}")
                    # Try manual API calls
                    return self.make_manual_api_calls()
            else:
                print("⚠️  test_api_samples.py not found, making manual API calls")
                return self.make_manual_api_calls()
                
        except subprocess.TimeoutExpired:
            print("⚠️  Test script timeout, making manual API calls")
            return self.make_manual_api_calls()
    
    def make_manual_api_calls(self) -> bool:
        """Make manual API calls to generate data."""
        try:
            # Housing API call
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
            
            response = requests.post('http://localhost:8000/predict', 
                                   json=housing_data, timeout=10)
            if response.status_code == 200:
                print("✅ Housing API call successful")
            
            # Iris API call
            iris_data = {
                "sepal_length": 5.8,
                "sepal_width": 3.0,
                "petal_length": 4.3,
                "petal_width": 1.3
            }
            
            response = requests.post('http://localhost:8001/predict', 
                                   json=iris_data, timeout=10)
            if response.status_code == 200:
                print("✅ Iris API call successful")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Manual API calls failed: {e}")
            return False
    
    def print_access_info(self):
        """Print access information for all services."""
        print("\n🌐 Your services are ready! Access them here:")
        print("=" * 60)
        
        for service_name, service_info in self.services.items():
            status = "🟢" if service_name in ['grafana', 'housing-api', 'iris-api'] else "🔵"
            print(f"{status} {service_info['name']}: {service_info['url']}")
        
        print("\n🎯 Quick Actions:")
        print("1. 📊 Open Grafana Dashboard: http://localhost:3000")
        print("   Login: admin / admin")
        print("2. 🏠 Test Housing API: http://localhost:8000/docs")
        print("3. 🌸 Test Iris API: http://localhost:8001/docs")
        print("4. 📈 View Raw Metrics: http://localhost:9090")
        
        print("\n💡 Pro Tips:")
        print("• Bookmark http://localhost:3000 for easy dashboard access")
        print("• Set dashboard auto-refresh to 30s for live monitoring")
        print("• Try the interactive API docs to make test predictions")
        print("• Check the 'MLOps Monitoring Dashboard' in Grafana")
    
    def open_dashboard(self):
        """Try to open the dashboard in the default browser."""
        try:
            import webbrowser
            print("\n🌐 Opening Grafana dashboard in your browser...")
            webbrowser.open('http://localhost:3000')
            time.sleep(2)
            print("✅ Dashboard should open in your browser")
            print("   If not, manually go to: http://localhost:3000")
        except Exception as e:
            print(f"⚠️  Could not auto-open browser: {e}")
            print("   Please manually go to: http://localhost:3000")
    
    def run(self):
        """Run the complete setup process."""
        self.print_banner()
        
        # Check prerequisites
        if not self.check_docker():
            print("\n❌ Please install Docker and try again")
            return False
        
        # Start services
        if not self.start_services():
            print("\n❌ Failed to start services")
            return False
        
        # Wait for services
        service_status = self.wait_for_services()
        ready_count = sum(service_status.values())
        total_count = len(service_status)
        
        print(f"\n📊 Service Status: {ready_count}/{total_count} ready")
        
        if ready_count < 3:  # At least core services should be ready
            print("⚠️  Some services are not ready, but continuing...")
        
        # Generate sample data
        self.generate_sample_data()
        
        # Print access information
        self.print_access_info()
        
        # Try to open dashboard
        self.open_dashboard()
        
        print("\n🎉 Setup complete! Your monitoring stack is ready.")
        print("=" * 60)
        
        return True

def main():
    """Main function."""
    starter = MonitoringStarter()
    success = starter.run()
    
    if success:
        print("\n✅ All done! Enjoy your monitoring dashboard!")
    else:
        print("\n❌ Setup had issues. Check the error messages above.")
        print("   You can try running individual commands manually.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
