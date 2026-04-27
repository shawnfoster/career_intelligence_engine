from __future__ import annotations

import re
from typing import Any, Dict, List

from config import LEVEL_PATTERNS, TOOL_CANDIDATES
from src.models import JobPosting
from src.utils import clean_text, tokenize_skills


def safe_get(d: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    current: Any = d
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def infer_level(text: str) -> str | None:
    text_l = text.lower()
    for level, patterns in LEVEL_PATTERNS.items():
        if any(re.search(pattern, text_l) for pattern in patterns):
            return level
    return None


def extract_tools(text: str) -> list[str]:
    text_l = clean_text(text).lower()
    tools = [tool for tool in TOOL_CANDIDATES if tool in text_l]
    return sorted(set(tools))


def enrich_job(job: JobPosting) -> None:
    text = job.combined_text()
    job.level_hint = job.level_hint or infer_level(text)
    job.derived_skills = tokenize_skills(text)
    job.derived_tools = extract_tools(text)

    keywords = set(job.derived_skills + job.derived_tools)
    if job.team:
        keywords.add(job.team.lower())
    job.derived_keywords = sorted(keywords)