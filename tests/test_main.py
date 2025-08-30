import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Clean up
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Payslip Microservice is running"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "payslip-microservice"


def test_get_payslips_empty(client):
    """Test getting payslips when none exist"""
    response = client.get("/payslips")
    assert response.status_code == 200
    assert response.json() == []


def test_upload_payslip_invalid_file_type(client):
    """Test uploading non-PDF file"""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
        tmp_file.write(b"test content")
        tmp_file.flush()

        with open(tmp_file.name, "rb") as f:
            response = client.post(
                "/payslips",
                data={"employee_id": 123, "month": 1, "year": 2024},
                files={"file": ("test.txt", f, "text/plain")},
            )

        os.unlink(tmp_file.name)

    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]


def test_upload_payslip_invalid_month(client):
    """Test uploading with invalid month"""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(b"fake pdf content")
        tmp_file.flush()

        with open(tmp_file.name, "rb") as f:
            response = client.post(
                "/payslips",
                data={"employee_id": 123, "month": 13, "year": 2024},  # Invalid month
                files={"file": ("test.pdf", f, "application/pdf")},
            )

        os.unlink(tmp_file.name)

    assert response.status_code == 400
    assert "Month must be between 1 and 12" in response.json()["detail"]


def test_get_nonexistent_payslip(client):
    """Test getting a payslip that doesn't exist"""
    response = client.get("/payslips/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payslip not found"


def test_payslip_filtering(client):
    """Test payslip filtering parameters"""
    response = client.get("/payslips?employee_id=123&year=2024&month=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_payslip_pagination(client):
    """Test payslip pagination"""
    response = client.get("/payslips?skip=0&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
