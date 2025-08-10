#!/usr/bin/env python3
"""
API Testing Script with Sample Data
Test both housing and iris APIs with valid and invalid samples.
"""

import json
import requests
import time
from typing import Dict, List
import argparse

class APITester:
    """Test APIs with sample data."""
    
    def __init__(self, housing_url: str = "http://localhost:8000", 
                 iris_url: str = "http://localhost:8001"):
        self.housing_url = housing_url
        self.iris_url = iris_url
        self.load_test_samples()
    
    def load_test_samples(self):
        """Load test samples from JSON file."""
        try:
            with open('test_samples.json', 'r') as f:
                self.samples = json.load(f)
        except FileNotFoundError:
            print("❌ test_samples.json not found. Please ensure the file exists.")
            exit(1)
    
    def test_housing_api(self, test_invalid: bool = True) -> Dict:
        """Test housing price prediction API."""
        print("🏠 Testing Housing Price Prediction API")
        print("=" * 50)
        
        results = {'valid': [], 'invalid': []}
        
        # Test valid samples
        print("\n✅ Testing Valid Samples:")
        for sample in self.samples['housing_api']['valid_samples']:
            print(f"\n📊 {sample['name']}: {sample['description']}")
            
            try:
                response = requests.post(
                    f"{self.housing_url}/predict",
                    json=sample['data'],
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    predicted_price = result['predicted_price']
                    print(f"   ✅ Prediction: ${predicted_price:.2f} hundred thousands")
                    print(f"   📈 Expected range: {sample['expected_price_range']}")
                    
                    results['valid'].append({
                        'name': sample['name'],
                        'prediction': predicted_price,
                        'status': 'success'
                    })
                else:
                    print(f"   ❌ Error: {response.status_code} - {response.text}")
                    results['valid'].append({
                        'name': sample['name'],
                        'status': 'error',
                        'error': response.text
                    })
                    
            except requests.exceptions.RequestException as e:
                print(f"   💥 Request failed: {e}")
                results['valid'].append({
                    'name': sample['name'],
                    'status': 'request_failed',
                    'error': str(e)
                })
        
        # Test invalid samples
        if test_invalid:
            print("\n❌ Testing Invalid Samples:")
            for sample in self.samples['housing_api']['invalid_samples']:
                print(f"\n🚫 {sample['name']}: {sample['description']}")
                
                try:
                    response = requests.post(
                        f"{self.housing_url}/predict",
                        json=sample['data'],
                        timeout=10
                    )
                    
                    if response.status_code == 422:
                        print(f"   ✅ Correctly rejected: {response.status_code}")
                        error_detail = response.json()
                        print(f"   📝 Error details: {error_detail}")
                        
                        results['invalid'].append({
                            'name': sample['name'],
                            'status': 'correctly_rejected',
                            'error': error_detail
                        })
                    else:
                        print(f"   ⚠️  Unexpected response: {response.status_code}")
                        results['invalid'].append({
                            'name': sample['name'],
                            'status': 'unexpected_response',
                            'response': response.text
                        })
                        
                except requests.exceptions.RequestException as e:
                    print(f"   💥 Request failed: {e}")
                    results['invalid'].append({
                        'name': sample['name'],
                        'status': 'request_failed',
                        'error': str(e)
                    })
        
        return results
    
    def test_iris_api(self, test_invalid: bool = True) -> Dict:
        """Test iris classification API."""
        print("\n\n🌸 Testing Iris Classification API")
        print("=" * 50)
        
        results = {'valid': [], 'invalid': []}
        
        # Test valid samples
        print("\n✅ Testing Valid Samples:")
        for sample in self.samples['iris_api']['valid_samples']:
            print(f"\n🌺 {sample['name']}: {sample['description']}")
            
            try:
                response = requests.post(
                    f"{self.iris_url}/predict",
                    json=sample['data'],
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    predicted_class = result['predicted_class']
                    class_name = result['class_name']
                    print(f"   ✅ Prediction: Class {predicted_class} ({class_name})")
                    print(f"   🎯 Expected: {sample['expected_class']}")
                    
                    results['valid'].append({
                        'name': sample['name'],
                        'predicted_class': predicted_class,
                        'class_name': class_name,
                        'expected': sample['expected_class'],
                        'status': 'success'
                    })
                else:
                    print(f"   ❌ Error: {response.status_code} - {response.text}")
                    results['valid'].append({
                        'name': sample['name'],
                        'status': 'error',
                        'error': response.text
                    })
                    
            except requests.exceptions.RequestException as e:
                print(f"   💥 Request failed: {e}")
                results['valid'].append({
                    'name': sample['name'],
                    'status': 'request_failed',
                    'error': str(e)
                })
        
        # Test invalid samples
        if test_invalid:
            print("\n❌ Testing Invalid Samples:")
            for sample in self.samples['iris_api']['invalid_samples']:
                print(f"\n🚫 {sample['name']}: {sample['description']}")
                
                try:
                    response = requests.post(
                        f"{self.iris_url}/predict",
                        json=sample['data'],
                        timeout=10
                    )
                    
                    if response.status_code == 422:
                        print(f"   ✅ Correctly rejected: {response.status_code}")
                        error_detail = response.json()
                        print(f"   📝 Error details: {error_detail}")
                        
                        results['invalid'].append({
                            'name': sample['name'],
                            'status': 'correctly_rejected',
                            'error': error_detail
                        })
                    else:
                        print(f"   ⚠️  Unexpected response: {response.status_code}")
                        results['invalid'].append({
                            'name': sample['name'],
                            'status': 'unexpected_response',
                            'response': response.text
                        })
                        
                except requests.exceptions.RequestException as e:
                    print(f"   💥 Request failed: {e}")
                    results['invalid'].append({
                        'name': sample['name'],
                        'status': 'request_failed',
                        'error': str(e)
                    })
        
        return results
    
    def run_all_tests(self, test_invalid: bool = True) -> Dict:
        """Run all API tests."""
        print("🧪 Starting Comprehensive API Testing")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test APIs
        housing_results = self.test_housing_api(test_invalid)
        iris_results = self.test_iris_api(test_invalid)
        
        end_time = time.time()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 Test Summary")
        print("=" * 60)
        
        housing_valid_success = sum(1 for r in housing_results['valid'] if r['status'] == 'success')
        housing_invalid_success = sum(1 for r in housing_results['invalid'] if r['status'] == 'correctly_rejected')
        
        iris_valid_success = sum(1 for r in iris_results['valid'] if r['status'] == 'success')
        iris_invalid_success = sum(1 for r in iris_results['invalid'] if r['status'] == 'correctly_rejected')
        
        print(f"🏠 Housing API:")
        print(f"   ✅ Valid samples: {housing_valid_success}/{len(housing_results['valid'])}")
        print(f"   ❌ Invalid samples: {housing_invalid_success}/{len(housing_results['invalid'])}")
        
        print(f"🌸 Iris API:")
        print(f"   ✅ Valid samples: {iris_valid_success}/{len(iris_results['valid'])}")
        print(f"   ❌ Invalid samples: {iris_invalid_success}/{len(iris_results['invalid'])}")
        
        print(f"\n⏱️  Total test time: {end_time - start_time:.2f} seconds")
        
        return {
            'housing': housing_results,
            'iris': iris_results,
            'summary': {
                'housing_valid_success': housing_valid_success,
                'housing_invalid_success': housing_invalid_success,
                'iris_valid_success': iris_valid_success,
                'iris_invalid_success': iris_invalid_success,
                'total_time': end_time - start_time
            }
        }

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test MLOps APIs with sample data')
    parser.add_argument('--housing-url', default='http://localhost:8000',
                       help='Housing API URL (default: http://localhost:8000)')
    parser.add_argument('--iris-url', default='http://localhost:8001',
                       help='Iris API URL (default: http://localhost:8001)')
    parser.add_argument('--skip-invalid', action='store_true',
                       help='Skip testing invalid samples')
    parser.add_argument('--save-results', action='store_true',
                       help='Save test results to JSON file')
    
    args = parser.parse_args()
    
    # Create tester
    tester = APITester(args.housing_url, args.iris_url)
    
    # Run tests
    results = tester.run_all_tests(test_invalid=not args.skip_invalid)
    
    # Save results if requested
    if args.save_results:
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f'test_results_{timestamp}.json'
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")

if __name__ == "__main__":
    main()
