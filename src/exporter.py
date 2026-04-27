from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.models import JobPosting, RankedJob, ranked_job_to_dict


def timestamp_slug() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def job_to_dict(job: JobPosting) -> dict[str, Any]:
    return {
        "source": job.source,
        "source_type": job.source_type,
        "external_id": job.external_id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "remote_type": job.remote_type,
        "employment_type": job.employment_type,
        "team": job.team,
        "level_hint": job.level_hint,
        "description": job.description,
        "requirements_text": job.requirements_text,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "currency": job.currency,
        "url": job.url,
        "posted_at": job.posted_at,
        "discovered_at": job.discovered_at,
        "derived_skills": job.derived_skills,
        "derived_tools": job.derived_tools,
        "derived_keywords": job.derived_keywords,
        "raw": job.raw,
    }


def save_raw_jobs(jobs: list[JobPosting], run_id: str) -> Path:
    path = Path(f"data/raw_jobs/raw_jobs_{run_id}.json")
    payload = [job.raw for job in jobs]
    write_json(path, payload)
    return path


def save_enriched_jobs(jobs: list[JobPosting], run_id: str) -> Path:
    path = Path(f"data/enriched_jobs/enriched_jobs_{run_id}.json")
    payload = [job_to_dict(job) for job in jobs]
    write_json(path, payload)
    return path


def export_ranked_jobs_json(ranked: list[RankedJob], output_path: Path) -> None:
    payload = [ranked_job_to_dict(item) for item in ranked]
    write_json(output_path, payload)


def save_ranked_snapshot(ranked: list[RankedJob], run_id: str) -> Path:
    path = Path(f"data/outputs/ranked_jobs_{run_id}.json")
    payload = [ranked_job_to_dict(item) for item in ranked]
    write_json(path, payload)
    return path


def print_ranked_jobs(ranked: list[RankedJob], limit: int = 10) -> None:
    print("\nTOP CAREER TARGETS:\n")

    for item in ranked[:limit]:
        print(f"{item.score.total:.2f} [{item.tier}] | {item.job.title} @ {item.job.company}")
        print(f"→ {item.likely_business_problem}")
        print(
            "   "
            f"skills: {item.score.skills_score:.2f} | "
            f"tools: {item.score.tools_score:.2f} | "
            f"roles: {item.score.role_score:.2f} | "
            f"industry: {item.score.industry_score:.2f} | "
            f"location: {item.score.location_score:.2f} | "
            f"penalty: {item.score.seniority_penalty:.2f} | "
            f"confidence: {item.score.confidence:.2f}"
        )
        print(f"   matched skills: {', '.join(item.score.matched_skills) or 'none'}")
        print(f"   matched tools: {', '.join(item.score.matched_tools) or 'none'}")
        print(f"   matched roles: {', '.join(item.score.matched_titles) or 'none'}")
        print(f"   positioning: {item.positioning_angle}")
        if item.job_dna:
            print(f"   hiring intent: {item.job_dna.get('hiring_intent')}")
            print(f"   operator type: {item.job_dna.get('operator_type')}")
            print(f"   wrong-hire risk: {item.job_dna.get('wrong_hire_risk')}")

        if item.score.notes:
            print(f"   notes: {' '.join(item.score.notes)}")

        print()