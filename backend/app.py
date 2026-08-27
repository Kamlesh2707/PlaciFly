from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
import os
import random
from services.scenario_db import get_companies, get_fresh_scenarios, get_company_prep_data, get_company_intel, refresh_company_intel_cache
from services.ai_service import evaluate_response, generate_custom_company_scenarios, generate_5_round_mock_drive, analyze_student_resume, generate_company_interviewer_question, generate_adaptive_followup, evaluate_full_interview_session, get_interviewer_for_difficulty
from data.gamification import calculate_xp, check_new_badges, calculate_level
from services.auth_service import generate_otp, verify_otp, send_otp_email, create_anonymous_session
from services.resume_parser import parse_resume_skills, get_skills_summary_for_prompt, get_resume_analysis_summary
from services.puzzle_bank import get_puzzles_for_interview, get_puzzle_by_id, get_puzzle_count

from services.security import rate_limiter, sanitize_input
from services.company_analyzer import analyze_company_text
from services.ai_service import generate_structured_interview_question, generate_structured_followup, evaluate_structured_interview


app = Flask(__name__, static_folder='../frontend')
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

@app.before_request
def enforce_rate_limiting():
    """Enforce sliding window rate limiting on API endpoints."""
    if request.path.startswith('/api/'):
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1').split(',')[0].strip()
        if not rate_limiter.is_allowed(client_ip):
            return jsonify({
                "error": "Too Many Requests",
                "message": "Rate limit exceeded (Max 40 requests per minute). Please slow down."
            }), 429

@app.route('/api/companies', methods=['GET'])
def api_get_companies():
    return jsonify({"companies": get_companies()})

@app.route('/api/company-intel/<company_name>', methods=['GET'])
def api_get_company_intel(company_name):
    intel = get_company_intel(company_name)
    return jsonify({"intel": intel})

@app.route('/api/company/analyze-url', methods=['POST'])
def api_analyze_company_url():
    data = request.json or {}
    url = sanitize_input(data.get('url', '').strip())
    if not url:
        return jsonify({"error": "Please provide a company website URL or domain."}), 400
    
    from services.company_analyzer import analyze_company_url
    analysis = analyze_company_url(url)
    return jsonify({"analysis": analysis})


@app.route('/api/interviewer/start-session', methods=['POST'])
def api_interviewer_start_session():
    data = request.json or {}
    company_name = data.get('company', 'TCS')
    difficulty = data.get('difficulty', 'Medium')
    interview_type = data.get('interview_type', 'Technical Interview')
    candidate_project = data.get('candidate_project', 'Placifly')
    candidate_skills = data.get('candidate_skills', '')
    asked_ids = data.get('asked_ids', [])
    session_id = data.get('session_id', f"session-{random.randint(10000,99999)}")

    intel = get_company_intel(company_name)
    interviewer = get_interviewer_for_difficulty(intel, difficulty)
    question = generate_company_interviewer_question(
        company_name, difficulty, interview_type, candidate_project,
        asked_ids, candidate_skills=candidate_skills, session_id=session_id
    )

    return jsonify({
        "session_id": session_id,
        "company": company_name,
        "difficulty": difficulty,
        "interviewer": interviewer,
        "initial_question": question
    })

@app.route('/api/interviewer/next-question', methods=['POST'])
def api_interviewer_next_question():
    data = request.json or {}
    company_name = data.get('company', 'TCS')
    previous_question = data.get('previous_question', '')
    candidate_answer = data.get('candidate_answer', '')
    candidate_project = data.get('candidate_project', 'Placifly')
    candidate_skills = data.get('candidate_skills', '')
    difficulty = data.get('difficulty', 'Medium')
    interview_type = data.get('interview_type', 'Technical Interview')
    asked_ids = data.get('asked_ids', [])
    session_id = data.get('session_id', 'global')
    turn_count = data.get('turn_count', 1)

    if turn_count % 2 == 1 and previous_question and candidate_answer:
        followup = generate_adaptive_followup(company_name, previous_question, candidate_answer, candidate_project, difficulty)
        return jsonify({"type": "followup", "question": followup})
    else:
        question = generate_company_interviewer_question(
            company_name, difficulty, interview_type, candidate_project,
            asked_ids, candidate_skills=candidate_skills, session_id=session_id
        )
        return jsonify({"type": "new_question", "question": question})

