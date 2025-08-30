import io

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Payslip

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Clean up database after each test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing"""
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
    return io.BytesIO(pdf_content)


class TestHealthEndpoint:
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "payslip-microservice"


class TestPayslipUpload:
    def test_upload_payslip_success(self, client, sample_pdf):
        """Test successful payslip upload"""
        files = {"file": ("test_payslip.pdf", sample_pdf, "application/pdf")}
        data = {"employee_id": 123, "month": 12, "year": 2024}

        response = client.post("/payslips", files=files, data=data)
        assert response.status_code == 200

        result = response.json()
        assert result["employee_id"] == 123
        assert result["month"] == 12
        assert result["year"] == 2024
        assert result["filename"] == "test_payslip.pdf"
        assert "file_url" in result
        assert "upload_timestamp" in result

    def test_upload_payslip_invalid_file_type(self, client):
        """Test upload with invalid file type"""
        files = {"file": ("test.txt", io.BytesIO(b"not a pdf"), "text/plain")}
        data = {"employee_id": 123, "month": 12, "year": 2024}

        response = client.post("/payslips", files=files, data=data)
        assert response.status_code == 415
        assert "Only PDF files are allowed" in response.json()["detail"]

    def test_upload_payslip_missing_fields(self, client, sample_pdf):
        """Test upload with missing required fields"""
        files = {"file": ("test_payslip.pdf", sample_pdf, "application/pdf")}
        data = {"employee_id": 123}  # Missing month and year

        response = client.post("/payslips", files=files, data=data)
        assert response.status_code == 422

    def test_upload_payslip_invalid_month(self, client, sample_pdf):
        """Test upload with invalid month"""
        files = {"file": ("test_payslip.pdf", sample_pdf, "application/pdf")}
        data = {"employee_id": 123, "month": 13, "year": 2024}  # Invalid month

        response = client.post("/payslips", files=files, data=data)
        assert response.status_code == 422

    def test_upload_payslip_duplicate(self, client, sample_pdf):
        """Test duplicate payslip upload"""
        files = {"file": ("test_payslip.pdf", sample_pdf, "application/pdf")}
        data = {"employee_id": 456, "month": 11, "year": 2024}

        # First upload should succeed
        response1 = client.post("/payslips", files=files, data=data)
        assert response1.status_code == 200

        # Second upload should fail
        sample_pdf.seek(0)  # Reset file pointer
        response2 = client.post("/payslips", files=files, data=data)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]


class TestPayslipRetrieval:
    def test_get_payslips_empty(self, client):
        """Test getting payslips when none exist"""
        response = client.get("/payslips")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_payslips_with_data(self, client, sample_pdf):
        """Test getting payslips after uploading some"""
        # Upload a test payslip first
        files = {"file": ("test_payslip.pdf", sample_pdf, "application/pdf")}
        data = {"employee_id": 789, "month": 10, "year": 2024}
        client.post("/payslips", files=files, data=data)

        # Now get payslips
        response = client.get("/payslips")
        assert response.status_code == 200
        payslips = response.json()
        assert len(payslips) >= 1
        assert any(p["employee_id"] == 789 for p in payslips)

    def test_get_payslips_with_filters(self, client, sample_pdf):
        """Test getting payslips with filters"""
        # Upload test payslips
        for month in [1, 2, 3]:
            sample_pdf.seek(0)
            files = {"file": (f"payslip_{month}.pdf", sample_pdf, "application/pdf")}
            data = {"employee_id": 999, "month": month, "year": 2024}
            client.post("/payslips", files=files, data=data)

        # Test employee_id filter
        response = client.get("/payslips?employee_id=999")
        assert response.status_code == 200
        payslips = response.json()
        assert all(p["employee_id"] == 999 for p in payslips)

        # Test year filter
        response = client.get("/payslips?year=2024")
        assert response.status_code == 200

        # Test month filter
        response = client.get("/payslips?month=1")
        assert response.status_code == 200
        payslips = response.json()
        assert all(p["month"] == 1 for p in payslips)

    def test_get_payslip_by_id(self, client, sample_pdf):
        """Test getting a specific payslip by ID"""
        # Upload a test payslip first
        files = {"file": ("specific_payslip.pdf", sample_pdf, "application/pdf")}
        data = {"employee_id": 555, "month": 6, "year": 2024}
        upload_response = client.post("/payslips", files=files, data=data)
        payslip_id = upload_response.json()["id"]

        # Get the specific payslip
        response = client.get(f"/payslips/{payslip_id}")
        assert response.status_code == 200
        payslip = response.json()
        assert payslip["id"] == payslip_id
        assert payslip["employee_id"] == 555

    def test_get_payslip_not_found(self, client):
        """Test getting a non-existent payslip"""
        response = client.get("/payslips/99999")
        assert response.status_code == 404


class TestPayslipDeletion:
    def test_delete_payslip_success(self, client, sample_pdf):
        """Test successful payslip deletion"""
        # Upload a test payslip first
        files = {"file": ("to_delete.pdf", sample_pdf, "application/pdf")}
        data = {"employee_id": 777, "month": 8, "year": 2024}
        upload_response = client.post("/payslips", files=files, data=data)
        payslip_id = upload_response.json()["id"]

        # Delete the payslip
        response = client.delete(f"/payslips/{payslip_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

        # Verify it's deleted
        get_response = client.get(f"/payslips/{payslip_id}")
        assert get_response.status_code == 404

    def test_delete_payslip_not_found(self, client):
        """Test deleting a non-existent payslip"""
        response = client.delete("/payslips/99999")
        assert response.status_code == 404


class TestErrorHandling:
    def test_invalid_endpoint(self, client):
        """Test accessing invalid endpoint"""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test using wrong HTTP method"""
        response = client.put("/payslips")
        assert response.status_code == 405

    def test_large_file_upload(self, client):
        """Test uploading a file that's too large"""
        # Create a large file (simulate 15MB)
        large_content = b"x" * (15 * 1024 * 1024)
        files = {"file": ("large.pdf", io.BytesIO(large_content), "application/pdf")}
        data = {"employee_id": 123, "month": 12, "year": 2024}

        response = client.post("/payslips", files=files, data=data)
        assert response.status_code == 413  # Payload Too Large
