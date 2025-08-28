# Payslip Microservice API Documentation

## Overview

The Payslip Microservice provides RESTful APIs for managing employee payslip uploads and retrieval. All endpoints return JSON responses and follow standard HTTP status codes.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-alb-domain.amazonaws.com`

## Authentication

The service integrates with the main HR platform's authentication system. Include the JWT token in the Authorization header:

```http
Authorization: Bearer <jwt-token>
```

## Content Types

- **Request**: `multipart/form-data` for file uploads, `application/json` for other requests
- **Response**: `application/json`

## Endpoints

### Health Check

#### GET /health

Returns the health status of the service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "service": "payslip-microservice"
}
```

**Status Codes:**
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is unhealthy

---

### Upload Payslip

#### POST /payslips

Upload a payslip PDF file for an employee.

**Request:**
```http
POST /payslips
Content-Type: multipart/form-data

employee_id: 123
month: 12
year: 2024
file: payslip.pdf
```

**Parameters:**
- `employee_id` (integer, required): Employee identifier
- `month` (integer, required): Month (1-12)
- `year` (integer, required): Year (2000-current year + 1)
- `file` (file, required): PDF file to upload

**Response:**
```json
{
  "id": 1,
  "employee_id": 123,
  "month": 12,
  "year": 2024,
  "filename": "payslip_dec_2024.pdf",
  "file_url": "https://s3.amazonaws.com/bucket/payslips/123/2024/12/uuid.pdf",
  "file_size": 1048576,
  "upload_timestamp": "2024-01-01T12:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Payslip uploaded successfully
- `400 Bad Request`: Invalid input data
- `409 Conflict`: Payslip already exists for this employee/month/year
- `413 Payload Too Large`: File size exceeds limit
- `415 Unsupported Media Type`: File is not a PDF
- `500 Internal Server Error`: Server error

**Error Response:**
```json
{
  "detail": "Only PDF files are allowed"
}
```

---

### Retrieve Payslips

#### GET /payslips

Retrieve payslips with optional filtering and pagination.

**Query Parameters:**
- `employee_id` (integer, optional): Filter by employee ID
- `year` (integer, optional): Filter by year
- `month` (integer, optional): Filter by month
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum records to return (default: 100, max: 1000)

**Examples:**
```http
GET /payslips
GET /payslips?employee_id=123
GET /payslips?employee_id=123&year=2024
GET /payslips?year=2024&month=12
GET /payslips?skip=20&limit=10
```

**Response:**
```json
[
  {
    "id": 1,
    "employee_id": 123,
    "month": 12,
    "year": 2024,
    "filename": "payslip_dec_2024.pdf",
    "file_url": "https://s3.amazonaws.com/bucket/payslips/123/2024/12/uuid.pdf",
    "file_size": 1048576,
    "upload_timestamp": "2024-01-01T12:00:00Z"
  }
]
```

**Status Codes:**
- `200 OK`: Payslips retrieved successfully
- `400 Bad Request`: Invalid query parameters
- `500 Internal Server Error`: Server error

---

### Get Specific Payslip

#### GET /payslips/{payslip_id}

Retrieve a specific payslip by ID.

**Path Parameters:**
- `payslip_id` (integer, required): Payslip identifier

**Response:**
```json
{
  "id": 1,
  "employee_id": 123,
  "month": 12,
  "year": 2024,
  "filename": "payslip_dec_2024.pdf",
  "file_url": "https://s3.amazonaws.com/bucket/payslips/123/2024/12/uuid.pdf",
  "file_size": 1048576,
  "upload_timestamp": "2024-01-01T12:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Payslip found
- `404 Not Found`: Payslip not found
- `500 Internal Server Error`: Server error

---

### Delete Payslip

#### DELETE /payslips/{payslip_id}

Delete a specific payslip (admin only).

**Path Parameters:**
- `payslip_id` (integer, required): Payslip identifier

**Response:**
```json
{
  "message": "Payslip deleted successfully"
}
```

**Status Codes:**
- `200 OK`: Payslip deleted successfully
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Payslip not found
- `500 Internal Server Error`: Server error

---

## Data Models

### Payslip

```json
{
  "id": "integer",
  "employee_id": "integer",
  "month": "integer (1-12)",
  "year": "integer (2000-current+1)",
  "filename": "string (max 255 chars)",
  "file_url": "string (max 500 chars)",
  "file_size": "integer (bytes)",
  "upload_timestamp": "string (ISO 8601 datetime)"
}
```

### Error Response

```json
{
  "detail": "string",
  "error_code": "string (optional)"
}
```

## Rate Limiting

- **Default**: 100 requests per minute per IP
- **Authenticated**: 1000 requests per minute per user
- **File Upload**: 10 uploads per minute per user

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## File Constraints

- **Format**: PDF only
- **Size**: Maximum 10MB
- **Naming**: Original filename preserved
- **Storage**: Organized by employee_id/year/month/

## Security Considerations

### Input Validation

- File type validation (PDF only)
- File size limits (10MB max)
- Month validation (1-12)
- Year validation (2000-current+1)
- Employee ID validation (positive integer)

### File Security

- Virus scanning (recommended for production)
- Content type verification
- Filename sanitization
- Secure file storage with encryption

### Access Control

- Employee-level access: Can only access own payslips
- HR Manager access: Can access all payslips
- Admin access: Full CRUD operations

## Error Handling

### Error Response Format

All errors return a consistent JSON format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "field_errors": {
    "field_name": ["Field-specific error message"]
  }
}
```

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

## Webhooks (Future Enhancement)

The service can be configured to send webhooks for payslip events:

```json
{
  "event": "payslip.uploaded",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "payslip_id": 1,
    "employee_id": 123,
    "month": 12,
    "year": 2024
  }
}
```

Events:
- `payslip.uploaded`: New payslip uploaded
- `payslip.deleted`: Payslip deleted
- `payslip.accessed`: Payslip accessed (audit trail)
