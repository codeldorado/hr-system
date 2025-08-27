import boto3
import os
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "payslip-storage-bucket")
        self.region = os.getenv("AWS_REGION", "eu-west-1")
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

    async def upload_file(self, file: UploadFile, key: str) -> str:
        """
        Upload file to S3 bucket
        
        Args:
            file: FastAPI UploadFile object
            key: S3 object key (path)
            
        Returns:
            str: S3 object URL
        """
        try:
            # Read file content
            file_content = await file.read()
            
            # Reset file pointer for potential reuse
            await file.seek(0)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ContentType='application/pdf',
                ServerSideEncryption='AES256',  # Encrypt at rest
                Metadata={
                    'original_filename': file.filename,
                    'content_type': file.content_type or 'application/pdf'
                }
            )
            
            # Generate S3 URL
            file_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            
            logger.info(f"Successfully uploaded file to S3: {key}")
            return file_url
            
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file to storage")
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {e}")
            raise HTTPException(status_code=500, detail="File upload failed")

    async def delete_file(self, file_url: str) -> bool:
        """
        Delete file from S3 bucket
        
        Args:
            file_url: Full S3 URL of the file
            
        Returns:
            bool: True if successful
        """
        try:
            # Extract key from URL
            key = file_url.split(f"{self.bucket_name}.s3.{self.region}.amazonaws.com/")[1]
            
            # Delete from S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            logger.info(f"Successfully deleted file from S3: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during file deletion: {e}")
            return False

    async def generate_presigned_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for secure file access
        
        Args:
            key: S3 object key
            expiration: URL expiration time in seconds
            
        Returns:
            str: Presigned URL or None if failed
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None

    def check_bucket_exists(self) -> bool:
        """Check if S3 bucket exists and is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            return False

# Create singleton instance
s3_service = S3Service()
