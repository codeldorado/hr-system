# Development environment configuration
environment = "dev"
aws_region  = "eu-west-1"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"

# Database Configuration
db_instance_class         = "db.t3.micro"
db_allocated_storage      = 20
db_max_allocated_storage  = 50
enable_deletion_protection = false
create_read_replica       = false

# Application Configuration
app_cpu           = 256
app_memory        = 512
app_desired_count = 1
app_min_capacity  = 1
app_max_capacity  = 3

# Auto-scaling Configuration
cpu_target_value    = 70
memory_target_value = 80

# Monitoring Configuration
enable_detailed_monitoring = false
log_retention_days        = 3

# S3 Configuration
s3_versioning_enabled = false
s3_lifecycle_enabled  = false
