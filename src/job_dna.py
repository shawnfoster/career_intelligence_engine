from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.models import JobPosting


@dataclass
class JobDNA:
    hiring_intent: str
    business_problem: str
    operator_type: str
    likely_success_profile: str
    wrong_hire_risk: str
    positioning_hook: str
    proof_points_needed: list[str]
    detected_signals: list[str]
    signal_scores: dict[str, float]
    primary_signal: str


SIGNAL_MAP: dict[str, dict[str, Any]] = {
    "analytics_visibility": {
        "keywords": {
            "data analyst": 4.0,
            "analytics analyst": 4.0,
            "business intelligence": 4.0,
            "dashboard": 2.4,
            "reporting": 2.4,
            "kpi": 2.2,
            "metrics": 2.0,
            "insights": 2.0,
            "analytics": 1.8,
            "data analysis": 2.0,
            "looker": 1.4,
            "tableau": 1.4,
            "power bi": 1.4,
            "sql": 0.8,
            "python": 0.7,
        },
        "business_problem": "Leadership likely needs clearer visibility into performance, trends, and operational bottlenecks.",
        "hiring_intent": "Decision-support analytics",
        "operator_type": "Analytical translator",
        "wrong_hire_risk": "Hiring someone who can build reports but cannot explain what the numbers mean for business action.",
        "positioning_hook": "Position yourself as someone who turns messy data into executive-ready decisions, not just dashboards.",
        "proof_points_needed": [
            "Dashboard or reporting example",
            "KPI framework",
            "Business recommendation based on data",
        ],
    },
    "finance_strategy": {
        "keywords": {
            "finance": 3.4,
            "financial": 2.8,
            "billing": 2.8,
            "fp&a": 3.5,
            "budget": 2.3,
            "forecast": 1.8,
            "modeling": 2.2,
            "variance": 2.4,
            "unit economics": 3.0,
            "pricing": 2.0,
            "accounting": 2.3,
            "margin": 1.8,
        },
        "business_problem": "The company likely needs sharper financial visibility, planning discipline, and decision support around growth tradeoffs.",
        "hiring_intent": "Financial planning and analytical support",
        "operator_type": "Finance-minded analyst",
        "wrong_hire_risk": "Hiring someone who can manipulate spreadsheets but cannot explain financial tradeoffs to operators.",
        "positioning_hook": "Lead with analytical rigor, accounting discipline, and your ability to explain financial implications clearly.",
        "proof_points_needed": [
            "Financial model or budget scenario",
            "Variance analysis example",
            "Business case or ROI analysis",
        ],
    },
    "revenue_operations": {
        "keywords": {
            "revenue operations": 3.2,
            "revops": 3.2,
            "sales operations": 3.0,
            "pipeline": 2.5,
            "crm": 1.7,
            "salesforce": 1.5,
            "arr": 1.3,
            "nrr": 1.3,
            "conversion": 1.4,
            "monetization": 2.2,
            "go-to-market": 2.0,
            "gtm": 2.0,
        },
        "business_problem": "The company likely needs cleaner revenue processes, better pipeline visibility, and stronger operating rhythm.",
        "hiring_intent": "Revenue process improvement",
        "operator_type": "Revenue systems operator",
        "wrong_hire_risk": "Hiring someone who understands tools but cannot connect process hygiene to revenue outcomes.",
        "positioning_hook": "Lead with Salesforce, forecasting, pipeline discipline, and your ability to make revenue data trustworthy.",
        "proof_points_needed": [
            "CRM/process cleanup example",
            "Forecasting or pipeline reporting example",
            "Revenue metric explanation: ARR, NRR, churn, or conversion",
        ],
    },
    "customer_success": {
        "keywords": {
            "customer success": 3.5,
            "retention": 2.7,
            "churn": 2.7,
            "adoption": 2.6,
            "renewal": 2.6,
            "customer health": 3.0,
            "customer outcome": 2.4,
            "onboarding": 2.0,
            "account management": 1.8,
            "nrr": 1.6,
            "arr": 1.1,
        },
        "business_problem": "The company likely needs to protect recurring revenue by improving adoption, retention, and customer health.",
        "hiring_intent": "Retention and adoption protection",
        "operator_type": "Customer outcome strategist",
        "wrong_hire_risk": "Hiring a relationship manager who cannot diagnose churn risk or translate customer behavior into action.",
        "positioning_hook": "Frame yourself around adoption, customer risk, and revenue protection instead of generic account support.",
        "proof_points_needed": [
            "Customer health framework",
            "Retention or adoption analysis",
            "Example of translating customer behavior into action",
        ],
    },
    "strategy_operations": {
        "keywords": {
            "business operations": 3.0,
            "process improvement": 2.8,
            "operating rhythm": 2.8,
            "cross-functional": 2.3,
            "program manager": 2.4,
            "stakeholder management": 1.6,
            "execution": 1.5,
            "roadmap": 1.3,
            "strategy": 0.9,
            "operations": 0.8,
            "planning": 0.8,
        },
        "business_problem": "The company likely needs someone who can bring structure to ambiguity and coordinate decisions across teams.",
        "hiring_intent": "Strategic operations support",
        "operator_type": "Structured ambiguity operator",
        "wrong_hire_risk": "Hiring someone who creates plans but cannot drive follow-through across teams.",
        "positioning_hook": "Position yourself as a systems thinker who can move from ambiguity to operating rhythm.",
        "proof_points_needed": [
            "Process improvement example",
            "Cross-functional project example",
            "Decision framework or operating cadence example",
        ],
    },
}


