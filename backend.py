# backend.py

import pdfplumber
import sqlite3
from datetime import datetime
import re

# ----------- New helper: Extract project section text ----------
def extract_project_section(text):
    # Simple heuristic: look for "project" section (case-insensitive)
    match = re.search(r'(projects|project experience|academic projects|personal projects)(.*?)(\n\n|\Z)', text, re.S | re.I)
    if match:
        return match.group(2).strip()
    return ""

# ----------- New: Analyze projects relevance for fresher ----------
def analyze_projects(text, desired_skills):
    project_section = extract_project_section(text)
    if not project_section:
        return ["⚠️ No Projects section found. Consider adding detailed projects relevant to your desired job role."]
    
    # Check if any desired skill words appear in projects
    skills_mentioned = [skill for skill in desired_skills if skill.lower() in project_section.lower()]
    
    if not skills_mentioned:
        return ["⚠️ Your project descriptions don't highlight key skills for the job role. Add technologies/tools used in projects."]
    
    return [f"✅ Projects highlight these relevant skills: {', '.join(skills_mentioned)}"]

# ----------- Updated evaluate_resume function to include project check ----------
def evaluate_resume(text, company, designation, experience):
    company_roles = COMPANY_DATA.get(company, {})
    role_skills = company_roles.get(designation, {}).get(experience.lower(), [])

    found_skills = [skill for skill in role_skills if skill in text]
    missing_skills = [skill for skill in role_skills if skill not in text]

    score = int((len(found_skills) / len(role_skills)) * 100) if role_skills else 0

    ats_feedback = []
    if "objective" not in text and "summary" not in text:
        ats_feedback.append("Include an Objective or Summary section.")
    if "experience" not in text and experience.lower() == "experienced":
        ats_feedback.append("Add an Experience section.")
    if "education" not in text:
        ats_feedback.append("Add an Education section.")
    if len(text) < 500:
        ats_feedback.append("Your resume content looks too short. Add more details.")

    ats_format = "\n".join(ats_feedback) if ats_feedback else "ATS format looks good."

    career_obj = CAREER_OBJECTIVES.get(company, {}).get(designation, "Write a concise, tailored career objective for this role.")

    tips = [f"Add more details about your experience with '{skill}'." for skill in missing_skills]

    # --- Project analysis for freshers ---
    project_tips = []
    if experience.lower() == "fresher":
        project_tips = analyze_projects(text, role_skills)

    # Combine tips
    all_tips = tips + project_tips

    return {
        "skills_found": found_skills,
        "missing": missing_skills,
        "score": score,
        "tips": all_tips,
        "ats_format": ats_format,
        "career_objective": career_obj
    }

# ----------------- Database Setup -----------------
conn = sqlite3.connect("resume_analysis.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        experience TEXT,
        company TEXT,
        designation TEXT,
        skills_found TEXT,
        score INTEGER,
        suggestions TEXT,
        ats_format TEXT,
        date_analyzed TEXT
    )
