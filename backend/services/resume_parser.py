import io
import json
import re

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import google.generativeai as genai
    from config import Config
    genai.configure(api_key=Config.GEMINI_API_KEY)
    _model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    print(f"[Resume Parser] Gemini init warning: {e}")
    _model = None

def extract_text_from_pdf(pdf_stream):
    """
    Extract plain text from a PDF file stream or bytes.
    """
    if not PdfReader:
        return ""
    try:
        if isinstance(pdf_stream, bytes):
            pdf_stream = io.BytesIO(pdf_stream)
        reader = PdfReader(pdf_stream)
        text_parts = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_parts.append(extracted)
        return "\n".join(text_parts).strip()
    except Exception as e:
        print(f"[PDF Extract Error] {e}")
        return ""



def parse_resume_skills(resume_text):
    """
    Parse resume text and extract structured candidate profile using Gemini AI.
    
    Args:
        resume_text: Raw resume text (pasted or extracted from PDF)
    
    Returns:
        dict: Structured candidate profile
        {
            "name": "Candidate Name",
            "skills": ["Python", "Java", "Flutter", "Firebase"],
            "programming_languages": ["Python", "Java", "C++"],
            "frameworks": ["Flask", "React", "Flutter"],
            "databases": ["MySQL", "MongoDB", "Firebase"],
            "projects": [
                {"name": "Project Name", "tech": ["Python", "Flask"], "description": "Brief desc"}
            ],
            "education": "MCA / B.Tech / B.Com",
            "experience_level": "fresher | junior | mid | senior",
            "strengths": ["Web Development", "Database Design"],
            "certifications": ["AWS Certified", "Google Cloud"],
            "summary": "2-line candidate summary"
        }
    """
    if not resume_text or len(resume_text.strip()) < 20:
        return _default_profile()
    
    if not _model:
        return _heuristic_parse(resume_text)
    
    prompt = f"""You are a resume parsing AI for a placement interview simulator.

Analyze this resume text and extract a structured JSON profile.

RESUME TEXT:
\"\"\"
{resume_text[:3000]}
\"\"\"

Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
{{
    "name": "Full Name of candidate (or 'Candidate' if not found)",
    "skills": ["skill1", "skill2", ...],
    "programming_languages": ["Python", "Java", ...],
    "frameworks": ["Flask", "React", ...],
    "databases": ["MySQL", "MongoDB", ...],
    "projects": [
        {{"name": "Project Name", "tech": ["tech1", "tech2"], "description": "One-line description"}}
    ],
    "education": "Degree name (e.g., MCA, B.Tech CS, BCA)",
    "experience_level": "fresher",
    "strengths": ["area1", "area2"],
    "certifications": ["cert1", "cert2"],
    "summary": "2-line summary of the candidate"
}}

Rules:
- Extract ONLY information present in the resume. Do NOT invent skills or projects.
- If a field is not found, use an empty array or appropriate default.
- For experience_level: use "fresher" for students/new graduates, "junior" for 0-2 years, "mid" for 2-5 years, "senior" for 5+ years.
- programming_languages should only include actual programming/scripting languages.
- frameworks should include libraries, frameworks, and tools.
"""

    try:
        response = _model.generate_content(prompt, generation_config={'temperature': 0.1})
        text = response.text.strip()
        
        # Clean markdown code blocks
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()
        
        profile = json.loads(text)
        
        # Validate required fields
        profile.setdefault('name', 'Candidate')
        profile.setdefault('skills', [])
        profile.setdefault('programming_languages', [])
        profile.setdefault('frameworks', [])
        profile.setdefault('databases', [])
        profile.setdefault('projects', [])
        profile.setdefault('education', 'Not specified')
        profile.setdefault('experience_level', 'fresher')
        profile.setdefault('strengths', [])
        profile.setdefault('certifications', [])
        profile.setdefault('summary', 'Candidate profile extracted from resume.')
        
        return profile
    
    except Exception as e:
        print(f"[Resume Parser] Gemini parse error: {e}")
        return _heuristic_parse(resume_text)


