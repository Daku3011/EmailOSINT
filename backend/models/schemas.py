"""Pydantic schemas for request/response validation.

All API data structures are defined here to maintain a single source of truth
for both request validation and response serialization.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class EmailRequest(BaseModel):
    """Incoming analysis request payload."""
    email: EmailStr = Field(
        ...,
        description="Email address to analyze",
        examples=["user@example.com"],
    )


class DomainInfo(BaseModel):
    """DNS and WHOIS information for the email domain."""
    domain: str
    mx_records: list[str] = Field(default_factory=list)
    dns_a_records: list[str] = Field(default_factory=list)
    whois: Optional[dict] = None


class Breach(BaseModel):
    """A single data breach record."""
    name: str
    domain: str = ""
    date: Optional[str] = None
    data_classes: list[str] = Field(default_factory=list)
    description: Optional[str] = None


class GravatarResult(BaseModel):
    """Gravatar profile lookup result."""
    exists: bool
    avatar_url: Optional[str] = None
    profile_url: Optional[str] = None


class UsernameResult(BaseModel):
    """Social media profile discovery result."""
    username: str
    platform: str
    profile_url: Optional[str] = None
    exists: bool = False


class SearchResult(BaseModel):
    """Web search result mentioning the email."""
    title: str = ""
    url: str
    snippet: Optional[str] = None


class Report(BaseModel):
    """Complete OSINT analysis report combining all intelligence sources."""
    id: str
    email: str
    is_valid: bool
    domain_info: Optional[DomainInfo] = None
    breaches: list[Breach] = Field(default_factory=list)
    gravatar: Optional[GravatarResult] = None
    usernames: list[UsernameResult] = Field(default_factory=list)
    search_results: list[SearchResult] = Field(default_factory=list)
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    created_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "is_valid": True,
                "risk_score": 45.0,
            }
        }


class ReportSummary(BaseModel):
    """Lightweight report listing item."""
    id: str
    email: str
    risk_score: float
    breach_count: int = 0
    created_at: Optional[datetime] = None
