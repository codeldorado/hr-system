# Payslip Microservice Infrastructure

This directory contains Terraform configurations for deploying the payslip microservice infrastructure on AWS.

## Architecture Overview

The infrastructure includes:

- **VPC**: Multi-AZ VPC with public, private, and database subnets
- **ECS Fargate**: Containerized application deployment with auto-scaling
- **RDS PostgreSQL**: Multi-AZ database with automated backups
- **Application Load Balancer**: High-availability load balancing
- **S3**: Secure file storage for payslip PDFs
- **CloudWatch**: Comprehensive monitoring and logging
- **Security Groups**: Least-privilege network security

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0 installed
3. **Docker** for building application images
4. **Environment variables** set:
   ```bash
   export TF_VAR_db_password="your-secure-database-password"
   export AWS_REGION="eu-west-1"
   ```

## Directory Structure

```
infrastructure/
├── main.tf                 # Main Terraform configuration
├── variables.tf            # Input variables
├── outputs.tf             # Output values
├── deploy.sh              # Deployment script
├── environments/          # Environment-specific configurations
│   ├── dev.tfvars
│   └── prod.tfvars
└── modules/               # Terraform modules
    ├── vpc/               # VPC and networking
    ├── security/          # Security groups
    ├── rds/              # Database
    ├── s3/               # File storage
    ├── ecs/              # Container orchestration
    └── cloudwatch/       # Monitoring and logging
```

## Quick Start

### 1. Initialize Terraform

```bash
cd infrastructure
terraform init
```

### 2. Plan Deployment

```bash
# Development environment
./deploy.sh -e dev -a plan

# Production environment
./deploy.sh -e prod -a plan
```

### 3. Deploy Infrastructure

```bash
# Development environment
export TF_VAR_db_password="dev-password-123"
./deploy.sh -e dev -a apply

# Production environment (with auto-approve)
export TF_VAR_db_password="prod-secure-password-456"
./deploy.sh -e prod -a apply --auto-approve
```

### 4. Access Application

After deployment, the application will be available at the ALB URL:

```bash
terraform output alb_url
```

## Environment Configurations

### Development (`dev.tfvars`)
- Single AZ deployment
- Minimal resources (t3.micro instances)
- Short log retention (3 days)
- No deletion protection

### Production (`prod.tfvars`)
- Multi-AZ deployment
- Larger instances (t3.small+)
- Extended log retention (30 days)
- Deletion protection enabled
- Read replicas for database

## Key Features

### Security
- All resources deployed in private subnets
- Security groups with least-privilege access
- Database encryption at rest
- S3 bucket encryption and public access blocking
- VPC Flow Logs for network monitoring

### High Availability
- Multi-AZ deployment across 2 availability zones
- Auto-scaling ECS services (1-20 instances)
- RDS Multi-AZ with automated failover
- Application Load Balancer with health checks

### Monitoring
- CloudWatch dashboard with key metrics
- Automated alarms for CPU, memory, and response time
- Centralized logging with configurable retention
- Performance Insights for database monitoring

### Cost Optimization
- Auto-scaling based on CPU and memory utilization
- S3 lifecycle policies for long-term storage
- Right-sized instances per environment
- Spot instances support (configurable)

## Customization

### Adding New Environments

1. Create new tfvars file: `environments/staging.tfvars`
2. Configure environment-specific values
3. Deploy: `./deploy.sh -e staging -a apply`

### Modifying Resources

Edit the relevant module in `modules/` directory and apply changes:

```bash
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"
```

### Scaling Configuration

Modify auto-scaling parameters in environment tfvars:

```hcl
app_min_capacity = 2
app_max_capacity = 50
cpu_target_value = 60
memory_target_value = 70
```

## Monitoring and Troubleshooting

### CloudWatch Dashboard

Access the dashboard at:
```bash
terraform output dashboard_url
```

### Application Logs

View ECS logs in CloudWatch:
```bash
aws logs tail /ecs/payslip-microservice-dev --follow
```

### Database Monitoring

Check RDS performance:
- CPU utilization
- Connection count
- Read/write latency
- Performance Insights

### Common Issues

1. **ECS Tasks Failing**: Check CloudWatch logs for application errors
2. **Database Connection Issues**: Verify security groups and network ACLs
3. **High Response Times**: Check auto-scaling policies and resource limits
4. **S3 Access Denied**: Verify IAM roles and S3 bucket policies

## Cleanup

To destroy the infrastructure:

```bash
# Development environment
./deploy.sh -e dev -a destroy

# Production environment (with confirmation)
./deploy.sh -e prod -a destroy --auto-approve
```

**Warning**: This will permanently delete all resources and data!

## Security Considerations

1. **Database Password**: Use AWS Secrets Manager in production
2. **Network Access**: Restrict ALB access to specific IP ranges
3. **IAM Roles**: Follow principle of least privilege
4. **Encryption**: Enable encryption for all data at rest and in transit
5. **Backup**: Ensure regular database backups and test restore procedures

## Support

For issues or questions:
1. Check CloudWatch logs and metrics
2. Review Terraform plan output
3. Validate AWS resource limits and quotas
4. Ensure proper IAM permissions
