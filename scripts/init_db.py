#!/usr/bin/env python3
"""
Database initialization script for the payslip microservice
"""
import sys
import os
import logging

# Add the parent directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database_manager import db_manager
from app.models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Initialize the database"""
    logger.info("Starting database initialization...")
    
    # Check connection
    if not db_manager.check_connection():
        logger.error("Cannot connect to database. Please check your DATABASE_URL.")
        return False
    
    # Create tables
    if not db_manager.create_tables():
        logger.error("Failed to create database tables.")
        return False
    
    # Get database info
    stats = db_manager.get_database_stats()
    if stats:
        logger.info(f"Database size: {stats.get('database_size', 'Unknown')}")
        logger.info(f"Active connections: {stats.get('active_connections', 'Unknown')}")
        
        table_info = stats.get('table_info', {})
        for table_name, info in table_info.items():
            logger.info(f"Table '{table_name}': {info['row_count']} rows, {len(info['columns'])} columns")
    
    logger.info("Database initialization completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
