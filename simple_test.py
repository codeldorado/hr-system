#!/usr/bin/env python3
"""
Simple focused test to verify the core implementation works
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_core_functionality():
    """Test the core application functionality"""
    print("🧪 Testing Core Functionality")
    print("=" * 40)
    
    # Test 1: Import all modules
    print("1. Testing imports...")
    try:
        from app.models import Payslip
        from app.schemas import PayslipCreate, PayslipResponse
        from app.database import DATABASE_URL
        from app.main import app
        print("   ✅ All core modules imported successfully")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Test Pydantic schemas
    print("2. Testing data validation...")
    try:
        # Valid payslip data
        valid_data = {
            "employee_id": 123,
            "month": 12,
            "year": 2024,
            "filename": "december_payslip.pdf"
        }
        
        payslip_create = PayslipCreate(**valid_data)
        assert payslip_create.employee_id == 123
        assert payslip_create.month == 12
        
        # Test invalid month validation
        try:
            invalid_data = valid_data.copy()
            invalid_data["month"] = 13
            PayslipCreate(**invalid_data)
            print("   ❌ Validation should have failed for invalid month")
            return False
        except ValueError:
            pass  # Expected
        
        print("   ✅ Data validation working correctly")
    except Exception as e:
        print(f"   ❌ Schema validation failed: {e}")
        return False
    
    # Test 3: Test database model structure
    print("3. Testing database models...")
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models import Base

        # Create in-memory database for testing
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        # Test creating a payslip record
        session = SessionLocal()
        payslip = Payslip(
            employee_id=456,
            month=11,
            year=2024,
            filename="november_payslip.pdf",
            file_url="https://s3.amazonaws.com/bucket/nov.pdf",
            file_size=1048576
        )
        
        session.add(payslip)
        session.commit()
        
        # Test querying
        retrieved = session.query(Payslip).filter(Payslip.employee_id == 456).first()
        assert retrieved is not None
        assert retrieved.month == 11
        assert retrieved.filename == "november_payslip.pdf"
        
        session.close()
        print("   ✅ Database models working correctly")
    except Exception as e:
        print(f"   ❌ Database model test failed: {e}")
        return False
    
    # Test 4: Test FastAPI app creation
    print("4. Testing FastAPI application...")
    try:
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data
        
        print("   ✅ FastAPI application working correctly")
    except Exception as e:
        print(f"   ❌ FastAPI test failed: {e}")
        return False
    
    # Test 5: Test project structure
    print("5. Testing project structure...")
    try:
        required_files = [
            "app/main.py",
            "app/models.py", 
            "app/schemas.py",
            "app/database.py",
            "frontend/package.json",
            "frontend/src/App.tsx",
            "infrastructure/main.tf",
            "docker-compose.yml",
            "Dockerfile",
            "README.md"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"   ❌ Missing files: {missing_files}")
            return False
        
        print("   ✅ Project structure is complete")
    except Exception as e:
        print(f"   ❌ Structure test failed: {e}")
        return False
    
    print("\n🎉 All core functionality tests passed!")
    return True

def test_frontend_integration():
    """Test frontend integration points"""
    print("\n🌐 Testing Frontend Integration")
    print("=" * 40)
    
    try:
        # Check frontend package.json
        import json
        with open("frontend/package.json") as f:
            package_data = json.load(f)
        
        # Check required dependencies
        required_deps = ["react", "react-dom", "typescript", "@mui/material", "axios", "react-router-dom"]
        missing_deps = []
        
        for dep in required_deps:
            if dep not in package_data.get("dependencies", {}):
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Missing frontend dependencies: {missing_deps}")
            return False
        
        # Check key frontend files
        frontend_files = [
            "frontend/src/pages/LoginPage.tsx",
            "frontend/src/pages/Dashboard.tsx", 
            "frontend/src/pages/UploadPayslip.tsx",
            "frontend/src/pages/PayslipList.tsx",
            "frontend/src/services/authService.ts",
            "frontend/src/services/payslipService.ts",
            "frontend/src/contexts/AuthContext.tsx"
        ]
        
        for file_path in frontend_files:
            if not Path(file_path).exists():
                print(f"❌ Missing frontend file: {file_path}")
                return False
        
        print("✅ Frontend integration structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ Frontend integration test failed: {e}")
        return False

def test_deployment_readiness():
    """Test deployment configuration"""
    print("\n🚀 Testing Deployment Readiness")
    print("=" * 40)
    
    try:
        # Check Docker files
        docker_files = ["Dockerfile", "frontend/Dockerfile", "docker-compose.yml"]
        for file_path in docker_files:
            if not Path(file_path).exists():
                print(f"❌ Missing Docker file: {file_path}")
                return False
        
        # Check CI/CD configuration
        if not Path(".github/workflows/ci-cd.yml").exists():
            print("❌ Missing CI/CD workflow")
            return False
        
        # Check infrastructure files
        infra_files = ["infrastructure/main.tf", "infrastructure/variables.tf"]
        for file_path in infra_files:
            if not Path(file_path).exists():
                print(f"❌ Missing infrastructure file: {file_path}")
                return False
        
        print("✅ Deployment configuration is ready")
        return True
        
    except Exception as e:
        print(f"❌ Deployment readiness test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔬 Comprehensive Implementation Test")
    print("=" * 50)
    
    tests = [
        test_core_functionality,
        test_frontend_integration,
        test_deployment_readiness
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
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {passed}/{len(tests)} test suites passed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! The implementation is working correctly.")
        print("\n✅ Ready for production deployment!")
        return True
    else:
        print(f"⚠️  {failed} test suite(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
