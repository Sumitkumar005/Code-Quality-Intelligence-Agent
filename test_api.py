import requests
import json
import time

# Test the API
def test_api():
    print("🧪 Testing CQIA API...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8001/health")
        print(f"✅ Health check: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test analysis endpoint
    try:
        test_files = {
            "test.py": """
def bad_function():
    password = "hardcoded123"  # Security issue
    for i in range(1000):
        for j in range(1000):  # Performance issue
            pass
    return "done"
"""
        }
        
        analyze_data = {
            "input": "local_files",
            "data": {"files": test_files}
        }
        
        response = requests.post(
            "http://localhost:8001/api/v1/analyze",
            json=analyze_data
        )
        
        if response.status_code == 200:
            result = response.json()
            report_id = result["report_id"]
            print(f"✅ Analysis started: {report_id}")
            
            # Wait for completion
            for i in range(10):
                status_response = requests.get(f"http://localhost:8001/api/v1/analyze/{report_id}/status")
                status_data = status_response.json()
                
                print(f"📊 Status: {status_data.get('status')} - {status_data.get('message', '')}")
                
                if status_data.get("status") == "completed":
                    print(f"✅ Analysis completed!")
                    print(f"📈 Quality Score: {status_data.get('summary', {}).get('quality_score', 0)}/100")
                    print(f"🔍 Issues Found: {len(status_data.get('issues', []))}")
                    break
                elif status_data.get("status") == "error":
                    print(f"❌ Analysis failed: {status_data.get('message')}")
                    break
                
                time.sleep(1)
            
            # Test Q&A
            qa_data = {
                "question": "What security issues did you find?",
                "report_id": report_id
            }
            
            qa_response = requests.post(
                "http://localhost:8001/api/v1/qa/ask",
                json=qa_data
            )
            
            if qa_response.status_code == 200:
                qa_result = qa_response.json()
                print(f"🤖 Q&A Response: {qa_result['answer'][:100]}...")
            
        else:
            print(f"❌ Analysis failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    test_api()