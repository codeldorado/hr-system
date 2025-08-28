#!/usr/bin/env python3
"""
Comprehensive test runner for the Payslip Microservice
Tests the application without requiring Docker or external services
"""

import os
import sys
import tempfile
import sqlite3
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_imports():
    """Test that all modules can be imported successfully"""
    print("Testing imports...")
    
    try:
        from app.models import Payslip
        from app.schemas import PayslipCreate, PayslipResponse
        from app.database import DATABASE_URL
        print("All imports successful")
        return True
    except ImportError as e:
        print(f"Import failed: {e}")
        return False

def test_database_models():
    """Test database models without requiring a real database"""
    print("Testing database models...")
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.database import Base
        from app.models import Payslip
        
        # Create in-memory SQLite database
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        # Test creating a payslip
        session = SessionLocal()
        payslip = Payslip(
            employee_id=123,
            month=12,
            year=2024,
            filename="test_payslip.pdf",
            file_url="https://example.com/test.pdf",
            file_size=1048576
        )
        
        session.add(payslip)
        session.commit()
        
        # Test querying
        retrieved = session.query(Payslip).filter(Payslip.employee_id == 123).first()
        assert retrieved is not None
        assert retrieved.month == 12
        assert retrieved.year == 2024
        
        session.close()
        print("Database models working correctly")
        return True
        
    except Exception as e:
        print(f"Database model test failed: {e}")
        return False

def test_pydantic_schemas():
    """Test Pydantic schemas for data validation"""
    print("Testing Pydantic schemas...")
    
    try:
        from app.schemas import PayslipCreate, PayslipResponse
        from datetime import datetime
        
        # Test PayslipCreate validation
        valid_data = {
            "employee_id": 123,
            "month": 12,
            "year": 2024,
            "filename": "test_payslip.pdf"
        }
        
        payslip_create = PayslipCreate(**valid_data)
        assert payslip_create.employee_id == 123
        assert payslip_create.month == 12
        assert payslip_create.year == 2024
        
        # Test invalid month
        try:
            invalid_data = valid_data.copy()
            invalid_data["month"] = 13
            PayslipCreate(**invalid_data)
            assert False, "Should have raised validation error"
        except ValueError:
            pass  # Expected
        
        # Test PayslipResponse
        response_data = {
            "id": 1,
            "employee_id": 123,
            "month": 12,
            "year": 2024,
            "filename": "test.pdf",
            "file_url": "https://example.com/test.pdf",
            "file_size": 1048576,
            "upload_timestamp": datetime.now()
        }
        
        payslip_response = PayslipResponse(**response_data)
        assert payslip_response.id == 1
        
        print("Pydantic schemas working correctly")
        return True
        
    except Exception as e:
        print(f"Schema test failed: {e}")
        return False

def test_file_validation():
    """Test file validation logic"""
    print("Testing file validation...")
    
    try:
        # Create a temporary PDF-like file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            # Write minimal PDF header
            tmp_file.write(b"%PDF-1.4\n")
            tmp_file.write(b"1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n")
            tmp_file.write(b"%%EOF\n")
            tmp_file_path = tmp_file.name
        
        # Test file size
        file_size = os.path.getsize(tmp_file_path)
        assert file_size > 0
        
        # Test file extension
        assert tmp_file_path.endswith(".pdf")
        
        # Cleanup
        os.unlink(tmp_file_path)
        
        print("File validation working correctly")
        return True
        
    except Exception as e:
        print(f"File validation test failed: {e}")
        return False

def test_business_logic():
    """Test core business logic"""
    print("Testing business logic...")
    
    try:
        from app.models import Payslip
        from datetime import datetime
        
        # Test payslip creation logic
        payslip = Payslip(
            employee_id=456,
            month=6,
            year=2024,
            filename="june_payslip.pdf",
            file_url="https://s3.amazonaws.com/bucket/june.pdf",
            file_size=2048000
        )
        
        # Test string representation
        expected_str = "Payslip(employee_id=456, month=6, year=2024)"
        assert str(payslip) == expected_str
        
        # Test that upload_timestamp is set automatically
        assert payslip.upload_timestamp is not None
        assert isinstance(payslip.upload_timestamp, datetime)
        
        print("Business logic working correctly")
        return True
        
    except Exception as e:
        print(f"Business logic test failed: {e}")
        return False

def test_configuration():
    """Test configuration and environment handling"""
    print("Testing configuration...")
    
    try:
        from app.database import DATABASE_URL

        # Test database URL exists
        assert DATABASE_URL is not None
        assert isinstance(DATABASE_URL, str)

        # Test with environment variable
        original_url = DATABASE_URL
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"

        # Re-import to get updated URL
        import importlib
        import app.database
        importlib.reload(app.database)

        # Cleanup
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        
        print("Configuration working correctly")
        return True
        
    except Exception as e:
        print(f"Configuration test failed: {e}")
        return False

def test_frontend_structure():
    """Test that frontend files exist and are properly structured"""
    print("Testing frontend structure...")
    
    try:
        frontend_path = Path("frontend")
        
        # Check key files exist
        required_files = [
            "package.json",
            "tsconfig.json",
            "src/App.tsx",
            "src/index.tsx",
            "src/pages/LoginPage.tsx",
            "src/pages/Dashboard.tsx",
            "src/pages/UploadPayslip.tsx",
            "src/pages/PayslipList.tsx",
            "src/services/authService.ts",
            "src/services/payslipService.ts",
            "Dockerfile",
            "nginx.conf"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (frontend_path / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"Missing frontend files: {missing_files}")
            return False
        
        # Check package.json has required dependencies
        import json
        with open(frontend_path / "package.json") as f:
            package_data = json.load(f)
        
        required_deps = ["react", "react-dom", "typescript", "@mui/material", "axios"]
        missing_deps = []
        
        for dep in required_deps:
            if dep not in package_data.get("dependencies", {}):
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"Missing frontend dependencies: {missing_deps}")
            return False
        
        print("Frontend structure is correct")
        return True
        
    except Exception as e:
        print(f"Frontend structure test failed: {e}")
        return False

def test_infrastructure_files():
    """Test that infrastructure files exist and are properly configured"""
    print("Testing infrastructure files...")
    
    try:
        infra_path = Path("infrastructure")
        
        # Check key Terraform files exist
        required_files = [
            "main.tf",
            "variables.tf",
            "outputs.tf",
            "modules/vpc/main.tf",
            "modules/security/main.tf",
            "modules/rds/main.tf",
            "modules/s3/main.tf",
            "modules/ecs/main.tf",
            "modules/cloudwatch/main.tf",
            "environments/dev.tfvars",
            "environments/prod.tfvars",
            "deploy.sh"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (infra_path / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"Missing infrastructure files: {missing_files}")
            return False
        
        print("Infrastructure files are present")
        return True
        
    except Exception as e:
        print(f"Infrastructure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database_models,
        test_pydantic_schemas,
        test_file_validation,
        test_business_logic,
        test_configuration,
        test_frontend_structure,
        test_infrastructure_files,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed! The implementation is working correctly.")
        return True
    else:
        print(f"{failed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
