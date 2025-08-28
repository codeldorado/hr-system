# CI/CD Pipeline Documentation

This directory contains GitHub Actions workflows for automated testing, building, and deployment of the payslip microservice.

## Workflows Overview

### 1. CI/CD Pipeline (`ci-cd.yml`)
Main pipeline for continuous integration and deployment.

**Triggers:**
- Push to `main`, `master`, or `develop` branches
- Pull requests to `main` or `master`

**Jobs:**
- **Test**: Run unit tests, linting, and coverage analysis
- **Security Scan**: Vulnerability scanning with Trivy
- **Build**: Build and push Docker images to ECR
- **Deploy Dev**: Deploy to development environment
- **Deploy Prod**: Deploy to production environment
- **Notify**: Send deployment status notifications

### 2. Infrastructure Deployment (`infrastructure.yml`)
Manages Terraform infrastructure deployments.

**Triggers:**
- Push to `main`/`master` with changes in `infrastructure/` directory
- Manual workflow dispatch

**Jobs:**
- **Validate**: Terraform format check and validation
- **Plan**: Generate Terraform execution plans
- **Apply**: Deploy infrastructure changes
- **Destroy**: Destroy infrastructure (manual only)

### 3. Database Migration (`database-migration.yml`)
Handles database schema migrations.

**Triggers:**
- Manual workflow dispatch only

**Actions:**
- `upgrade`: Apply pending migrations
- `downgrade`: Rollback migrations
- `current`: Show current revision
- `history`: Show migration history

## Required Secrets

Configure these secrets in your GitHub repository:

### AWS Credentials
```
AWS_ACCESS_KEY_ID       # AWS access key for deployment
AWS_SECRET_ACCESS_KEY   # AWS secret key for deployment
```

### Database
```
DB_PASSWORD            # Database master password for Terraform
```

### Optional
```
CODECOV_TOKEN         # For code coverage reporting
SLACK_WEBHOOK_URL     # For deployment notifications
```

## Environment Setup

### Development Environment
- Automatic deployment on push to `develop` branch
- Uses minimal resources
- Short log retention

### Production Environment
- Manual approval required
- Automatic deployment on push to `main`/`master`
- Full resources with high availability
- Extended monitoring and logging

## Docker Configuration

### Multi-stage Dockerfile
- **Builder stage**: Install dependencies and build tools
- **Production stage**: Minimal runtime image with security hardening

### Features
- Non-root user execution
- Health checks
- Optimized layer caching
- Security scanning

### Local Development
```bash
# Start all services
docker-compose up

# Start with development hot-reload
docker-compose --profile dev up app-dev

# Run tests
docker-compose run --rm app pytest
```

## Pipeline Stages

### 1. Code Quality
- **Linting**: flake8, black, isort
- **Testing**: pytest with coverage
- **Security**: Trivy vulnerability scanning

### 2. Build & Package
- **Docker Build**: Multi-stage optimized build
- **Image Scanning**: Security vulnerability check
- **Registry Push**: Push to Amazon ECR

### 3. Deployment
- **Infrastructure**: Terraform apply (if changes)
- **Database**: Run migrations
- **Application**: Deploy to ECS Fargate
- **Health Check**: Verify deployment success

### 4. Monitoring
- **Deployment Status**: Success/failure notifications
- **Application Health**: Post-deployment verification
- **Rollback**: Automatic rollback on failure

## Deployment Process

### Automatic Deployment
1. Developer pushes code to `main` branch
2. Pipeline runs tests and security scans
3. Docker image is built and pushed to ECR
4. Infrastructure is updated (if needed)
5. Application is deployed to ECS
6. Health checks verify deployment
7. Notifications sent to team

### Manual Deployment
1. Navigate to Actions tab in GitHub
2. Select "Infrastructure Deployment" workflow
3. Click "Run workflow"
4. Choose environment and action
5. Monitor deployment progress

## Monitoring & Troubleshooting

### Pipeline Monitoring
- **GitHub Actions**: View workflow runs and logs
- **AWS CloudWatch**: Monitor ECS deployments
- **ECR**: Track image builds and vulnerabilities

### Common Issues

#### Build Failures
- Check test results and coverage reports
- Review linting errors
- Verify Docker build context

#### Deployment Failures
- Check ECS service events
- Review CloudWatch logs
- Verify IAM permissions

#### Database Issues
- Check migration logs
- Verify database connectivity
- Review Alembic configuration

### Debugging Commands
```bash
# View ECS service status
aws ecs describe-services --cluster CLUSTER_NAME --services SERVICE_NAME

# Check application logs
aws logs tail /ecs/payslip-microservice-prod --follow

# View recent deployments
aws ecs list-tasks --cluster CLUSTER_NAME --service-name SERVICE_NAME

# Check database migration status
alembic current
```

## Security Considerations

### Image Security
- Base images are regularly updated
- Vulnerability scanning in CI/CD
- Non-root user execution
- Minimal attack surface

### Secrets Management
- AWS Secrets Manager for production secrets
- GitHub Secrets for CI/CD credentials
- No hardcoded secrets in code

### Network Security
- Private subnets for application
- Security groups with least privilege
- VPC endpoints for AWS services

## Performance Optimization

### Build Optimization
- Multi-stage Docker builds
- Layer caching
- Parallel job execution
- Artifact caching

### Deployment Optimization
- Blue-green deployments
- Health check optimization
- Auto-scaling configuration
- Resource right-sizing

## Rollback Procedures

### Automatic Rollback
- Failed health checks trigger rollback
- ECS service maintains previous task definition
- Database migrations are not auto-rolled back

### Manual Rollback
```bash
# Rollback ECS service
aws ecs update-service --cluster CLUSTER --service SERVICE --task-definition PREVIOUS_TASK_DEF

# Rollback database (if needed)
alembic downgrade -1
```

## Best Practices

1. **Always test locally** before pushing
2. **Use feature branches** for development
3. **Review pull requests** thoroughly
4. **Monitor deployments** actively
5. **Keep secrets secure** and rotated
6. **Document changes** in commit messages
7. **Test rollback procedures** regularly
