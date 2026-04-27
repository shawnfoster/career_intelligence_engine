from __future__ import annotations

from typing import Tuple

from config import INDUSTRY_KEYWORDS, TITLE_WEIGHTS
from src.job_dna import build_job_dna, job_dna_to_dict
from src.models import CandidateProfile, JobPosting, RankedJob, ScoreBreakdown
from src.positioning import likely_business_problem, positioning_angle
from src.utils import normalize_term


def overlap_score(candidate_terms: list[str], job_terms: list[str], weight: float = 1.0) -> Tuple[float, list[str]]:
    cand = {normalize_term(x) for x in candidate_terms}
    job = {normalize_term(x) for x in job_terms}
    matched = sorted(cand.intersection(job))

    if not cand:
        return 0.0, matched

    score = (len(matched) / len(cand)) * weight
    return score, matched


def title_match_score(target_titles: list[str], job_title: str) -> Tuple[float, list[str]]:
    title_l = job_title.lower()
    matches = []
    score = 0.0

    for target in target_titles:
        target_l = target.lower()
        if target_l in title_l or title_l in target_l:
            matches.append(target)
            score = max(score, TITLE_WEIGHTS.get(target_l, 1.8))
        else:
            token_overlap = set(target_l.split()).intersection(set(title_l.split()))
            if len(token_overlap) >= 2:
                matches.append(target)
                score = max(score, TITLE_WEIGHTS.get(target_l, 1.5))

    return score, sorted(set(matches))


def industry_score(candidate_industries: list[str], job_text: str) -> float:
    text_l = job_text.lower()
    score = 0.0

    for industry in candidate_industries:
        for kw in INDUSTRY_KEYWORDS.get(industry.lower(), []):
            if kw in text_l:
                score += 0.3

    return min(score, 1.5)


def location_score(candidate_locations: list[str], job_location: str | None, remote_type: str | None) -> float:
    if remote_type and "remote" in remote_type.lower():
        return 1.0
    if not candidate_locations:
        return 0.3
    if not job_location:
        return 0.2

    jl = job_location.lower()
    for loc in candidate_locations:
        if loc.lower() in jl:
            return 1.0

    return 0.0


def seniority_penalty(profile: CandidateProfile, job: JobPosting) -> float:
    title_l = job.title.lower()
    text_l = job.combined_text().lower()

    if any(x in title_l for x in ["director", "vp", "vice president", "head of"]):
        return 2.0
    if job.level_hint == "senior" and (profile.years_experience_hint or 0) < 4:
        return 1.2
    if "10+ years" in text_l and (profile.years_experience_hint or 0) < 6:
        return 2.5

    return 0.0


def confidence_estimate(job: JobPosting) -> float:
    completeness = 0

    for field_name in [job.title, job.company, job.description, job.url, job.location, job.posted_at]:
        if field_name:
            completeness += 1

    return round(completeness / 6, 2)


def tier_from_score(score: float) -> str:
    if score >= 5.0:
        return "HIGH"
    if score >= 3.2:
        return "MEDIUM"
    return "LOW"


def score_job(profile: CandidateProfile, job: JobPosting) -> ScoreBreakdown:
    skills_score, matched_skills = overlap_score(profile.skills, job.derived_skills, weight=3.0)
    tools_score, matched_tools = overlap_score(profile.tools, job.derived_tools, weight=2.0)
    role_score, matched_titles = title_match_score(profile.target_titles, job.title)
    ind_score = industry_score(profile.industries, job.combined_text())
    loc_score = location_score(profile.must_have_locations, job.location, job.remote_type)
    penalty = seniority_penalty(profile, job)
    confidence = confidence_estimate(job)

    total = skills_score + tools_score + role_score + ind_score + loc_score - penalty

    notes = []

    if matched_skills:
        notes.append("Strong skill overlap is present.")
    if matched_tools:
        notes.append("Relevant tool overlap is present.")
    if matched_titles:
        notes.append("Role alignment is especially strong.")
    if penalty > 0:
        notes.append("Job may be priced or leveled above a smart-entry target.")
    if confidence < 0.6:
        notes.append("Source data is incomplete, so confidence is lower.")

    return ScoreBreakdown(
        total=round(total, 2),
        skills_score=round(skills_score, 2),
        tools_score=round(tools_score, 2),
        role_score=round(role_score, 2),
        industry_score=round(ind_score, 2),
        location_score=round(loc_score, 2),
        seniority_penalty=round(penalty, 2),
        confidence=confidence,
        matched_skills=matched_skills,
        matched_tools=matched_tools,
        matched_titles=matched_titles,
        notes=notes,
    )


def rank_jobs(profile: CandidateProfile, jobs: list[JobPosting]) -> list[RankedJob]:
    ranked: list[RankedJob] = []

    for job in jobs:
        score = score_job(profile, job)
        dna = build_job_dna(job)

        ranked.append(
            RankedJob(
                rank=0,
                tier=tier_from_score(score.total),
                job=job,
                score=score,
                positioning_angle=positioning_angle(
                    profile, job, score.matched_skills, score.matched_titles
                ),
                likely_business_problem=likely_business_problem(job),
                job_dna=job_dna_to_dict(dna),
            )
        )

    ranked.sort(key=lambda x: (x.score.total, x.score.confidence), reverse=True)

    for idx, item in enumerate(ranked, start=1):
        item.rank = idx

    return ranked