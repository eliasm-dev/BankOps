"""
Development entry point.

Usage:
    python run.py
    uvicorn app.main:app --reload --port 8000
"""
import uvicorn

from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
