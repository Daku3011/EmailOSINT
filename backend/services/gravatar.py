"""Gravatar profile lookup service.

Checks whether an email has an associated Gravatar profile
by querying the Gravatar avatar URL with a 404 default.
"""

import hashlib
import logging

import httpx

from models.schemas import GravatarResult
from config import HTTP_TIMEOUT

logger = logging.getLogger(__name__)


async def check_gravatar(email: str) -> GravatarResult:
    """Check if a Gravatar profile exists for the given email.

    Uses MD5 hashing per Gravatar API specification.

    Args:
        email: Normalized email address.

    Returns:
        GravatarResult with existence flag and URLs.
    """
    email_hash = hashlib.md5(email.lower().strip().encode("utf-8")).hexdigest()
    avatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=404&size=200"
    profile_url = f"https://www.gravatar.com/{email_hash}"

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.head(avatar_url, follow_redirects=True)

        exists = response.status_code == 200
        logger.debug("Gravatar check for %s: exists=%s", email, exists)

        return GravatarResult(
            exists=exists,
            avatar_url=avatar_url if exists else None,
            profile_url=profile_url if exists else None,
        )
    except httpx.TimeoutException:
        logger.warning("Gravatar request timed out for %s", email)
        return GravatarResult(exists=False)
    except Exception as e:
        logger.warning("Gravatar check error for %s: %s", email, e)
        return GravatarResult(exists=False)