@app.route('/api/interviewer/evaluate-session', methods=['POST'])
def api_interviewer_evaluate_session():
    data = request.json or {}
    company_name = sanitize_input(data.get('company', 'TCS'))
    session_turns = data.get('turns', [])
    candidate_project = sanitize_input(data.get('candidate_project', 'Placifly'))
    difficulty = sanitize_input(data.get('difficulty', 'Medium'))
    session_id = data.get('session_id')

    evaluation = evaluate_full_interview_session(company_name, session_turns, candidate_project, difficulty, session_id=session_id)
    return jsonify({"evaluation": evaluation})

@app.route('/api/scenarios/fetch', methods=['POST'])
def api_fetch_scenarios():
    data = request.json or {}
    company = data.get('company', 'TCS')
    difficulty = data.get('difficulty', 'Medium')
    interview_type = data.get('interview_type', 'Technical Interview')
    custom_website = data.get('custom_website')

    if company and company not in [c['name'] for c in get_companies()]:
        scenarios = generate_custom_company_scenarios(company, custom_website, difficulty, interview_type)
        return jsonify({"scenarios": scenarios})

    scenarios = get_fresh_scenarios(company, difficulty, interview_type)
    return jsonify({"scenarios": scenarios})

@app.route('/api/custom-company/scenarios', methods=['POST'])
def api_custom_company_scenarios():
    data = request.json or {}
    company_name = data.get('company_name', 'Custom Corp')
    company_website = data.get('company_website', '')
    difficulty = data.get('difficulty', 'Medium')
    interview_type = data.get('interview_type', 'Technical Interview')

    scenarios = generate_custom_company_scenarios(company_name, company_website, difficulty, interview_type)
    return jsonify({"scenarios": scenarios})

@app.route('/api/mock-drive/start', methods=['POST'])
def api_start_mock_drive():
    data = request.json or {}
    company_name = data.get('company_name', 'TCS')
    company_website = data.get('company_website', '')

    rounds = generate_5_round_mock_drive(company_name, company_website)
    return jsonify({"company": company_name, "rounds": rounds, "total_rounds": len(rounds) if isinstance(rounds, list) else 1})

@app.route('/api/company-prep/<company_name>', methods=['GET'])
def api_get_company_prep(company_name):
    prep_data = get_company_prep_data(company_name)
    return jsonify({"prep": prep_data})

@app.route('/api/resume/analyze', methods=['POST'])
def api_resume_analyze():
    data = request.json or {}
    resume_text = data.get('resume_text', '')
    target_company = data.get('target_company', 'TCS')
    target_role = data.get('target_role', 'Software Engineer')

    if not resume_text.strip():
        return jsonify({"error": "Please provide your resume text for analysis."}), 400

    analysis = analyze_student_resume(resume_text, target_company, target_role)
    return jsonify({"analysis": analysis})

@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    data = request.json or {}
    student_answer = data.get('answer', '')
    time_taken = data.get('time_taken', 120)

    scenario = {
        "id": data.get('scenario_id', 'dynamic-scenario'),
        "company": data.get('company', 'Target Company'),
        "category": data.get('category', 'Technical'),
        "difficulty": data.get('difficulty', 'Medium'),
        "interview_type": data.get('interview_type', 'Technical Interview'),
        "situation": data.get('situation', 'Interview situation'),
        "question": data.get('question', 'How would you handle this scenario?'),
        "ideal_approach": data.get('ideal_approach', 'Structured problem solving.'),
        "estimated_time": 300,
        "skills_tested": ["Communication", "Problem Solving", "Technical Understanding"]
    }

    evaluation = evaluate_response(scenario, student_answer, time_taken)
    return jsonify({"evaluation": evaluation})

@app.route('/api/assessment/complete', methods=['POST'])
def api_assessment_complete():
    data = request.json or {}
    results = data.get('results', [])
    current_badges = data.get('current_badges', [])

    total_score = 0
    total_xp = 0
    session_stats = {"total_completed": len(results), "best_score": 0}

    for res in results:
        score = res.get('scores', {}).get('overall_score', 0)
        total_score += score
        xp_earned = calculate_xp('Medium', score)
        total_xp += xp_earned
        session_stats["best_score"] = max(session_stats["best_score"], score)

    avg_score = total_score / len(results) if results else 0
    session_stats["average_score"] = avg_score
    session_stats["total_xp"] = total_xp

    new_badges = check_new_badges(session_stats, current_badges)
    company_readiness = min(100, int(avg_score * 1.1))
    placement_readiness = "High" if avg_score > 85 else "Medium" if avg_score > 60 else "Low"

    report = {
        "overall_score": round(avg_score, 2),
        "strengths": ["Communication", "Problem Solving"],
        "weaknesses": ["Time Management"],
        "company_readiness_percent": company_readiness,
        "placement_readiness": placement_readiness,
        "skill_improvement_plan": "Practice structured problem solving.",
        "xp_earned": total_xp,
        "new_badges": new_badges
    }

    return jsonify({"report": report})

