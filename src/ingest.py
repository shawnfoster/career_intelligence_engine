from __future__ import annotations

from typing import Any, Dict, Iterable, List, Protocol

import requests

from config import DEFAULT_HEADERS, DEFAULT_TIMEOUT
from src.models import JobPosting
from src.parser import enrich_job, safe_get
from src.utils import clean_text, slugify


class JobSource(Protocol):
    def fetch_jobs(self) -> List[JobPosting]:
        ...


class GreenhouseSource:
    def __init__(self, board_token: str):
        self.board_token = board_token

    def fetch_jobs(self) -> List[JobPosting]:
        url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_token}/jobs"
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        payload = response.json()

        jobs: List[JobPosting] = []

        for item in payload.get("jobs", []):
            job_id = item.get("id")

            detail_url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_token}/jobs/{job_id}"
            detail_response = requests.get(
                detail_url,
                headers=DEFAULT_HEADERS,
                timeout=DEFAULT_TIMEOUT,
            )

            detail_data: Dict[str, Any] = {}
            description = ""
            requirements = ""

            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                description = clean_text(detail_data.get("content", ""))

            job = JobPosting(
                source="greenhouse",
                source_type="hosted_board",
                external_id=str(job_id),
                title=item.get("title", "Unknown Title"),
                company=self.board_token,
                location=safe_get(item, ["location", "name"]),
                url=item.get("absolute_url"),
                posted_at=item.get("updated_at"),
                description=description,
                requirements_text=requirements,
                raw=detail_data or item,
            )

            enrich_job(job)
            jobs.append(job)

        return jobs


class LeverSource:
    def __init__(self, company_handle: str):
        self.company_handle = company_handle

    def fetch_jobs(self) -> List[JobPosting]:
        url = f"https://api.lever.co/v0/postings/{self.company_handle}?mode=json"
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        payload = response.json()

        jobs: List[JobPosting] = []

        for item in payload:
            description = clean_text(
                item.get("descriptionPlain")
                or item.get("description")
                or ""
            )

            requirements = clean_text(
                item.get("lists", [{}])[0].get("text", "")
                if item.get("lists")
                else ""
            )

            categories = item.get("categories", {})

            job = JobPosting(
                source="lever",
                source_type="hosted_board",
                external_id=str(item.get("id")),
                title=item.get("text", "Unknown Title"),
                company=self.company_handle,
                location=categories.get("location"),
                team=categories.get("team"),
                employment_type=categories.get("commitment"),
                remote_type=categories.get("workplaceType"),
                url=item.get("hostedUrl") or item.get("applyUrl"),
                posted_at=item.get("createdAt"),
                description=description,
                requirements_text=requirements,
                raw=item,
            )

            enrich_job(job)
            jobs.append(job)

        return jobs


class AshbySource:
    def __init__(self, organization_slug: str):
        self.organization_slug = organization_slug

    def fetch_jobs(self) -> List[JobPosting]:
        url = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"

        payload = {
            "query": (
                "query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) {"
                " jobBoard: jobBoardWithTeams(organizationHostedJobsPageName: $organizationHostedJobsPageName) {"
                "   teams { id name parentTeamId }"
                "   jobPostings {"
                "     id title locationName employmentType updatedAt"
                "     secondaryLocations { locationName }"
                "     applyUrl"
                "     descriptionHtml"
                "     team { name }"
                "   }"
                " }"
                "}"
            ),
            "variables": {
                "organizationHostedJobsPageName": self.organization_slug,
            },
        }

        response = requests.post(
            url,
            json=payload,
            headers=DEFAULT_HEADERS,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        postings = safe_get(data, ["data", "jobBoard", "jobPostings"], [])
        jobs: List[JobPosting] = []

        for item in postings:
            job = JobPosting(
                source="ashby",
                source_type="hosted_board",
                external_id=str(item.get("id")),
                title=item.get("title", "Unknown Title"),
                company=self.organization_slug,
                location=item.get("locationName"),
                employment_type=item.get("employmentType"),
                team=safe_get(item, ["team", "name"]),
                url=item.get("applyUrl"),
                posted_at=item.get("updatedAt"),
                description=clean_text(item.get("descriptionHtml", "")),
                raw=item,
            )

            enrich_job(job)
            jobs.append(job)

        return jobs


class GenericJsonSource:
    def __init__(
        self,
        url: str,
        company_name: str,
        title_key: str = "title",
        desc_key: str = "description",
    ):
        self.url = url
        self.company_name = company_name
        self.title_key = title_key
        self.desc_key = desc_key

    def fetch_jobs(self) -> List[JobPosting]:
        response = requests.get(
            self.url,
            headers=DEFAULT_HEADERS,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        items: Iterable[Dict[str, Any]]

        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            items = payload.get("jobs", [])
        else:
            items = []

        jobs: List[JobPosting] = []

        for item in items:
            job = JobPosting(
                source="generic_json",
                source_type="company_json",
                external_id=str(
                    item.get("id")
                    or item.get("req_id")
                    or slugify(item.get(self.title_key, "job"))
                ),
                title=item.get(self.title_key, "Unknown Title"),
                company=self.company_name,
                location=item.get("location"),
                employment_type=item.get("employment_type"),
                url=item.get("url") or item.get("apply_url"),
                posted_at=item.get("posted_at"),
                description=clean_text(item.get(self.desc_key, "")),
                requirements_text=clean_text(item.get("requirements", "")),
                raw=item,
            )

            enrich_job(job)
            jobs.append(job)

        return jobs


def dedupe_jobs(jobs: List[JobPosting]) -> List[JobPosting]:
    seen: set[str] = set()
    deduped: List[JobPosting] = []

    for job in jobs:
        key = (
            f"{job.company.lower()}::"
            f"{job.title.lower()}::"
            f"{(job.location or '').lower()}::"
            f"{job.url or job.external_id}"
        )

        if key not in seen:
            seen.add(key)
            deduped.append(job)

    return deduped


def fetch_from_sources(sources: List[JobSource]) -> List[JobPosting]:
    all_jobs: List[JobPosting] = []

    for source in sources:
        try:
            jobs = source.fetch_jobs()
            all_jobs.extend(jobs)

        except requests.HTTPError as exc:
            print(f"[WARN] HTTP error from source {source.__class__.__name__}: {exc}")

        except requests.RequestException as exc:
            print(f"[WARN] Network error from source {source.__class__.__name__}: {exc}")

        except Exception as exc:
            print(f"[WARN] Unexpected error from source {source.__class__.__name__}: {exc}")

    return dedupe_jobs(all_jobs)