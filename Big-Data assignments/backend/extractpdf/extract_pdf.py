# """
#  Copyright 2024 Adobe
#  All Rights Reserved.
#
#  NOTICE: Adobe permits you to use, modify, and distribute this file in
#  accordance with the terms of the Adobe license agreement accompanying it.
# """
#
# Initialize the logger
import csv
import logging
import os
from base64 import b64decode

import boto3
from datetime import datetime

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_renditions_element_type import \
    ExtractRenditionsElementType
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult
from PIL import Image
import json
import zipfile
import os
import pandas as pd
from google.ai.generativelanguage_v1.types import content
from tabulate import tabulate
from pathlib import Path
from datetime import datetime

# # Initialize the logger
# logging.basicConfig(level=logging.INFO)
#
#
os.environ["PDF_SERVICES_CLIENT_ID"] = "4953843489324519ba1dc490a33002c7"
os.environ["PDF_SERVICES_CLIENT_SECRET"] = "p8e-cSgcGP1K5cL2IEYT4rCVdMANej-KIFPo"


# AWS Credentials and S3 Bucket
ACCESS_KEY = 'AKIA2MNVL2SX4KKVXNEI'
SECRET_KEY = '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'
S3_BUCKET = 'web-scraper-storage-sahil'

class PDFProcessor:

    def __init__(self):
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        logging.basicConfig(level=logging.INFO)

    def process_pdf(self, input_pdf_path):
        try:
            logging.info(f"Starting to process PDF: {input_pdf_path}")

            # Read the input PDF file
            with open(input_pdf_path, 'rb') as file:
                input_stream = file.read()

            logging.info("PDF file read successfully")

            # Initial setup, create credentials instance
            credentials = ServicePrincipalCredentials(
                client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
                client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')
            )

            # Creates a PDF Services instance
            pdf_services = PDFServices(credentials=credentials)

            # Creates an asset from source file and upload
            input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)

            # Create parameters for the job
            extract_pdf_params = ExtractPDFParams(
                elements_to_extract=[ExtractElementType.TEXT, ExtractElementType.TABLES],
                elements_to_extract_renditions=[ExtractRenditionsElementType.TABLES,
                                                ExtractRenditionsElementType.FIGURES,
                                                ExtractRenditionsElementType.IMAGES]
            )

            # Creates a new job instance
            extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)

            # Submit the job and get the job result
            location = pdf_services.submit(extract_pdf_job)
            pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)

            pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)
            result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
            content_json = pdf_services.get_content(result_asset).get_input_stream().read()

            # Save JSON output for debug
            extracted_content_path = os.path.join(self.output_dir, "extracted_content.json")
            with open(extracted_content_path, "wb") as json_file:
                json_file.write(content_json)

            # Parse the JSON for extracting text, tables, and images
            extracted_content = json.loads(content_json.decode("utf-8"))

            # Process each content element type
            self.save_markdown(extracted_content)
            self.save_images(extracted_content)
            self.save_csv_or_txt(extracted_content)







            # Extract content from the resulting asset
            result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)

            # Write the output file
            output_file_path = self.create_output_file_path()
            with open(output_file_path, "wb") as file:
                file.write(stream_asset.get_input_stream())


            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_markdown = f"{self.output_dir}/enterprise_converted_{timestamp}.md"

            # Convert extracted PDF to Markdown and generate additional files
            self.convert_extracted_pdf_to_markdown(output_file_path, output_markdown)


            self.upload_files_to_s3(self.output_dir, prefix="web_sources/enterprise/markdown_files")

            return output_file_path, output_markdown

        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            logging.exception(f'Exception encountered while executing operation: {e}')
            raise

    def create_output_file_path(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(self.output_dir, f"processed_pdf_{timestamp}.pdf")

    def convert_extracted_pdf_to_markdown(self, input_pdf_path, output_markdown):
        # Dummy implementation for converting PDF content to Markdown
        logging.info(f"Converting extracted PDF content to Markdown: {output_markdown}")
        with open(output_markdown, "w") as md_file:
            md_file.write(f"# Extracted content from: {input_pdf_path}\n")
        logging.info("Conversion to Markdown completed.")

    def upload_files_to_s3(self, local_folder_path):
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
                    'UploadDate': datetime.now().isoformat(),
                    'OriginalFilename': file,
                    'FileSize': str(os.path.getsize(local_file_path)),
                    'ContentType': f"application/{file_ext}"
                }

                # Add image-specific metadata for image files
                if file_ext in prefix_mapping['image']['extensions']:
                    metadata.update(self.get_image_metadata(local_file_path))

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

                    logging.info(f"Uploaded {file} to S3 bucket {S3_BUCKET} as {s3_key} with metadata and tags")
                except Exception as e:
                    logging.error(f"Error uploading {file}: {str(e)}")

    def get_image_metadata(self, file_path):
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
            logging.error(f"Error reading image metadata: {str(e)}")
            return {}

    def save_images(self, extracted_content):
        image_dir = os.path.join(self.output_dir, "images")
        os.makedirs(image_dir, exist_ok=True)

        for index, element in enumerate(content.get('renditions', [])):
            if element['Type'] == 'image':
                image_data = b64decode(element['data'])
                image_path = os.path.join(image_dir, f"image_{index + 1}.png")
                with open(image_path, "wb") as img_file:
                    img_file.write(image_data)
                logging.info(f"Image saved: {image_path}")
        self.upload_files_to_s3(image_dir, prefix="web_sources/enterprise/extracted_images")

    def save_csv_or_txt(self, content):
        raw_dir = os.path.join(self.output_dir, "raw_files")
        os.makedirs(raw_dir, exist_ok=True)

        for index, table in enumerate(content.get('tables', [])):
            csv_path = os.path.join(raw_dir, f"table_{index + 1}.csv")
            with open(csv_path, "w", newline='', encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                for row in table.get('data', []):
                    writer.writerow(row)
                logging.info(f"CSV file saved: {csv_path}")
        self.upload_files_to_s3(raw_dir, prefix="web_sources/enterprise/raw_files/ExtractEnterprise")




if __name__ == "__main__":
    processor = PDFProcessor()
    input_pdf = r"C:\Users\Dhrumil Patel\Downloads\MergedPDF 1.pdf"  # Replace with actual PDF path
    try:
        output_pdf, output_md = processor.process_pdf(input_pdf)
        logging.info(f"Processing completed. Output PDF: {output_pdf}, Markdown: {output_md}")
    except Exception as e:
        logging.error(f"An error occurred during PDF processing: {e}")