# ===========================
# AUTH ROUTES
# ===========================

@app.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    data = request.json or {}
    name = sanitize_input(data.get('name', '').strip())
    email = sanitize_input(data.get('email', '').strip())
    password = data.get('password', '').strip()
    
    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email, and password are required."}), 400
    
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400
    
    from services.auth_service import register_user_initiate
    result = register_user_initiate(name, email, password)
    return jsonify(result)

@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    data = request.json or {}
    email = sanitize_input(data.get('email', '').strip())
    password = data.get('password', '').strip()
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400
    
    from services.auth_service import login_user
    result = login_user(email, password)
    return jsonify(result)

@app.route('/api/auth/send-otp', methods=['POST'])
def api_send_otp():
    data = request.json or {}
    email = sanitize_input(data.get('email', '').strip())
    purpose = sanitize_input(data.get('purpose', 'Verification').strip())
    
    if not email or '@' not in email:
        return jsonify({"error": "Please provide a valid email address."}), 400
    
    from services.auth_service import generate_otp, send_otp_email
    otp = generate_otp(email, purpose=purpose)
    result = send_otp_email(email, otp, purpose=purpose)
    return jsonify(result)

@app.route('/api/auth/verify-otp', methods=['POST'])
def api_verify_otp():
    data = request.json or {}
    email = sanitize_input(data.get('email', '').strip())
    otp = data.get('otp', '').strip()
    
    if not email or not otp:
        return jsonify({"success": False, "message": "Email and OTP are required."}), 400
    
    from services.auth_service import verify_registration_otp
    result = verify_registration_otp(email, otp)
    return jsonify(result)

