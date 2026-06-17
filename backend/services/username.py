"""Username enumeration and Sherlock integration service.

Generates candidate usernames from the email local part and
runs Sherlock to discover social media profiles.
"""

import asyncio
import logging
import re

from models.schemas import UsernameResult
from config import SHERLOCK_PATH, SHERLOCK_TIMEOUT

logger = logging.getLogger(__name__)

# Maximum usernames to check (limits resource usage)
MAX_USERNAMES = 3


def generate_usernames(email: str) -> list[str]:
    """Generate candidate usernames from an email's local part.

    Produces variations by removing/replacing dots and extracting
    first/last name components.

    Args:
        email: Normalized email address.

    Returns:
        List of unique candidate usernames.
    """
    local_part = email.split("@")[0]
    # Sanitize: only allow alphanumeric, dots, hyphens, underscores
    local_part = re.sub(r"[^a-zA-Z0-9._\-]", "", local_part)

    if not local_part:
        return []

    usernames = set()
    usernames.add(local_part)
    usernames.add(local_part.replace(".", ""))
    usernames.add(local_part.replace(".", "_"))
    usernames.add(local_part.replace(".", "-"))

    if "." in local_part:
        parts = local_part.split(".")
        if parts[0]:
            usernames.add(parts[0])
        if len(parts) >= 2 and parts[0] and parts[-1]:
            usernames.add(f"{parts[0]}{parts[-1]}")

    # Filter out empty strings and very short usernames
    return [u for u in usernames if len(u) >= 2]


async def run_sherlock(username: str) -> list[UsernameResult]:
    """Run Sherlock to discover social profiles for a username.

    Args:
        username: Username to search for.

    Returns:
        List of UsernameResult for confirmed profiles.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            SHERLOCK_PATH,
            username,
            "--output",
            "/dev/null",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=SHERLOCK_TIMEOUT
        )
        output = stdout.decode("utf-8", errors="replace")
        results = []

        for line in output.split("\n"):
            if "] [" in line and ": " in line:
                parts = line.split(": ", 1)
                if len(parts) == 2:
                    platform = parts[0].strip("[] ")
                    url = parts[1].strip()
                    if platform and url.startswith("http"):
                        results.append(
                            UsernameResult(
                                username=username,
                                platform=platform,
                                profile_url=url,
                                exists=True,
                            )
                        )

        logger.info("Sherlock found %d profiles for '%s'", len(results), username)
        return results

    except FileNotFoundError:
        logger.warning("Sherlock binary not found at %s", SHERLOCK_PATH)
        return []
    except asyncio.TimeoutError:
        logger.warning("Sherlock timed out for '%s' after %ds", username, SHERLOCK_TIMEOUT)
        return []
    except Exception as e:
        logger.warning("Sherlock error for '%s': %s", username, e)
        return []


async def search_usernames(email: str) -> list[UsernameResult]:
    """Generate usernames from email and run Sherlock on each.

    Limits the number of concurrent Sherlock processes.

    Args:
        email: Normalized email address.

    Returns:
        Flattened list of all discovered profiles.
    """
    usernames = generate_usernames(email)
    if not usernames:
        return []

    tasks = [run_sherlock(u) for u in usernames[:MAX_USERNAMES]]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    flat = []
    for result in results:
        if isinstance(result, Exception):
            logger.warning("Username search failed: %s", result)
        else:
            flat.extend(result)

    return flat
