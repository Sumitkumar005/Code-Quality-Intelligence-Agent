#!/usr/bin/env python3
"""
Test script for Backend API endpoints
"""

import requests
import json
import time

def test_backend_api():
    """Test all backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🚀 BACKEND API TESTING")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Health Check")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"✅ Version: {data['version']}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Supported Languages
    print("\n2. Supported Languages")
    try:
        response = requests.get(f"{base_url}/api/v1/analyze/supported-languages")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data['languages'])} languages:")
            for lang in data['languages']:
                print(f"   - {lang['name']}: {lang['extensions']}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Analysis Endpoint
    print("\n3. Analysis Endpoint")
    try:
        # Prepare test data
        test_data = {
            "input": "test_project",
            "data": {
                "files": {
                    "test.py": """# Test Python file with security issues
password = "admin123"
api_key = "sk-1234567890abcdef"

def long_function():
    # This function is too long
    for i in range(100):
        for j in range(100):
            print(i * j)
    return True
""",
                    "test.js": """// Test JavaScript file
console.log("Debug message");
var password = "admin123";
var api_key = "sk-1234567890abcdef";

if (x == 1) {
    console.log("loose equality");
}
"""
                }
            }
        }
        
        response = requests.post(f"{base_url}/api/v1/analyze", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis Started Successfully!")
            print(f"   Report ID: {result['report_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            
            # Test status endpoint
            report_id = result['report_id']
            print(f"\n4. Checking Analysis Status")
            
            # Wait a moment for processing
            time.sleep(2)
            
            status_response = requests.get(f"{base_url}/api/v1/analyze/{report_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"✅ Status Check: {status_data.get('status', 'unknown')}")
                print(f"   Progress: {status_data.get('progress', 0)}%")
                print(f"   Message: {status_data.get('message', 'No message')}")
                
                # If completed, show results
                if status_data.get('status') == 'completed':
                    print(f"\n📊 Analysis Results:")
                    summary = status_data.get('summary', {})
                    print(f"   Files: {summary.get('total_files', 0)}")
                    print(f"   Lines: {summary.get('total_lines', 0)}")
                    print(f"   Quality Score: {summary.get('quality_score', 0)}/100")
                    
                    issues = status_data.get('issues', [])
                    print(f"   Issues Found: {len(issues)}")
                    
                    # Show first few issues
                    for i, issue in enumerate(issues[:3]):
                        print(f"   Issue {i+1}: [{issue.get('severity')}] {issue.get('message')}")
                
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                
        else:
            print(f"❌ Analysis Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Analysis Error: {e}")
    
    # Test 5: Q&A Endpoint (if we have a report)
    print(f"\n5. Q&A Endpoint Test")
    try:
        qa_data = {
            "question": "What security issues should I fix?",
            "report_id": "test-report-123"
        }
        
        response = requests.post(f"{base_url}/api/v1/ask", json=qa_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Q&A Response:")
            print(f"   Answer: {result.get('answer', 'No answer')[:100]}...")
        else:
            print(f"❌ Q&A Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Q&A Error: {e}")
    
    print(f"\n🎯 API Testing Complete!")

if __name__ == "__main__":
    test_backend_api()