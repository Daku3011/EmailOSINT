"""Email OSINT Tool - FastAPI Application Entry Point.

Provides API endpoints for email intelligence analysis including
domain info, breach detection, social profile discovery, and risk scoring.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers.analysis import router as analysis_router
from database import init_db
from config import ALLOWED_ORIGINS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully.")
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title="Email OSINT Tool",
    version="1.1.0",
    description="Open-source intelligence tool for email analysis",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return safe error responses."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again later."},
    )


app.include_router(analysis_router, prefix="/api", tags=["analysis"])


@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint for monitoring and container orchestration."""
    return {"status": "healthy", "version": "1.1.0"}
