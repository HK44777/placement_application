"""
utils/s3.py
───────────
Utility functions for interacting with AWS S3, including generating
presigned URLs for direct frontend uploads and secure downloads.
"""

import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import uuid
import re

# Load configuration from environment variables
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME')

def secure_filename(filename: str) -> str:
    """A simple replacement for werkzeug's secure_filename."""
    if not filename:
        return ""
    # Keep only alphanumerics, dots, underscores, dashes
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    # Strip leading dots/dashes
    filename = re.sub(r'^[\.\-]+', '', filename)
    return filename

def get_s3_client():
    """Returns a configured boto3 S3 client."""
    return boto3.client(
        's3',
        region_name=AWS_REGION,
        endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4')
    )

def generate_presigned_upload_url(file_name: str, file_type: str, folder: str, expiration=3600):
    """
    Generate a presigned URL to upload a file directly to S3.
    Returns the URL and the generated object key.
    """
    s3_client = get_s3_client()
    
    # Clean the filename and append a UUID to ensure uniqueness
    safe_name = secure_filename(file_name)
    unique_id = str(uuid.uuid4())
    object_key = f"{folder}/{unique_id}_{safe_name}"

    try:
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': AWS_S3_BUCKET_NAME,
                'Key': object_key,
                'ContentType': file_type
            },
            ExpiresIn=expiration
        )
    except ClientError as e:
        print(f"Error generating presigned upload URL: {e}")
        return None, None

    return response, object_key

def generate_presigned_download_url(object_key: str, expiration=3600):
    """
    Generate a presigned URL to download/view a file from S3.
    """
    s3_client = get_s3_client()
    
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': AWS_S3_BUCKET_NAME,
                'Key': object_key
            },
            ExpiresIn=expiration
        )
    except ClientError as e:
        print(f"Error generating presigned download URL: {e}")
        return None

    return response
