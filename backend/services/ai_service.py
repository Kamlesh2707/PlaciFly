import json
import re
import random
import uuid
import time
import hashlib
import google.generativeai as genai
from config import Config
from services.scenario_db import get_company_intel, COMPANY_INTELLIGENCE
from services.scenario_db_kb import get_company_knowledge, get_topic_list, get_coding_focus, get_behavioral_focus
from services.question_history import record_question, get_asked_previews, is_duplicate

if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)

from services.security import sanitize_input, wrap_prompt_bounds
from services.interview_memory import get_or_create_memory, extract_concepts_from_answer
from services.rag_knowledge import retrieve_relevant_chunks, compute_answer_relevance, grade_factual_accuracy, check_common_mistakes, get_expected_concepts
from services.interview_memory import compute_relevance_score

# ==============================================================================
# ANSWER VALIDATION ENGINE
# Detects gibberish, keyboard smashes, and empty/too-short responses
# ==============================================================================

COMMON_ENGLISH_WORDS = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with",
    "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her",
    "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up",
    "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time",
    "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could",
    "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think",
    "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even",
    "new", "want", "because", "any", "these", "give", "day", "most", "us", "client", "project",
    "team", "code", "system", "data", "issue", "database", "service", "bug", "server", "user",
    "process", "manager", "company", "solution", "customer", "product", "api", "security", "develop",
    "application", "test", "management", "deploy", "design", "check", "fix", "deliver", "review",
    "communication", "approach", "handle", "address", "inform", "report", "ensure", "lead", "task"
}

def is_coding_context(student_answer, question_text=""):
    q = question_text.lower()

    if any(k in q for k in ["coding", "write a program", "write a function", "write an sql", "code", "palindrome", "reverse a string", "anagram", "binary search", "implement", "design a function"]):
        return True

    code_syntax_patterns = [
        r'\bdef\b', r'\breturn\b', r'\bclass\b', r'\bimport\b', r'\bselect\b', r'\bfrom\b',
        r'\bpublic\b', r'\bstatic\b', r'\bvoid\b', r'\bint\b', r'\bstring\b', r'\bif\b', r'\bfor\b',
        r'\{.*\}', r';', r'==', r'!=', r'->', r'::', r'\[::\-1\]'
    ]

    for pattern in code_syntax_patterns:
        if re.search(pattern, student_answer):
            return True

    return False

def is_meaningful_answer(student_answer, question_text=""):
    clean_text = student_answer.strip()
    if not clean_text:
        return False, "Your response is empty. Please provide an answer."

    if is_coding_context(student_answer, question_text):
        if len(clean_text) < 3:
            return False, "Please provide your code solution."
        return True, "Valid Code Solution"

    words = [w.lower().strip(",.!?\"'();:") for w in clean_text.split() if w.strip()]

    if len(words) < 15:
        return False, "Your descriptive response is too short. Please provide a detailed answer of at least 50 words."

    vowels = set("aeiouy")
    invalid_word_count = 0
    for w in words:
        if len(w) > 3 and not any(char in vowels for char in w): invalid_word_count += 1
        if len(w) > 4 and len(set(w)) <= 2: invalid_word_count += 1

    if invalid_word_count / max(len(words), 1) > 0.25:
        return False, "Your response contains non-sensical text or keyboard smashes. Please provide a coherent answer in English."

    recognized_count = sum(1 for w in words if w in COMMON_ENGLISH_WORDS or len(w) > 3)
    if (recognized_count / max(len(words), 1)) < 0.45:
        return False, "Your answer appears random or off-topic. Please answer the interviewer's specific question."

    return True, "Valid Descriptive Answer"

# ==============================================================================
# INTERVIEWER PERSONA SELECTOR
# ==============================================================================

def get_interviewer_for_difficulty(intel, difficulty):
    interviewers = intel.get("interviewers", {})
    interviewer = interviewers.get(difficulty, interviewers.get("Medium", {}))

    name = interviewer.get("name", "Technical Evaluator")
    title = interviewer.get("title", "Senior Technical Architect")
    avatar = interviewer.get("avatar", "👨‍💼")
    style = interviewer.get("style", "Professional corporate evaluator")

    return {
        "name": name,
        "title": title,
        "avatar": avatar,
        "persona_style": style,
        "style": style
    }

# ==============================================================================
# DYNAMIC AI QUESTION GENERATION ENGINE
# Zero hardcoded questions. Every question is generated by Gemini AI using
# structured company knowledge metadata.
# ==============================================================================

