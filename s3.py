import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError
load_dotenv()
from pathlib import Path
import json


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") 
AWS_REGION = 'us-east-1'
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")



# Add error checking for environment variables
if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_S3_BUCKET_NAME]):
    raise ValueError("Missing required AWS credentials in .env file")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def test_s3_connection():
    try:
        s3_client.head_bucket(Bucket=AWS_S3_BUCKET_NAME)
        return True
    except Exception as e:
        print(f"S3 Connection Error: {str(e)}")
        return False
def ensure_s3_structure():
    """Ensure the basic folder structure exists in S3"""
    base_folders = [
        'web_sources/',
        'web_sources/raw/',
        'web_sources/extracted_markdown/',
        'web_sources/extracted_images/',
        'web_sources/enterprise/',
        'web_sources/enterprise/raw/',
        'web_sources/enterprise/extracted_markdown/',
        'web_sources/enterprise/extracted_images/',
        'web_sources/open_source/',
        'web_sources/open_source/raw/',
        'web_sources/open_source/extracted_markdown/', 
        'web_sources/open_source/extracted_images/'
    ]
    
    try:
        for folder in base_folders:
            s3_client.put_object(
                Bucket=AWS_S3_BUCKET_NAME,
                Key=folder
            )
        return True
    except Exception as e:
        print(f"Error creating S3 structure: {e}")
        return False

def upload_image_to_s3(image_bytes: bytes, key: str, image_ext: str) -> str:
    """Helper function to upload an image to S3 and return its URL"""
    try:
        content_type = f'image/{image_ext}' if image_ext in ['jpeg', 'jpg', 'png'] else 'application/octet-stream'
        s3_client.put_object(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=key,
            Body=image_bytes,
            ContentType=content_type,
            ACL='public-read'
        )
        return f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"
    except Exception as e:
        raise Exception(f"Failed to upload image to S3: {str(e)}")
    
def upload_pdf_to_s3(file_content: bytes, original_filename: str, document_id: str) -> dict:
    """
    Uploads PDF and its processed content to S3 with proper structure.
    Returns dict of URLs for each uploaded file.
    """
    urls = {}
    try:
        # Upload original PDF
        raw_key = f"pdf_sources/raw/{document_id}/{original_filename}"
        s3_client.put_object(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=raw_key,
            Body=file_content
        )
        urls['raw_pdf'] = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{raw_key}"
        
        return urls
    except Exception as e:
        raise Exception(f"Failed to upload PDF to S3: {e}")

def upload_processed_content_to_s3(local_directory: str, document_id: str, source_type: str) -> dict:
    """
    Uploads processed content with proper content types and disposition
    """
    urls = {}
    base_path = Path(local_directory)  # Convert string to Path object
    try:
        # Handle raw files (PDF)  
        if source_type == 'pdf':  
            raw_dir = base_path / "raw"
            if raw_dir.exists():
                for file in raw_dir.iterdir():
                    if file.is_file():
                        raw_key = f"{source_type}_sources/raw/{document_id}/{file.name}"
                        with open(file, 'rb') as f:
                            s3_client.put_object(
                                Bucket=AWS_S3_BUCKET_NAME,
                                Key=raw_key,
                                Body=f.read(),
                                ACL='public-read',
                                ContentType='application/pdf',
                                ContentDisposition='inline'
                            )
                        urls['raw_file'] = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{raw_key}"

        # Handle markdown and images
        for root, _, files in os.walk(base_path):
            for filename in files:  # Changed 'file' to 'filename'
                local_path = Path(root) / filename  # Use filename string
                relative_path = local_path.relative_to(base_path)
                
                # Skip raw directory as we've already handled it
                if 'raw' in str(relative_path):
                    continue
                
                # Determine the correct S3 prefix and content type
                if 'extracted_markdown' in str(relative_path):
                    s3_prefix = f"{source_type}_sources/extracted_markdown/{document_id}"
                    content_type = 'text/markdown'
                elif 'extracted_images' in str(relative_path):
                    s3_prefix = f"{source_type}_sources/extracted_images/{document_id}"
                    ext = filename.lower().split('.')[-1]  # Get extension from filename
                    if ext in ['png']:
                        content_type = 'image/png'
                    elif ext in ['jpg', 'jpeg']:
                        content_type = 'image/jpeg'
                    else:
                        content_type = 'application/octet-stream'
                else:
                    continue
                
                s3_key = f"{s3_prefix}/{filename}"  # Use filename directly
                
                # Upload file with proper content type
                with open(local_path, 'rb') as f:
                    s3_client.put_object(
                        Bucket=AWS_S3_BUCKET_NAME,
                        Key=s3_key,
                        Body=f.read(),
                        ACL='public-read',
                        ContentType=content_type,
                        ContentDisposition='inline'
                    )
                    urls[str(relative_path)] = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        
        return urls
    except Exception as e:
        raise Exception(f"Failed to upload content to S3: {str(e)}")  # Added str() for better error messages
# Run this when the module loads to ensure S3 structure exists
ensure_s3_structure()

if not test_s3_connection():
    print("WARNING: Cannot access S3 bucket. Please check your credentials and permissions.")

def configure_bucket_policy_and_cors():
    """Configure bucket policy and CORS for the S3 bucket"""
    try:
        # Bucket Policy
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": f"arn:aws:s3:::{AWS_S3_BUCKET_NAME}/*"
                }
            ]
        }
        
        # Convert the policy to JSON string
        bucket_policy = json.dumps(bucket_policy)
        
        # Set the bucket policy
        s3_client.put_bucket_policy(
            Bucket=AWS_S3_BUCKET_NAME,
            Policy=bucket_policy
        )

        # CORS Configuration
        cors_configuration = {
            'CORSRules': [{
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': ['ETag']
            }]
        }
        
        # Set the CORS configuration
        s3_client.put_bucket_cors(
            Bucket=AWS_S3_BUCKET_NAME,
            CORSConfiguration=cors_configuration
        )
        
        print(f"Successfully configured bucket policy and CORS for {AWS_S3_BUCKET_NAME}")
        return True
        
    except Exception as e:
        print(f"Error configuring bucket policy and CORS: {str(e)}")
        return False

# Add this to your initialization code
if test_s3_connection():
    ensure_s3_structure()
    configure_bucket_policy_and_cors()
else:
    print("WARNING: Cannot access S3 bucket. Please check your credentials and permissions.")