"""API router for email OSINT analysis operations.

Handles the /analyze endpoint which orchestrates all intelligence
gathering services, and the /report endpoint for retrieving saved reports.
"""

import uuid
import asyncio
import logging
import time
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Request
from models.schemas import EmailRequest, Report
from services.validator import validate_email
from services.domain import get_domain_info
from services.breach import check_breaches
from services.gravatar import check_gravatar
from services.search import search_email
from services.username import search_usernames
from services.social import check_social_profiles
from database import save_report, get_report
from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS

logger = logging.getLogger(__name__)

router = APIRouter()

# Simple in-memory rate limiter
_rate_store: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(client_ip: str) -> bool:
    """Return True if the client is within rate limits.

    Uses a sliding window counter pattern.
    """
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    # Clean expired entries
    _rate_store[client_ip] = [
        ts for ts in _rate_store[client_ip] if ts > window_start
    ]
    if len(_rate_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    _rate_store[client_ip].append(now)
    return True


@router.post("/analyze", response_model=Report, summary="Analyze an email address")
async def analyze_email(req: EmailRequest, request: Request):
    """Run comprehensive OSINT analysis on an email address.

    Gathers domain information, breach data, Gravatar profile,
    web mentions, and social media profiles concurrently.

    Returns a complete Report with a calculated risk score.
    """
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )

    # Validate email
    is_valid, normalized_email = validate_email(req.email)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid email: {normalized_email}")

    report_id = str(uuid.uuid4())
    logger.info("Starting analysis %s for %s from %s", report_id, normalized_email, client_ip)

    # Run all intelligence gathering concurrently
    domain = normalized_email.split("@")[1]
    tasks = {
        "domain": get_domain_info(domain),
        "breaches": check_breaches(normalized_email),
        "gravatar": check_gravatar(normalized_email),
        "search": search_email(normalized_email),
        "usernames": search_usernames(normalized_email),
    }

    raw_results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    results = dict(zip(tasks.keys(), raw_results))

    # Extract results with graceful fallbacks and logging
    domain_info = results["domain"] if not isinstance(results["domain"], Exception) else None
    breaches = results["breaches"] if not isinstance(results["breaches"], Exception) else []
    gravatar = results["gravatar"] if not isinstance(results["gravatar"], Exception) else None
    search_results = results["search"] if not isinstance(results["search"], Exception) else []
    username_results = results["usernames"] if not isinstance(results["usernames"], Exception) else []

    # Log any service failures
    for key, result in results.items():
        if isinstance(result, Exception):
            logger.warning("Service '%s' failed for %s: %s", key, normalized_email, result)

    # Enrich with social profile checks
    if username_results:
        social_tasks = [check_social_profiles(u.username) for u in username_results]
        social_results = await asyncio.gather(*social_tasks, return_exceptions=True)
        social_profiles = []
        for sr in social_results:
            if not isinstance(sr, Exception):
                social_profiles.extend(sr)
            else:
                logger.warning("Social profile check failed: %s", sr)

        # Deduplicate by (username, platform)
        seen_profiles: set[tuple[str, str]] = set()
        all_usernames = []
        for u in username_results + social_profiles:
            key = (u.username, u.platform)
            if key not in seen_profiles:
                seen_profiles.add(key)
                all_usernames.append(u)
    else:
        all_usernames = []

    risk_score = calculate_risk(
        len(breaches),
        gravatar.exists if gravatar else False,
        len(all_usernames),
    )

    report = Report(
        id=report_id,
        email=normalized_email,
        is_valid=True,
        domain_info=domain_info,
        breaches=breaches,
        gravatar=gravatar,
        usernames=all_usernames,
        search_results=search_results,
        risk_score=risk_score,
    )

    await save_report(report)
    logger.info("Analysis complete for %s — risk: %.0f%%", normalized_email, risk_score)
    return report


@router.get("/report/{report_id}", response_model=Report, summary="Retrieve a saved report")
async def get_existing_report(report_id: str):
    """Fetch a previously generated analysis report by its ID.

    Returns 404 if the report doesn't exist.
    """
    # Basic UUID format validation
    try:
        uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid report ID format")

    report = await get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


def calculate_risk(breach_count: int, has_gravatar: bool, profile_count: int) -> float:
    """Calculate a composite risk score from 0-100.

    Weighting:
    - Breaches: up to 50 points (15 per breach)
    - Gravatar presence: 10 points (indicates public profile)
    - Social profiles: up to 20 points (5 per profile)
    - Base exposure: 20 points (email exists on the internet)

    Args:
        breach_count: Number of breaches found.
        has_gravatar: Whether a Gravatar profile exists.
        profile_count: Number of social profiles discovered.

    Returns:
        Risk score between 0 and 100.
    """
    score = 0.0
    score += min(breach_count * 15, 50)
    if has_gravatar:
        score += 10
    score += min(profile_count * 5, 20)
    score += 20  # base exposure score
    return min(score, 100)
