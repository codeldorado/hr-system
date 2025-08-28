import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.database import Base
from app.models import Payslip

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_models.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_payslip_data():
    return {
        "employee_id": 123,
        "month": 12,
        "year": 2024,
        "filename": "payslip_dec_2024.pdf",
        "file_url": "https://s3.amazonaws.com/bucket/payslips/123/2024/12/uuid.pdf",
        "file_size": 1048576
    }

class TestPayslipModel:
    def test_create_payslip(self, db_session, sample_payslip_data):
        """Test creating a new payslip record"""
        payslip = Payslip(**sample_payslip_data)
        db_session.add(payslip)
        db_session.commit()
        
        assert payslip.id is not None
        assert payslip.employee_id == 123
        assert payslip.month == 12
        assert payslip.year == 2024
        assert payslip.filename == "payslip_dec_2024.pdf"
        assert payslip.upload_timestamp is not None
        assert isinstance(payslip.upload_timestamp, datetime)

    def test_payslip_string_representation(self, db_session, sample_payslip_data):
        """Test payslip string representation"""
        payslip = Payslip(**sample_payslip_data)
        db_session.add(payslip)
        db_session.commit()
        
        expected = f"Payslip(employee_id=123, month=12, year=2024)"
        assert str(payslip) == expected

    def test_unique_constraint_violation(self, db_session, sample_payslip_data):
        """Test unique constraint on employee_id, month, year"""
        # Create first payslip
        payslip1 = Payslip(**sample_payslip_data)
        db_session.add(payslip1)
        db_session.commit()
        
        # Try to create duplicate
        payslip2 = Payslip(**sample_payslip_data)
        payslip2.filename = "different_filename.pdf"  # Different filename
        payslip2.file_url = "different_url.pdf"  # Different URL
        
        db_session.add(payslip2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()

    def test_file_url_unique_constraint(self, db_session, sample_payslip_data):
        """Test unique constraint on file_url"""
        # Create first payslip
        payslip1 = Payslip(**sample_payslip_data)
        db_session.add(payslip1)
        db_session.commit()
        
        # Try to create payslip with same file_url but different employee
        duplicate_data = sample_payslip_data.copy()
        duplicate_data["employee_id"] = 456
        duplicate_data["month"] = 11
        
        payslip2 = Payslip(**duplicate_data)
        db_session.add(payslip2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()

    def test_required_fields(self, db_session):
        """Test that required fields cannot be null"""
        # Test missing employee_id
        with pytest.raises(IntegrityError):
            payslip = Payslip(
                month=12,
                year=2024,
                filename="test.pdf",
                file_url="test_url.pdf",
                file_size=1000
            )
            db_session.add(payslip)
            db_session.commit()
        
        db_session.rollback()
        
        # Test missing month
        with pytest.raises(IntegrityError):
            payslip = Payslip(
                employee_id=123,
                year=2024,
                filename="test.pdf",
                file_url="test_url2.pdf",
                file_size=1000
            )
            db_session.add(payslip)
            db_session.commit()
        
        db_session.rollback()

    def test_field_constraints(self, db_session):
        """Test field length and type constraints"""
        # Test filename length constraint
        long_filename = "x" * 300  # Exceeds 255 character limit
        
        with pytest.raises(Exception):  # Could be IntegrityError or DataError
            payslip = Payslip(
                employee_id=123,
                month=12,
                year=2024,
                filename=long_filename,
                file_url="test_url3.pdf",
                file_size=1000
            )
            db_session.add(payslip)
            db_session.commit()
        
        db_session.rollback()

    def test_query_operations(self, db_session):
        """Test basic query operations"""
        # Create test data
        payslips_data = [
            {
                "employee_id": 100,
                "month": 1,
                "year": 2024,
                "filename": "jan_2024.pdf",
                "file_url": "jan_url.pdf",
                "file_size": 1000
            },
            {
                "employee_id": 100,
                "month": 2,
                "year": 2024,
                "filename": "feb_2024.pdf",
                "file_url": "feb_url.pdf",
                "file_size": 2000
            },
            {
                "employee_id": 200,
                "month": 1,
                "year": 2024,
                "filename": "jan_2024_emp200.pdf",
                "file_url": "jan_emp200_url.pdf",
                "file_size": 1500
            }
        ]
        
        for data in payslips_data:
            payslip = Payslip(**data)
            db_session.add(payslip)
        
        db_session.commit()
        
        # Test filtering by employee_id
        employee_100_payslips = db_session.query(Payslip).filter(
            Payslip.employee_id == 100
        ).all()
        assert len(employee_100_payslips) == 2
        
        # Test filtering by year
        year_2024_payslips = db_session.query(Payslip).filter(
            Payslip.year == 2024
        ).all()
        assert len(year_2024_payslips) == 3
        
        # Test filtering by month
        jan_payslips = db_session.query(Payslip).filter(
            Payslip.month == 1
        ).all()
        assert len(jan_payslips) == 2
        
        # Test combined filters
        specific_payslip = db_session.query(Payslip).filter(
            Payslip.employee_id == 100,
            Payslip.month == 2,
            Payslip.year == 2024
        ).first()
        assert specific_payslip is not None
        assert specific_payslip.filename == "feb_2024.pdf"

    def test_ordering(self, db_session):
        """Test ordering of payslip records"""
        # Create test data with different timestamps
        import time
        
        payslips_data = [
            {
                "employee_id": 300,
                "month": 1,
                "year": 2024,
                "filename": "first.pdf",
                "file_url": "first_url.pdf",
                "file_size": 1000
            },
            {
                "employee_id": 300,
                "month": 2,
                "year": 2024,
                "filename": "second.pdf",
                "file_url": "second_url.pdf",
                "file_size": 1000
            }
        ]
        
        for i, data in enumerate(payslips_data):
            payslip = Payslip(**data)
            db_session.add(payslip)
            db_session.commit()
            if i == 0:
                time.sleep(0.1)  # Ensure different timestamps
        
        # Test ordering by upload_timestamp descending
        payslips = db_session.query(Payslip).filter(
            Payslip.employee_id == 300
        ).order_by(Payslip.upload_timestamp.desc()).all()
        
        assert len(payslips) == 2
        assert payslips[0].filename == "second.pdf"  # Most recent first
        assert payslips[1].filename == "first.pdf"

    def test_update_operations(self, db_session, sample_payslip_data):
        """Test updating payslip records"""
        # Create a payslip
        payslip = Payslip(**sample_payslip_data)
        db_session.add(payslip)
        db_session.commit()
        
        original_id = payslip.id
        original_timestamp = payslip.upload_timestamp
        
        # Update filename
        payslip.filename = "updated_filename.pdf"
        db_session.commit()
        
        # Verify update
        updated_payslip = db_session.query(Payslip).filter(
            Payslip.id == original_id
        ).first()
        
        assert updated_payslip.filename == "updated_filename.pdf"
        assert updated_payslip.upload_timestamp == original_timestamp  # Should not change

    def test_delete_operations(self, db_session, sample_payslip_data):
        """Test deleting payslip records"""
        # Create a payslip
        payslip = Payslip(**sample_payslip_data)
        payslip.employee_id = 999  # Use unique employee_id
        db_session.add(payslip)
        db_session.commit()
        
        payslip_id = payslip.id
        
        # Delete the payslip
        db_session.delete(payslip)
        db_session.commit()
        
        # Verify deletion
        deleted_payslip = db_session.query(Payslip).filter(
            Payslip.id == payslip_id
        ).first()
        
        assert deleted_payslip is None
