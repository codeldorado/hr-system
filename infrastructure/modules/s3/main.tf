# S3 Bucket for payslip storage
resource "aws_s3_bucket" "payslips" {
  bucket = "${var.name_prefix}-payslips-${random_string.bucket_suffix.result}"

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-payslips-bucket"
  })
}

# Random string for bucket name uniqueness
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "payslips" {
  bucket = aws_s3_bucket.payslips.id
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

# S3 Bucket Server Side Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "payslips" {
  bucket = aws_s3_bucket.payslips.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "payslips" {
  bucket = aws_s3_bucket.payslips.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Lifecycle Configuration
resource "aws_s3_bucket_lifecycle_configuration" "payslips" {
  count = var.enable_lifecycle ? 1 : 0

  bucket = aws_s3_bucket.payslips.id

  rule {
    id     = "payslip_lifecycle"
    status = "Enabled"

    # Transition to IA after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Transition to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Transition to Deep Archive after 365 days
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    # Delete old versions after 90 days
    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

# S3 Bucket Notification (for future integration with Lambda)
resource "aws_s3_bucket_notification" "payslips" {
  bucket = aws_s3_bucket.payslips.id

  # Placeholder for future Lambda integration
  # lambda_function {
  #   lambda_function_arn = aws_lambda_function.processor.arn
  #   events              = ["s3:ObjectCreated:*"]
  #   filter_prefix       = "payslips/"
  #   filter_suffix       = ".pdf"
  # }
}

# IAM Policy for ECS tasks to access S3
resource "aws_iam_policy" "s3_access" {
  name        = "${var.name_prefix}-s3-access"
  description = "Policy for ECS tasks to access S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.payslips.arn,
          "${aws_s3_bucket.payslips.arn}/*"
        ]
      }
    ]
  })

  tags = var.tags
}

# CloudWatch Metrics for S3
resource "aws_cloudwatch_metric_alarm" "s3_bucket_size" {
  alarm_name          = "${var.name_prefix}-s3-bucket-size"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "BucketSizeBytes"
  namespace           = "AWS/S3"
  period              = "86400"  # 24 hours
  statistic           = "Average"
  threshold           = "10737418240"  # 10 GB in bytes
  alarm_description   = "This metric monitors S3 bucket size"

  dimensions = {
    BucketName  = aws_s3_bucket.payslips.bucket
    StorageType = "StandardStorage"
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "s3_number_of_objects" {
  alarm_name          = "${var.name_prefix}-s3-object-count"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "NumberOfObjects"
  namespace           = "AWS/S3"
  period              = "86400"  # 24 hours
  statistic           = "Average"
  threshold           = "100000"  # 100k objects
  alarm_description   = "This metric monitors S3 object count"

  dimensions = {
    BucketName  = aws_s3_bucket.payslips.bucket
    StorageType = "AllStorageTypes"
  }

  tags = var.tags
}
