"""
Database engine, session factory, and declarative base.

SQLAlchemy 2.0 style with connection pooling tuned for a
small-to-medium operational dashboard.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

from app.config import settings

# Build engine with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,       # verify connections before use
    pool_recycle=3600,        # recycle connections after 1 hour
    echo=settings.debug,      # log SQL in development
)

# Session factory — each request gets its own session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Declarative base class for all models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session.

    Usage in a route:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
