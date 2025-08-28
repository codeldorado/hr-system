# Deployment Guide

This guide covers the complete deployment process for the Payslip Microservice, from infrastructure setup to application deployment.

## Prerequisites

### Required Tools
- **AWS CLI** v2.x configured with appropriate credentials
- **Terraform** v1.6+ for infrastructure management
- **Docker** for local testing and image building
- **Git** for version control

### AWS Permissions
Ensure your AWS credentials have the following permissions:
- EC2, VPC, and networking resources
- RDS database management
- S3 bucket operations
- ECS and Fargate services
- IAM role and policy management
- CloudWatch logs and metrics
- Secrets Manager access

## Infrastructure Deployment

### 1. Clone Repository
```bash
git clone <repository-url>
cd payslip-microservice
```

### 2. Configure Environment Variables
```bash
# Set database password
export TF_VAR_db_password="your-secure-database-password"

# Optional: Customize AWS region
export AWS_REGION="eu-west-1"
```

### 3. Deploy Infrastructure

#### Development Environment
```bash
cd infrastructure
./deploy.sh -e dev -a plan    # Review changes
./deploy.sh -e dev -a apply   # Deploy infrastructure
```

#### Production Environment
```bash
cd infrastructure
./deploy.sh -e prod -a plan   # Review changes
./deploy.sh -e prod -a apply  # Deploy infrastructure
```

### 4. Verify Infrastructure
```bash
# Check outputs
terraform output

# Verify ALB is accessible
curl -f $(terraform output -raw alb_url)/health
```

## Application Deployment

### Option 1: GitHub Actions (Recommended)

1. **Configure GitHub Secrets:**
   ```
   AWS_ACCESS_KEY_ID: Your AWS access key
   AWS_SECRET_ACCESS_KEY: Your AWS secret key
   DB_PASSWORD: Database password
   ```

2. **Push to Main Branch:**
   ```bash
   git push origin main
   ```

3. **Monitor Deployment:**
   - Go to GitHub Actions tab
   - Watch the CI/CD pipeline execution
   - Verify deployment success

### Option 2: Manual Deployment

1. **Build and Push Docker Image:**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region eu-west-1 | \
     docker login --username AWS --password-stdin \
     <account-id>.dkr.ecr.eu-west-1.amazonaws.com

   # Build image
   docker build -t payslip-microservice .

   # Tag and push
   docker tag payslip-microservice:latest \
     <account-id>.dkr.ecr.eu-west-1.amazonaws.com/payslip-microservice:latest
   
   docker push <account-id>.dkr.ecr.eu-west-1.amazonaws.com/payslip-microservice:latest
   ```

2. **Update ECS Service:**
   ```bash
   aws ecs update-service \
     --cluster payslip-microservice-prod-cluster \
     --service payslip-microservice-prod-service \
     --force-new-deployment
   ```

3. **Wait for Deployment:**
   ```bash
   aws ecs wait services-stable \
     --cluster payslip-microservice-prod-cluster \
     --services payslip-microservice-prod-service
   ```

## Database Setup

### 1. Run Migrations
```bash
# Set database URL
export DATABASE_URL="postgresql://username:password@endpoint:5432/database"

# Run migrations
alembic upgrade head
```

### 2. Verify Database
```bash
# Check current revision
alembic current

# Verify tables exist
psql $DATABASE_URL -c "\dt"
```

## Configuration Management

### Environment Variables

#### Required Variables
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
AWS_REGION=eu-west-1
S3_BUCKET_NAME=payslip-storage-bucket
```

#### Optional Variables
```bash
APP_ENV=production
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760
SECRET_KEY=your-secret-key
```

### AWS Secrets Manager

For production, store sensitive configuration in AWS Secrets Manager:

```bash
# Create database URL secret
aws secretsmanager create-secret \
  --name "payslip-microservice-prod-db-url" \
  --description "Database URL for payslip microservice" \
  --secret-string "postgresql://user:pass@host:5432/db"

# Create S3 bucket name secret
aws secretsmanager create-secret \
  --name "payslip-microservice-prod-s3-bucket" \
  --description "S3 bucket name for payslip storage" \
  --secret-string "your-bucket-name"
```

## Health Checks and Verification

### 1. Application Health
```bash
# Check health endpoint
curl -f https://your-alb-domain.amazonaws.com/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "service": "payslip-microservice"
}
```

### 2. Database Connectivity
```bash
# Test database connection
python -c "
from app.database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('Database connection successful')
"
```

### 3. S3 Access
```bash
# Test S3 bucket access
aws s3 ls s3://your-bucket-name/
```

### 4. ECS Service Status
```bash
# Check ECS service
aws ecs describe-services \
  --cluster payslip-microservice-prod-cluster \
  --services payslip-microservice-prod-service
```

