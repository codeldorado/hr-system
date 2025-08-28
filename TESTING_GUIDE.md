# Comprehensive Testing Guide

## Testing Procedures

### Prerequisites
1. **Docker Desktop** (for full stack testing)
2. **Node.js 18+** (for frontend development)
3. **Python 3.11+** (for backend development)

### Backend API Testing

#### 1. Start Backend Services
```bash
# Start database and supporting services
docker-compose up -d postgres redis localstack

# Start backend in development mode
docker-compose --profile dev up app-dev
```

#### 2. Test API Endpoints

**Health Check:**
```bash
curl http://localhost:8001/health
# Expected: {"status": "healthy", "timestamp": "...", "service": "payslip-microservice"}
```

**API Documentation:**
- Visit: http://localhost:8001/docs
- Verify all endpoints are documented
- Test interactive API documentation

**Upload Payslip:**
```bash
# Create a test PDF file
echo "%PDF-1.4" > test_payslip.pdf

# Upload payslip
curl -X POST "http://localhost:8001/payslips" \
  -H "Content-Type: multipart/form-data" \
  -F "employee_id=123" \
  -F "month=12" \
  -F "year=2024" \
  -F "file=@test_payslip.pdf"
```

**Get Payslips:**
```bash
# Get all payslips
curl http://localhost:8001/payslips

# Get payslips with filters
curl "http://localhost:8001/payslips?employee_id=123&year=2024"
```

### Frontend Testing

#### 1. Start Frontend Services
```bash
# Production build
docker-compose up frontend

# Development mode
docker-compose --profile dev up frontend-dev
```

#### 2. Manual UI Testing

**Access Application:**
- Production: http://localhost:3000
- Development: http://localhost:3001

**Login Testing:**
1. **Employee Account:**
   - Email: `demo@company.com`
   - Password: `demo123`
   - Expected: Access to personal dashboard and payslips

2. **HR Manager Account:**
   - Email: `hr@company.com`
   - Password: `hr123`
   - Expected: Access to all employee payslips and admin features

**Dashboard Testing:**
1. Verify welcome message displays user name
2. Check statistics cards show correct data
3. Test quick action buttons navigate correctly
4. Verify recent payslips list displays properly

**Upload Functionality:**
1. Navigate to Upload page
2. Test drag-and-drop file upload
3. Test file selection via click
4. Verify form validation (required fields, file type)
5. Test upload progress indicator
6. Verify success/error messages

**Payslip Management:**
1. Navigate to Payslips page
2. Test filtering by employee, year, month
3. Verify table displays correct data
4. Test download functionality
5. Test delete functionality (HR/Admin only)

**Responsive Design:**
1. Test on mobile devices (Chrome DevTools)
2. Verify navigation menu works on mobile
3. Check form layouts adapt to screen size
4. Test touch interactions

### Integration Testing

#### 1. End-to-End Workflow
1. **Login** as employee
2. **Upload** a payslip PDF
3. **Verify** payslip appears in list
4. **Download** the uploaded payslip
5. **Logout** and login as HR manager
6. **View** all employee payslips
7. **Filter** payslips by criteria
8. **Delete** a payslip (admin function)

#### 2. Error Handling
1. **Invalid Login:** Test with wrong credentials
2. **File Upload Errors:** Test with invalid file types, oversized files
3. **Network Errors:** Disconnect network and test error messages
4. **Validation Errors:** Submit forms with missing/invalid data

#### 3. Performance Testing
1. **Upload Large Files:** Test with maximum file size (10MB)
2. **Multiple Uploads:** Upload several files simultaneously
3. **Large Dataset:** Test with many payslips in the system
4. **Concurrent Users:** Test with multiple browser sessions

### Infrastructure Testing

#### 1. Docker Testing
```bash
# Build all images
docker-compose build

# Test production deployment
docker-compose up -d

# Verify all services are healthy
docker-compose ps
```

#### 2. Database Testing
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d payslip_db

# Verify tables exist
\dt

# Check sample data
SELECT * FROM payslips LIMIT 5;
```

#### 3. S3 Integration (LocalStack)
```bash
# Check S3 bucket
aws --endpoint-url=http://localhost:4566 s3 ls s3://payslip-storage-bucket/
```

## 🐛 Common Issues and Solutions

### Backend Issues
1. **Database Connection Failed**
   - Solution: Ensure PostgreSQL is running and accessible
   - Check: `docker-compose logs postgres`

2. **S3 Upload Failed**
   - Solution: Verify LocalStack is running
   - Check: `docker-compose logs localstack`

3. **Import Errors**
   - Solution: Install Python dependencies
   - Run: `pip install -r requirements.txt`

### Frontend Issues
1. **Build Failed**
   - Solution: Install Node.js dependencies
   - Run: `cd frontend && npm install`

2. **API Connection Failed**
   - Solution: Check backend is running on correct port
   - Verify: `REACT_APP_API_URL` environment variable

3. **Authentication Issues**
   - Solution: Clear browser storage and try again
   - Check: Browser developer tools for errors

### Docker Issues
1. **Container Won't Start**
   - Solution: Check Docker Desktop is running
   - Run: `docker system prune` to clean up

2. **Port Conflicts**
   - Solution: Change ports in docker-compose.yml
   - Check: `netstat -an | findstr :3000`