import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(name, path, payload):
    print(f"Testing {name} ({path})...")
    try:
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        res = urllib.request.urlopen(req, timeout=15)
        data = json.loads(res.read().decode('utf-8'))
        print(f"  [SUCCESS] Status {res.status}. Keys: {list(data.keys())}")
        return True, data
    except Exception as e:
        print(f"  [ERROR] {e}")
        if hasattr(e, 'read'):
            print(f"  [BODY] {e.read().decode('utf-8', errors='ignore')[:300]}")
        return False, None

print("=== PLACIFLY SIMULATOR API DIAGNOSTICS ===")

# 1. Fetch Scenarios
ok1, d1 = test_endpoint(
    "Fetch Scenarios",
    "/api/scenarios/fetch",
    {"company": "TCS", "difficulty": "Medium", "interview_type": "Technical Interview"}
)

# 2. Start Session
ok2, d2 = test_endpoint(
    "Start Session",
    "/api/interviewer/start-session",
    {"company": "TCS", "difficulty": "Medium", "interview_type": "Technical Interview"}
)

# 3. Next Question
ok3, d3 = test_endpoint(
    "Next Question",
    "/api/interviewer/next-question",
    {
        "session_id": "diag-101",
        "company": "TCS",
        "difficulty": "Medium",
        "turns": [
            {"question": "Explain Java OOP concepts.", "answer": "OOP includes Inheritance, Polymorphism, Abstraction, and Encapsulation."}
        ]
    }
)

# 4. Evaluate Session
ok4, d4 = test_endpoint(
    "Evaluate Session",
    "/api/interviewer/evaluate-session",
    {
        "session_id": "diag-101",
        "company": "TCS",
        "difficulty": "Medium",
        "turns": [
            {"question": "Explain Java OOP concepts.", "answer": "OOP includes Inheritance, Polymorphism, Abstraction, and Encapsulation."}
        ]
    }
)

print("==========================================")
if ok1 and ok2 and ok3 and ok4:
    print("ALL API ENDPOINTS ARE WORKING CORRECTLY!")
else:
    print("SOME ENDPOINTS FAILED. SEE ERRORS ABOVE.")
