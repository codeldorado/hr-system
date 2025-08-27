"""
Database management utilities for the payslip microservice
"""
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
import os
from typing import Optional

from .database import DATABASE_URL, engine
from .models import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database management operations"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or DATABASE_URL
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_database(self) -> bool:
        """Create database if it doesn't exist"""
        try:
            # Extract database name from URL
            db_name = self.database_url.split('/')[-1]
            base_url = self.database_url.rsplit('/', 1)[0]
            
            # Connect to postgres database to create our database
            postgres_url = f"{base_url}/postgres"
            temp_engine = create_engine(postgres_url)
            
            with temp_engine.connect() as conn:
                # Check if database exists
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": db_name}
                )
                
                if not result.fetchone():
                    # Create database
                    conn.execute(text("COMMIT"))  # End any existing transaction
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    logger.info(f"Database {db_name} created successfully")
                else:
                    logger.info(f"Database {db_name} already exists")
            
            temp_engine.dispose()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database: {e}")
            return False

    def create_tables(self) -> bool:
        """Create all tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tables: {e}")
            return False

    def drop_tables(self) -> bool:
        """Drop all tables (use with caution)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop tables: {e}")
            return False

    def check_connection(self) -> bool:
        """Check database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection failed: {e}")
            return False

    def get_table_info(self) -> dict:
        """Get information about database tables"""
        try:
            with self.engine.connect() as conn:
                # Get table names
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result]
                
                table_info = {}
                for table in tables:
                    # Get row count
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    row_count = count_result.scalar()
                    
                    # Get column info
                    columns_result = conn.execute(text(f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = '{table}'
                        ORDER BY ordinal_position
                    """))
                    columns = [
                        {
                            "name": row[0],
                            "type": row[1],
                            "nullable": row[2] == "YES"
                        }
                        for row in columns_result
                    ]
                    
                    table_info[table] = {
                        "row_count": row_count,
                        "columns": columns
                    }
                
                return table_info
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to get table info: {e}")
            return {}

    def cleanup_old_records(self, days: int = 365) -> int:
        """Clean up old payslip records (older than specified days)"""
        try:
            with self.SessionLocal() as db:
                from .models import Payslip
                from datetime import datetime, timedelta
                
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                # Find old records
                old_records = db.query(Payslip).filter(
                    Payslip.upload_timestamp < cutoff_date
                ).all()
                
                count = len(old_records)
                
                # Delete old records (in production, you might want to archive instead)
                for record in old_records:
                    db.delete(record)
                
                db.commit()
                logger.info(f"Cleaned up {count} old records")
                return count
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to cleanup old records: {e}")
            return 0

    def get_database_stats(self) -> dict:
        """Get database statistics"""
        try:
            with self.engine.connect() as conn:
                # Database size
                db_name = self.database_url.split('/')[-1]
                size_result = conn.execute(text(f"""
                    SELECT pg_size_pretty(pg_database_size('{db_name}')) as size
                """))
                db_size = size_result.scalar()
                
                # Connection count
                conn_result = conn.execute(text("""
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE datname = current_database()
                """))
                connection_count = conn_result.scalar()
                
                return {
                    "database_size": db_size,
                    "active_connections": connection_count,
                    "table_info": self.get_table_info()
                }
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

# Create singleton instance
db_manager = DatabaseManager()
