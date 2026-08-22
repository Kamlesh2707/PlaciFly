"""
Company Intelligence & Metadata Directory
Comprehensive database of 26 top companies + dynamic custom company support.
"""

COMPANY_DIRECTORY = [
    {"name": "TCS", "full_name": "Tata Consultancy Services", "color": "#0072C6", "industry": "IT Services & Consulting", "role": "Software Engineer", "desc": "India's largest IT services firm specializing in global digital transformation and enterprise systems."},
    {"name": "Infosys", "full_name": "Infosys Ltd", "color": "#007CC3", "industry": "IT Services & Consulting", "role": "Specialist Programmer / Systems Engineer", "desc": "Global leader in next-generation digital services and consulting across cloud, AI, and enterprise tech."},
    {"name": "Wipro", "full_name": "Wipro Technologies", "color": "#E05A47", "industry": "IT Services & Consulting", "role": "Project Engineer", "desc": "Leading global information technology, consulting, and business process services company."},
    {"name": "Accenture", "full_name": "Accenture", "color": "#A100FF", "industry": "Technology Consulting", "role": "Associate Software Engineer", "desc": "Global professional services company with leading capabilities in digital, cloud, and security."},
    {"name": "Deloitte", "full_name": "Deloitte Consulting", "color": "#86BC25", "industry": "Consulting & Analytics", "role": "Analyst / Consultant", "desc": "World's leading management & technology consultancy solving high-impact enterprise challenges."},
    {"name": "Capgemini", "full_name": "Capgemini", "color": "#0070AD", "industry": "IT Consulting & Digital", "role": "Analyst / Software Engineer", "desc": "Global leader in partnering with companies to transform and manage their business by harnessing technology."},
    {"name": "Cognizant", "full_name": "Cognizant", "color": "#0033A0", "industry": "IT & Business Services", "role": "Programmer Analyst", "desc": "Multinational IT corporation providing digital products, digital IT services, and consulting."},
    {"name": "IBM", "full_name": "IBM", "color": "#1F70C1", "industry": "Enterprise & Cloud Tech", "role": "Application Developer", "desc": "Pioneer in hybrid cloud computing, enterprise middleware, mainframe systems, and AI technologies."},
    {"name": "HCLTech", "full_name": "HCL Technologies", "color": "#005EB8", "industry": "IT & Engineering Services", "role": "Graduate Engineer Trainee", "desc": "Global technology company helping enterprises reimagine their businesses for the digital age."},
    {"name": "Tech Mahindra", "full_name": "Tech Mahindra", "color": "#D71920", "industry": "Telecom & Digital IT", "role": "Associate Software Engineer", "desc": "Specialist in telecom networks, next-generation digital experiences, and connected enterprise solutions."},
    {"name": "LTIMindtree", "full_name": "LTIMindtree", "color": "#005696", "industry": "Digital Transformation", "role": "Software Engineer", "desc": "Global technology consulting and digital solutions company enabling enterprises across industries."},
    {"name": "Google", "full_name": "Google / Alphabet", "color": "#EA4335", "industry": "Big Tech & AI", "role": "Software Engineer (L3/L4)", "desc": "World's leading technology company renowned for search algorithms, distributed systems, and AI innovation."},
    {"name": "Microsoft", "full_name": "Microsoft", "color": "#00A4EF", "industry": "Cloud & Software", "role": "Software Development Engineer", "desc": "Global leader in cloud computing (Azure), enterprise software, operating systems, and developer tools."},
    {"name": "Amazon", "full_name": "Amazon", "color": "#FF9900", "industry": "Cloud & E-Commerce", "role": "Software Development Engineer (SDE)", "desc": "Global leader in high-scale cloud platforms (AWS), e-commerce infrastructure, and distributed logistics."},
    {"name": "Apple", "full_name": "Apple", "color": "#A2AAAD", "industry": "Consumer Tech & Hardware/OS", "role": "Software Engineer", "desc": "World leader in high-performance hardware, operating systems (iOS/macOS), and consumer software ecosystems."},
    {"name": "Meta", "full_name": "Meta (Facebook)", "color": "#0668E1", "industry": "Social Tech & AI", "role": "Software Engineer", "desc": "Creator of global social platforms serving billions of users with cutting-edge frontend and infrastructure scale."},
    {"name": "Netflix", "full_name": "Netflix", "color": "#E50914", "industry": "Streaming & Cloud Scale", "role": "Software Engineer", "desc": "Pioneer in global entertainment streaming, chaos engineering, microservice resiliency, and recommendation systems."},
    {"name": "Adobe", "full_name": "Adobe Systems", "color": "#FF0000", "industry": "Creative & Cloud Tech", "role": "Software Development Engineer", "desc": "Global leader in creative software, digital experiences, rendering engines, and document cloud platforms."},
    {"name": "Oracle", "full_name": "Oracle Corporation", "color": "#F80000", "industry": "Database & Cloud ERP", "role": "Associate Applications Developer", "desc": "Enterprise leader in high-performance relational databases, cloud ERP, and mission-critical infrastructure."},
    {"name": "Salesforce", "full_name": "Salesforce", "color": "#00A1E0", "industry": "Cloud CRM & SaaS", "role": "MTS (Member of Technical Staff)", "desc": "World's #1 AI CRM platform empowering companies to connect with their customers in a whole new way."},
    {"name": "NVIDIA", "full_name": "NVIDIA", "color": "#76B900", "industry": "AI & GPU Computing", "role": "Software Engineer (Compute/AI)", "desc": "World leader in GPU accelerated computing, CUDA, deep learning hardware, and AI supercomputing platforms."},
    {"name": "JPMorgan Chase", "full_name": "JPMorgan Chase & Co.", "color": "#1170A0", "industry": "Investment Banking & FinTech", "role": "Software Engineer", "desc": "Global financial powerhouse operating high-frequency trading systems, secure banking clouds, and fintech APIs."},
    {"name": "Goldman Sachs", "full_name": "Goldman Sachs", "color": "#7399C6", "industry": "Investment Banking & Quant", "role": "Engineering Analyst", "desc": "Premier global investment banking firm building low-latency algorithmic trading and quantitative risk systems."},
    {"name": "EY", "full_name": "Ernst & Young (EY)", "color": "#FFE600", "industry": "Assurance & Tech Consulting", "role": "Technology Consultant", "desc": "Global leader in assurance, consulting, strategy, and digital risk analytics for Fortune 500 leaders."},
    {"name": "PwC", "full_name": "PricewaterhouseCoopers", "color": "#D04A02", "industry": "Tech Advisory & Consulting", "role": "Associate Consultant", "desc": "Prestigious professional services network delivering human-led and tech-powered business solutions."},
    {"name": "KPMG", "full_name": "KPMG", "color": "#00338D", "industry": "Advisory & Strategy", "role": "Analyst / Associate", "desc": "Global network of professional firms providing audit, tax, and tech advisory services."}
]


