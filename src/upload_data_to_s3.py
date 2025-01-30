

import datetime
import os

import boto3
from PIL import Image

# AWS Credentials
ACCESS_KEY = 'AKIA2MNVL2SX4KKVXNEI'
SECRET_KEY = 'XGibeH9mbCCZU2k4vGEUA+iHxrjcKEvEc4My2Y6Q'

S3_BUCKET = 'web-scraper-storage-sahil'  # Set this as your actual bucket name


def get_image_metadata(file_path):
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            format = img.format
            mode = img.mode
            return {
                'Width': str(width),
                'Height': str(height),
                'Format': format,
                'ColorMode': mode
            }
    except Exception as e:
        print(f"Error reading image metadata: {str(e)}")
        return {}


def upload_files_to_s3(local_folder_path, s3_prefix):
    s3 = boto3.client('s3',
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                local_file_path = os.path.join(root, file)

                # Create S3 key with prefix structure
                relative_path = os.path.relpath(local_file_path, local_folder_path)
                s3_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")

                # Get image metadata
                img_metadata = get_image_metadata(local_file_path)

                # Prepare metadata
                metadata = {
                    'FileType': 'Image',
                    'Source': os.path.basename(root),
                    'UploadDate': datetime.datetime.now().isoformat(),
                    'OriginalFilename': file,
                    'FileSize': str(os.path.getsize(local_file_path)),
                    'ContentType': f"image/{os.path.splitext(file)[1][1:].lower()}",
                    **img_metadata
                }

                # Add custom tags for improved searchability
                tags = {
                    'Project': 'WebScraper',
                    'Category': 'EnterpriseImages',
                    'Source': 'OracleSQL'
                }

                try:
                    # Upload file with metadata
                    s3.upload_file(
                        Filename=local_file_path,
                        Bucket=S3_BUCKET,
                        Key=s3_key,
                        ExtraArgs={
                            "Metadata": metadata,
                            "ServerSideEncryption": "AES256",
                            "ContentType": metadata['ContentType']
                        }
                    )

                    # Add tags to the uploaded object
                    s3.put_object_tagging(
                        Bucket=S3_BUCKET,
                        Key=s3_key,
                        Tagging={'TagSet': [{'Key': k, 'Value': v} for k, v in tags.items()]}
                    )

                    print(f"Uploaded {file} to S3 as {s3_key} with metadata and tags")
                except Exception as e:
                    print(f"Error uploading {file}: {str(e)}")


def main():
    local_folder_path = r'C:\Users\Dhrumil Patel\PycharmProjects\assignment1\output-test\extractedOpnSrc_20250129_131721'
    s3_prefix = 'web_sources/enterprise/extracted_images'
    upload_files_to_s3(local_folder_path, s3_prefix)


if __name__ == "__main__":
    main()
