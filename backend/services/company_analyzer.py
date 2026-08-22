"""
Company URL Analyzer Service
Analyzes custom company website URLs for custom interview preparation.
"""

import re
import urllib.parse

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


def analyze_company_url(url_or_domain):
    """
    Analyze a custom company URL or domain name to extract interview intelligence.
    """
    raw_input = url_or_domain.strip()
    
    # Extract clean domain and company name
    parsed = urllib.parse.urlparse(raw_input if '://' in raw_input else f"https://{raw_input}")
    domain = parsed.netloc or parsed.path
    domain = re.sub(r'^www\.', '', domain).split('/')[0]
    company_name = domain.split('.')[0].capitalize()
    if not company_name or len(company_name) < 2:
        company_name = "Custom Tech Enterprise"

    # 1. If Gemini is available, generate deep analysis
    if _gemini_model:
        try:
            prompt = f"""You are an AI placement research assistant for Placifly.
Analyze this company website/domain: "{raw_input}" (Domain: {domain}).

Return a structured JSON summary (no markdown):
{{
    "name": "{company_name}",
    "domain": "{domain}",
    "industry": "Industry category (e.g. FinTech, Cloud SaaS, HealthTech, E-Commerce)",
    "headquarters": "Likely HQ or global distribution",
    "products": ["Product/Service 1", "Product/Service 2", "Product/Service 3"],
    "tech_stack": ["Key Tech 1", "Key Tech 2", "Key Tech 3", "Key Tech 4"],
    "culture": "1-2 sentence description of company engineering & work culture",
    "prep_areas": [
        "Core Programming Fundamentals",
        "Data Structures & Algorithms",
        "REST APIs & Web Services",
        "Database Design & SQL",
        "Company Product Knowledge",
        "Problem Solving & Communication"
    ],
    "sample_case_study_topic": "A realistic technical challenge this company solves"
}}
"""
            res = _gemini_model.generate_content(prompt, generation_config={'temperature': 0.2})
            text = res.text.strip()
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            import json
            data = json.loads(text.strip())
            data["verified"] = False
            data["note"] = "AI-generated practice preparation insights based on public company information."
            return data
        except Exception as e:
            print(f"[Company Analyzer LLM Error] {e}")

    # 2. Fallback Heuristic Analysis
    return {
        "name": company_name,
        "domain": domain,
        "industry": "Software & Digital Technology",
        "headquarters": "Global / Remote",
        "products": [f"{company_name} Platform", f"{company_name} Cloud Services", "Digital Client Solutions"],
        "tech_stack": ["Python", "Java", "REST APIs", "SQL / Databases", "Cloud Infrastructure"],
        "culture": "Engineering-first, customer-focused team solving modern digital challenges with scalable software.",
        "prep_areas": [
            "Core Programming & OOP Fundamentals",
            "Data Structures & Problem Solving",
            "REST APIs & Backend Integration",
            "Database Schema Design & Query Optimization",
            "Understanding Company Products & Engineering Needs",
            "Structured Communication (STAR Method)"
        ],
        "sample_case_study_topic": f"How {company_name} handles scalable user traffic and secure data transactions.",
        "verified": False,
        "note": "AI-generated practice preparation recommendations based on public domain data."
    }
