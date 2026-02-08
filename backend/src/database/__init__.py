"""
Database setup and session management for the chat API.
Provides database connection and session management for all models.
"""
from sqlmodel import create_engine, Session
from typing import Generator
from contextlib import contextmanager
from ..config import settings
import urllib.parse
from ..models.task import Task


# Safely encode the database URL to handle special characters
database_url_encoded = settings.database_url
if '%' in settings.database_url:
    database_url_encoded = urllib.parse.unquote(settings.database_url)


# Create the database engine
engine = create_engine(
    database_url_encoded,
    echo=settings.db_echo,  # Set to True to see SQL queries in logs
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=300,       # Recycle connections every 5 minutes
)


def create_db_and_tables():
    """
    Create database tables if they don't exist.
    This should be called on application startup.
    """
    from sqlmodel import SQLModel
    from sqlalchemy import inspect, text

    try:
        # Check if tables exist and create them
        SQLModel.metadata.create_all(engine)

        # For PostgreSQL, we may need to handle schema updates manually
        # Check if tasks table has the status column, and if not, add it
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if 'tasks' in tables:
            columns = [col['name'] for col in inspector.get_columns('tasks')]

            # If status column doesn't exist, we need to add it (this is a workaround)
            if 'status' not in columns:
                print("Adding missing 'status' column to tasks table...")
                with engine.connect() as conn:
                    # Add the status column with a default value - using proper PostgreSQL syntax
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN status VARCHAR(20) DEFAULT 'pending'"))
                    conn.commit()
                    print("Successfully added 'status' column to tasks table")
            else:
                print("'status' column already exists in tasks table")
        else:
            print("Tasks table does not exist, it will be created by SQLModel.metadata.create_all()")

    except Exception as e:
        print(f"Error during database initialization: {e}")
        # Still attempt to create the tables even if inspection fails
        SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session for use with FastAPI dependency injection.

    Yields:
        Session: Database session for queries
    """
    with Session(engine) as session:
        yield session


@contextmanager
def get_db_session():
    """
    Context manager for getting a database session.
    Use this when you need to manage the session lifecycle yourself.

    Yields:
        Session: Database session for queries
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Global session maker
def get_session_maker():
    """
    Get a session maker for creating new sessions.
    """
    return Session(engine)