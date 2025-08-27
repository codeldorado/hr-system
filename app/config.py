import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database settings
    database_url: str = "postgresql://postgres:password@localhost:5432/payslip_db"
    
    # AWS settings
    aws_region: str = "eu-west-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_bucket_name: str = "payslip-storage-bucket"
    
    # Application settings
    app_env: str = "development"
    log_level: str = "INFO"
    max_file_size: int = 10485760  # 10MB
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    cors_origins: list = ["*"]  # Configure properly for production
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