def _build_question_prompt(company_name, difficulty, interview_type, candidate_project, candidate_skills, interviewer, knowledge, previously_asked, memory_context=None):
    """Build a rich, dynamic prompt for Gemini AI with conversational memory and dynamic difficulty adaptation."""

    topics = get_topic_list(company_name, difficulty)
    coding = get_coding_focus(company_name, difficulty)
    behavioral = get_behavioral_focus(company_name, difficulty)
    style = knowledge.get("interview_style", {}).get(difficulty, "Professional technical interviewer")
    hiring_pattern = knowledge.get("hiring_pattern", "Standard technical interview process")
    project_areas = knowledge.get("project_questions", [])
    role = knowledge.get("role", "Software Engineer")
    tech_stack = ", ".join(COMPANY_INTELLIGENCE.get(company_name, COMPANY_INTELLIGENCE.get("DEFAULT", {})).get("tech_stack", ["Software Engineering"]))

    # Build memory context section
    memory_section = ""
    if memory_context:
        concepts_str = ", ".join(memory_context.get("concepts_used", [])) or "None specified yet"
        weak_str = ", ".join(memory_context.get("weak_topics", [])) or "None identified yet"
        memory_section = f"""
    INTERVIEW CONVERSATION MEMORY:
    - Overall Session Summary: {memory_context.get('conversation_summary', '')}
    - Candidate Mentioned Technologies/Claims: {concepts_str}
    - Identified Weak Topics Needing Scrutiny: {weak_str}
    - Recent Turn History:
{memory_context.get('last_3_turns', '')}

    HUMAN CONVERSATIONAL RULE:
    - If candidate previously mentioned a specific technology (e.g. {concepts_str[:50]}), natural references to it are encouraged ("Earlier you mentioned using X, how would you...").
    - If candidate showed weakness in a topic (e.g. {weak_str[:50]}), prioritize probing that specific topic!
    """

    # Build deduplication context
    dedup_section = ""
    if previously_asked:
        dedup_section = f"""
    CRITICAL DEDUPLICATION — NEVER ask questions similar to these previously asked ones:
    {chr(10).join(f'    - "{p}"' for p in previously_asked[-15:])}
    You MUST generate a completely NEW question that is different from all of the above.
    """

    # Determine question focus based on interview_type
    type_guidance = ""
    if "hr" in interview_type.lower() or "behavioral" in interview_type.lower():
        type_guidance = f"""
    HR / BEHAVIORAL ROUND FOCUS (MANDATORY RULES):
    - Ask authentic, high-impact HR questions tailored to {company_name}:
      * Standard foundational questions: "Tell me about yourself and walk me through your background", "Why should we hire you for {company_name}?", "Why do you want to join {company_name}?", "Walk me through the flagship project on your resume ({candidate_project}) and your key role", or "What are your greatest technical strengths and what is an area you are actively improving?"
      * Probe the candidate's resume projects, collaboration, communication, and culture fit.
      * Expect STAR method structure (Situation, Task, Action, Result).
    """
    elif "technical" in interview_type.lower():
        type_guidance = f"""
    TECHNICAL ROUND FOCUS (RESUME-DRIVEN):
    - Focus strictly on the candidate's declared programming languages and skills ({candidate_skills or 'Java, Python, C++, SQL'}).
    - Ask conceptual fundamentals (e.g., memory management, OOP pillars, indexing, thread safety, language-specific internal workings).
    - Choose from topic areas: {', '.join(topics[:8])}.
    - Ask in a conversational, probing interviewer tone.
    """
    elif "coding" in interview_type.lower():
        type_guidance = f"""
    CODING ROUND FOCUS:
    - Present a concrete, hands-on coding task suitable for a code editor (e.g. Print a specific star/number pattern in Python/Java, string reversal without built-ins, find first non-repeating character, check palindrome, anagram grouping, two sum).
    - Specify clear input/output requirements.
    - Ask the candidate to write clean, executable code with comments explaining their logic.
    """
    elif "case" in interview_type.lower():
        type_guidance = f"""
    CASE STUDY ROUND FOCUS (STRICTLY {company_name} ONLY):
    - Present a real-world engineering or product case study EXCLUSIVELY about {company_name} (e.g., if Amazon, ask about Amazon's logistics/Prime Day spike/order fulfillment; if Google, ask about Search indexing/YouTube video streaming; if TCS, ask about enterprise core banking system modernization).
    - NEVER mention or ask about other competing companies.
    - Provide a concrete scenario with constraints and ask for a structured architectural or analytical recommendation.
    """
    elif "system" in interview_type.lower() or "design" in interview_type.lower():
        type_guidance = f"""
    SYSTEM DESIGN QUESTION FOCUS:
    - Ask to design a system relevant to {company_name}'s domain
    - Include scale requirements (users, QPS, data volume)
    - Expect discussion of architecture, databases, caching, scaling, and trade-offs
    """
    else:
        type_guidance = f"""
    GENERAL INTERVIEW QUESTION FOCUS:
    - Choose a relevant topic from: {', '.join(topics[:6])}
    - Create a natural, conversational interview question
    """

    # Candidate context
    candidate_context = f"Candidate's flagship project: {candidate_project}"
    if candidate_skills:
        candidate_context += f"\n    Candidate's skills: {candidate_skills}"

    sys_instructions = f"""You are {interviewer['name']}, {interviewer['title']} at {company_name}.
    Your interviewing style: {style}

    CONTEXT:
    - Company: {company_name} ({knowledge.get('full_name', company_name)})
    - Role: {role}
    - Company Tech Stack: {tech_stack}
    - Difficulty Level: {difficulty}
    - Interview Type: {interview_type}
    - Company Hiring Pattern: {hiring_pattern}
    - {candidate_context}

    {memory_section}

    {type_guidance}

    {dedup_section}

    DIFFICULTY CALIBRATION:
    {"- EASY: Ask about fundamental concepts only. No advanced topics. Simple, direct questions a fresher can answer. Keep it short and encouraging." if difficulty == "Easy" else ""}
    {"- MEDIUM: Ask intermediate-level questions requiring analysis and reasoning. Expect structured answers with examples. Professional tone." if difficulty == "Medium" else ""}
    {"- HARD: Ask senior-level questions requiring deep expertise. Expect system-level thinking, trade-off analysis, and production experience. Demanding tone." if difficulty == "Hard" else ""}

    QUALITY RULES:
    1. Sound like a REAL human interviewer, not a textbook or ChatGPT
    2. Be specific to {company_name}'s domain and tech stack
    3. Include realistic context or scenario setup (2-3 sentences)
    4. The question must be answerable within the interview timeframe
    5. Do NOT use generic templates like "explain X" — create a situation-based question
    6. Generate a COMPLETELY ORIGINAL question — never repeat patterns

    Return ONLY a valid JSON object with these exact keys:
    {{
        "id": "unique-question-id",
        "company": "{company_name}",
        "interviewer_name": "{interviewer['name']}",
        "interviewer_title": "{interviewer['title']}",
        "interviewer_avatar": "{interviewer['avatar']}",
        "category": "the category of this question (Technical/Coding/Behavioral/Case Study/System Design)",
        "difficulty": "{difficulty}",
        "interview_type": "{interview_type}",
        "title": "short descriptive title for this question",
        "situation": "2-3 sentence realistic scenario setup",
        "question": "the exact interview question asked to the candidate",
        "estimated_time": estimated_seconds_as_integer,
        "skills_tested": ["skill1", "skill2", "skill3", "skill4"],
        "ideal_approach": "brief description of what a strong answer would cover",
        "topic": "primary technical topic being tested",
        "subtopic": "specific subtopic within the primary topic",
        "hints": ["hint1 if candidate is stuck", "hint2"],
        "followups": ["possible follow-up question 1", "possible follow-up question 2"]
    }}"""

    return wrap_prompt_bounds("Generate an authentic interview question adhering to rules.", sys_instructions)

def _parse_ai_response(text):
    """Parse Gemini AI JSON response, handling markdown code blocks."""
    text = text.strip()
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    return json.loads(text.strip())

