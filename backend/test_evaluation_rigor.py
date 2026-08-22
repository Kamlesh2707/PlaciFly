import urllib.request
import json

BASE_URL = "http://127.0.0.1:5000"

def test_wrong_answer_evaluation():
    print("--- 1. Testing Evaluation of Wrong / Refusal / Nonsense Answers ---")
    req = urllib.request.Request(
        f"{BASE_URL}/api/interviewer/evaluate-session",
        data=json.dumps({
            "company": "Amazon",
            "difficulty": "Medium",
            "session_id": "test-rigor-001",
            "turns": [
                {
                    "question": "Design a rate limiter for Amazon's API Gateway handling 100,000 QPS.",
                    "answer": "I don't know the answer. I have no idea how rate limiting works. abcd abcd abcd abcd abcd abcd abcd abcd abcd abcd abcd abcd abcd abcd abcd."
                }
            ]
        }).encode(),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())["evaluation"]
    print("  [RESULT] Score:", data.get("overall_score"))
    print("  [RESULT] Verdict:", data.get("hiring_verdict"))
    print("  [RESULT] Justification:", data.get("score_justification", "")[:120])
    
    assert data.get("overall_score", 100) < 40, f"Expected score < 40 for wrong answer, got {data.get('overall_score')}"
    assert data.get("hiring_verdict") == "REJECT", f"Expected REJECT verdict, got {data.get('hiring_verdict')}"
    print("  [PASSED] Wrong answer correctly received REJECT verdict and low score (<40)!")

def test_correct_answer_evaluation():
    print("\n--- 2. Testing Evaluation of Correct Technical Answer ---")
    req = urllib.request.Request(
        f"{BASE_URL}/api/interviewer/evaluate-session",
        data=json.dumps({
            "company": "Amazon",
            "difficulty": "Medium",
            "session_id": "test-rigor-002",
            "turns": [
                {
                    "question": "Design a rate limiter for Amazon's API Gateway handling 100,000 QPS.",
                    "answer": "To design a high-throughput rate limiter for Amazon's API Gateway at 100,000 QPS, I would use the Sliding Window Counter algorithm backed by Redis Cluster for in-memory atomic operations. We can store key-value pairs where key is user_id:minute_timestamp and increment using Redis INCR with a 60-second TTL. To handle 100k QPS without Redis bottleneck, we can use local memory caching (L1 cache) with Token Bucket in API Gateway instances, falling back to Redis (L2 cache) for global sync."
                }
            ]
        }).encode(),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())["evaluation"]
    print("  [RESULT] Score:", data.get("overall_score"))
    print("  [RESULT] Verdict:", data.get("hiring_verdict"))
    print("  [RESULT] Justification:", data.get("score_justification", "")[:120])
    
    assert data.get("overall_score", 0) >= 75, f"Expected score >= 75 for accurate answer, got {data.get('overall_score')}"
    assert data.get("hiring_verdict") == "HIRE", f"Expected HIRE verdict, got {data.get('hiring_verdict')}"
    print("  [PASSED] Correct technical answer correctly received HIRE verdict and high score (>=75)!")

if __name__ == "__main__":
    test_wrong_answer_evaluation()
    test_correct_answer_evaluation()
    print("\n==========================================")
    print("ANSWER EVALUATION RIGOR TESTS PASSED!")
    print("==========================================")