TITLE_BOOSTS: dict[str, dict[str, float]] = {
    "analytics_visibility": {
        "data analyst": 5.0,
        "analytics analyst": 5.0,
        "business intelligence": 5.0,
        "bi analyst": 5.0,
        "analyst": 1.5,
        "analytics": 3.0,
    },
    "finance_strategy": {
        "finance": 4.0,
        "financial": 3.2,
        "billing": 3.0,
        "fp&a": 4.0,
    },
    "revenue_operations": {
        "revenue operations": 4.0,
        "revops": 4.0,
        "sales operations": 3.5,
        "monetization": 2.5,
    },
    "customer_success": {
        "customer success": 4.0,
        "retention": 3.0,
        "renewal": 3.0,
    },
    "strategy_operations": {
        "strategy & operations": 4.0,
        "strategy and operations": 4.0,
        "business operations": 3.5,
        "program manager": 3.0,
        "people operations": 3.0,
    },
}


def job_text(job: JobPosting) -> str:
    return " ".join(
        [
            job.title or "",
            job.team or "",
            job.description or "",
            job.requirements_text or "",
            " ".join(job.derived_skills or []),
            " ".join(job.derived_tools or []),
        ]
    ).lower()


def count_keyword_hits(text: str, keyword: str) -> int:
    return text.count(keyword.lower())


def score_signal(job: JobPosting, signal_name: str, signal_data: dict[str, Any]) -> float:
    text = job_text(job)
    title = (job.title or "").lower()
    score = 0.0

    for keyword, weight in signal_data["keywords"].items():
        hits = count_keyword_hits(text, keyword)
        if hits:
            score += min(hits, 3) * float(weight)

    for keyword, boost in TITLE_BOOSTS.get(signal_name, {}).items():
        if keyword in title:
            score += float(boost)

    return round(score, 2)


def apply_calibration_rules(job: JobPosting, scores: dict[str, float]) -> dict[str, float]:
    title = (job.title or "").lower()

    if "data analyst" in title or "analytics analyst" in title or "business intelligence" in title:
        scores["analytics_visibility"] += 4.0
        scores["strategy_operations"] *= 0.65

    if "finance" in title or "financial" in title or "billing" in title or "fp&a" in title:
        scores["finance_strategy"] += 3.0

    if "customer success" in title:
        scores["customer_success"] += 4.0

    if "monetization" in title and "operations" in title:
        scores["revenue_operations"] += 5.0
        scores["finance_strategy"] *= 0.55
        scores["analytics_visibility"] *= 0.85

    if "program manager" in title or "people operations" in title:
        scores["strategy_operations"] += 3.0

    return {k: round(v, 2) for k, v in scores.items()}


def score_all_signals(job: JobPosting) -> dict[str, float]:
    scores = {
        signal_name: score_signal(job, signal_name, signal_data)
        for signal_name, signal_data in SIGNAL_MAP.items()
    }

    scores = apply_calibration_rules(job, scores)
    return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))


def choose_primary_signal(signal_scores: dict[str, float]) -> str:
    if not signal_scores:
        return "analytics_visibility"

    top_signal, top_score = next(iter(signal_scores.items()))
    if top_score <= 0:
        return "analytics_visibility"

    return top_signal


def detected_signals_from_scores(signal_scores: dict[str, float]) -> list[str]:
    return [signal for signal, score in signal_scores.items() if score > 0]


def build_job_dna(job: JobPosting) -> JobDNA:
    signal_scores = score_all_signals(job)
    primary_signal = choose_primary_signal(signal_scores)
    signal_data = SIGNAL_MAP[primary_signal]

    return JobDNA(
        hiring_intent=signal_data["hiring_intent"],
        business_problem=signal_data["business_problem"],
        operator_type=signal_data["operator_type"],
        likely_success_profile=build_success_profile(job, primary_signal),
        wrong_hire_risk=signal_data["wrong_hire_risk"],
        positioning_hook=signal_data["positioning_hook"],
        proof_points_needed=signal_data["proof_points_needed"],
        detected_signals=detected_signals_from_scores(signal_scores),
        signal_scores=signal_scores,
        primary_signal=primary_signal,
    )


def build_success_profile(job: JobPosting, primary_signal: str) -> str:
    if primary_signal == "analytics_visibility":
        return "Someone who can analyze data, explain patterns clearly, and connect findings to business decisions."
    if primary_signal == "finance_strategy":
        return "Someone who can combine financial discipline with practical operating judgment."
    if primary_signal == "revenue_operations":
        return "Someone who understands systems, process, reporting, and revenue accountability."
    if primary_signal == "customer_success":
        return "Someone who can understand customer behavior, spot risk early, and protect retention."
    if primary_signal == "strategy_operations":
        return "Someone who can create structure, improve workflows, and keep cross-functional execution moving."

    return "Someone who can bring order to ambiguity and turn information into action."


def job_dna_to_dict(dna: JobDNA) -> dict[str, Any]:
    return asdict(dna)