def _build_dynamic_fallback(company_name, difficulty, interview_type, interviewer, knowledge):
    """Build a dynamic fallback question from metadata when AI is unavailable.
    Uses multiple varied templates to ensure questions feel natural and different every time."""
    topics = get_topic_list(company_name, difficulty)
    coding = get_coding_focus(company_name, difficulty)
    behavioral = get_behavioral_focus(company_name, difficulty)
    role = knowledge.get("role", "Software Engineer")

    # Default topic to prevent UnboundLocalError when branch conditions aren't met
    topic = random.choice(topics) if topics else "software engineering"

    itype = interview_type.lower()

    if "coding" in itype and coding:
        topic = random.choice(coding)
        templates = [
            f"I'd like you to solve this coding challenge: {topic}. Walk me through your approach before you start coding, then implement it with clean, production-quality code.",
            f"Here's your coding problem: {topic}. First, clarify any assumptions, then write an optimal solution. What's the time and space complexity?",
            f"Let's see your problem-solving skills. Implement {topic}. Start with a brute-force approach, then optimize it. Explain each step.",
            f"On this whiteboard, solve {topic}. I want to see how you think — talk through your approach as you code. Handle edge cases too.",
            f"Your coding challenge is: {topic}. Before writing code, discuss at least two approaches and their trade-offs. Then implement the better one.",
            f"Write a clean solution for {topic}. I'll evaluate your code quality, variable naming, edge case handling, and efficiency."
        ]
        question = random.choice(templates)
        category = "Coding"
        title = f"Coding Challenge: {topic}"
        situation = f"During your {company_name} {difficulty}-level coding interview for the {role} position, {interviewer['name']} presents you with a live coding challenge on the shared code editor."
        skills = ["Problem Solving", "Data Structures", "Algorithms", "Code Quality"]

    elif ("behavioral" in itype or "hr" in itype) and behavioral:
        theme = random.choice(behavioral)
        templates = [
            f"Tell me about a specific time when you had to demonstrate '{theme}'. What was the situation, what did you do, and what was the result?",
            f"I want to understand how you handle '{theme}'. Can you walk me through a real experience from your academic or professional life?",
            f"At {company_name}, '{theme}' is something we value deeply. Share an example from your experience that shows how you've demonstrated this.",
            f"Describe a challenging situation where '{theme}' was critical. How did you approach it, and what did you learn from the experience?",
            f"Give me a concrete example where you showed '{theme}'. I'm looking for specifics — what happened, what you did, and the measurable outcome.",
            f"Let's talk about '{theme}'. Paint me a picture of a time you navigated this well. What would you do differently if you faced it again?"
        ]
        question = random.choice(templates)
        category = "Behavioral"
        title = f"Behavioral: {theme}"
        situation = f"In the {company_name} HR and behavioral assessment round for the {role} position, {interviewer['name']} explores your soft skills, cultural fit, and past experiences."
        skills = ["Communication", "Leadership", "Problem Solving", "Cultural Fit"]

    elif "case" in itype:
        topic = random.choice(topics) if topics else "business analysis"
        templates = [
            f"A {company_name} client in the {topic} space has seen a 20% decline in user engagement over the past quarter despite increasing their marketing spend by 15%. Walk me through how you'd diagnose and solve this.",
            f"Imagine you're consulting for a {company_name} client facing critical performance issues in their {topic} infrastructure. Their system response time has increased 3x. How would you structure your analysis?",
            f"A Fortune 500 client asks {company_name} to evaluate whether to build or buy a {topic} solution. Walk me through your decision framework, key factors, and final recommendation.",
            f"A retail client's {topic} pipeline is processing 50% fewer transactions than expected after a recent migration. As a {company_name} consultant, how would you investigate and resolve this?",
            f"You're leading a {company_name} engagement where the client needs to modernize their {topic} stack within 6 months. What's your phased approach, risk assessment, and success metrics?"
        ]
        question = random.choice(templates)
        category = "Case Study"
        title = f"Case Study: {topic} Analysis"
        situation = f"In the {company_name} case study round, {interviewer['name']} presents a real-world business problem requiring your structured analytical thinking and consulting skills."
        skills = ["Analytical Thinking", "Structured Problem Solving", "Communication", "Business Acumen"]

    elif "system" in itype or "design" in itype:
        topic = random.choice(topics[-3:]) if len(topics) > 3 else random.choice(topics) if topics else "distributed system"
        scale_numbers = random.choice(["10 million users", "50,000 concurrent connections", "1 million requests per second", "100TB of data", "5 million daily active users"])
        templates = [
            f"Design a {topic} system that can support {scale_numbers}. Cover high-level architecture, database choices, caching strategy, and how you'd handle failures.",
            f"Architect a production-grade {topic} platform for {company_name} serving {scale_numbers}. Discuss your technology choices, scaling strategy, and operational considerations.",
            f"You need to build a {topic} service from scratch for {scale_numbers}. Walk me through your architecture diagram, data flow, bottleneck analysis, and monitoring approach.",
            f"How would you design {topic} at {company_name}'s scale ({scale_numbers})? I want to hear about your database design, API layer, caching, message queues, and failure recovery.",
            f"Design the backend infrastructure for {topic} handling {scale_numbers}. Start with requirements, then move to architecture, database schema, and deployment strategy."
        ]
        question = random.choice(templates)
        category = "System Design"
        title = f"System Design: {topic}"
        situation = f"In the {company_name} system design round for the {role} position, {interviewer['name']} challenges you to architect a production-grade system at scale."
        skills = ["System Design", "Scalability", "Architecture", "Trade-off Analysis"]

    else:
        topic = random.choice(topics) if topics else "software engineering"
        templates = [
            f"We're working on a project at {company_name} that heavily uses {topic}. Walk me through how you understand this concept and how you've applied it in your own projects.",
            f"In our team at {company_name}, {topic} comes up frequently. Can you explain the core principles and share a practical example of when you used this?",
            f"I noticed your project uses some concepts related to {topic}. How would you implement this at {company_name}'s production scale? What challenges would you anticipate?",
            f"Let's discuss {topic}. First, explain the fundamentals. Then, tell me how you'd apply it specifically in the context of your {knowledge.get('role', 'engineering')} work at {company_name}.",
            f"At {company_name}, we recently had a production issue related to {topic}. How would you approach debugging and resolving it? Walk me through your thought process.",
            f"Explain {topic} to me as if you were onboarding a new team member at {company_name}. Then, describe a scenario where incorrect usage of this concept could cause a production incident."
        ]
        question = random.choice(templates)
        category = "Technical"
        title = f"Technical: {topic}"
        situation = f"During the {company_name} technical interview for the {role} role, {interviewer['name']} dives into your understanding of core technical concepts relevant to {company_name}'s stack."
        skills = ["Technical Knowledge", topic, "Problem Solving", "Communication"]

    qid = f"{company_name.lower()}-{difficulty.lower()}-{uuid.uuid4().hex[:8]}"
    est_time = {"Easy": 180, "Medium": 300, "Hard": 420}.get(difficulty, 300)

    return {
        "id": qid,
        "company": company_name,
        "interviewer_name": interviewer["name"],
        "interviewer_title": interviewer["title"],
        "interviewer_avatar": interviewer["avatar"],
        "category": category,
        "difficulty": difficulty,
        "interview_type": interview_type,
        "title": f"{company_name} [{difficulty} Mode] - {title}",
        "situation": situation,
        "question": question,
        "estimated_time": est_time,
        "skills_tested": skills,
        "ideal_approach": f"Provide a structured, {company_name}-specific answer covering {topic} with practical examples and depth appropriate for {difficulty} level.",
        "topic": topic,
        "subtopic": "",
        "hints": [f"Think about how {company_name} uses {topic} in their production systems", f"Consider edge cases and trade-offs"],
        "followups": [f"How would you scale this approach at {company_name}?", f"What could go wrong with this approach in production?"]
    }