def _heuristic_parse(resume_text):
    """
    Fallback heuristic parser when Gemini is unavailable.
    Uses keyword matching to extract basic profile.
    """
    text_lower = resume_text.lower()
    
    # Language detection
    lang_keywords = {
        'Python': ['python'], 'Java': ['java'], 'JavaScript': ['javascript', 'js', 'es6'],
        'C++': ['c++', 'cpp'], 'C': [' c '], 'C#': ['c#', 'csharp'],
        'TypeScript': ['typescript', 'ts'], 'Go': ['golang', ' go '],
        'Rust': ['rust'], 'PHP': ['php'], 'Ruby': ['ruby'],
        'Swift': ['swift'], 'Kotlin': ['kotlin'], 'Dart': ['dart'],
        'SQL': ['sql', 'mysql', 'postgresql', 'oracle sql'],
        'R': [' r '], 'MATLAB': ['matlab'], 'Scala': ['scala']
    }
    
    framework_keywords = {
        'Flask': ['flask'], 'Django': ['django'], 'React': ['react', 'reactjs'],
        'Angular': ['angular'], 'Vue.js': ['vue', 'vuejs'], 'Node.js': ['node', 'nodejs', 'express'],
        'Spring Boot': ['spring', 'spring boot'], 'Flutter': ['flutter'],
        'React Native': ['react native'], '.NET': ['.net', 'asp.net'],
        'TensorFlow': ['tensorflow'], 'PyTorch': ['pytorch'],
        'Tailwind CSS': ['tailwind'], 'Bootstrap': ['bootstrap'],
        'Next.js': ['next.js', 'nextjs'], 'FastAPI': ['fastapi']
    }
    
    db_keywords = {
        'MySQL': ['mysql'], 'PostgreSQL': ['postgresql', 'postgres'],
        'MongoDB': ['mongodb', 'mongo'], 'Firebase': ['firebase', 'firestore'],
        'Redis': ['redis'], 'SQLite': ['sqlite'], 'Oracle': ['oracle'],
        'SQL Server': ['sql server', 'mssql'], 'DynamoDB': ['dynamodb'],
        'Cassandra': ['cassandra'], 'Neo4j': ['neo4j']
    }
    
    languages = [k for k, v in lang_keywords.items() if any(kw in text_lower for kw in v)]
    frameworks = [k for k, v in framework_keywords.items() if any(kw in text_lower for kw in v)]
    databases = [k for k, v in db_keywords.items() if any(kw in text_lower for kw in v)]
    
    # Experience level detection
    exp_level = 'fresher'
    if any(kw in text_lower for kw in ['senior', '5+ years', '7+ years', '10+ years']):
        exp_level = 'senior'
    elif any(kw in text_lower for kw in ['3 years', '4 years', '2-5 years']):
        exp_level = 'mid'
    elif any(kw in text_lower for kw in ['1 year', '2 years', 'junior']):
        exp_level = 'junior'
    
    # Education detection
    education = 'Not specified'
    for deg in ['Ph.D', 'M.Tech', 'MCA', 'M.Sc', 'B.Tech', 'B.E', 'BCA', 'B.Sc', 'B.Com', 'MBA']:
        if deg.lower() in text_lower:
            education = deg
            break
    
    return {
        'name': 'Candidate',
        'skills': languages + frameworks + databases,
        'programming_languages': languages or ['Python', 'Java'],
        'frameworks': frameworks,
        'databases': databases,
        'projects': [],
        'education': education,
        'experience_level': exp_level,
        'strengths': [],
        'certifications': [],
        'summary': f'Candidate with skills in {", ".join(languages[:3]) if languages else "general programming"}.'
    }


def _default_profile():
    """Default profile when no resume is provided."""
    return {
        'name': 'Candidate',
        'skills': ['Python', 'Java', 'SQL', 'Data Structures'],
        'programming_languages': ['Python', 'Java'],
        'frameworks': [],
        'databases': ['MySQL'],
        'projects': [],
        'education': 'Not specified',
        'experience_level': 'fresher',
        'strengths': ['Problem Solving'],
        'certifications': [],
        'summary': 'General candidate profile (no resume provided).'
    }


def get_skills_summary_for_prompt(profile):
    """
    Format the candidate profile into a concise string for injection into AI prompts.
    Used by ai_service.py for personalized question generation.
    """
    parts = []
    
    if profile.get('name') and profile['name'] != 'Candidate':
        parts.append(f"Name: {profile['name']}")
    
    langs = profile.get('programming_languages', [])
    if langs:
        parts.append(f"Languages: {', '.join(langs[:5])}")
    
    frameworks = profile.get('frameworks', [])
    if frameworks:
        parts.append(f"Frameworks: {', '.join(frameworks[:5])}")
    
    dbs = profile.get('databases', [])
    if dbs:
        parts.append(f"Databases: {', '.join(dbs[:3])}")
    
    projects = profile.get('projects', [])
    if projects:
        proj_strs = [f"{p['name']} ({', '.join(p.get('tech', [])[:3])})" for p in projects[:2]]
        parts.append(f"Projects: {'; '.join(proj_strs)}")
    
    if profile.get('education') and profile['education'] != 'Not specified':
        parts.append(f"Education: {profile['education']}")
    
    parts.append(f"Level: {profile.get('experience_level', 'fresher')}")
    
    return ' | '.join(parts) if parts else 'General fresher candidate'
