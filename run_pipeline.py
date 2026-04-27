from __future__ import annotations

import argparse
from pathlib import Path

from src.exporter import (
    export_ranked_jobs_json,
    print_ranked_jobs,
    save_enriched_jobs,
    save_ranked_snapshot,
    save_raw_jobs,
    timestamp_slug,
)
from src.ingest import AshbySource, GreenhouseSource, JobSource, LeverSource, fetch_from_sources
from src.models import CandidateProfile
from src.scorer import rank_jobs


def get_default_profile() -> CandidateProfile:
    return CandidateProfile(
        name="Shawn Foster",
        target_titles=[
            "Business Intelligence Analyst",
            "Data Analyst",
            "Business Analyst",
            "Revenue Operations Analyst",
            "Strategy Operations Analyst",
            "Customer Success Manager",
        ],
        industries=["saas", "healthcare", "education", "fintech"],
        skills=[
            "sql",
            "python",
            "analytics",
            "business intelligence",
            "dashboarding",
            "data analysis",
            "stakeholder management",
            "customer success",
            "revenue operations",
            "forecasting",
            "pipeline management",
            "onboarding",
            "adoption",
            "churn",
            "nrr",
            "arr",
            "a/b testing",
        ],
        tools=[
            "sql",
            "python",
            "tableau",
            "power bi",
            "looker",
            "salesforce",
            "excel",
            "sheets",
        ],
        strengths=[
            "Turns messy information into structured decision-making",
            "Connects analytics to revenue, retention, and customer outcomes",
            "Can frame business problems in operator language, not just analyst language",
        ],
        risk_reframes=[
            "May not come from a brand-name SaaS ladder, but brings real operator judgment and cross-functional pattern recognition.",
            "Can bridge BI, customer-facing insight, and strategic execution in smaller or ambiguous environments.",
        ],
        must_have_locations=["Chicago", "Remote", "Illinois"],
        avoid_titles=["Director", "Vice President", "Head of"],
        years_experience_hint=4.0,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Career Intelligence Engine Pipeline")
    parser.add_argument("--greenhouse", nargs="*", default=[], help="Greenhouse board tokens")
    parser.add_argument("--lever", nargs="*", default=[], help="Lever company handles")
    parser.add_argument("--ashby", nargs="*", default=[], help="Ashby organization slugs")
    parser.add_argument("--output", default="data/outputs/ranked_jobs.json")
    parser.add_argument("--limit", type=int, default=10)
    return parser.parse_args()


def build_sources(args: argparse.Namespace) -> list[JobSource]:
    sources: list[JobSource] = []
    sources.extend(GreenhouseSource(token) for token in args.greenhouse)
    sources.extend(LeverSource(handle) for handle in args.lever)
    sources.extend(AshbySource(slug) for slug in args.ashby)
    return sources


def main() -> None:
    args = parse_args()
    profile = get_default_profile()
    sources = build_sources(args)
    run_id = timestamp_slug()

    if not sources:
        print("No sources provided.")
        print("Example: python run_pipeline.py --greenhouse stripe")
        return

    print("Running Career Intelligence Engine...\n")
    print(f"Run ID: {run_id}")

    jobs = fetch_from_sources(sources)
    print(f"Jobs found: {len(jobs)}")

    raw_path = save_raw_jobs(jobs, run_id)
    enriched_path = save_enriched_jobs(jobs, run_id)

    ranked = rank_jobs(profile, jobs)
    print_ranked_jobs(ranked, limit=args.limit)

    export_ranked_jobs_json(ranked, Path(args.output))
    ranked_snapshot_path = save_ranked_snapshot(ranked, run_id)

    print("Saved files:")
    print(f"- Raw jobs: {raw_path}")
    print(f"- Enriched jobs: {enriched_path}")
    print(f"- Latest ranked output: {args.output}")
    print(f"- Ranked snapshot: {ranked_snapshot_path}")


if __name__ == "__main__":
    main()