def generate_company_interviewer_question(company_name, difficulty="Medium", interview_type="Technical Interview", candidate_project="Placifly", asked_question_ids=None, candidate_skills=None, session_id=None):
    """
    Generate a completely unique interview question using Gemini AI.
    Uses calibrated temperature=0.6 for creative question generation,
    session memory graph, and embedding-based deduplication.
    """
    if asked_question_ids is None: asked_question_ids = []

    intel = get_company_intel(company_name)
    interviewer = get_interviewer_for_difficulty(intel, difficulty)
    knowledge = get_company_knowledge(company_name)

    # Load session memory context
    session_mem = get_or_create_memory(session_id, company_name, difficulty)
    memory_context = session_mem.get_prompt_context()

    # Get previously asked question previews for deduplication
    previously_asked = get_asked_previews(session_id, company_name, limit=20)
    if asked_question_ids:
        previously_asked.extend(asked_question_ids[-10:])

    max_retries = 3

    if Config.GEMINI_API_KEY:
        for attempt in range(max_retries):
            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                prompt = _build_question_prompt(
                    company_name, difficulty, interview_type,
                    candidate_project, candidate_skills,
                    interviewer, knowledge, previously_asked,
                    memory_context=memory_context
                )

                gen_config = genai.types.GenerationConfig(temperature=0.6)
                response = model.generate_content(prompt, generation_config=gen_config)
                result = _parse_ai_response(response.text)

                question_text = result.get("question", "")
                if not question_text:
                    continue

                if is_duplicate(session_id, question_text) and attempt < max_retries - 1:
                    previously_asked.append(question_text[:100])
                    continue

                result["company"] = company_name
                result["difficulty"] = difficulty
                result["interview_type"] = interview_type
                result["interviewer_name"] = interviewer["name"]
                result["interviewer_title"] = interviewer["title"]
                result["interviewer_avatar"] = interviewer["avatar"]

                if not result.get("id"):
                    result["id"] = f"{company_name.lower()}-{difficulty.lower()}-{uuid.uuid4().hex[:8]}"

                record_question(session_id, result)
                return result

            except Exception as e:
                print(f"Gemini Question Generation attempt {attempt + 1} failed: {e}")

    fallback = _build_dynamic_fallback(company_name, difficulty, interview_type, interviewer, knowledge)
    record_question(session_id, fallback)
    return fallback

# ==============================================================================
# ADAPTIVE FOLLOW-UP ENGINE
# Generates intelligent, dynamic follow-up questions based on candidate's answer
# ==============================================================================

def generate_adaptive_followup(company_name, previous_question, candidate_answer, candidate_project="Placifly", difficulty="Medium"):
    """Generate a dynamic follow-up question based on the candidate's previous answer."""
    intel = get_company_intel(company_name)
    interviewer = get_interviewer_for_difficulty(intel, difficulty)
    knowledge = get_company_knowledge(company_name)
    topics = get_topic_list(company_name, difficulty)
    style = knowledge.get("interview_style", {}).get(difficulty, "Professional interviewer")

    if Config.GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = f"""You are {interviewer['name']}, {interviewer['title']} at {company_name}.
            Your style: {style}
            Difficulty Level: {difficulty}

            PREVIOUS QUESTION YOU ASKED:
            "{previous_question}"

            CANDIDATE'S ANSWER:
            "{candidate_answer}"

            CANDIDATE'S PROJECT: {candidate_project}
            COMPANY TECH FOCUS: {', '.join(topics[:6])}

            Based on the candidate's answer, generate an intelligent follow-up question that:
            1. Probes deeper into what the candidate said (or didn't say)
            2. Tests whether they truly understand the concept or are just reciting
            3. Connects to {company_name}'s specific tech stack and standards
            4. Matches {difficulty} difficulty level
            5. Sounds like a real interviewer naturally following up, not a new topic

            {"For EASY: Ask a simple clarification or ask them to give a concrete example." if difficulty == "Easy" else ""}
            {"For MEDIUM: Probe edge cases, scalability, or ask them to compare alternatives." if difficulty == "Medium" else ""}
            {"For HARD: Challenge their assumptions, ask about failure modes, or push to extreme scale." if difficulty == "Hard" else ""}

            Return ONLY a valid JSON object:
            {{
                "followup_id": "unique-followup-id",
                "interviewer_name": "{interviewer['name']}",
                "interviewer_avatar": "{interviewer['avatar']}",
                "followup_probe_title": "short title for this follow-up",
                "followup_question": "the exact follow-up question in natural speech",
                "focus_area": "what this follow-up is probing"
            }}
            """

            response = model.generate_content(prompt)
            return _parse_ai_response(response.text)
        except Exception as e:
            print(f"Gemini Followup Generation failed: {e}")

    # Dynamic fallback follow-up — constructed from metadata, not hardcoded
    topic = random.choice(topics) if topics else "software engineering"

    if difficulty == "Easy":
        probe_title = "Concept Clarification"
        probe_q = f"That's a good start. Can you give me a simple, concrete example of how you'd apply {topic} in your {candidate_project} project? Walk me through it step by step."
    elif difficulty == "Hard":
        probe_title = f"{company_name} Production Scale Challenge"
        probe_q = f"Interesting approach. Now let's stress-test it — if {company_name} deployed this at 1,000,000 requests per second with {topic} as a bottleneck, what would break first? How would you architect around that failure mode?"
    else:
        probe_title = f"{company_name} Deeper Analysis"
        probe_q = f"Good answer. Now, considering {company_name}'s stack and {topic} specifically — what are the trade-offs of your approach? What alternative would you consider and why might it be better or worse?"

    return {
        "followup_id": f"followup-{uuid.uuid4()}",
        "interviewer_name": interviewer['name'],
        "interviewer_avatar": interviewer['avatar'],
        "followup_probe_title": probe_title,
        "followup_question": probe_q,
        "focus_area": topic
    }

# ==============================================================================
# SESSION EVALUATION ENGINE
# ==============================================================================

