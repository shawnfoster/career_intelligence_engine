from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional

from config import CORE_SKILLS, TOOL_ALIASES


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def clean_text(value: Optional[str]) -> str:
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_term(term: str) -> str:
    term = term.strip().lower()
    return TOOL_ALIASES.get(term, term)


def tokenize_skills(text: str) -> list[str]:
    text_l = clean_text(text).lower()
    found = []
    for skill in CORE_SKILLS:
        if skill in text_l:
            found.append(skill)
    return sorted(set(found))