import math

BADGES = [
    {"id": "first_flight", "name": "First Flight", "description": "Completed your first scenario.", "icon_emoji": "🚀", "criteria": lambda stats: stats.get("total_completed", 0) >= 1},
    {"id": "streak_5", "name": "Case Study Streak x5", "description": "Complete 5 case studies.", "icon_emoji": "🔥", "criteria": lambda stats: stats.get("total_completed", 0) >= 5},
    {"id": "deloitte_master", "name": "Deloitte Master", "description": "Scored 90+ in a Deloitte scenario.", "icon_emoji": "🟢", "criteria": lambda stats: stats.get("best_deloitte_score", 0) >= 90},
    {"id": "ethical_leader", "name": "Ethical Leader", "description": "Scored 90+ in an Ethical Decision Making scenario.", "icon_emoji": "⚖️", "criteria": lambda stats: stats.get("best_ethics_score", 0) >= 90},
    {"id": "speed_demon", "name": "Speed Demon", "description": "Completed a scenario in under half the estimated time with a score > 80.", "icon_emoji": "⚡", "criteria": lambda stats: stats.get("speed_demon_earned", False)},
    {"id": "perfect_score", "name": "Perfect Score", "description": "Achieved a 100/100 score.", "icon_emoji": "💯", "criteria": lambda stats: stats.get("best_score", 0) == 100},
    {"id": "tech_wizard", "name": "Tech Wizard", "description": "Scored 90+ in a Technical Interview.", "icon_emoji": "💻", "criteria": lambda stats: stats.get("best_tech_score", 0) >= 90},
    {"id": "hr_expert", "name": "HR Expert", "description": "Scored 90+ in an HR Interview.", "icon_emoji": "🤝", "criteria": lambda stats: stats.get("best_hr_score", 0) >= 90},
    {"id": "leadership_pro", "name": "Leadership Pro", "description": "Scored 90+ in Leadership skills.", "icon_emoji": "👑", "criteria": lambda stats: stats.get("best_leadership_score", 0) >= 90},
    {"id": "problem_solver_elite", "name": "Problem Solver Elite", "description": "Scored 90+ in Problem Solving.", "icon_emoji": "🧩", "criteria": lambda stats: stats.get("best_problem_solving_score", 0) >= 90},
    {"id": "creative_thinker", "name": "Creative Thinker", "description": "Scored 90+ in Creativity.", "icon_emoji": "💡", "criteria": lambda stats: stats.get("best_creativity_score", 0) >= 90},
    {"id": "time_master", "name": "Time Master", "description": "Scored 90+ in Time Management.", "icon_emoji": "⏳", "criteria": lambda stats: stats.get("best_time_management_score", 0) >= 90},
    {"id": "consistency_king", "name": "Consistency King", "description": "Complete 10 scenarios with average score > 80.", "icon_emoji": "👑", "criteria": lambda stats: stats.get("total_completed", 0) >= 10 and stats.get("average_score", 0) > 80},
    {"id": "rising_star", "name": "Rising Star", "description": "Reach Level 5.", "icon_emoji": "⭐", "criteria": lambda stats: calculate_level(stats.get("total_xp", 0)) >= 5},
    {"id": "placement_ready", "name": "Placement Ready", "description": "Reach Level 10 and have an average score > 85.", "icon_emoji": "🎓", "criteria": lambda stats: calculate_level(stats.get("total_xp", 0)) >= 10 and stats.get("average_score", 0) > 85},
]

def calculate_xp(difficulty, score):
    base_xp = {"Easy": 100, "Medium": 200, "Hard": 300}.get(difficulty, 100)
    score_multiplier = score / 100.0
    return int(base_xp * score_multiplier)

def calculate_level(total_xp):
    return math.floor(total_xp / 500) + 1

def check_new_badges(session_stats, current_badges):
    new_badges = []
    current_badge_ids = set(current_badges)
    
    for badge in BADGES:
        if badge["id"] not in current_badge_ids:
            try:
                if badge["criteria"](session_stats):
                    new_badges.append({
                        "id": badge["id"],
                        "name": badge["name"],
                        "description": badge["description"],
                        "icon_emoji": badge["icon_emoji"]
                    })
            except Exception:
                pass
                
    return new_badges
