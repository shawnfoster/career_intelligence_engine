from __future__ import annotations

# Configuration for Career Intelligence Engine

# API Keys (set these in environment variables or .env file)
OPENAI_API_KEY = ""
GOOGLE_SHEETS_API_KEY = ""

# File paths
DATA_DIR = "data"
RAW_JOBS_DIR = "data/raw_jobs"
ENRICHED_JOBS_DIR = "data/enriched_jobs"
RESUMES_DIR = "data/resumes"
OUTPUTS_DIR = "data/outputs"

# Model settings
DEFAULT_MODEL = "gpt-4"
MAX_TOKENS = 2000

CORE_SKILLS = {
    "sql",
    "python",
    "tableau",
    "power bi",
    "looker",
    "analytics",
    "business intelligence",
    "dashboarding",
    "data analysis",
    "stakeholder management",
    "customer success",
    "salesforce",
    "revenue operations",
    "forecasting",
    "pipeline management",
    "experimentation",
    "a/b testing",
    "onboarding",
    "adoption",
    "churn",
    "nrr",
    "arr",
}

TOOL_ALIASES = {
    "powerbi": "power bi",
    "ms excel": "excel",
    "google sheets": "sheets",
    "sfdc": "salesforce",
    "bi": "business intelligence",
}

DEFAULT_HEADERS = {
    "User-Agent": "CareerIntelligenceEngine/0.1 (+https://localhost)",
    "Accept": "application/json, text/plain, */*",
}

DEFAULT_TIMEOUT = 20

LEVEL_PATTERNS = {
    "entry": [r"\bentry\b", r"\bjunior\b", r"\bassociate\b", r"0\s*-\s*2 years", r"1\s*-\s*3 years"],
    "mid": [r"\bmid\b", r"\bintermediate\b", r"3\s*-\s*5 years", r"4\+ years"],
    "senior": [r"\bsenior\b", r"\bstaff\b", r"\blead\b", r"\bprincipal\b", r"5\+ years", r"7\+ years"],
}

TOOL_CANDIDATES = {
    "sql",
    "python",
    "tableau",
    "power bi",
    "looker",
    "salesforce",
    "excel",
    "sheets",
    "hubspot",
    "snowflake",
    "bigquery",
    "dbt",
    "mode",
}

TITLE_WEIGHTS = {
    "business intelligence analyst": 2.6,
    "data analyst": 2.3,
    "business analyst": 2.2,
    "revenue operations analyst": 2.5,
    "customer success manager": 2.0,
    "strategy operations analyst": 2.1,
    "product analyst": 2.0,
    "sales operations analyst": 2.2,
}

INDUSTRY_KEYWORDS = {
    "saas": ["saas", "subscription", "arr", "nrr", "churn", "customer success"],
    "healthcare": ["healthcare", "clinical", "patient", "medical"],
    "fintech": ["payments", "fintech", "banking", "fraud", "financial platform"],
    "education": ["education", "edtech", "learning", "student"],
}
# Scoring weights
SKILLS_WEIGHT = 0.4
EXPERIENCE_WEIGHT = 0.3
EDUCATION_WEIGHT = 0.2
CULTURE_FIT_WEIGHT = 0.1

# Google Sheets settings
SPREADSHEET_ID = ""  # Your Google Sheet ID