''')
conn.commit()

# ----------------- Company & Job Role Skills -----------------
COMPANY_REQUIREMENTS = {
    "TCS": {
        "Software Developer": ["java", "spring", "git", "mysql", "rest api", "oop"],
        "System Engineer": ["linux", "networking", "troubleshooting", "shell scripting", "tcp/ip"],
        "IT Support Trainee": ["customer support", "troubleshooting", "communication", "hardware basics"],
        "Data Analyst Trainee": ["excel", "sql","python" "power bi", "data visualization", "statistics"],
        "Business Analyst": ["requirement gathering", "ppt", "communication", "uml", "stakeholder management"],
        "HR Executive": ["recruitment", "interviewing", "communication", "ms office"],
        "QA Tester": ["manual testing", "test cases", "jira", "automation basics"],
        "Project Coordinator": ["planning", "communication", "risk management", "agile"],
        "Finance Associate": ["accounting", "ms excel", "sap", "invoice processing"],
        "Marketing Executive": ["seo", "content creation", "social media", "digital marketing"]
    },
    "Infosys": {
        "Java Developer": ["java", "spring boot", "hibernate", "sql", "maven", "microservices"],
        "Python Developer": ["python", "flask", "django", "rest api", "sql", "oop"],
        "HR Associate": ["recruitment", "onboarding", "communication", "employee engagement"],
        "Data Scientist": ["python", "machine learning", "pandas", "numpy", "statistics", "tensorflow"],
        "IT Support Engineer": ["networking", "troubleshooting", "windows server", "customer support"],
        "Business Analyst": ["business process", "ppt", "excel", "stakeholder communication", "uml"],
        "Cloud Engineer": ["aws", "azure", "docker", "kubernetes"],
        "Automation Tester": ["selenium", "java", "cucumber", "test automation"],
        "Technical Writer": ["documentation", "communication", "ms office", "editing"],
        "Sales Executive": ["lead generation", "crm", "communication", "negotiation"]
    },
    "Accenture": {
        "Data Analyst": ["python", "sql", "excel", "tableau", "power bi", "statistics"],
        "Business Analyst": ["excel", "communication", "sql", "ppt", "uml", "stakeholder management"],
        "Cloud Consultant": ["aws", "azure", "terraform", "docker", "ci/cd"],
        "Software Tester": ["selenium", "java", "test cases", "jira", "manual testing"],
        "Project Manager": ["project management", "communication", "risk management", "agile", "scrum"],
        "Cybersecurity Analyst": ["firewalls", "penetration testing", "security", "incident response", "network security"],
        "DevOps Engineer": ["jenkins", "docker", "kubernetes", "linux", "ansible"],
        "UI/UX Designer": ["figma", "prototyping", "adobe xd", "user research", "wireframing"],
        "HR Coordinator": ["recruitment", "communication", "ms office", "employee relations"],
        "Content Strategist": ["seo", "content creation", "editing", "analytics"]
    },
    "Wipro": {
        "Cloud Engineer": ["aws", "azure", "linux", "docker", "kubernetes", "terraform"],
        "Test Engineer": ["selenium", "java", "jira", "test cases", "automation"],
        "IT Support": ["hardware", "networking", "customer support", "troubleshooting"],
        "Data Analyst": ["excel", "sql", "power bi", "data visualization", "statistics"],
        "BPO Executive": ["communication", "ms office", "crm", "customer service"],
        "DevOps Engineer": ["jenkins", "docker", "kubernetes", "linux", "ansible"],
        "Technical Recruiter": ["recruitment", "interviewing", "communication", "sourcing"],
        "Finance Analyst": ["accounting", "ms excel", "sap", "financial reporting"],
        "Network Engineer": ["routing", "switching", "ccna", "firewalls"],
        "Marketing Analyst": ["market research", "data analysis", "excel", "digital marketing"]
    },
    "Capgemini": {
        "DevOps Engineer": ["jenkins", "docker", "kubernetes", "linux", "ansible", "terraform"],
        "Support Analyst": ["ticketing", "communication", "sql", "troubleshooting"],
        "Finance Associate": ["excel", "sap", "invoice", "accounting", "financial analysis"],
        "Software Developer": ["java", "spring", "hibernate", "rest api", "oop"],
        "HR Associate": ["recruitment", "communication", "ms office", "employee engagement"],
        "Business Analyst": ["ppt", "excel", "communication", "stakeholder management", "uml"],
        "Cloud Engineer": ["aws", "azure", "terraform", "docker"],
        "QA Tester": ["manual testing", "automation", "selenium", "jira"],
        "Data Scientist": ["python", "machine learning", "sql", "statistics", "tensorflow"],
        "Technical Writer": ["documentation", "communication", "ms office", "editing"]
    },
    "Tech Mahindra": {
        "Frontend Developer": ["html", "css", "javascript", "react", "redux"],
        "BPO Executive": ["communication", "ms office", "crm", "customer handling"],
        "Business Support": ["data entry", "ppt", "customer interaction", "excel"],
        "Backend Developer": ["nodejs", "express", "mongodb", "api"],
        "QA Tester": ["manual testing", "automation", "selenium", "jira"],
        "Cloud Engineer": ["aws", "azure", "docker", "kubernetes"],
        "HR Executive": ["recruitment", "onboarding", "communication"],
        "Data Analyst": ["excel", "sql", "power bi", "data visualization"],
        "Technical Writer": ["documentation", "editing", "communication"],
        "Sales Executive": ["crm", "lead generation", "communication"]
    },
    "Cognizant": {
        "Automation Tester": ["selenium", "java", "cucumber", "test automation"],
        "Backend Developer": ["nodejs", "api", "mongodb", "express"],
        "KPO Analyst": ["research", "excel", "reporting", "communication"],
        "Data Analyst Trainee": ["excel", "sql","python" "power bi", "data visualization", "statistics"],
        "Data Scientist": ["python", "machine learning", "statistics", "sql"],
        "Business Analyst": ["ppt", "excel", "stakeholder communication"],
        "Cloud Engineer": ["aws", "azure", "terraform", "docker"],
        "HR Associate": ["recruitment", "communication", "ms office"],
        "Support Engineer": ["customer support", "troubleshooting", "communication"],
        "QA Tester": ["manual testing", "automation", "selenium"],
        "Technical Writer": ["documentation", "communication", "editing"]
    },
    "IBM": {
        "AI Engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch"],
        "Consultant": ["problem solving", "communication", "project management"],
        "Database Admin": ["oracle", "sql", "performance tuning", "backup recovery"],
        "Cloud Architect": ["aws", "azure", "gcp", "terraform"],
        "Cybersecurity Analyst": ["firewalls", "penetration testing", "incident response"],
        "Software Developer": ["java", "spring", "hibernate", "rest api"],
        "HR Executive": ["recruitment", "communication", "ms office"],
        "Data Scientist": ["python", "statistics", "sql", "machine learning"],
        "Technical Writer": ["documentation", "editing", "communication"],
        "Project Manager": ["project management", "risk management", "agile", "scrum"]
    },
    "HCL": {
        "Technical Support": ["communication", "network", "troubleshooting", "customer support"],
        "Data Entry": ["typing", "ms excel", "accuracy"],
        "NOC Engineer": ["linux", "monitoring", "incident management", "networking"],
        "Cloud Engineer": ["aws", "azure", "docker", "kubernetes"],
        "QA Tester": ["selenium", "manual testing", "automation"],
        "Business Analyst": ["ppt", "excel", "communication"],
        "HR Assistant": ["recruitment", "communication", "ms office"],
        "Software Developer": ["java", "spring", "hibernate", "rest api"],
        "Data Analyst": ["excel", "sql", "power bi"],
        "Project Coordinator": ["planning", "communication", "risk management"]
    },
    "Google": {
        "Software Engineer": ["c++", "algorithms", "system design", "data structures"],
        "ML Engineer": ["python", "machine learning", "tensorflow", "pandas", "numpy"],
        "UX Designer": ["figma", "prototyping", "user testing", "wireframing"],
        "Product Manager": ["agile", "scrum", "communication", "roadmapping"],
        "Cloud Architect": ["gcp", "aws", "terraform", "docker"],
        "Data Scientist": ["python", "statistics", "machine learning"],
        "Technical Writer": ["documentation", "editing", "communication"],
        "Sales Engineer": ["crm", "lead generation", "communication"],
        "Support Engineer": ["customer support", "troubleshooting", "communication"],
        "Recruiter": ["recruitment", "interviewing", "communication"]
    },
    "Microsoft": {
        "Software Developer": ["c#", ".net", "sql", "azure", "oop"],
        "Security Analyst": ["firewalls", "siem", "threat analysis", "incident response"],
        "Content Strategist": ["seo", "blog", "editing", "content marketing"],
        "Cloud Engineer": ["azure", "aws", "terraform", "docker"],
        "Data Scientist": ["python", "machine learning", "statistics"],
        "UX Designer": ["figma", "adobe xd", "prototyping", "user research"],
        "HR Executive": ["recruitment", "communication", "ms office"],
        "Project Manager": ["project management", "agile", "scrum", "risk management"],
        "QA Tester": ["manual testing", "automation", "selenium"],
        "Technical Writer": ["documentation", "editing", "communication"]
    },
    "Amazon": {
        "Cloud Architect": ["aws", "terraform", "ci/cd", "docker"],
        "Operations Executive": ["excel", "sql", "erp", "communication"],
        "Customer Support": ["communication", "crm", "problem solving"],
        "Data Analyst": ["excel", "sql", "power bi", "data visualization"],
        "Software Developer": ["java", "spring", "hibernate", "rest api"],
        "Logistics Manager": ["supply chain", "excel", "communication"],
        "Product Manager": ["agile", "scrum", "roadmapping"],
        "HR Associate": ["recruitment", "onboarding", "communication"],
        "QA Engineer": ["selenium", "manual testing", "automation"],
        "Marketing Specialist": ["seo", "content marketing", "social media"]
    },
    "Deloitte": {
        "Data Scientist": ["python", "statistics", "sql", "visualization", "machine learning"],
        "Consulting Analyst": ["communication", "ppt", "excel", "stakeholder management"],
        "IT Auditor": ["audit", "risk", "information systems", "compliance"],
        "Tax Consultant": ["taxation", "accounting", "ms excel"],
        "Financial Analyst": ["accounting", "financial modeling", "ms excel"],
        "Business Analyst": ["business process", "communication", "ppt"],
        "Cybersecurity Analyst": ["firewalls", "penetration testing", "incident response"],
        "Project Manager": ["project management", "risk management", "agile"],
        "HR Executive": ["recruitment", "communication", "employee relations"],
        "Technical Writer": ["documentation", "editing", "communication"]
    },
    "EY": {
        "Finance Analyst": ["ms excel", "accounting", "erp", "financial reporting"],
        "Auditor": ["audit", "tax", "reporting", "compliance"],
        "Compliance Officer": ["legal", "compliance", "reporting"],
        "Business Analyst": ["communication", "excel", "ppt", "stakeholder management"],
        "Tax Consultant": ["taxation", "accounting", "compliance"],
        "HR Associate": ["recruitment", "communication", "ms office"],
        "IT Consultant": ["project management", "cloud", "itil"],
        "Data Scientist": ["python", "machine learning", "statistics"],
        "Cybersecurity Analyst": ["security", "penetration testing", "incident response"],
        "Technical Writer": ["documentation", "communication", "editing"]
    },
    "KPMG": {
        "Risk Consultant": ["ms excel", "compliance", "analysis", "risk management"],
        "HR Assistant": ["recruitment", "hrms", "communication"],
        "IT Consultant": ["project management", "itil", "cloud", "devops"],
        "Audit Associate": ["audit", "financial statements", "reporting"],
        "Business Analyst": ["communication", "ppt", "excel"],
        "Cybersecurity Analyst": ["security", "penetration testing", "incident response"],
        "Data Analyst": ["sql", "excel", "power bi"],
        "Tax Consultant": ["tax", "accounting", "compliance"],
        "Technical Writer": ["documentation", "editing", "communication"],
        "Project Manager": ["project management", "agile", "risk management"]
    },
    "IBM": {
        "AI Engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch"],
        "Consultant": ["problem solving", "communication", "project management"],
        "Database Admin": ["oracle", "sql", "performance tuning", "backup recovery"],
        "Cloud Architect": ["aws", "azure", "gcp", "terraform"],
        "Cybersecurity Analyst": ["firewalls", "penetration testing", "incident response"],
        "Software Developer": ["java", "spring", "hibernate", "rest api"],
        "HR Executive": ["recruitment", "communication", "ms office"],
        "Data Scientist": ["python", "statistics", "sql", "machine learning"],
        "Technical Writer": ["documentation", "editing", "communication"],
        "Project Manager": ["project management", "risk management", "agile", "scrum"]
    },
    "Oracle": {
        "Database Developer": ["sql", "pl/sql", "performance tuning", "oracle forms"],
        "Java Developer": ["java", "spring", "hibernate", "rest api"],
        "Cloud Engineer": ["oci", "terraform", "docker", "kubernetes"],
        "Support Engineer": ["customer support", "troubleshooting", "communication"],
        "QA Tester": ["manual testing", "automation", "selenium"],
        "Business Analyst": ["requirement gathering", "ppt", "excel"],
        "Technical Writer": ["documentation", "editing", "communication"],
        "HR Executive": ["recruitment", "communication", "ms office"],
        "Data Scientist": ["python", "machine learning", "statistics"],
        "Project Manager": ["project management", "agile", "scrum"]
    },
    "SAP": {
        "SAP Consultant": ["sap fi", "sap mm", "configuration", "business process"],
        "Business Analyst": ["excel", "ppt", "stakeholder communication"],
        "Project Manager": ["project management", "agile", "communication"],
        "Support Engineer": ["customer support", "troubleshooting"],
        "Data Analyst": ["excel", "sql", "power bi"],
        "QA Tester": ["manual testing", "automation", "selenium"],
        "Technical Writer": ["documentation", "editing", "communication"],
        "HR Associate": ["recruitment", "communication", "ms office"],
        "Finance Analyst": ["accounting", "ms excel", "sap"],
        "Marketing Executive": ["seo", "content creation", "social media"]
    },
    "Facebook": {
        "Software Engineer": ["c++", "algorithms", "system design"],
        "Data Scientist": ["python", "machine learning", "statistics"],
        "Product Manager": ["agile", "scrum", "communication"],
        "UX Designer": ["figma", "prototyping", "user research"],
        "Cloud Engineer": ["aws", "azure", "terraform"],
        "Technical Writer": ["documentation", "editing", "communication"],
        "HR Executive": ["recruitment", "communication", "ms office"],
        "Sales Engineer": ["crm", "lead generation", "communication"],
        "Support Engineer": ["customer support", "troubleshooting", "communication"],
        "Marketing Specialist": ["seo", "content marketing", "social media"]
    },
    "LinkedIn": {
        "Software Developer": ["java", "spring", "sql", "rest api"],
        "Data Analyst": ["excel", "sql", "power bi", "data visualization"],
        "HR Associate": ["recruitment", "communication", "ms office"],
        "Product Manager": ["agile", "scrum", "roadmapping"],
        "Marketing Executive": ["seo", "content marketing", "social media"],
        "QA Tester": ["manual testing", "automation", "selenium"],
        "Technical Writer": ["documentation", "editing", "communication"],
        "Sales Executive": ["crm", "lead generation", "communication"],
        "Cloud Engineer": ["aws", "azure", "terraform"],
        "UX Designer": ["figma", "prototyping", "wireframing"]
    }
}

# ----------------- Career Objectives by Company and Designation -----------------
CAREER_OBJECTIVES = {
    company: {role: f"Aspiring {role} eager to contribute skills and grow at {company}."
              for role in roles}
    for company, roles in COMPANY_REQUIREMENTS.items()
}

# ----------------- Resume Parsing -----------------
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content
    return text.lower()

# ----------------- Resume Evaluation -----------------
def analyze_resume(text, company, designation, experience):
    expected_skills = COMPANY_REQUIREMENTS.get(company, {}).get(designation, [])
    found_skills = [skill for skill in expected_skills if skill in text]
    missing_skills = [skill for skill in expected_skills if skill not in text]
    score = int((len(found_skills) / len(expected_skills)) * 100) if expected_skills else 0

    tips = []
    for skill in missing_skills:
        tips.append(f"💡 Add more details about your experience with **{skill}**.")

    ats_feedback = []
    if "objective" not in text and "summary" not in text:
        ats_feedback.append("📌 Missing an objective or summary section.")
    if "experience" not in text and experience.lower() == "experienced":
        ats_feedback.append("📌 No experience section found.")
    if "education" not in text:
        ats_feedback.append("📌 No education section detected.")
    if len(text) < 500:
        ats_feedback.append("📌 Resume content too short, consider adding more details.")

    format_tips = "\n".join(ats_feedback) if ats_feedback else "✅ ATS format looks good."

    career_obj = CAREER_OBJECTIVES.get(company, {}).get(designation, None)

    return {
        "skills_found": found_skills,
        "missing": missing_skills,
        "score": score,
        "tips": tips,
        "ats_format": format_tips,
        "career_objective": career_obj
    }

# ----------------- DB Insertion -----------------
def save_result(name, company, designation, experience, result):
    cursor.execute('''
        INSERT INTO resume_results (name, company, designation, experience, skills_found, score, suggestions, ats_format, date_analyzed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        name,
        company,
        designation,
        experience,
        ", ".join(result['skills_found']),
        result['score'],
        ", ".join(result['missing']),
        result['ats_format'],
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()

# ----------------- Admin: View History -----------------
def get_history():
    cursor.execute("SELECT name, company, designation, experience, score, date_analyzed FROM resume_results ORDER BY id DESC")
    return cursor.fetchall()
