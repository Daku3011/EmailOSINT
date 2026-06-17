"""Social media profile checker.

Performs HTTP HEAD requests against popular social platforms to
determine if a username has an active profile. Uses a shared
httpx client for connection reuse.
"""

import logging

import httpx

from models.schemas import UsernameResult
from config import HTTP_TIMEOUT

logger = logging.getLogger(__name__)

PLATFORMS: dict[str, str] = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "LinkedIn": "https://www.linkedin.com/in/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "Reddit": "https://www.reddit.com/user/{}",
}


async def check_platform(
    client: httpx.AsyncClient,
    username: str,
    platform: str,
    url_template: str,
) -> UsernameResult:
    """Check if a username exists on a specific platform.

    Uses HTTP HEAD with redirect following to determine profile existence.

    Args:
        client: Shared httpx client for connection reuse.
        username: Username to check.
        platform: Platform name for reporting.
        url_template: URL template with {} placeholder.

    Returns:
        UsernameResult with existence status.
    """
    url = url_template.format(username)
    try:
        response = await client.head(url, follow_redirects=True)
        exists = response.status_code == 200
    except httpx.TimeoutException:
        logger.debug("Timeout checking %s for '%s'", platform, username)
        exists = False
    except Exception as e:
        logger.debug("Error checking %s for '%s': %s", platform, username, e)
        exists = False

    return UsernameResult(
        username=username,
        platform=platform,
        profile_url=url if exists else None,
        exists=exists,
    )


async def check_social_profiles(username: str) -> list[UsernameResult]:
    """Check a username against all configured social platforms.

    Uses a single shared HTTP client for all platform checks
    to benefit from connection pooling.

    Args:
        username: Username to search for.

    Returns:
        List of UsernameResult for platforms where the profile exists.
    """
    async with httpx.AsyncClient(
        timeout=HTTP_TIMEOUT,
        headers={"User-Agent": "EmailOSINT/1.1"},
    ) as client:
        import asyncio
        tasks = [
            check_platform(client, username, platform, template)
            for platform, template in PLATFORMS.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    found = []
    for r in results:
        if isinstance(r, Exception):
            logger.debug("Social check failed: %s", r)
        elif r.exists:
            found.append(r)

    logger.debug("Found %d social profiles for '%s'", len(found), username)
    return found
