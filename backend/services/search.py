"""Web search service for email mentions.

Uses Google search to find public web pages mentioning the email address.
Runs synchronous search in a thread executor for async compatibility.
"""

import logging
import asyncio

from googlesearch import search
from models.schemas import SearchResult

logger = logging.getLogger(__name__)

MAX_SEARCH_RESULTS = 10


async def search_email(email: str) -> list[SearchResult]:
    """Search the web for public mentions of an email address.

    Args:
        email: Email address to search for.

    Returns:
        List of SearchResult with URLs where the email was found.
    """
    loop = asyncio.get_running_loop()

    def _search() -> list[SearchResult]:
        results = []
        for url in search(f'"{email}"', num_results=MAX_SEARCH_RESULTS):
            if url and isinstance(url, str):
                results.append(SearchResult(title="", url=url))
        return results

    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, _search),
            timeout=15.0,
        )
    except asyncio.TimeoutError:
        logger.warning("Web search timed out for %s", email)
        return []
    except Exception as e:
        logger.warning("Web search error for %s: %s", email, e)
        return []