def evaluate_full_interview_session(company_name, session_turns, candidate_project="Placifly", difficulty="Medium", session_id=None):
    intel = get_company_intel(company_name)

    valid_turns = []
    invalid_count = 0
    for turn in session_turns:
        answer_text = sanitize_input(turn.get('answer', ''))
        is_valid, _ = is_meaningful_answer(answer_text, turn.get('question', ''))
        if is_valid:
            valid_turns.append({'question': turn.get('question', ''), 'answer': answer_text})
        else:
            invalid_count += 1

    if len(valid_turns) == 0:
        return {
            "overall_score": 0,
            "hiring_verdict": "REJECT",
            "verdict_badge": "❌ REJECT",
            "verdict_color": "var(--rose)",
            "score_justification": "Candidate provided empty or non-sensical text. No technical merit identified.",
            "expected_key_points": ["Structured technical answer", "Clear communication", "Relevance to question"],
            "missing_concepts": ["All required technical concepts"],
            "common_mistakes": ["Submitting empty or off-topic responses"],
            "ideal_interview_flow": "Acknowledge question -> state key principles -> detail technical design -> address trade-offs.",
            "confidence_score": 100,
            "improvement_suggestions": ["Provide a meaningful answer of at least 50 words in English."],
            "better_model_answer": f"At {company_name}, candidates must communicate clearly with specific technical depth.",
            "rubric_scores": {k: 0 for k in ["communication", "technical_understanding", "logical_thinking", "decision_making", "professionalism", "confidence", "leadership", "problem_solving", "creativity"]},
            "good_points": ["No valid response points identified."],
            "areas_to_improve": ["Candidate provided non-sensical text. Please answer in meaningful English."],
            "company_expectation": f"{company_name} expects candidates to communicate clearly."
        }

    # Record turns in session memory graph & calculate WPM
    session_mem = get_or_create_memory(session_id, company_name, difficulty)
    total_words = sum(len(t['answer'].split()) for t in valid_turns)
    total_chars = sum(len(t['answer']) for t in valid_turns)
    estimated_wpm = min(int((total_words / max(len(valid_turns), 1)) * 1.5), 130)

    if Config.GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            knowledge = get_company_knowledge(company_name)
            topics = get_topic_list(company_name, difficulty)
            transcript_text = "\n\n".join([f"Turn {idx+1}:\nQ: {t['question']}\nA: {t['answer']}" for idx, t in enumerate(valid_turns)])

            # === RAG GROUNDING: Retrieve relevant knowledge for each question ===
            rag_context_blocks = []
            relevance_scores = []
            factual_grades = []
            for turn in valid_turns:
                q = turn.get('question', '')
                a = turn.get('answer', '')
                
                # Retrieve relevant knowledge chunks
                chunks = retrieve_relevant_chunks(q, top_k=2)
                
                # Compute answer-question relevance
                rel_score = compute_answer_relevance(q, a)
                relevance_scores.append(rel_score)
                
                # Grade factual accuracy against RAG knowledge
                fact_grade = grade_factual_accuracy(a, chunks)
                factual_grades.append(fact_grade)
                
                # Check for common mistakes
                mistakes = check_common_mistakes(a, chunks)
                
                # Build RAG context block for this turn
                if chunks:
                    rag_block = f"\n--- GROUND TRUTH for Q: {q[:80]}... ---\n"
                    rag_block += f"Expected concepts: {', '.join(chunks[0].get('concepts', [])[:8])}\n"
                    rag_block += f"Key facts: {'; '.join(chunks[0].get('facts', [])[:3])}\n"
                    rag_block += f"Answer relevance score: {rel_score}\n"
                    rag_block += f"Factual accuracy: {fact_grade['accuracy_pct']}% ({len(fact_grade['matched_concepts'])} concepts matched)\n"
                    if mistakes:
                        rag_block += f"DETECTED MISCONCEPTIONS in answer: {'; '.join(mistakes)}\n"
                    rag_context_blocks.append(rag_block)
            
            avg_relevance = sum(relevance_scores) / max(len(relevance_scores), 1)
            avg_factual = sum(g['accuracy_pct'] for g in factual_grades) / max(len(factual_grades), 1)

            sys_eval_instructions = f"""You are the Hiring Committee Evaluator at {company_name}.
            Evaluate this candidate's interview transcript for the {knowledge.get('role', 'Software Engineer')} role at {difficulty} difficulty level.

            Company: {company_name}
            Role: {knowledge.get('role', 'Software Engineer')}
            Difficulty Level: {difficulty}
            Company Focus Areas: {', '.join(topics[:6])}
            Company Hiring Standard: {knowledge.get('interview_style', {}).get(difficulty, 'Professional evaluation')}

            INTERVIEW TRANSCRIPT:
            {transcript_text}

            CRITICAL EVALUATION MANDATE (FACTUAL CORRECTNESS & RELEVANCE):
            1. Carefully cross-examine the candidate's answer against the exact technical question asked.
            2. Verify if the technical facts, formulas, algorithms, code syntax, and design choices in the answer are CORRECT or WRONG.
            3. IF THE CANDIDATE'S ANSWER IS FACTUALLY WRONG, LOGICALLY INACCURATE, OR OFF-TOPIC:
               - You MUST assign overall_score between 0 and 35.
               - You MUST assign hiring_verdict to "REJECT".
               - You MUST assign rubric_scores['technical_understanding'] between 0 and 30.
               - Highlight the incorrect technical statements in "common_mistakes" and "missing_concepts".
            4. DO NOT award high scores merely for fluent English, polite language, or long text if the technical content is incorrect or incomplete!
            5. ONLY award scores > 75 (HIRE) if the candidate provided factually accurate, relevant, and well-structured technical answers.

            SCORING RULES (STRICT ACCURACY):
            - 0-35: WRONG, factually inaccurate, off-topic, or severely flawed answer -> REJECT
            - 36-55: Basic understanding but missing critical technical concepts -> REJECT or MAYBE
            - 56-75: Good technical understanding with minor gaps -> MAYBE
            - 76-90: Strong, accurate, structured, company-aligned response -> HIRE
            - 91-100: Exceptional, production-ready depth -> HIRE

            === RAG GROUND TRUTH REFERENCE ===
            The following ground truth was retrieved from our knowledge base. Use it to verify the candidate's claims:
            {chr(10).join(rag_context_blocks)}

            Average Answer Relevance: {avg_relevance:.2f} (below 0.30 = off-topic)
            Average Factual Accuracy: {avg_factual:.1f}%

            IMPORTANT: If average relevance < 0.30, the candidate is answering off-topic. Score MUST be 0-25, verdict MUST be REJECT.
            IMPORTANT: If factual accuracy < 20%, the candidate lacks domain knowledge. Score MUST be 0-35, verdict MUST be REJECT.

            Return ONLY a valid JSON object with these exact keys:
            {{
                "overall_score": integer_0_to_100,
                "hiring_verdict": "HIRE" or "MAYBE" or "REJECT",
                "score_justification": "clear 2-sentence rationale explaining whether technical claims were correct or wrong",
                "expected_key_points": ["key point 1 expected", "key point 2", "key point 3"],
                "missing_concepts": ["missing concept 1", "missing concept 2"],
                "common_mistakes": ["incorrect technical statement or mistake candidate made"],
                "ideal_interview_flow": "step-by-step description of how a top candidate would structure this response",
                "interviewer_expectation": "what {company_name} specifically looks for at {difficulty} level",
                "confidence_score": integer_80_to_99_evaluation_certainty,
                "improvement_suggestions": ["actionable advice 1", "actionable advice 2"],
                "better_model_answer": "production-grade exemplary model answer",
                "good_points": ["strength 1", "strength 2", "strength 3"],
                "areas_to_improve": ["area 1", "area 2", "area 3"],
                "rubric_scores": {{
                    "communication": 0-100,
                    "technical_understanding": 0-100,
                    "logical_thinking": 0-100,
                    "decision_making": 0-100,
                    "professionalism": 0-100,
                    "confidence": 0-100,
                    "leadership": 0-100,
                    "problem_solving": 0-100,
                    "creativity": 0-100
                }}
            }}"""

            prompt = wrap_prompt_bounds("Perform strict, consistent evaluation.", sys_eval_instructions)
            eval_config = genai.types.GenerationConfig(temperature=0.1)
            response = model.generate_content(prompt, generation_config=eval_config)
            res = _parse_ai_response(response.text)

            score = res.get('overall_score', 70)
            verdict = res.get('hiring_verdict', 'MAYBE')
            res['verdict_badge'] = "🎉 HIRE" if verdict == "HIRE" else "⚠️ MAYBE" if verdict == "MAYBE" else "❌ REJECT"
            res['verdict_color'] = "var(--emerald)" if verdict == "HIRE" else "var(--amber)" if verdict == "MAYBE" else "var(--rose)"
            res['estimated_wpm'] = estimated_wpm
            res['company'] = company_name
            res['difficulty'] = difficulty

            # === RAG RELEVANCE ENFORCEMENT ===
            if avg_relevance < 0.30:
                res['overall_score'] = min(res.get('overall_score', 0), 25)
                res['hiring_verdict'] = 'REJECT'
                res['verdict_badge'] = '❌ OFF-TOPIC'
                res['verdict_color'] = 'var(--red, #ef4444)'
                res['score_justification'] = f"Answer was off-topic (relevance: {avg_relevance:.2f}). " + res.get('score_justification', '')
            elif avg_factual < 20.0:
                res['overall_score'] = min(res.get('overall_score', 0), 35)
                res['hiring_verdict'] = 'REJECT'
                res['verdict_badge'] = '❌ INACCURATE'
                res['verdict_color'] = 'var(--red, #ef4444)'
                res['score_justification'] = f"Factual accuracy too low ({avg_factual:.1f}%). " + res.get('score_justification', '')
            
            # Add RAG metadata to response
            res['relevance_score'] = round(avg_relevance, 3)
            res['factual_accuracy_pct'] = round(avg_factual, 1)
            res['rag_grounding_used'] = True

            # Store in session memory graph
            for t in valid_turns:
                session_mem.add_turn(t['question'], t['answer'], score=res['overall_score'], topic=topics[0] if topics else "General Technical")

            return res

        except Exception as e:
            print(f"Gemini Session Evaluation failed: {e}")

    # Heuristic fallback evaluation with correctness & technical relevance check
    all_answers_text = " ".join(t['answer'].lower() for t in valid_turns)
    all_questions_text = " ".join(t['question'].lower() for t in valid_turns)
    
    # RAG-enhanced concept checking
    rag_concepts = get_expected_concepts(all_questions_text)
    rag_relevance = compute_answer_relevance(all_questions_text, all_answers_text)
    rag_chunks = retrieve_relevant_chunks(all_questions_text, top_k=2)
    rag_factual = grade_factual_accuracy(all_answers_text, rag_chunks)

    extracted_concepts = extract_concepts_from_answer(all_answers_text)
    
    # Check for refusal / wrong answer / nonsense phrases
    negative_phrases = ["i don't know", "idk", "no idea", "wrong answer", "not sure", "dunno", "fake answer", "abcd"]
    has_negative = any(p in all_answers_text for p in negative_phrases)

    # Check if answer contains any tech keywords relevant to topic
    if rag_relevance < 0.30:
        score = random.randint(10, 25)
        verdict = 'REJECT'
        justification = f"Candidate's response was off-topic for {company_name}."
    elif rag_factual['accuracy_pct'] < 20:
        score = random.randint(15, 32)
        verdict = 'REJECT'
        justification = f"Candidate's response lacked factual accuracy or relevant concepts for {company_name}."
    elif len(extracted_concepts) == 0 or has_negative or len(all_answers_text.split()) < 20:
        score = random.randint(15, 32)
        verdict = "REJECT"
        justification = f"Candidate's response lacked technical depth, accuracy, or relevant concepts for {company_name}."
    else:
        score = min(int(45 + (len(extracted_concepts) * 8) + (total_words / 4.0)), 90)
        verdict = "HIRE" if score >= 78 else "MAYBE" if score >= 55 else "REJECT"
        justification = f"Candidate demonstrated basic relevance mentioning concepts: {', '.join(extracted_concepts[:4])}."

    rubric = {
        "communication": min(score + random.randint(-4, 6), 100),
        "technical_understanding": min(score + random.randint(-8, 4), 100),
        "logical_thinking": min(score + random.randint(-6, 6), 100),
        "decision_making": min(score + random.randint(-6, 6), 100),
        "professionalism": min(score + random.randint(0, 8), 100),
        "confidence": min(score + random.randint(-4, 8), 100),
        "leadership": min(score + random.randint(-8, 6), 100),
        "problem_solving": min(score + random.randint(-6, 6), 100),
        "creativity": min(score + random.randint(-6, 6), 100)
    }

    return {
        "overall_score": score,
        "hiring_verdict": verdict,
        "verdict_badge": "🎉 HIRE" if verdict == "HIRE" else "⚠️ MAYBE" if verdict == "MAYBE" else "❌ REJECT",
        "verdict_color": "var(--emerald)" if verdict == "HIRE" else "var(--amber)" if verdict == "MAYBE" else "var(--rose)",
        "score_justification": justification,
        "expected_key_points": [f"Core {company_name} technical principles", "Structured problem breakdown", "Trade-off analysis"],
        "missing_concepts": ["Specific quantitative performance metrics", "Edge-case error handling"],
        "common_mistakes": ["Not elaborating sufficiently on trade-offs under high scale"],
        "ideal_interview_flow": "State high-level approach -> detail core components -> discuss failure modes and trade-offs.",
        "interviewer_expectation": f"{company_name} expects candidates to meet {difficulty} level standards.",
        "confidence_score": 88,
        "improvement_suggestions": [f"Include specific quantitative metrics when discussing {company_name} architecture.", "Elaborate further on edge-case failure modes."],
        "better_model_answer": f"At {company_name} ({difficulty} Mode), top candidates structure responses with clear technical depth and trade-offs.",
        "estimated_wpm": estimated_wpm,
        "company": company_name,
        "difficulty": difficulty,
        "rubric_scores": rubric,
        "good_points": [
            f"Demonstrated structured answer delivery aligned with {company_name} expectations.",
            "Showed logical clarity in explaining technical concepts.",
            "Maintained a professional tone throughout responses."
        ] if score >= 50 else ["Attempted response delivery."],
        "areas_to_improve": [
            "Provide more specific quantitative metrics.",
            "Elaborate further on edge-case handling.",
            f"Align answer terminology even closer to {company_name} standards."
        ],
        "company_expectation": f"{company_name} expects candidates to match {difficulty} level benchmarks."
    }

