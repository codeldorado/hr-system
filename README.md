# Payslip Microservice

A scalable, production-ready microservice for managing employee payslip uploads and retrieval, built with FastAPI and deployed on AWS infrastructure.

## Architecture Overview

This project implements a comprehensive HR platform payslip management system designed to handle 100,000+ active users with peak traffic handling and auto-scaling capabilities.

### System Components

- **React Frontend**: Modern TypeScript UI with Material-UI components
- **FastAPI Backend**: High-performance async API with automatic documentation
- **PostgreSQL Database**: Multi-AZ RDS with automated backups and read replicas
- **S3 Storage**: Encrypted file storage with lifecycle management
- **ECS Fargate**: Containerized deployment with auto-scaling
- **Application Load Balancer**: High-availability load balancing
- **CloudWatch**: Comprehensive monitoring and alerting

### Key Features

- **Scalable Architecture**: Auto-scaling from 1-20 instances based on demand
- **High Availability**: Multi-AZ deployment with 99.9% uptime SLA
- **Security**: Encryption at rest/transit, VPC isolation, IAM roles
- **Monitoring**: CloudWatch dashboards, alarms, and centralized logging
- **CI/CD**: Automated testing, building, and deployment pipeline
- **Infrastructure as Code**: Complete Terraform configuration

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- AWS CLI (for deployment)
- Terraform (for infrastructure)

### Local Development Setup

1. **Clone and setup environment:**
   ```bash
   git clone <repository-url>
   cd payslip-microservice
   chmod +x scripts/setup-dev.sh
   ./scripts/setup-dev.sh
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Demo Credentials

For testing the application, use these demo accounts:

**Employee Account:**
- Email: `demo@company.com`
- Password: `demo123`

**HR Manager Account:**
- Email: `hr@company.com`
- Password: `hr123`

## API Documentation

### Core Endpoints

#### Upload Payslip
```http
POST /payslips
Content-Type: multipart/form-data

employee_id: 123
month: 12
year: 2024
file: payslip.pdf
```

#### Retrieve Payslips
```http
GET /payslips?employee_id=123&year=2024&month=12
```

#### Get Specific Payslip
```http
GET /payslips/{payslip_id}
```

### Response Format
```json
{
  "id": 1,
  "employee_id": 123,
  "month": 12,
  "year": 2024,
  "filename": "payslip_dec_2024.pdf",
  "file_url": "https://s3.amazonaws.com/bucket/path/file.pdf",
  "file_size": 1048576,
  "upload_timestamp": "2024-12-01T10:30:00Z"
}
```

### Error Handling
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Payslip not found
- `409 Conflict`: Duplicate payslip
- `500 Internal Server Error`: Server error

## Infrastructure

### AWS Architecture

The infrastructure follows a microservices architecture with:

- **VPC**: Multi-AZ setup with public, private, and database subnets
- **ECS Fargate**: Serverless container deployment
- **RDS PostgreSQL**: Multi-AZ database with automated backups
- **S3**: Encrypted storage with versioning and lifecycle policies
- **ALB**: Application Load Balancer with health checks
- **CloudWatch**: Monitoring, logging, and alerting

### Deployment

#### Infrastructure Deployment
```bash
cd infrastructure
export TF_VAR_db_password="your-secure-password"
./deploy.sh -e prod -a apply
```

#### Application Deployment
Automated via GitHub Actions on push to main branch.

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_main.py -v
```

### Code Quality
```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Project Structure
```
payslip-microservice/
├── frontend/              # React TypeScript frontend
│   ├── src/              # React source code
│   ├── public/           # Static assets
│   └── Dockerfile        # Frontend container
├── app/                  # FastAPI application
│   ├── main.py          # Main application entry
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # Database configuration
│   └── services/        # Business logic
├── infrastructure/      # Terraform configurations
│   ├── modules/        # Reusable Terraform modules
│   └── environments/   # Environment-specific configs
├── tests/              # Test suite
├── docs/               # Documentation
├── .github/            # CI/CD workflows
└── scripts/            # Utility scripts
```

## Security

### Authentication & Authorization

The microservice integrates with the broader HR platform's authentication system:

- **JWT Token Validation**: Validates tokens from the main authentication service
- **Role-Based Access**: Different permissions for employees, HR managers, and administrators
- **API Key Management**: Service-to-service authentication

### Implementation Notes

For production deployment, integrate with:
1. **Corporate SSO**: SAML/OIDC integration
2. **API Gateway**: Centralized authentication and rate limiting
3. **Secrets Manager**: Secure credential storage

### Security Features

- **Encryption**: All data encrypted at rest and in transit
- **Network Security**: Private subnets, security groups, NACLs
- **File Validation**: PDF-only uploads with size limits
- **Audit Logging**: All operations logged for compliance

## Monitoring & Observability

### CloudWatch Integration

- **Application Metrics**: Response time, error rates, throughput
- **Infrastructure Metrics**: CPU, memory, network utilization
- **Custom Metrics**: Business-specific KPIs
- **Alarms**: Automated alerting for critical issues

### Logging

- **Structured Logging**: JSON format for easy parsing
- **Centralized Logs**: CloudWatch Logs aggregation
- **Log Retention**: Configurable retention policies
- **Error Tracking**: Detailed error logging and alerting

### Health Checks

- **Application Health**: `/health` endpoint with dependency checks
- **Infrastructure Health**: ECS health checks and ALB monitoring
- **Database Health**: Connection and performance monitoring

## Deployment

### Environments

#### Development
- **Purpose**: Feature development and testing
- **Resources**: Minimal (t3.micro instances)
- **Auto-scaling**: 1-3 instances
- **Data Retention**: 3 days

#### Production
- **Purpose**: Live user traffic
- **Resources**: Optimized (t3.small+ instances)
- **Auto-scaling**: 2-20 instances
- **Data Retention**: 30 days
- **High Availability**: Multi-AZ deployment

### CI/CD Pipeline

1. **Code Push**: Developer pushes to main branch
2. **Testing**: Automated tests and security scans
3. **Build**: Docker image creation and ECR push
4. **Deploy**: ECS service update with health checks
5. **Verify**: Post-deployment health verification
6. **Monitor**: Continuous monitoring and alerting

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# AWS Configuration
AWS_REGION=eu-west-1
S3_BUCKET_NAME=payslip-storage-bucket

# Application
APP_ENV=production
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760  # 10MB
```

### Feature Flags

- `ENABLE_FILE_VALIDATION`: Enable strict file validation
- `ENABLE_AUDIT_LOGGING`: Enable detailed audit logs
- `ENABLE_RATE_LIMITING`: Enable API rate limiting

## Integration with HR Platform

### Service Communication

The payslip microservice integrates with the broader HR platform through:

1. **API Gateway**: Centralized routing and authentication
2. **Event Bus**: Async communication for payslip events
3. **Shared Database**: Employee data synchronization
4. **Service Mesh**: Secure service-to-service communication

### Data Flow

1. **Employee Authentication**: Via main HR platform
2. **Payslip Upload**: Direct to microservice
3. **Notification**: Event published to notification service
4. **Audit Trail**: Logged to central audit system

### Optimization

- **Database**: Connection pooling, query optimization
- **Caching**: Redis for session and frequently accessed data
- **CDN**: CloudFront for static content delivery
- **Async Processing**: Background tasks for heavy operations


### Support

- **Logs**: Check CloudWatch Logs for detailed error information
- **Metrics**: Monitor CloudWatch dashboards for system health
- **Alerts**: Configure SNS notifications for critical issues
