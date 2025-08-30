import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./payslip_demo.db"  # Use SQLite for demo
)

# Create engine with enhanced connection pooling
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite specific
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,  # Recycle connections every hour
        pool_timeout=30,  # Timeout for getting connection from pool
        echo=os.getenv("SQL_ECHO", "false").lower()
        == "true",  # Log SQL queries in debug mode
    )


# Add connection event listeners for better error handling
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set connection parameters"""
    if "postgresql" in DATABASE_URL:
        with dbapi_connection.cursor() as cursor:
            # Set timezone to UTC
            cursor.execute("SET timezone TO 'UTC'")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout"""
    logger.debug("Connection checked out from pool")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin"""
    logger.debug("Connection checked in to pool")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency to get database session with proper error handling
    """
    db = SessionLocal()
    try:
        yield db
    except DisconnectionError:
        logger.error("Database disconnection error")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session():
    """
    Get database session for direct use (not as dependency)
    """
    return SessionLocal()