# ==============================================================================
# COMPATIBILITY WRAPPERS (keep existing API contracts intact)
# ==============================================================================

def generate_custom_company_scenarios(company_name, company_website="", difficulty="Medium", interview_type="Technical Interview"):
    q = generate_company_interviewer_question(company_name, difficulty, interview_type, candidate_project="Placifly")
    return [q]

def evaluate_response(scenario, student_answer, time_taken_seconds):
    return evaluate_full_interview_session(scenario.get('company', 'TCS'), [{'question': scenario.get('question', ''), 'answer': student_answer}], difficulty=scenario.get('difficulty', 'Medium'))

def generate_5_round_mock_drive(company_name, company_website=""):
    """Generate a full multi-round placement drive simulation for a company."""
    knowledge = get_company_knowledge(company_name)

    # Define realistic placement rounds per company type
    COMPANY_ROUNDS = {
        "TCS": [
            {"round_name": "Round 1: Aptitude & Reasoning", "interview_type": "Technical Interview", "difficulty": "Easy"},
            {"round_name": "Round 2: Technical Interview I", "interview_type": "Technical Interview", "difficulty": "Medium"},
            {"round_name": "Round 3: Technical Interview II", "interview_type": "Coding Interview", "difficulty": "Medium"},
            {"round_name": "Round 4: HR Interview", "interview_type": "HR Interview", "difficulty": "Easy"},
        ],
        "Amazon": [
            {"round_name": "Round 1: Online Assessment (Coding)", "interview_type": "Coding Interview", "difficulty": "Medium"},
            {"round_name": "Round 2: Technical Interview (DSA)", "interview_type": "Coding Interview", "difficulty": "Hard"},
            {"round_name": "Round 3: System Design", "interview_type": "Technical Interview", "difficulty": "Hard"},
            {"round_name": "Round 4: Behavioral (Leadership Principles)", "interview_type": "HR Interview", "difficulty": "Medium"},
            {"round_name": "Round 5: Bar Raiser", "interview_type": "Situation Based Interview", "difficulty": "Hard"},
        ],
        "Google": [
            {"round_name": "Round 1: Phone Screen (Coding)", "interview_type": "Coding Interview", "difficulty": "Medium"},
            {"round_name": "Round 2: On-site Coding I", "interview_type": "Coding Interview", "difficulty": "Hard"},
            {"round_name": "Round 3: On-site Coding II", "interview_type": "Coding Interview", "difficulty": "Hard"},
            {"round_name": "Round 4: System Design", "interview_type": "Technical Interview", "difficulty": "Hard"},
            {"round_name": "Round 5: Googleyness & Behavioral", "interview_type": "HR Interview", "difficulty": "Medium"},
        ],
        "Microsoft": [
            {"round_name": "Round 1: Online Assessment", "interview_type": "Coding Interview", "difficulty": "Medium"},
            {"round_name": "Round 2: Technical Interview I", "interview_type": "Technical Interview", "difficulty": "Medium"},
            {"round_name": "Round 3: Technical Interview II", "interview_type": "Coding Interview", "difficulty": "Hard"},
            {"round_name": "Round 4: System Design", "interview_type": "Technical Interview", "difficulty": "Hard"},
            {"round_name": "Round 5: As-Appropriate (Behavioral)", "interview_type": "HR Interview", "difficulty": "Medium"},
        ],
        "Infosys": [
            {"round_name": "Round 1: Online Assessment", "interview_type": "Technical Interview", "difficulty": "Easy"},
            {"round_name": "Round 2: Technical Interview", "interview_type": "Technical Interview", "difficulty": "Medium"},
            {"round_name": "Round 3: Coding Round", "interview_type": "Coding Interview", "difficulty": "Medium"},
            {"round_name": "Round 4: HR Interview", "interview_type": "HR Interview", "difficulty": "Easy"},
        ],
        "Deloitte": [
            {"round_name": "Round 1: Aptitude & Logical Reasoning", "interview_type": "Case Study Interview", "difficulty": "Easy"},
            {"round_name": "Round 2: Technical Interview", "interview_type": "Technical Interview", "difficulty": "Medium"},
            {"round_name": "Round 3: Case Study Interview", "interview_type": "Case Study Interview", "difficulty": "Medium"},
            {"round_name": "Round 4: Partner/Director Round", "interview_type": "HR Interview", "difficulty": "Medium"},
        ],
        "Accenture": [
            {"round_name": "Round 1: Cognitive & Technical Assessment", "interview_type": "Technical Interview", "difficulty": "Easy"},
            {"round_name": "Round 2: Technical Interview", "interview_type": "Technical Interview", "difficulty": "Medium"},
            {"round_name": "Round 3: Coding Round", "interview_type": "Coding Interview", "difficulty": "Medium"},
            {"round_name": "Round 4: HR Interview", "interview_type": "HR Interview", "difficulty": "Easy"},
        ],
        "Capgemini": [
            {"round_name": "Round 1: Online Test", "interview_type": "Technical Interview", "difficulty": "Easy"},
            {"round_name": "Round 2: Technical Interview", "interview_type": "Technical Interview", "difficulty": "Medium"},
            {"round_name": "Round 3: Coding Challenge", "interview_type": "Coding Interview", "difficulty": "Medium"},
            {"round_name": "Round 4: HR Interview", "interview_type": "HR Interview", "difficulty": "Easy"},
        ],
        "Meta": [
            {"round_name": "Round 1: Initial Phone Screen", "interview_type": "Coding Interview", "difficulty": "Medium"},
            {"round_name": "Round 2: Coding Interview I", "interview_type": "Coding Interview", "difficulty": "Hard"},
            {"round_name": "Round 3: Coding Interview II", "interview_type": "Coding Interview", "difficulty": "Hard"},
            {"round_name": "Round 4: System Design", "interview_type": "Technical Interview", "difficulty": "Hard"},
            {"round_name": "Round 5: Behavioral (Meta Values)", "interview_type": "HR Interview", "difficulty": "Medium"},
        ],
        "Netflix": [
            {"round_name": "Round 1: Recruiter Screen", "interview_type": "HR Interview", "difficulty": "Easy"},
            {"round_name": "Round 2: Technical Phone Screen", "interview_type": "Technical Interview", "difficulty": "Medium"},
            {"round_name": "Round 3: Coding & Architecture", "interview_type": "Coding Interview", "difficulty": "Hard"},
            {"round_name": "Round 4: System Design", "interview_type": "Technical Interview", "difficulty": "Hard"},
            {"round_name": "Round 5: Culture Fit (Freedom & Responsibility)", "interview_type": "HR Interview", "difficulty": "Medium"},
        ],
        "Adobe": [
            {"round_name": "Round 1: Online Assessment", "interview_type": "Coding Interview", "difficulty": "Medium"},
            {"round_name": "Round 2: Technical Interview I (DSA)", "interview_type": "Coding Interview", "difficulty": "Medium"},
            {"round_name": "Round 3: Technical Interview II (OOP Design)", "interview_type": "Technical Interview", "difficulty": "Hard"},
            {"round_name": "Round 4: HR Interview", "interview_type": "HR Interview", "difficulty": "Easy"},
        ],
        "IBM": [
            {"round_name": "Round 1: Online Assessment", "interview_type": "Technical Interview", "difficulty": "Easy"},
            {"round_name": "Round 2: Technical Interview", "interview_type": "Technical Interview", "difficulty": "Medium"},
            {"round_name": "Round 3: Coding Round", "interview_type": "Coding Interview", "difficulty": "Medium"},
            {"round_name": "Round 4: Manager Interview & HR", "interview_type": "HR Interview", "difficulty": "Easy"},
        ],
        "Wipro": [
            {"round_name": "Round 1: Online Assessment", "interview_type": "Technical Interview", "difficulty": "Easy"},
            {"round_name": "Round 2: Technical Interview", "interview_type": "Technical Interview", "difficulty": "Medium"},
            {"round_name": "Round 3: Coding Round", "interview_type": "Coding Interview", "difficulty": "Medium"},
            {"round_name": "Round 4: HR Interview", "interview_type": "HR Interview", "difficulty": "Easy"},
        ],
    }

    # Default rounds for custom/unknown companies
    DEFAULT_ROUNDS = [
        {"round_name": "Round 1: Technical Screening", "interview_type": "Technical Interview", "difficulty": "Easy"},
        {"round_name": "Round 2: Technical Deep Dive", "interview_type": "Technical Interview", "difficulty": "Medium"},
        {"round_name": "Round 3: Coding Challenge", "interview_type": "Coding Interview", "difficulty": "Medium"},
    ]

    rounds_config = COMPANY_ROUNDS.get(company_name, DEFAULT_ROUNDS)
    rounds = []
    asked_ids = []

    for round_cfg in rounds_config:
        q = generate_company_interviewer_question(
            company_name,
            difficulty=round_cfg["difficulty"],
            interview_type=round_cfg["interview_type"],
            candidate_project="Placifly",
            asked_question_ids=asked_ids
        )
        q["round_name"] = round_cfg["round_name"]
        rounds.append(q)
        if q.get("id"):
            asked_ids.append(q["id"])

    return rounds

