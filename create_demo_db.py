#!/usr/bin/env python3
"""
Create demo database and tables for the payslip microservice
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.database import engine, Base
from app.models import Payslip

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def add_sample_data():
    """Add some sample data for demonstration"""
    from app.database import SessionLocal
    from datetime import datetime
    
    print("Adding sample data...")
    
    session = SessionLocal()
    
    # Sample payslips
    sample_payslips = [
        {
            "employee_id": 123,
            "month": 11,
            "year": 2024,
            "filename": "november_2024_payslip.pdf",
            "file_url": "http://localhost:8000/files/payslips/123/2024/11/demo-sample.pdf",
            "file_size": 1048576
        },
        {
            "employee_id": 123,
            "month": 10,
            "year": 2024,
            "filename": "october_2024_payslip.pdf",
            "file_url": "http://localhost:8000/files/payslips/123/2024/10/demo-sample.pdf",
            "file_size": 987654
        },
        {
            "employee_id": 456,
            "month": 11,
            "year": 2024,
            "filename": "november_2024_hr_payslip.pdf",
            "file_url": "http://localhost:8000/files/payslips/456/2024/11/demo-sample.pdf",
            "file_size": 1234567
        }
    ]
    
    for payslip_data in sample_payslips:
        # Check if payslip already exists
        existing = session.query(Payslip).filter(
            Payslip.employee_id == payslip_data["employee_id"],
            Payslip.month == payslip_data["month"],
            Payslip.year == payslip_data["year"]
        ).first()
        
        if not existing:
            payslip = Payslip(**payslip_data)
            session.add(payslip)
    
    session.commit()
    session.close()
    
    print("✅ Sample data added successfully!")

if __name__ == "__main__":
    create_tables()
    add_sample_data()
    print("\n🎉 Demo database setup complete!")
    print("You can now start the backend server with:")
    print("python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