def get_companies():
    """Return all companies in directory."""
    return COMPANY_DIRECTORY


def get_company_by_name(name):
    """Retrieve specific company metadata."""
    if not name:
        return COMPANY_DIRECTORY[0]
    name_clean = name.strip().lower()
    for c in COMPANY_DIRECTORY:
        if c['name'].lower() == name_clean or c['full_name'].lower() == name_clean:
            return c
    return {
        "name": name,
        "full_name": name,
        "color": "#0066FF",
        "industry": "Technology & Software",
        "role": "Software Engineer",
        "desc": f"Custom company interview preparation for {name}."
    }


def get_company_intel(company_name):
    """Return interviewer persona details for round generation."""
    c = get_company_by_name(company_name)
    return {
        "company": c['full_name'],
        "color": c['color'],
        "interviewers": {
            "Easy": {"name": "Alex Morgan", "title": "University Recruiter", "avatar": "👨‍💼", "style": "Friendly, encouraging, testing programming and fundamental logic."},
            "Medium": {"name": "Rajesh Sharma", "title": "Senior Technical Assessor", "avatar": "👨‍💻", "style": "Professional interviewer probing programming, databases, and structured reasoning."},
            "Hard": {"name": "Elena Rostova", "title": "Staff Engineer & Bar Raiser", "avatar": "🧑‍🔬", "style": "Strict Senior Engineer probing deep architecture, optimization, and complex trade-offs."}
        },
        "tech_stack": ["Java", "Python", "SQL", "DBMS", "OOP", "Data Structures", "System Design"]
    }


COMPANY_INTELLIGENCE = {c['name']: get_company_intel(c['name']) for c in COMPANY_DIRECTORY}


def get_fresh_scenarios(company_name, difficulty="Medium", count=5):
    return []


def get_company_prep_data(company_name):
    c = get_company_by_name(company_name)
    return {"company": c, "topics": ["Programming", "DBMS", "DSA", "OOP", "System Design"]}


def refresh_company_intel_cache(company_name):
    return get_company_intel(company_name)
