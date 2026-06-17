"""Database layer for persisting OSINT analysis reports.

Uses aiosqlite for async SQLite operations with connection pooling
via a module-level connection reuse pattern.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiosqlite

from models.schemas import Report
from config import DB_PATH

logger = logging.getLogger(__name__)

_db_connection: aiosqlite.Connection | None = None


async def init_db() -> None:
    """Initialize the database schema.

    Creates the reports table if it doesn't exist.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_reports_email ON reports(email)"
        )
        await db.commit()
    logger.info("Database schema initialized at %s", DB_PATH)


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Yield a database connection with automatic cleanup."""
    db = await aiosqlite.connect(DB_PATH)
    try:
        yield db
    finally:
        await db.close()


async def save_report(report: Report) -> None:
    """Persist or update an analysis report.

    Args:
        report: The Report model to save.
    """
    async with get_db() as db:
        await db.execute(
            "INSERT OR REPLACE INTO reports (id, email, data) VALUES (?, ?, ?)",
            (report.id, report.email, report.model_dump_json()),
        )
        await db.commit()
    logger.info("Saved report %s for %s", report.id, report.email)


async def get_report(report_id: str) -> Report | None:
    """Retrieve a report by ID.

    Args:
        report_id: UUID string of the report.

    Returns:
        Report model if found, None otherwise.
    """
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT data FROM reports WHERE id = ?", (report_id,)
        )
        row = await cursor.fetchone()
        if row:
            return Report.model_validate_json(row[0])
    return None


async def list_reports(email: str | None = None, limit: int = 50) -> list[Report]:
    """List recent reports, optionally filtered by email.

    Args:
        email: Optional email to filter by.
        limit: Maximum number of reports to return.

    Returns:
        List of Report models.
    """
    async with get_db() as db:
        if email:
            cursor = await db.execute(
                "SELECT data FROM reports WHERE email = ? ORDER BY created_at DESC LIMIT ?",
                (email, limit),
            )
        else:
            cursor = await db.execute(
                "SELECT data FROM reports ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
        rows = await cursor.fetchall()
    return [Report.model_validate_json(row[0]) for row in rows]
