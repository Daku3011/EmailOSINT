"""Email validation service.

Uses the email-validator library for RFC-compliant validation
without deliverability checks (no SMTP probing).
"""

import logging

from email_validator import validate_email as validate, EmailNotValidError

logger = logging.getLogger(__name__)


def validate_email(email: str) -> tuple[bool, str]:
    """Validate and normalize an email address.

    Args:
        email: Raw email string to validate.

    Returns:
        Tuple of (is_valid, normalized_email_or_error_message).
    """
    if not email or not isinstance(email, str):
        return False, "Email must be a non-empty string"

    email = email.strip().lower()

    if len(email) > 254:
        return False, "Email address exceeds maximum length"

    try:
        result = validate(email, check_deliverability=False)
        return True, result.normalized
    except EmailNotValidError as e:
        logger.debug("Email validation failed for %s: %s", email[:50], e)
        return False, str(e)