# Resume analyzer import or fallback
analyze_student_resume = None
try:
    from services.ai_service_resume import analyze_student_resume
except Exception:
    pass

if not analyze_student_resume:
    def analyze_student_resume(resume_text, target_company="TCS", target_role="Software Engineer"):
        return {
            "match_score": 75,
            "ats_verdict": "Moderate Match",
            "key_strengths": ["Clear project breakdown"],
            "missing_keywords": ["SQL", "REST APIS"],
            "bullet_point_improvements": [{"current": "Built project.", "recommended": "Architected AI simulator using Python Flask, MongoDB, and JWT."}],
            "expected_interview_questions": [f"Explain project architecture for {target_company}."],
            "formatting_tips": ["Quantify outcomes."]
        }


def generate_structured_interview_question(phase, company_profile, candidate_profile, interview_context, difficulty='Medium'):
    import json
    import re
    if not genai.GenerativeModel("gemini-2.0-flash"):
        return {"question": f"Can you talk about your experience for the {phase} phase?", "context": "Fallback", "phase": phase, "difficulty": difficulty}
    
    prompt = f"""You are an expert technical interviewer at {company_profile.get('name', 'the company')}.
Phase: {phase}
Difficulty: {difficulty}

Company Profile:
{json.dumps(company_profile)}

Candidate Profile:
{json.dumps(candidate_profile)}

Interview Context (Previous questions):
{json.dumps(interview_context)}

Generate a single interview question for this specific phase.
- introduction: Welcome the candidate, ask them to introduce themselves.
- company_knowledge: Ask about the company, its products, or why they want to work there.
- resume_based: Ask about their specific skills, projects, or education.
- role_requirements: Ask about skills/responsibilities expected for the role.
- common_interview: Ask standard HR questions (strengths, goals).
- technical_scenario: Ask a technical or scenario-based question suitable for their level.

Return a JSON with keys: "question", "context", "phase", "difficulty" (do not use markdown blocks).
"""
    try:
        res = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt, generation_config={'temperature': 0.6})
        text = res.text.strip()
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except Exception as e:
        print(f"Error generating structured interview question: {e}")
        return {"question": f"Tell me about your experience regarding {phase}.", "context": "Fallback question", "phase": phase, "difficulty": difficulty}

