import urllib.request
import json

BASE_URL = "http://127.0.0.1:5000"

print("--- OFF-TOPIC ANSWER TEST (Cooking answer to Rate Limiter question) ---")
req = urllib.request.Request(
    f"{BASE_URL}/api/interviewer/evaluate-session",
    data=json.dumps({
        "company": "Amazon",
        "difficulty": "Medium",
        "session_id": "test-offtopic-001",
        "turns": [
            {
                "question": "Design a rate limiter for Amazon's API Gateway handling 100,000 QPS.",
                "answer": "I love cooking pasta. The best recipe is to boil water for 10 minutes, add salt, then put in the spaghetti. You can also make garlic bread on the side. My favorite is carbonara with extra cheese and bacon."
            }
        ]
    }).encode(),
    headers={"Content-Type": "application/json"}
)
res = urllib.request.urlopen(req)
data = json.loads(res.read())["evaluation"]

print("  Score:", data.get("overall_score"))
print("  Verdict:", data.get("hiring_verdict"))
print("  Relevance Score:", data.get("relevance_score", "N/A"))
print("  Factual Accuracy %:", data.get("factual_accuracy_pct", "N/A"))
print("  RAG Grounding Used:", data.get("rag_grounding_used", "N/A"))
print("  Justification:", data.get("score_justification", "")[:150])

score = data.get("overall_score", 100)
verdict = data.get("hiring_verdict", "")
assert score <= 30, f"Expected score <= 30 for off-topic, got {score}"
assert verdict == "REJECT", f"Expected REJECT, got {verdict}"
print("  [PASSED] Off-topic cooking answer correctly scored <= 30 with REJECT!")
print()
print("=== ALL RAG EVALUATION TESTS PASSED ===")
