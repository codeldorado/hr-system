# Production environment configuration
environment = "prod"
aws_region  = "eu-west-1"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"

# Database Configuration
db_instance_class         = "db.t3.small"
db_allocated_storage      = 100
db_max_allocated_storage  = 1000
enable_deletion_protection = true
create_read_replica       = true
backup_retention_period   = 30

# Application Configuration
app_cpu           = 1024
app_memory        = 2048
app_desired_count = 3
app_min_capacity  = 2
app_max_capacity  = 20

# Auto-scaling Configuration
cpu_target_value    = 60
memory_target_value = 70

# Monitoring Configuration
enable_detailed_monitoring = true
log_retention_days        = 30

# S3 Configuration
s3_versioning_enabled = true
s3_lifecycle_enabled  = true

# Security Configuration
allowed_cidr_blocks = ["0.0.0.0/0"]  # Configure with actual allowed IPs in production