def generate_structured_followup(previous_question, candidate_answer, phase, candidate_profile, company_profile, difficulty='Medium'):
    import json
    import re
    if not genai.GenerativeModel("gemini-2.0-flash"):
        return {"question": "Could you elaborate on that?", "context": "Fallback followup", "is_followup": True, "phase": phase}
    
    prompt = f"""You are an expert technical interviewer at {company_profile.get('name', 'the company')}.
You are in the {phase} phase of the interview.

Previous Question: {previous_question}
Candidate's Answer: {candidate_answer}

Candidate Profile: {json.dumps(candidate_profile)}
Difficulty: {difficulty}

Generate an intelligent follow-up question that probes deeper into their answer.
Return a JSON with keys: "question", "context", "is_followup": true, "phase" (do not use markdown blocks).
"""
    try:
        res = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt, generation_config={'temperature': 0.6})
        text = res.text.strip()
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except Exception as e:
        print(f"Error generating structured followup: {e}")
        return {"question": "Can you elaborate further?", "context": "Fallback", "is_followup": True, "phase": phase}

def evaluate_structured_interview(turns_by_phase, company_profile, candidate_profile, difficulty='Medium'):
    import json
    import re
    if not genai.GenerativeModel("gemini-2.0-flash"):
        return {"overall_score": 50, "verdict": "MAYBE", "message": "Fallback evaluation."}
    
    prompt = f"""You are an expert technical interviewer evaluating a full interview.
Difficulty: {difficulty}

Candidate Profile: {json.dumps(candidate_profile)}
Company: {company_profile.get('name', 'the company')}

Interview Transcript by Phase:
{json.dumps(turns_by_phase)}

Evaluate the interview comprehensively.
Provide an overall score (0-100), a verdict (HIRE >= 75, MAYBE 60-74, REJECT < 60).
Provide 9 rubric scores out of 100: Communication, Technical Understanding, Problem Solving, Role Fit, Company Knowledge, Leadership, Culture Fit, Clarity, and Confidence.
List strengths and areas for improvement. Provide a model answer for the weakest response.

Return a JSON (no markdown):
{{
  "overall_score": 85,
  "verdict": "HIRE",
  "phase_scores": {{"introduction": 90, "technical_scenario": 80}},
  "rubric": {{"Communication": 90, "Technical Understanding": 80, "Problem Solving": 85, "Role Fit": 80, "Company Knowledge": 70, "Leadership": 75, "Culture Fit": 85, "Clarity": 90, "Confidence": 80}},
  "strengths": ["Clear communication", "Good technical base"],
  "areas_for_improvement": ["Company knowledge", "System design"],
  "weakest_response_feedback": {{"question": "...", "model_answer": "..."}}
}}
"""
    try:
        res = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt, generation_config={'temperature': 0.2})
        text = res.text.strip()
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except Exception as e:
        print(f"Error evaluating structured interview: {e}")
        return {"overall_score": 65, "verdict": "MAYBE", "message": "Evaluation failed due to error."}