@app.route('/api/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    data = request.json or {}
    email = sanitize_input(data.get('email', '').strip())
    if not email:
        return jsonify({"success": False, "message": "Email is required."}), 400
    
    from services.auth_service import request_password_reset
    result = request_password_reset(email)
    return jsonify(result)

@app.route('/api/auth/reset-password', methods=['POST'])
def api_reset_password():
    data = request.json or {}
    email = sanitize_input(data.get('email', '').strip())
    otp = data.get('otp', '').strip()
    new_password = data.get('new_password', '').strip()
    
    if not email or not otp or not new_password:
        return jsonify({"success": False, "message": "Email, OTP, and new password are required."}), 400
    
    from services.auth_service import complete_password_reset
    result = complete_password_reset(email, otp, new_password)
    return jsonify(result)

@app.route('/api/auth/skip', methods=['POST'])
def api_auth_skip():
    from services.auth_service import create_anonymous_session
    result = create_anonymous_session()
    return jsonify(result)

# ===========================
# PLACE DISCOVERY ROUTES
# ===========================

@app.route('/api/places', methods=['GET'])
def api_get_places():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    price_level = request.args.get('price_level', '')
    min_rating = float(request.args.get('rating', 0.0))
    tags = request.args.get('tags', '')
    
    from services.place_service import search_places
    places = search_places(query=query, category=category, city=city, price_level=price_level, min_rating=min_rating, tags=tags)
    return jsonify({"places": places, "count": len(places)})

@app.route('/api/places/<place_id>', methods=['GET'])
def api_get_place(place_id):
    from services.place_service import get_place_by_id
    place = get_place_by_id(place_id)
    if not place:
        return jsonify({"error": "Place not found."}), 404
    return jsonify({"place": place})

@app.route('/api/places/categories', methods=['GET'])
def api_get_place_categories():
    from services.place_service import get_categories
    return jsonify({"categories": get_categories()})

@app.route('/api/places/favorite', methods=['POST'])
def api_toggle_favorite():
    data = request.json or {}
    email = sanitize_input(data.get('email', '').strip())
    place_id = sanitize_input(data.get('place_id', '').strip())
    
    if not email or not place_id:
        return jsonify({"success": False, "message": "Email and place_id required."}), 400
    
    from services.auth_service import toggle_user_favorite
    result = toggle_user_favorite(email, place_id)
    return jsonify(result)

@app.route('/api/places/favorites', methods=['GET'])
def api_get_favorites():
    email = sanitize_input(request.args.get('email', '').strip())
    if not email:
        return jsonify({"favorites": []})
    
    from services.auth_service import get_user_favorites
    fav_ids = get_user_favorites(email)
    from services.place_service import get_place_by_id
    fav_places = [get_place_by_id(pid) for pid in fav_ids if get_place_by_id(pid)]
    return jsonify({"favorites": fav_places, "ids": fav_ids})

# ===========================
# RESUME PARSING ROUTE
# ===========================

@app.route('/api/resume/parse-skills', methods=['POST'])
def api_parse_resume_skills():
    resume_text = ""
    
    if 'file' in request.files or 'resume_file' in request.files:
        file = request.files.get('file') or request.files.get('resume_file')
        if file and file.filename:
            filename = file.filename.lower()
            if filename.endswith('.pdf'):
                from services.resume_parser import extract_text_from_pdf
                resume_text = extract_text_from_pdf(file.read())
            else:
                try:
                    resume_text = file.read().decode('utf-8', errors='ignore')
                except Exception:
                    resume_text = ""
    
    if not resume_text and request.is_json:
        data = request.json or {}
        resume_text = data.get('resume_text', '')
    elif not resume_text and request.form:
        resume_text = request.form.get('resume_text', '')
    
    if not resume_text or not resume_text.strip():
        return jsonify({"error": "Please provide your resume text or upload a valid PDF file."}), 400
    
    from services.resume_parser import parse_resume_skills
    profile = parse_resume_skills(resume_text)
    return jsonify({"profile": profile, "extracted_length": len(resume_text), "preview": resume_text[:200]})

# ===========================
# PUZZLE BANK ROUTES
# ===========================

@app.route('/api/puzzles/get', methods=['POST'])
def api_get_puzzles():
    data = request.json or {}
    difficulty = data.get('difficulty', 'Medium')
    count = min(data.get('count', 1), 5)
    
    puzzles = get_puzzles_for_interview(difficulty, count)
    safe_puzzles = []
    for p in puzzles:
        safe_puzzles.append({
            'id': p['id'],
            'title': p['title'],
            'description': p['description'],
            'difficulty': p['difficulty'],
            'category': p['category'],
            'time_limit': p.get('time_limit', 180)
        })
    return jsonify({"puzzles": safe_puzzles})

@app.route('/api/puzzles/evaluate', methods=['POST'])
def api_evaluate_puzzle():
    data = request.json or {}
    puzzle_id = data.get('puzzle_id', '')
    candidate_answer = data.get('answer', '')
    
    puzzle = get_puzzle_by_id(puzzle_id)
    if not puzzle:
        return jsonify({"error": "Puzzle not found."}), 404
    
    from services.ai_service import evaluate_response
    scenario = {
        "id": puzzle_id,
        "company": "Interview",
        "category": "Situational / Puzzle",
        "difficulty": puzzle['difficulty'],
        "interview_type": "Situational Round",
        "situation": puzzle['description'],
        "question": puzzle['title'],
        "ideal_approach": puzzle['solution'],
        "estimated_time": puzzle.get('time_limit', 180),
        "skills_tested": ["Logical Thinking", "Problem Solving", "Structured Reasoning"]
    }
    evaluation = evaluate_response(scenario, candidate_answer, 120)
    return jsonify({"evaluation": evaluation})

# ===========================
# CODE EVALUATION ROUTE (RIGOROUS)
# ===========================

@app.route('/api/interviewer/evaluate-code', methods=['POST'])
def api_evaluate_code():
    data = request.json or {}
    question = data.get('question', '')
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    from services.code_evaluator import evaluate_code_rigorous
    evaluation = evaluate_code_rigorous(question, code, language)
    return jsonify({"evaluation": evaluation})


# ===========================
# STATIC FILE SERVING
# ===========================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
        return "Frontend not found.", 404


# ===========================
# STRUCTURED INTERVIEW ENDPOINTS
# ===========================
import uuid

@app.route('/api/company/analyze-text', methods=['POST'])
def api_analyze_company_text():
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({"error": "Company information text is required"}), 400
    text = sanitize_input(text)
    from services.company_analyzer import analyze_company_text
    analysis = analyze_company_text(text)
    return jsonify({"analysis": analysis})

@app.route('/api/interview/structured/start', methods=['POST'])
def api_structured_interview_start():
    data = request.get_json()
    company_profile = data.get('company_profile', {})
    candidate_profile = data.get('candidate_profile', {})
    interview_type = data.get('interview_type', 'normal')
    difficulty = data.get('difficulty', 'Medium')
    
    session_id = str(uuid.uuid4())
    
    # Using existing gamification/interviewer logic
    from services.ai_service import get_interviewer_for_difficulty
    interviewer = get_interviewer_for_difficulty({}, difficulty)
    
    question_data = generate_structured_interview_question(
        'introduction', company_profile, candidate_profile, [], difficulty
    )
    
    return jsonify({
        "session_id": session_id,
        "interviewer": interviewer,
        "question": question_data.get('question', ''),
        "phase": "introduction"
    })

@app.route('/api/interview/structured/next', methods=['POST'])
def api_structured_interview_next():
    data = request.get_json()
    session_id = data.get('session_id')
    current_phase = data.get('current_phase', 'introduction')
    candidate_answer = data.get('candidate_answer', '')
    previous_question = data.get('previous_question', '')
    company_profile = data.get('company_profile', {})
    candidate_profile = data.get('candidate_profile', {})
    difficulty = data.get('difficulty', 'Medium')
    previous_questions = data.get('previous_questions', [])
    is_followup_turn = data.get('is_followup_turn', False)
    
    if is_followup_turn:
        followup_data = generate_structured_followup(
            previous_question, candidate_answer, current_phase, candidate_profile, company_profile, difficulty
        )
        return jsonify(followup_data)
    else:
        question_data = generate_structured_interview_question(
            current_phase, company_profile, candidate_profile, previous_questions, difficulty
        )
        return jsonify(question_data)

@app.route('/api/interview/structured/evaluate', methods=['POST'])
def api_structured_interview_evaluate():
    data = request.get_json()
    turns_by_phase = data.get('turns_by_phase', {})
    company_profile = data.get('company_profile', {})
    candidate_profile = data.get('candidate_profile', {})
    difficulty = data.get('difficulty', 'Medium')
    session_id = data.get('session_id')
    
    evaluation = evaluate_structured_interview(
        turns_by_phase, company_profile, candidate_profile, difficulty
    )
    
    overall_score = evaluation.get('overall_score', 0)
    xp_earned = calculate_xp(difficulty, overall_score)
    
    # Just passing dummy stats to check_new_badges
    session_stats = {"total_completed": 1, "best_score": overall_score, "average_score": overall_score, "total_xp": xp_earned}
    new_badges = check_new_badges(session_stats, [])
    
    return jsonify({
        "evaluation": evaluation,
        "xp_earned": xp_earned,
        "new_badges": new_badges
    })

@app.route('/api/resume/parse-skills-enhanced', methods=['POST'])
def api_parse_resume_skills_enhanced():
    resume_text = ""
    
    if 'file' in request.files or 'resume_file' in request.files:
        file = request.files.get('file') or request.files.get('resume_file')
        if file and file.filename:
            filename = file.filename.lower()
            if filename.endswith('.pdf'):
                from services.resume_parser import extract_text_from_pdf
                resume_text = extract_text_from_pdf(file.read())
            else:
                try:
                    resume_text = file.read().decode('utf-8', errors='ignore')
                except Exception:
                    resume_text = ""
    
    if not resume_text and request.is_json:
        data = request.json or {}
        resume_text = data.get('resume_text', '')
    elif not resume_text and request.form:
        resume_text = request.form.get('resume_text', '')
    
    if not resume_text or not resume_text.strip():
        return jsonify({"error": "Please provide your resume text or upload a valid PDF file."}), 400
    
    from services.resume_parser import parse_resume_skills, get_resume_analysis_summary
    profile = parse_resume_skills(resume_text)
    summary = get_resume_analysis_summary(profile)
    
    return jsonify({"profile": profile, "summary": summary, "extracted_length": len(resume_text)})


# ==============================================================================
# DAILY INTERVIEW CHALLENGE API ENDPOINTS
# ==============================================================================
from services.daily_challenge_service import (
    get_daily_questions,
    validate_typed_answer,
    get_leaderboard_data,
    RAPID_FIRE_QUESTIONS,
    SPRINT_MCQ_BANK,
    LOGO_CHALLENGE_BANK
)

@app.route('/api/daily-challenge/questions', methods=['GET'])
def api_daily_challenge_questions():
    """Retrieve questions for the specified challenge mode."""
    mode = request.args.get('mode', 'rapid_fire')
    valid_modes = ['rapid_fire', 'mcq_sprint', 'logo_quiz']
    if mode not in valid_modes:
        mode = 'rapid_fire'
    
    questions = get_daily_questions(mode)
    return jsonify({
        "mode": mode,
        "total_questions": len(questions),
        "questions": questions
    })

@app.route('/api/daily-challenge/verify-answer', methods=['POST'])
def api_daily_challenge_verify():
    """Verify an individual question answer (typed or MCQ option index)."""
    data = request.json or {}
    mode = data.get('mode', 'rapid_fire')
    question_id = data.get('question_id', '')
    typed_answer = sanitize_input(data.get('typed_answer', '')).strip()
    selected_option = data.get('selected_option', None)
    
    # Locate question
    question_pool = RAPID_FIRE_QUESTIONS + SPRINT_MCQ_BANK + LOGO_CHALLENGE_BANK
    q = next((item for item in question_pool if item["id"] == question_id), None)
    
    if not q:
        return jsonify({"error": "Question not found."}), 404
        
    is_correct = False
    
    # Check typed answer first if provided
    if typed_answer and "accepted_answers" in q:
        is_correct = validate_typed_answer(typed_answer, q["accepted_answers"])
    elif selected_option is not None:
        try:
            is_correct = (int(selected_option) == int(q["correct_option_index"]))
        except (ValueError, TypeError):
            is_correct = False
            
    double_points = bool(data.get('double_points', False))
    points_multiplier = 2 if double_points else 1
    
    return jsonify({
        "question_id": question_id,
        "is_correct": is_correct,
        "correct_option_index": q.get("correct_option_index", 0),
        "correct_answer": q["options"][q.get("correct_option_index", 0)] if "options" in q else q.get("name", ""),
        "explanation": q.get("explanation", ""),
        "double_points": double_points,
        "points_multiplier": points_multiplier
    })

@app.route('/api/daily-challenge/leaderboard', methods=['GET'])
def api_daily_challenge_leaderboard():
    """Get today's dynamic leaderboard."""
    user_score = int(request.args.get('user_score', 0))
    user_name = request.args.get('user_name', 'You (Candidate)')
    board = get_leaderboard_data(user_score=user_score, user_name=user_name)
    return jsonify({"leaderboard": board})

@app.route('/api/daily-challenge/submit-session', methods=['POST'])
def api_daily_challenge_submit():
    """Submit full challenge session to calculate XP and unlock badges."""
    data = request.json or {}
    mode = data.get('mode', 'rapid_fire')
    score = int(data.get('score', 0))
    accuracy = float(data.get('accuracy', 0))
    streak = int(data.get('streak', 1))
    
    # XP calculation
    base_xp = score // 10
    streak_bonus = streak * 15
    total_xp = max(50, base_xp + streak_bonus)
    
    # Badges check
    badges_earned = []
    if accuracy == 100:
        badges_earned.append({"name": "Flawless Execution", "icon": "🎯", "desc": "Achieved 100% accuracy in a Daily Challenge."})
    if mode == "mcq_sprint" and score >= 2000:
        badges_earned.append({"name": "Speed Demon", "icon": "⚡", "desc": "Crushed the 30s MCQ Speed Sprint."})
    if mode == "rapid_fire" and score >= 800:
        badges_earned.append({"name": "Rapid Fire Prodigy", "icon": "🔥", "desc": "Mastered Rapid Fire tech questions."})
    if mode == "logo_quiz" and score >= 800:
        badges_earned.append({"name": "Tech Stack Guru", "icon": "🧩", "desc": "Identified all developer logos with speed."})
    if streak >= 3:
        badges_earned.append({"name": "Streak Warrior", "icon": "🌟", "desc": "Maintained a 3+ day practice streak."})
        
    return jsonify({
        "xp_earned": total_xp,
        "streak": streak,
        "badges_earned": badges_earned,
        "message": "Challenge session saved successfully!"
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"🚀 Starting Placifly Server on http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)


