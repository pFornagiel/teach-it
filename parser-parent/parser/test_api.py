"""
Simple test script for the Upside Learning API
"""
import requests
import uuid
import json
BASE_URL = "http://localhost:7312"
def test_health_check():
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200
def test_root():
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200
def test_file_upload(user_id, file_path):
    print("\n=== Testing File Upload ===")
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'user_id': str(user_id)}
        
        response = requests.post(
            f"{BASE_URL}/api/ingestion/upload",
            files=files,
            data=data
        )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()['file_id']
    return None
def test_file_status(file_id):
    print("\n=== Testing File Status ===")
    response = requests.get(f"{BASE_URL}/api/ingestion/status/{file_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200
def test_search(user_id, query):
    print("\n=== Testing Knowledge Search ===")
    
    data = {
        'query': query,
        'user_id': str(user_id),
        'top_k': 3
    }
    
    response = requests.post(
        f"{BASE_URL}/api/retrieval/search",
        json=data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200
def test_teaching_session(user_id, topic):
    print("\n=== Testing Teaching Session ===")
    
    print("\n--- Starting Session ---")
    response = requests.post(
        f"{BASE_URL}/api/teaching/start-session",
        json={'user_id': str(user_id), 'topic': topic}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 201:
        return False
    
    session_data = response.json()
    session_id = session_data['session_id']
    
    for i in range(3):
        print(f"\n--- Answering Question {i+1} ---")
        answer_data = {
            'session_id': session_id,
            'answer': f"This is my answer to question {i+1}. I understand the concept."
        }
        
        response = requests.post(
            f"{BASE_URL}/api/teaching/answer",
            json=answer_data
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n--- Evaluating Session ---")
    response = requests.get(f"{BASE_URL}/api/teaching/evaluate/{session_id}")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200
def main():
    print("=" * 60)
    print("Upside Learning API Test Suite")
    print("=" * 60)
    
    user_id = uuid.uuid4()
    print(f"\nTest User ID: {user_id}")
    
    results = []
    
    results.append(("Health Check", test_health_check()))
    results.append(("Root Endpoint", test_root()))
    
    
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
if __name__ == "__main__":
    main()
