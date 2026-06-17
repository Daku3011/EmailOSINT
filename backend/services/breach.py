"""Breach detection service.

Checks email against the XposedOrNot API and a local breach database
for known data breaches. Results are deduplicated.
"""

import json
import logging
import asyncio
import pathlib
from functools import lru_cache

import httpx

from models.schemas import Breach
from config import HTTP_TIMEOUT

logger = logging.getLogger(__name__)

XON_API = "https://api.xposedornot.com/v1"
BREACH_DB_PATH = pathlib.Path(__file__).parent / "breach_data.json"


@lru_cache(maxsize=1)
def _load_local_breaches() -> dict[str, dict]:
    """Load and cache the local breach database.

    Returns:
        Dict mapping lowercase domain to breach record.
    """
    try:
        with open(BREACH_DB_PATH, encoding="utf-8") as f:
            breaches = json.load(f)
        return {
            b["Domain"].lower(): b
            for b in breaches
            if isinstance(b, dict) and b.get("Domain")
        }
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Failed to load local breach DB: %s", e)
        return {}


async def check_breaches(email: str) -> list[Breach]:
    """Check an email against breach databases.

    Queries the XposedOrNot API and local breach records,
    deduplicating by breach name.

    Args:
        email: Normalized email address.

    Returns:
        List of unique Breach records found.
    """
    seen: set[str] = set()
    results: list[Breach] = []

    # Check XposedOrNot API
    xon_results = await _check_xposedornot(email)
    for b in xon_results:
        if b.name not in seen:
            seen.add(b.name)
            results.append(b)

    # Check local database
    loop = asyncio.get_running_loop()
    local_db = await loop.run_in_executor(None, _load_local_breaches)
    domain = email.split("@")[1].lower() if "@" in email else ""

    if domain in local_db:
        b = local_db[domain]
        breach_name = b.get("Name", "Unknown")
        if breach_name not in seen:
            seen.add(breach_name)
            results.append(Breach(
                name=breach_name,
                domain=b.get("Domain", ""),
                date=b.get("BreachDate"),
                data_classes=b.get("DataClasses", []),
                description=b.get("Description"),
            ))

    logger.info("Found %d breaches for %s", len(results), email)
    return results


async def _check_xposedornot(email: str) -> list[Breach]:
    """Query the XposedOrNot API for breach data.

    Args:
        email: Email to check.

    Returns:
        List of Breach records from the API.
    """
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            resp = await client.get(f"{XON_API}/check-email/{email}")

        if resp.status_code == 200:
            data = resp.json()
            breaches_raw = data.get("breaches", [])
            return [
                Breach(
                    name=b[0] if isinstance(b, list) else str(b),
                    domain="",
                    date=None,
                )
                for b in breaches_raw
            ]
        elif resp.status_code == 404:
            # No breaches found — expected response
            return []
        else:
            logger.warning(
                "XposedOrNot returned %d for %s", resp.status_code, email
            )
    except httpx.TimeoutException:
        logger.warning("XposedOrNot request timed out for %s", email)
    except Exception as e:
        logger.warning("XposedOrNot error for %s: %s", email, e)

    return []
