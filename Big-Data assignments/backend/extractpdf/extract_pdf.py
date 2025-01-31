"""
 Copyright 2024 Adobe
 All Rights Reserved.

 NOTICE: Adobe permits you to use, modify, and distribute this file in
 accordance with the terms of the Adobe license agreement accompanying it.
"""

# Initialize the logger
import logging
import os
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
import json
import zipfile
import os
import pandas as pd
from tabulate import tabulate
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

# Initialize the logger
logging.basicConfig(level=logging.INFO)
 
 
os.environ["PDF_SERVICES_CLIENT_ID"] = "4953843489324519ba1dc490a33002c7"
os.environ["PDF_SERVICES_CLIENT_SECRET"] = "p8e-cSgcGP1K5cL2IEYT4rCVdMANej-KIFPo"
 
#
# This sample illustrates how to extract Text, Table Elements Information from PDF along with renditions of Figure,
# Table elements.
#
# Refer to README.md for instructions on how to run the samples & understand output zip file.
#
class ExtractTextTableInfoWithFiguresTablesRenditionsFromPDF:
    def __init__(self):
        try:
            file = open(r"C:\Users\Dhrumil Patel\Downloads\MergedPDF 1.pdf", 'rb')
            input_stream = file.read()
            file.close()
 
            # Initial setup, create credentials instance
            credentials = ServicePrincipalCredentials(
                client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
                client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')
            )
 
            # Creates a PDF Services instance
            pdf_services = PDFServices(credentials=credentials)
 
            # Creates an asset(s) from source file(s) and upload
            input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)
 
            # Create parameters for the job
            extract_pdf_params = ExtractPDFParams(
                elements_to_extract=[ExtractElementType.TEXT, ExtractElementType.TABLES],
                elements_to_extract_renditions=[ExtractRenditionsElementType.TABLES, ExtractRenditionsElementType.FIGURES],
            )
 
            # Creates a new job instance
            extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)
 
            # Submit the job and gets the job result
            location = pdf_services.submit(extract_pdf_job)
            pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)
 
            # Get content from the resulting asset(s)
            result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)
 
            # Creates an output stream and copy stream asset's content to it
            output_file_path = self.create_output_file_path()
            with open(output_file_path, "wb") as file:
                file.write(stream_asset.get_input_stream())
 
            output_markdown = "C:/Assignment1BigData/output/converted_document.md"


 
            self.convert_extracted_pdf_to_markdown(output_file_path, output_markdown)
 
        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            logging.exception(f'Exception encountered while executing operation: {e}')

    def upload_to_s3(self, file_path, bucket_name, s3_key, content_type):
        s3_client = boto3.client(
            's3',
            aws_access_key_id='AKIA2MNVL2SX4KKVXNEI',
            aws_secret_access_key='XGibeH9mbCCZU2k4vGEUA+iHxrjcKEvEc4My2Y6Q',
            region_name='us-east-1'  # Replace with your preferred region if different
        )
        try:
            s3_client.upload_file(
                file_path,
                bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            logging.info(f"File uploaded successfully to {s3_key}")
        except ClientError as e:
            logging.error(f"Error uploading file to S3: {e}")

    def convert_extracted_pdf_to_markdown(self,zip_file_path, output_markdown_path):
        # Create a temporary directory to extract files
        temp_dir = "temp_extracted"
        os.makedirs(temp_dir, exist_ok=True)
   
        markdown_content = []
   
        try:
            # Extract the zip file
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Read the structuredData.json file
            with open(os.path.join(temp_dir, 'structuredData.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
       
            # Process each element in order
            for element in data['elements']:
                element_type = element.get('Path', '')
           
                # Process text elements
                if element.get('Text'):
                    markdown_content.append(element['Text'])
                    markdown_content.append('\n\n')
           
                # Process headings
                elif element_type.startswith('H'):
                    level = element_type[1]  # Get heading level (1-6)
                    heading_text = element.get('Text', '')
                    markdown_content.append(f"{'#' * int(level)} {heading_text}\n\n")
           
                # Process tables
                elif element.get('TableData'):
                    table_id = element.get('TableID')
                    csv_file = os.path.join(temp_dir, f'tables/table_{table_id}.csv')
               
                    if os.path.exists(csv_file):
                        # Read CSV and convert to markdown table
                        df = pd.read_csv(csv_file)
                        table_markdown = df.to_markdown(index=False)
                        markdown_content.append(table_markdown)
                        markdown_content.append('\n\n')
           
                # Process images
                elif element.get('FilePath', '').endswith(('.png', '.jpg', '.jpeg')):
                    image_path = element.get('FilePath')
                    image_name = os.path.basename(image_path)
                    # Copy image to output directory and create markdown reference
                    markdown_content.append(f"![{image_name}](images/{image_name})\n\n")
   
            # Combine all content
            final_markdown = ''.join(markdown_content)
       
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_markdown_path)
            os.makedirs(output_dir, exist_ok=True)
       
            # Save the markdown file
            with open(output_markdown_path, 'w', encoding='utf-8') as f:
                f.write(final_markdown)
       
            # Create images directory and copy images
            images_dir = os.path.join(output_dir, 'images')
            os.makedirs(images_dir, exist_ok=True)
       
            # Copy all images to the images directory
            for file in os.listdir(os.path.join(temp_dir, 'figures')):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    src = os.path.join(temp_dir, 'figures', file)
                    dst = os.path.join(images_dir, file)
                    with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst:
                        f_dst.write(f_src.read())
       
            print(f"Markdown file created successfully at: {output_markdown_path}")

            # Upload markdown file to S3
            bucket_name = "web-scraper-storage-sahil"  # Replace with your actual bucket name
            self.upload_to_s3(
                output_markdown_path,
                bucket_name,
                f"web_sources/enterprise/markdown_files/{os.path.basename(output_markdown_path)}",
                'text/markdown'
            )

            # Upload images to S3
            for file in os.listdir(images_dir):
                file_path = os.path.join(images_dir, file)
                file_ext = os.path.splitext(file)[1].lower()
                s3_key = f"web_sources/enterprise/extracted_images/{file}"
                content_type = f'image/{file_ext[1:]}'
                self.upload_to_s3(file_path, bucket_name, s3_key, content_type)

            # Upload CSV files to S3
            tables_dir = os.path.join(temp_dir, 'tables')
            for file in os.listdir(tables_dir):
                if file.endswith('.csv'):
                    file_path = os.path.join(tables_dir, file)
                    s3_key = f"web_sources/enterprise/extracted_tables/{file}"
                    self.upload_to_s3(file_path, bucket_name, s3_key, 'text/csv')

            print("All files uploaded to S3 successfully")

        except Exception as e:
            print(f"Error converting to markdown or uploading to S3: {str(e)}")


        finally:
            # Cleanup: Remove temporary directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
   
   

   
    # Generates a string containing a directory structure and file name for the output file
    @staticmethod
    def create_output_file_path() -> str:
        now = datetime.now()
        time_stamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        os.makedirs("output/ExtractEnterprise", exist_ok=True)
        return f"output/ExtractEnterprise/extract{time_stamp}.zip"
   
   
 
 
if __name__ == "__main__":
    ExtractTextTableInfoWithFiguresTablesRenditionsFromPDF()