"""
Database session management for CQIA.
Provides SQLAlchemy session handling with proper error handling and transaction management.
"""

import structlog
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..core.database import SessionLocal, engine
from ..core.exceptions import DatabaseError

logger = structlog.get_logger(__name__)


def get_db_session() -> Generator[Session, None, None]:
    """
    Get database session for dependency injection.
    Use this in FastAPI route dependencies.

    Yields:
        Session: Database session

    Raises:
        DatabaseError: If session creation fails
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error("Database session error", error=str(e))
        raise DatabaseError(f"Database session error: {str(e)}")
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Automatically handles commit/rollback and session cleanup.

    Usage:
        with get_db_context() as db:
            # perform database operations
            db.add(some_object)
            # commit happens automatically on successful exit

    Yields:
        Session: Database session

    Raises:
        DatabaseError: If database operations fail
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
        logger.debug("Database transaction committed successfully")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Database transaction rolled back", error=str(e))
        raise DatabaseError(f"Database operation failed: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error("Unexpected database error", error=str(e))
        raise DatabaseError(f"Unexpected database error: {str(e)}")
    finally:
        db.close()
        logger.debug("Database session closed")


def get_db_session_sync() -> Session:
    """
    Get a synchronous database session.
    Use this for background tasks and utilities that need sync access.

    Returns:
        Session: Database session

    Raises:
        DatabaseError: If session creation fails
    """
    try:
        db = SessionLocal()
        return db
    except SQLAlchemyError as e:
        logger.error("Failed to create database session", error=str(e))
        raise DatabaseError(f"Failed to create database session: {str(e)}")


def execute_in_transaction(func):
    """
    Decorator to execute function within a database transaction.

    Args:
        func: Function to execute within transaction

    Returns:
        Decorated function

    Raises:
        DatabaseError: If transaction fails
    """
    def wrapper(*args, **kwargs):
        with get_db_context() as db:
            return func(db, *args, **kwargs)
    return wrapper


def check_database_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
        logger.info("Database connection is healthy")
        return True
    except Exception as e:
        logger.error("Database connection check failed", error=str(e))
        return False


def get_database_stats() -> dict:
    """
    Get database statistics and health information.

    Returns:
        dict: Database statistics including connection info
    """
    try:
        with get_db_context() as db:
            # Get connection info
            connection = db.connection()
            stats = {
                "connection_status": "healthy",
                "engine_url": str(engine.url).replace(engine.url.password or '', '***') if engine.url.password else str(engine.url),
                "pool_size": engine.pool.size(),
                "checked_connections": engine.pool.checked_in(),
                "overflow_connections": engine.pool.checked_out(),
                "invalid_connections": engine.pool.invalid(),
            }

            logger.debug("Database statistics retrieved", stats=stats)
            return stats

    except Exception as e:
        logger.error("Failed to get database statistics", error=str(e))
        return {
            "connection_status": "unhealthy",
            "error": str(e)
        }
