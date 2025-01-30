import os
import datetime
import boto3
from PIL import Image

# Assuming these are defined elsewhere in the actual script
ACCESS_KEY = 'AKIA2MNVL2SX4KKVXNEI'
SECRET_KEY = 'XGibeH9mbCCZU2k4vGEUA+iHxrjcKEvEc4My2Y6Q'

S3_BUCKET = 'web-scraper-storage-sahil'  # Your actual bucket name

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

def upload_files_to_s3(local_folder_path):
    s3 = boto3.client('s3',
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    # Define file type to S3 prefix mapping
    prefix_mapping = {
        'image': {
            'extensions': ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'],
            's3_prefix': 'web_sources/enterprise/extracted_images'
        },
        'markdown': {
            'extensions': ['md', 'markdown'],
            's3_prefix': 'web_sources/enterprise/markdown_files'
        },
        'raw': {
            'extensions': ['csv', 'txt', 'json', 'xml', 'log'],
            's3_prefix': 'web_sources/enterprise/raw_files'
        }
    }

    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1][1:].lower()

            # Determine the appropriate prefix
            upload_config = None
            for file_type, config in prefix_mapping.items():
                if file_ext in config['extensions']:
                    upload_config = config
                    break

            # If no specific prefix found, use raw prefix as default
            if upload_config is None:
                upload_config = prefix_mapping['raw']

            # Create S3 key with prefix structure
            relative_path = os.path.relpath(local_file_path, local_folder_path)
            s3_key = os.path.join(upload_config['s3_prefix'], relative_path).replace("\\", "/")

            # Prepare metadata
            metadata = {
                'FileType': file_type if 'file_type' in locals() else 'raw',
                'Source': os.path.basename(root),
                'UploadDate': datetime.datetime.now().isoformat(),
                'OriginalFilename': file,
                'FileSize': str(os.path.getsize(local_file_path)),
                'ContentType': f"application/{file_ext}"
            }

            # Add image-specific metadata for image files
            if file_ext in prefix_mapping['image']['extensions']:
                metadata.update(get_image_metadata(local_file_path))

            # Add custom tags for improved searchability
            tags = {
                'Project': 'WebScraper',
                'Category': 'EnterpriseFiles',
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

                print(f"Uploaded {file} to S3 bucket {S3_BUCKET} as {s3_key} with metadata and tags")
            except Exception as e:
                print(f"Error uploading {file}: {str(e)}")

def main():
    local_folder_path = r'C:\Users\Dhrumil Patel\PycharmProjects\assignment1\output-test\extractedOpnSrc_20250129_131721'
    upload_files_to_s3(local_folder_path)

if __name__ == "__main__":
    main()












# S3_IMAGE_BUCKET = 'web-scraper-storage-sahil/web_sources/enterprise/extracted_images'
# S3_RAW_BUCKET = 'web-scraper-storage-sahil/web_sources/enterprise/extracted_markdown'
# S3_MARKDOWN_BUCKET = 'web-scraper-storage-sahil/web_sources/enterprise/raw'
#
#
# def get_image_metadata(file_path):
#     try:
#         with Image.open(file_path) as img:
#             width, height = img.size
#             format = img.format
#             mode = img.mode
#             return {
#                 'Width': str(width),
#                 'Height': str(height),
#                 'Format': format,
#                 'ColorMode': mode
#             }
#     except Exception as e:
#         print(f"Error reading image metadata: {str(e)}")
#         return {}
#
#
# def upload_files_to_s3(local_folder_path):
#     s3 = boto3.client('s3',
#                       aws_access_key_id=ACCESS_KEY,
#                       aws_secret_access_key=SECRET_KEY)
#
#     # Define file type to S3 bucket mapping
#     bucket_mapping = {
#         'image': {
#             'extensions': ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'],
#             'bucket': S3_IMAGE_BUCKET,
#             's3_prefix': 'web_sources/enterprise/extracted_images'
#         },
#         'markdown': {
#             'extensions': ['md', 'markdown'],
#             'bucket': S3_MARKDOWN_BUCKET,
#             's3_prefix': 'web_sources/enterprise/markdown_files'
#         },
#         'raw': {
#             'extensions': ['csv', 'txt', 'json', 'xml', 'log'],
#             'bucket': S3_RAW_BUCKET,
#             's3_prefix': 'web_sources/enterprise/raw_files'
#         }
#     }
#
#     for root, dirs, files in os.walk(local_folder_path):
#         for file in files:
#             local_file_path = os.path.join(root, file)
#             file_ext = os.path.splitext(file)[1][1:].lower()
#
#             # Determine the appropriate bucket and prefix
#             upload_config = None
#             for file_type, config in bucket_mapping.items():
#                 if file_ext in config['extensions']:
#                     upload_config = config
#                     break
#
#             # If no specific bucket found, use raw bucket as default
#             if upload_config is None:
#                 upload_config = bucket_mapping['raw']
#
#             # Create S3 key with prefix structure
#             relative_path = os.path.relpath(local_file_path, local_folder_path)
#             s3_key = os.path.join(upload_config['s3_prefix'], relative_path).replace("\\", "/")
#
#             # Prepare metadata
#             metadata = {
#                 'FileType': file_type,
#                 'Source': os.path.basename(root),
#                 'UploadDate': datetime.datetime.now().isoformat(),
#                 'OriginalFilename': file,
#                 'FileSize': str(os.path.getsize(local_file_path)),
#                 'ContentType': f"application/{file_ext}"
#             }
#
#             # Add image-specific metadata for image files
#             if file_ext in bucket_mapping['image']['extensions']:
#                 metadata.update(get_image_metadata(local_file_path))
#
#             # Add custom tags for improved searchability
#             tags = {
#                 'Project': 'WebScraper',
#                 'Category': 'EnterpriseFiles',
#                 'Source': 'OracleSQL'
#             }
#
#             try:
#                 # Upload file with metadata
#                 s3.upload_file(
#                     Filename=local_file_path,
#                     Bucket=upload_config['bucket'],
#                     Key=s3_key,
#                     ExtraArgs={
#                         "Metadata": metadata,
#                         "ServerSideEncryption": "AES256",
#                         "ContentType": metadata['ContentType']
#                     }
#                 )
#
#                 # Add tags to the uploaded object
#                 s3.put_object_tagging(
#                     Bucket=upload_config['bucket'],
#                     Key=s3_key,
#                     Tagging={'TagSet': [{'Key': k, 'Value': v} for k, v in tags.items()]}
#                 )
#
#                 print(f"Uploaded {file} to S3 bucket {upload_config['bucket']} as {s3_key} with metadata and tags")
#             except Exception as e:
#                 print(f"Error uploading {file}: {str(e)}")
#
#
# def main():
#     local_folder_path = r'C:\Users\Dhrumil Patel\PycharmProjects\assignment1\output-test\extractedOpnSrc_20250129_131721'
#     upload_files_to_s3(local_folder_path)
#
#
# if __name__ == "__main__":
#     main()
