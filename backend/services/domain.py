"""Domain intelligence service.

Resolves MX records, A records, and WHOIS data for a given domain.
DNS queries are run concurrently for performance.
"""

import logging
import asyncio
from datetime import datetime

import dns.resolver
import whois

from models.schemas import DomainInfo

logger = logging.getLogger(__name__)


async def get_domain_info(domain: str) -> DomainInfo:
    """Gather DNS and WHOIS intelligence for a domain.

    Runs MX, A record lookups and WHOIS query concurrently.

    Args:
        domain: The domain name to analyze.

    Returns:
        DomainInfo with populated DNS and WHOIS data.
    """
    loop = asyncio.get_running_loop()

    async def resolve_mx() -> list[str]:
        try:
            answers = await loop.run_in_executor(
                None, lambda: dns.resolver.resolve(domain, "MX")
            )
            return [str(r.exchange) for r in answers]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers) as e:
            logger.debug("MX lookup for %s: %s", domain, e)
            return []
        except Exception as e:
            logger.warning("MX lookup error for %s: %s", domain, e)
            return []

    async def resolve_a() -> list[str]:
        try:
            answers = await loop.run_in_executor(
                None, lambda: dns.resolver.resolve(domain, "A")
            )
            return [str(r) for r in answers]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers) as e:
            logger.debug("A record lookup for %s: %s", domain, e)
            return []
        except Exception as e:
            logger.warning("A record lookup error for %s: %s", domain, e)
            return []

    async def get_whois() -> dict | None:
        try:
            w = await loop.run_in_executor(None, whois.whois, domain)
            # Serialize datetime objects for JSON compatibility
            result = {}
            for key, value in dict(w).items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, list):
                    result[key] = [
                        v.isoformat() if isinstance(v, datetime) else v
                        for v in value
                    ]
                else:
                    result[key] = value
            return result
        except Exception as e:
            logger.warning("WHOIS lookup error for %s: %s", domain, e)
            return None

    mx_records, dns_a_records, whois_data = await asyncio.gather(
        resolve_mx(), resolve_a(), get_whois()
    )

    return DomainInfo(
        domain=domain,
        mx_records=mx_records,
        dns_a_records=dns_a_records,
        whois=whois_data,
    )