## Monitoring Setup

### 1. CloudWatch Dashboards
Access the CloudWatch dashboard:
```bash
terraform output dashboard_url
```

### 2. Log Monitoring
```bash
# View application logs
aws logs tail /ecs/payslip-microservice-prod --follow

# View specific log stream
aws logs get-log-events \
  --log-group-name /ecs/payslip-microservice-prod \
  --log-stream-name ecs/app/task-id
```

### 3. Metrics and Alarms
Key metrics to monitor:
- ECS CPU and memory utilization
- ALB response time and error rates
- RDS connection count and performance
- S3 request metrics

## Scaling Configuration

### Auto Scaling Policies
The infrastructure includes auto-scaling based on:
- CPU utilization (target: 70%)
- Memory utilization (target: 80%)

### Manual Scaling
```bash
# Scale ECS service
aws ecs update-service \
  --cluster payslip-microservice-prod-cluster \
  --service payslip-microservice-prod-service \
  --desired-count 5
```

### Database Scaling
- **Vertical**: Modify RDS instance class
- **Horizontal**: Add read replicas for read-heavy workloads

## Security Hardening

### 1. Network Security
- All resources in private subnets
- Security groups with minimal required access
- VPC Flow Logs enabled

### 2. Encryption
- RDS encryption at rest
- S3 server-side encryption
- ECS task encryption
- ALB SSL/TLS termination

### 3. IAM Roles
- Least privilege access
- Service-specific roles
- No hardcoded credentials

## Backup and Recovery

### 1. Database Backups
- Automated daily backups (7-day retention for dev, 30-day for prod)
- Point-in-time recovery available
- Cross-region backup replication (production)

### 2. S3 Backup
- Versioning enabled
- Cross-region replication (production)
- Lifecycle policies for cost optimization

### 3. Disaster Recovery
- Multi-AZ deployment
- Automated failover
- Recovery procedures documented

## Troubleshooting

### Common Issues

#### 1. ECS Tasks Not Starting
```bash
# Check task definition
aws ecs describe-task-definition --task-definition payslip-microservice-prod-task

# Check service events
aws ecs describe-services \
  --cluster payslip-microservice-prod-cluster \
  --services payslip-microservice-prod-service \
  --query 'services[0].events'
```

#### 2. Database Connection Issues
```bash
# Check security groups
aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx

# Test connectivity from ECS task
aws ecs execute-command \
  --cluster payslip-microservice-prod-cluster \
  --task task-id \
  --container app \
  --interactive \
  --command "/bin/bash"
```

#### 3. S3 Access Issues
```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket your-bucket-name

# Check IAM role permissions
aws iam get-role-policy \
  --role-name payslip-microservice-prod-ecs-task-role \
  --policy-name S3AccessPolicy
```

### Log Analysis
```bash
# Search for errors in logs
aws logs filter-log-events \
  --log-group-name /ecs/payslip-microservice-prod \
  --filter-pattern "ERROR"

# Get recent application errors
aws logs filter-log-events \
  --log-group-name /ecs/payslip-microservice-prod \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "{ $.level = \"ERROR\" }"
```

## Rollback Procedures

### 1. Application Rollback
```bash
# Rollback to previous task definition
aws ecs update-service \
  --cluster payslip-microservice-prod-cluster \
  --service payslip-microservice-prod-service \
  --task-definition payslip-microservice-prod-task:PREVIOUS_REVISION
```

### 2. Database Rollback
```bash
# Rollback database migration
alembic downgrade -1

# Or rollback to specific revision
alembic downgrade revision_id
```

### 3. Infrastructure Rollback
```bash
# Rollback infrastructure changes
cd infrastructure
git checkout previous-commit
terraform plan -var-file="environments/prod.tfvars"
terraform apply -var-file="environments/prod.tfvars"
```

## Maintenance

### Regular Tasks
1. **Security Updates**: Keep base images and dependencies updated
2. **Log Cleanup**: Monitor log retention and costs
3. **Backup Verification**: Test backup and restore procedures
4. **Performance Review**: Analyze metrics and optimize resources
5. **Cost Optimization**: Review and right-size resources

### Scheduled Maintenance
- **Database Maintenance**: During low-traffic windows
- **Infrastructure Updates**: Use blue-green deployment
- **Security Patches**: Automated through CI/CD pipeline

## Support and Escalation

### Monitoring Alerts
- Critical: Page on-call engineer immediately
- Warning: Create ticket for next business day
- Info: Log for trend analysis

### Escalation Path
1. **Level 1**: Application team
2. **Level 2**: Infrastructure team
3. **Level 3**: AWS support (if needed)

### Documentation
- Runbooks for common issues
- Architecture diagrams
- Contact information for key personnel
