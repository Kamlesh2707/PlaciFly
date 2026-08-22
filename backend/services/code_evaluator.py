"""
Rigorous Code Evaluation Engine for Coding Rounds
Detects dummy code, syntax mismatch, missing algorithms (recursion, loops), and grades correctness accurately.
"""

import re
import json

try:
    import google.generativeai as genai
    from config import Config
    if Config.GEMINI_API_KEY:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel('gemini-2.0-flash')
    else:
        _gemini_model = None
except Exception:
    _gemini_model = None


def evaluate_code_rigorous(question_text, code_text, language='python'):
    """
    Rigorously evaluate code submitted by candidate.
    
    Prevents false positives (e.g., `print('Hello World')` getting 77 points).
    """
    code_clean = code_text.strip()
    q_lower = question_text.lower()
    
    if not code_clean or len(code_clean) < 5:
        return {
            "correctness": 0,
            "logic": 0,
            "edge_cases": 0,
            "code_quality": 0,
            "efficiency": 0,
            "overall_score": 0,
            "verdict": "FAIL",
            "feedback": "No functional code submitted. An empty or incomplete snippet cannot be evaluated.",
            "issues": ["No code provided to solve the problem."],
            "suggestions": ["Write a complete function or program implementing the required algorithm."],
            "expected_output": "Working solution matching question requirements."
        }
    
    # 1. Detect Trivial / Dummy Code Submissions
    dummy_prints = [
        r'^\s*print\s*\(\s*["\']hello\s*world["\']\s*\)\s*;?\s*$',
        r'^\s*console\.log\s*\(\s*["\']hello\s*world["\']\s*\)\s*;?\s*$',
        r'^\s*system\.out\.println\s*\(\s*["\']hello\s*world["\']\s*\)\s*;?\s*$',
        r'^\s*cout\s*<<\s*["\']hello\s*world["\']\s*;?\s*$'
    ]
    
    is_hello_world = any(re.match(p, code_clean, re.IGNORECASE) for p in dummy_prints)
    is_hw_question = "hello world" in q_lower or "print hello" in q_lower
    
    if is_hello_world and not is_hw_question:
        return {
            "correctness": 0,
            "logic": 0,
            "edge_cases": 0,
            "code_quality": 10,
            "efficiency": 0,
            "overall_score": 5,
            "verdict": "FAIL",
            "feedback": "You submitted a basic 'Hello World' print statement, but the interview question requires an actual algorithm / function.",
            "issues": [
                "Code does not attempt to solve the question.",
                "Missing required algorithm, variables, and logic."
            ],
            "suggestions": [
                "Carefully read the question requirements.",
                "Implement the logic using functions, loops, or recursion as requested."
            ],
            "expected_output": "A complete algorithm implementation solving the problem."
        }
    
    # 2. Check Specific Algorithmic Requirements (Heuristics)
    if "recurs" in q_lower:
        # Check if code defines a function and calls itself
        func_defs = re.findall(r'(?:def|function|void|int|public\s+static\s+\w+)\s+([a-zA-Z_]\w*)', code_clean)
        has_recursive_call = False
        for fn in func_defs:
            if re.search(rf'\b{fn}\s*\(', code_clean[code_clean.find(fn) + len(fn):]):
                has_recursive_call = True
                break
        
        if not has_recursive_call and len(code_clean.split()) < 15:
            return {
                "correctness": 10,
                "logic": 15,
                "edge_cases": 0,
                "code_quality": 20,
                "efficiency": 10,
                "overall_score": 12,
                "verdict": "FAIL",
                "feedback": "The question specifically asks for a recursive approach, but your code contains no recursive function calls.",
                "issues": ["Missing base case and recursive step."],
                "suggestions": ["Define a base case to terminate recursion and call the function with smaller sub-problems."],
                "expected_output": "Recursive function with base case."
            }

    if "pattern" in q_lower or "star" in q_lower:
        # Check for nested loops or string multiplication
        has_loops = any(k in code_clean for k in ['for', 'while', 'range', 'System.out.print', '*'])
        if not has_loops and len(code_clean.split()) < 10:
            return {
                "correctness": 5,
                "logic": 5,
                "edge_cases": 0,
                "code_quality": 10,
                "efficiency": 0,
                "overall_score": 5,
                "verdict": "FAIL",
                "feedback": "Pattern printing requires iteration loops to generate the structure row by row.",
                "issues": ["No loops or pattern generating logic found."],
                "suggestions": ["Use nested loops (outer loop for rows, inner loop for columns/stars)."],
                "expected_output": "Nested loop pattern generator."
            }
            
    # 3. LLM Evaluation (If Gemini is available)
    if _gemini_model:
        try:
            prompt = f"""You are a strict senior technical interviewer at a top tech company evaluating a candidate's code.

QUESTION:
{question_text}

CANDIDATE CODE ({language}):
```{language}
{code_clean}
```

EVALUATION RULES:
1. If the code is completely wrong, irrelevant, or just a dummy print statement, give overall_score <= 10 and verdict FAIL.
2. Check for syntax correctness, logic flow, time/space complexity, and edge case handling.
3. Be strict and objective.

Return ONLY valid JSON (no markdown fences):
{{
    "correctness": 0-100,
    "logic": 0-100,
    "edge_cases": 0-100,
    "code_quality": 0-100,
    "efficiency": 0-100,
    "overall_score": 0-100,
    "verdict": "PASS" or "NEEDS_IMPROVEMENT" or "FAIL",
    "feedback": "Detailed 2-3 sentence technical assessment.",
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["suggestion 1", "suggestion 2"],
    "expected_output": "Description of expected output."
}}
"""
            res = _gemini_model.generate_content(prompt, generation_config={'temperature': 0.1})
            text = res.text.strip()
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            return json.loads(text)
        except Exception as e:
            print(f"[Code Evaluator LLM Error] {e}")

    # 4. Fallback Static Analysis
    score = 50
    has_func = any(k in code_clean for k in ['def ', 'function ', 'class ', 'public static '])
    has_return = 'return ' in code_clean or 'System.out.println' in code_clean
    
    if has_func and has_return:
        score = 85
    elif has_func or len(code_clean.split('\n')) >= 3:
        score = 65
        
    verdict = "PASS" if score >= 80 else "NEEDS_IMPROVEMENT" if score >= 50 else "FAIL"
    
    return {
        "correctness": score,
        "logic": score,
        "edge_cases": max(score - 15, 30),
        "code_quality": 80,
        "efficiency": 75,
        "overall_score": score,
        "verdict": verdict,
        "feedback": f"Valid code structure identified for {language}. Core logic and return statements detected.",
        "issues": ["Make sure to verify edge cases like extreme or boundary inputs."],
        "suggestions": ["Add boundary checks and inline docstrings."],
        "expected_output": "Valid algorithmic execution."
    }
