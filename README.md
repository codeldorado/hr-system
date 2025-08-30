# HR Platform - Payslip Management System

A comprehensive, production-ready full-stack application for managing employee payslip uploads and retrieval. Built with modern technologies including React TypeScript frontend, FastAPI backend, and designed for cloud-native deployment on AWS infrastructure.


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

#### **Architecture & Scalability**
- **Scalable Architecture**: Auto-scaling from 1-20 instances based on demand
- **High Availability**: Multi-AZ deployment with 99.9% uptime SLA
- **Cloud-Native**: AWS-first design with local development support
- **Microservices Ready**: Designed for integration with larger HR platform

## Quick Start Guide

### Prerequisites

#### Required Software
- **Python 3.11+**: Backend runtime
- **Node.js 16+**: Frontend development
- **Git**: Version control

#### Optional (for production deployment)
- **Docker & Docker Compose**: Containerization
- **AWS CLI**: Cloud deployment
- **Terraform**: Infrastructure as Code

### Complete Deployment & Testing Guide

#### Option 1: Local Development (Recommended for Testing)

1. **Clone the Repository**
   ```bash
   cd hr-payslip-system
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Create demo database with sample data
   python create_demo_db.py

   # Start backend server
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend Setup** (in a new terminal)
   ```bash
   cd frontend

   # Install dependencies
   npm install

   # Create environment file
   echo "GENERATE_SOURCEMAP=false
   SKIP_PREFLIGHT_CHECK=true
   REACT_APP_API_URL=http://localhost:8000
   WDS_SOCKET_HOST=localhost
   WDS_SOCKET_PORT=3000
   WDS_SOCKET_PATH=/ws
   NODE_OPTIONS=--openssl-legacy-provider" > .env

   # Start frontend development server
   npm start
   ```

4. **Access the Application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

#### Option 2: Docker Deployment

1. **Using Docker Compose**
   ```bash
   # Clone repository
   cd hr-payslip-system

   # Start all services
   docker-compose up -d

   # Check service status
   docker-compose ps

   # View logs
   docker-compose logs -f
   ```

2. **Access Services**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - Database: PostgreSQL on port 5432

#### Option 3: Production AWS Deployment

1. **Infrastructure Setup**
   ```bash
   cd infrastructure

   # Configure AWS credentials
   aws configure

   # Set environment variables
   export TF_VAR_db_password="your-secure-password"
   export TF_VAR_environment="prod"

   # Deploy infrastructure
   terraform init
   terraform plan
   terraform apply
   ```

2. **Application Deployment**
   ```bash
   # Build and push Docker images
   ./scripts/build-and-deploy.sh

   # Deploy to ECS
   aws ecs update-service --cluster payslip-cluster --service payslip-service --force-new-deployment
   ```

### Testing Guide

#### Demo Credentials

For testing the application, use these demo accounts:

**Employee Account:**
- Email: `demo@company.com`
- Password: `demo123`
- Access: View own payslips, upload new payslips

**HR Manager Account:**
- Email: `hr@company.com`
- Password: `hr123`
- Access: View all payslips, manage employee payslips, admin functions

#### Complete Testing Workflow

1. **Authentication Testing**
   ```bash
   # Test employee login
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "demo@company.com", "password": "demo123"}'

   # Test HR manager login
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "hr@company.com", "password": "hr123"}'
   ```

2. **Frontend Testing Checklist**
   - **Login Flow**: Test both employee and HR manager accounts
   - **Dashboard**: Verify payslip statistics and recent uploads
   - **File Upload**: Upload PDF files with form validation
   - **File Download**: Click download buttons to test file serving
   - **File Viewing**: Click view buttons to open PDFs in browser
   - **Responsive Design**: Test on mobile, tablet, and desktop
   - **Error Handling**: Test with invalid files and network errors
   - **Role-Based Access**: Verify different permissions per role

3. **Backend API Testing**
   ```bash
   # Health check
   curl http://localhost:8000/health

   # Get payslips (requires authentication)
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/payslips

   # Upload payslip
   curl -X POST http://localhost:8000/payslips \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -F "employee_id=123" \
     -F "month=12" \
     -F "year=2024" \
     -F "file=@sample_payslip.pdf"

   # Download file
   curl http://localhost:8000/files/payslips/123/2024/11/demo-sample.pdf
   ```

4. **Database Testing**
   ```bash
   # Connect to demo database
   sqlite3 payslip_demo.db

   # Check sample data
   SELECT * FROM payslips;
   SELECT COUNT(*) FROM payslips;

   # Verify data integrity
   SELECT employee_id, COUNT(*) FROM payslips GROUP BY employee_id;
   ```

5. **File Storage Testing**
   ```bash
   # Check local storage directory
   ls -la local_storage/payslips/

   # Verify file structure
   find local_storage -name "*.pdf" -type f

   # Test file permissions
   ls -la local_storage/payslips/123/2024/11/
   ```

#### Performance Testing

1. **Load Testing with curl**
   ```bash
   # Concurrent requests
   for i in {1..10}; do
     curl -s http://localhost:8000/health &
   done
   wait

   # File upload stress test
   for i in {1..5}; do
     curl -X POST http://localhost:8000/payslips \
       -F "employee_id=$i" \
       -F "month=12" \
       -F "year=2024" \
       -F "file=@test_payslip.pdf" &
   done
   wait
   ```

2. **Frontend Performance**
   - Open browser DevTools (F12)
   - Check Network tab for API response times
   - Monitor Console for errors or warnings
   - Test file upload progress indicators
   - Verify responsive design on different screen sizes

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


**Code Style:**
```bash
# Frontend linting and formatting
cd frontend
npm run lint          # ESLint for code quality
npm run format        # Prettier for code formatting
npm run type-check    # TypeScript compilation check

# Backend code quality
black app/ tests/     # Python code formatting
isort app/ tests/     # Import sorting
flake8 app/          # Linting
mypy app/            # Type checking
```

**Testing Standards:**
```bash
# Backend testing
pytest                           # Run all tests
pytest --cov=app --cov-report=html  # Coverage report
pytest tests/test_main.py -v    # Specific test file

# Frontend testing
cd frontend
npm test                        # Jest unit tests
npm run test:coverage          # Coverage report
npm run test:e2e              # End-to-end tests
```