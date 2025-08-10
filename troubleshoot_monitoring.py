#!/usr/bin/env python3
"""
Troubleshooting Script for MLOps Monitoring
This script helps diagnose and fix common issues with the monitoring stack.
"""

import os
import sys
import subprocess
import requests
import time
from typing import Dict, List, Tuple

class MonitoringTroubleshooter:
    """Helper class to troubleshoot monitoring issues."""
    
    def __init__(self):
        self.services = {
            'grafana': {'url': 'http://localhost:3000', 'port': 3000},
            'prometheus': {'url': 'http://localhost:9090', 'port': 9090},
            'housing-api': {'url': 'http://localhost:8000', 'port': 8000},
            'iris-api': {'url': 'http://localhost:8001', 'port': 8001},
            'retraining': {'url': 'http://localhost:8002', 'port': 8002},
            'mlflow': {'url': 'http://localhost:5000', 'port': 5000}
        }
    
    def print_banner(self):
        """Print troubleshooting banner."""
        print("=" * 60)
        print("🔧 MLOps Monitoring Troubleshooter")
        print("=" * 60)
        print("This script will help diagnose common issues:")
        print("🔍 Check service status")
        print("🔍 Test network connectivity")
        print("🔍 Verify configurations")
        print("🔍 Suggest fixes")
        print("=" * 60)
    
    def check_docker_status(self) -> Tuple[bool, str]:
        """Check if Docker is running."""
        try:
            result = subprocess.run(['docker', 'info'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return True, "Docker is running"
            else:
                return False, f"Docker error: {result.stderr}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "Docker is not installed or not running"
    
    def check_compose_file(self) -> Tuple[bool, str]:
        """Check if docker-compose file exists and is valid."""
        if not os.path.exists('docker-compose.monitoring.yml'):
            return False, "docker-compose.monitoring.yml not found"
        
        try:
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.monitoring.yml', 
                'config'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, "Docker compose file is valid"
            else:
                return False, f"Docker compose file error: {result.stderr}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "docker-compose not found or timeout"
    
    def check_container_status(self) -> Dict[str, Dict]:
        """Check status of all containers."""
        try:
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.monitoring.yml', 
                'ps'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {}
            
            # Parse container status
            lines = result.stdout.strip().split('\n')[2:]  # Skip header
            container_status = {}
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        name = parts[0]
                        state = parts[-1]
                        container_status[name] = {
                            'status': state,
                            'running': 'Up' in state
                        }
            
            return container_status
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {}
    
    def check_port_availability(self) -> Dict[str, bool]:
        """Check if required ports are available."""
        import socket
        
        port_status = {}
        for service, info in self.services.items():
            port = info['port']
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            port_status[service] = result == 0
            sock.close()
        
        return port_status
    
    def check_service_health(self) -> Dict[str, Dict]:
        """Check health of all services."""
        health_status = {}
        
        for service, info in self.services.items():
            try:
                # Different health check endpoints
                if service == 'grafana':
                    response = requests.get(f"{info['url']}/api/health", timeout=5)
                elif service == 'prometheus':
                    response = requests.get(f"{info['url']}/-/healthy", timeout=5)
                else:
                    response = requests.get(f"{info['url']}/health", timeout=5)
                
                health_status[service] = {
                    'healthy': response.status_code == 200,
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
                
            except requests.exceptions.RequestException as e:
                health_status[service] = {
                    'healthy': False,
                    'error': str(e),
                    'response_time': None
                }
        
        return health_status
    
    def check_metrics_availability(self) -> Dict[str, bool]:
        """Check if metrics endpoints are working."""
        metrics_status = {}
        
        # Check Prometheus metrics
        try:
            response = requests.get('http://localhost:9090/api/v1/query?query=up', timeout=10)
            metrics_status['prometheus'] = response.status_code == 200
        except:
            metrics_status['prometheus'] = False
        
        # Check API metrics
        for api in ['housing-api', 'iris-api']:
            try:
                url = f"http://localhost:{self.services[api]['port']}/mlops-metrics"
                response = requests.get(url, timeout=10)
                metrics_status[api] = response.status_code == 200
            except:
                metrics_status[api] = False
        
        return metrics_status
    
    def suggest_fixes(self, issues: List[str]) -> List[str]:
        """Suggest fixes for common issues."""
        fixes = []
        
        if "Docker is not running" in str(issues):
            fixes.append("🔧 Start Docker Desktop or Docker daemon")
            fixes.append("   Windows: Start Docker Desktop application")
            fixes.append("   Linux: sudo systemctl start docker")
        
        if "docker-compose.monitoring.yml not found" in str(issues):
            fixes.append("🔧 Make sure you're in the project root directory")
            fixes.append("   cd /path/to/mlops-housing-pipeline")
        
        if "containers not running" in str(issues):
            fixes.append("🔧 Start the services:")
            fixes.append("   docker-compose -f docker-compose.monitoring.yml up -d")
        
        if "port conflicts" in str(issues):
            fixes.append("🔧 Stop conflicting services or change ports")
            fixes.append("   Check what's using the ports: netstat -an | findstr :3000")
        
        if "services not healthy" in str(issues):
            fixes.append("🔧 Wait a few minutes for services to start")
            fixes.append("🔧 Check logs: docker-compose -f docker-compose.monitoring.yml logs")
            fixes.append("🔧 Restart services: docker-compose -f docker-compose.monitoring.yml restart")
        
        if "no metrics" in str(issues):
            fixes.append("🔧 Generate some data: python test_api_samples.py")
            fixes.append("🔧 Check Prometheus targets: http://localhost:9090/targets")
        
        return fixes
    
    def run_diagnostics(self):
        """Run complete diagnostics."""
        print("\n🔍 Running diagnostics...\n")
        
        issues = []
        
        # Check Docker
        docker_ok, docker_msg = self.check_docker_status()
        if docker_ok:
            print(f"✅ {docker_msg}")
        else:
            print(f"❌ {docker_msg}")
            issues.append(docker_msg)
        
        # Check compose file
        compose_ok, compose_msg = self.check_compose_file()
        if compose_ok:
            print(f"✅ {compose_msg}")
        else:
            print(f"❌ {compose_msg}")
            issues.append(compose_msg)
        
        # Check containers
        print("\n📦 Container Status:")
        container_status = self.check_container_status()
        if container_status:
            for name, status in container_status.items():
                if status['running']:
                    print(f"✅ {name}: {status['status']}")
                else:
                    print(f"❌ {name}: {status['status']}")
                    issues.append(f"Container {name} not running")
        else:
            print("❌ Could not get container status")
            issues.append("containers not running")
        
        # Check ports
        print("\n🔌 Port Availability:")
        port_status = self.check_port_availability()
        for service, available in port_status.items():
            port = self.services[service]['port']
            if available:
                print(f"✅ {service}: Port {port} is accessible")
            else:
                print(f"❌ {service}: Port {port} is not accessible")
                issues.append(f"Port {port} not accessible")
        
        # Check service health
        print("\n🏥 Service Health:")
        health_status = self.check_service_health()
        for service, health in health_status.items():
            if health.get('healthy', False):
                rt = health.get('response_time', 0)
                print(f"✅ {service}: Healthy (response: {rt:.2f}s)")
            else:
                error = health.get('error', 'Unknown error')
                print(f"❌ {service}: Unhealthy - {error}")
                issues.append(f"Service {service} unhealthy")
        
        # Check metrics
        print("\n📊 Metrics Availability:")
        metrics_status = self.check_metrics_availability()
        for service, available in metrics_status.items():
            if available:
                print(f"✅ {service}: Metrics available")
            else:
                print(f"❌ {service}: Metrics not available")
                issues.append("no metrics")
        
        # Suggest fixes
        if issues:
            print("\n🔧 Suggested Fixes:")
            fixes = self.suggest_fixes(issues)
            for fix in fixes:
                print(fix)
        else:
            print("\n🎉 All checks passed! Your monitoring stack looks healthy.")
        
        return len(issues) == 0
    
    def quick_fix(self):
        """Try to automatically fix common issues."""
        print("\n🔧 Attempting quick fixes...\n")
        
        try:
            # Try to start services
            print("🔄 Starting services...")
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.monitoring.yml', 
                'up', '-d'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Services started")
                
                # Wait a bit
                print("⏳ Waiting for services to be ready...")
                time.sleep(30)
                
                # Generate sample data
                print("📊 Generating sample data...")
                try:
                    subprocess.run([sys.executable, 'test_api_samples.py'], 
                                 timeout=60, check=True)
                    print("✅ Sample data generated")
                except:
                    print("⚠️  Could not generate sample data automatically")
                
                print("✅ Quick fix completed")
                return True
            else:
                print(f"❌ Failed to start services: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Quick fix failed: {e}")
            return False
    
    def run(self):
        """Run the troubleshooter."""
        self.print_banner()
        
        # Run diagnostics
        all_good = self.run_diagnostics()
        
        if not all_good:
            print("\n❓ Would you like to try automatic fixes? (y/n): ", end="")
            try:
                response = input().lower().strip()
                if response in ['y', 'yes']:
                    self.quick_fix()
                    print("\n🔍 Running diagnostics again...")
                    self.run_diagnostics()
            except KeyboardInterrupt:
                print("\n\n👋 Troubleshooting cancelled")
        
        print("\n📞 Need more help?")
        print("• Check logs: docker-compose -f docker-compose.monitoring.yml logs")
        print("• Restart everything: docker-compose -f docker-compose.monitoring.yml restart")
        print("• Clean restart: docker-compose -f docker-compose.monitoring.yml down && docker-compose -f docker-compose.monitoring.yml up -d")
        print("• Check the DASHBOARD_GUIDE.md for detailed instructions")

def main():
    """Main function."""
    troubleshooter = MonitoringTroubleshooter()
    troubleshooter.run()

if __name__ == "__main__":
    main()
