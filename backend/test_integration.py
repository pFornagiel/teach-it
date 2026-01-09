import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_integration():
    print("1. Testing Health...")
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(r.json())
    except:
        print("Backend not running?")
        return

    print("\n2. Uploading File...")
    # Create a dummy file
    with open("test_physics.txt", "w") as f:
        f.write("Quantum physics is the study of matter and energy at the most fundamental level. It aims to uncover the properties and behaviors of the very building blocks of nature. While many quantum experiments examine very small objects, such as electrons and photons, quantum phenomena are all around us, acting on every scale.")
    
    files = {'file': open('test_physics.txt', 'rb')}
    r = requests.post(f"{BASE_URL}/api/upload", files=files)
    print(r.json())
    filenames = r.json().get('filenames', [])

    print("\n3. Getting Topics...")
    r = requests.post(f"{BASE_URL}/api/topics", json={'filenames': filenames})
    print(r.json())
    topics = r.json().get('topics', [])
    if not topics:
        print("No topics found!")
        return
    
    topic = topics[0]
    print(f"Selected Topic: {topic}")

    print("\n4. Starting Session...")
    r = requests.post(f"{BASE_URL}/api/start_session", json={'topic': topic, 'filenames': filenames})
    print(r.json())
    session_id = r.json().get('session_id')
    
    print("\n5. Chat Loop...")
    # First get the initial question - actually chat with answer=None or something?
    # Based on app.py: current frontend sends answer=None to get first question?
    # Wait, implementation of StudentAgent.chat handles user_answer=None.
    # The frontend usually sends answer=NULL first? 
    # Let's assume the flow: Start -> Chat(answer=None) -> Returns Q1.
    
    r = requests.post(f"{BASE_URL}/api/chat", json={'session_id': session_id})
    print("Initial Question Response:", r.json())
    
    q1 = r.json().get('question')
    print(f"Agent: {q1}")
    
    # Answer 1
    ans1 = "It is about small particles like electrons."
    print(f"User: {ans1}")
    r = requests.post(f"{BASE_URL}/api/chat", json={'session_id': session_id, 'answer': ans1})
    print("Response 1:", r.json())
    
    # Answer 2
    ans2 = "I don't know much more."
    print(f"User: {ans2}")
    r = requests.post(f"{BASE_URL}/api/chat", json={'session_id': session_id, 'answer': ans2})
    print("Response 2:", r.json())
    
    # Answer 3
    ans3 = "That's it."
    print(f"User: {ans3}")
    r = requests.post(f"{BASE_URL}/api/chat", json={'session_id': session_id, 'answer': ans3})
    print("Response 3:", r.json()) 
    # Should say finished here or next time?
    
    print("\n6. Evaluating...")
    r = requests.post(f"{BASE_URL}/api/evaluate", json={'session_id': session_id})
    print(r.json())

if __name__ == "__main__":
    test_integration()
