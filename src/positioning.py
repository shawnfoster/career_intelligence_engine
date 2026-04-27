from __future__ import annotations

from src.models import CandidateProfile, JobPosting


def likely_business_problem(job: JobPosting) -> str:
    text = job.combined_text().lower()

    if any(x in text for x in ["dashboard", "reporting", "kpi", "insights"]):
        return "They likely need clearer visibility into performance so leaders can make faster decisions."
    if any(x in text for x in ["customer success", "retention", "churn", "adoption"]):
        return "They are likely trying to reduce customer risk, improve adoption, or protect recurring revenue."
    if any(x in text for x in ["salesforce", "pipeline", "forecasting", "revops"]):
        return "They likely have revenue process friction and need cleaner systems, forecasting, and pipeline trust."
    return "They likely need a more reliable operator who can turn messy information into decisions and action."


def positioning_angle(
    profile: CandidateProfile,
    job: JobPosting,
    matched_skills: list[str],
    matched_titles: list[str],
) -> str:
    if matched_titles:
        return (
            f"Position as a low-ramp operator for {matched_titles[0]} work: "
            f"someone who can step in, organize ambiguity, and translate data into action."
        )
    if any(skill in matched_skills for skill in ["customer success", "churn", "nrr", "arr"]):
        return "Lead with revenue protection, adoption, and cross-functional insight rather than generic analytics language."
    if any(skill in matched_skills for skill in ["sql", "tableau", "power bi", "looker"]):
        return "Lead with decision support: reporting clarity, KPI design, and stakeholder trust in the numbers."
    return "Lead with pattern recognition, business judgment, and the ability to bring order to fast-moving environments."