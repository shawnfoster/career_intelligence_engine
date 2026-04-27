from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from src.utils import now_utc_iso


@dataclass
class JobPosting:
    source: str
    source_type: str
    external_id: str
    title: str
    company: str
    location: Optional[str] = None
    remote_type: Optional[str] = None
    employment_type: Optional[str] = None
    team: Optional[str] = None
    level_hint: Optional[str] = None
    description: str = ""
    requirements_text: str = ""
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    url: Optional[str] = None
    posted_at: Optional[str] = None
    discovered_at: str = field(default_factory=now_utc_iso)
    raw: Dict[str, Any] = field(default_factory=dict)

    derived_skills: List[str] = field(default_factory=list)
    derived_tools: List[str] = field(default_factory=list)
    derived_keywords: List[str] = field(default_factory=list)

    def combined_text(self) -> str:
        return "\n".join([
            self.title or "",
            self.team or "",
            self.description or "",
            self.requirements_text or "",
        ]).strip()


@dataclass
class CandidateProfile:
    name: str
    target_titles: List[str]
    industries: List[str]
    skills: List[str]
    tools: List[str]
    strengths: List[str]
    risk_reframes: List[str] = field(default_factory=list)
    must_have_locations: List[str] = field(default_factory=list)
    avoid_titles: List[str] = field(default_factory=list)
    years_experience_hint: Optional[float] = None


@dataclass
class ScoreBreakdown:
    total: float
    skills_score: float
    tools_score: float
    role_score: float
    industry_score: float
    location_score: float
    seniority_penalty: float
    confidence: float
    matched_skills: List[str]
    matched_tools: List[str]
    matched_titles: List[str]
    notes: List[str]


@dataclass
class RankedJob:
    rank: int
    tier: str
    job: JobPosting
    score: ScoreBreakdown
    positioning_angle: str
    likely_business_problem: str
    job_dna: Dict[str, Any] = field(default_factory=dict)


def ranked_job_to_dict(item: RankedJob) -> Dict[str, Any]:
    return {
        "rank": item.rank,
        "tier": item.tier,
        "job": {
            "title": item.job.title,
            "company": item.job.company,
            "location": item.job.location,
            "remote_type": item.job.remote_type,
            "url": item.job.url,
            "source": item.job.source,
            "posted_at": item.job.posted_at,
            "derived_skills": item.job.derived_skills,
            "derived_tools": item.job.derived_tools,
        },
        "score": asdict(item.score),
        "positioning_angle": item.positioning_angle,
        "likely_business_problem": item.likely_business_problem,
        "job_dna": item.job_dna,
    }