from PyPDF2 import PdfReader
import fitz
import pandas as pd
import camelot
import os
from datetime import datetime
from docling.document_converter import DocumentConverter
from pathlib import Path
import boto3
from PIL import Image

# AWS S3 configuration
ACCESS_KEY = 'AKIA2MNVL2SX4KKVXNEI'
SECRET_KEY = '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'
S3_BUCKET = 'web-scraper-storage-sahil'


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

            upload_config = None
            for file_type, config in prefix_mapping.items():
                if file_ext in config['extensions']:
                    upload_config = config
                    break

            if upload_config is None:
                upload_config = prefix_mapping['raw']

            relative_path = os.path.relpath(local_file_path, local_folder_path)
            s3_key = os.path.join(upload_config['s3_prefix'], relative_path).replace("\\", "/")

            metadata = {
                'FileType': file_type if 'file_type' in locals() else 'raw',
                'Source': os.path.basename(root),
                'UploadDate': datetime.now().isoformat(),
                'OriginalFilename': file,
                'FileSize': str(os.path.getsize(local_file_path)),
                'ContentType': f"application/{file_ext}"
            }

            if file_ext in prefix_mapping['image']['extensions']:
                metadata.update(get_image_metadata(local_file_path))

            tags = {
                'Project': 'WebScraper',
                'Category': 'EnterpriseFiles',
                'Source': 'OracleSQL'
            }

            try:
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

                s3.put_object_tagging(
                    Bucket=S3_BUCKET,
                    Key=s3_key,
                    Tagging={'TagSet': [{'Key': k, 'Value': v} for k, v in tags.items()]}
                )

                print(f"Uploaded {file} to S3 bucket {S3_BUCKET} as {s3_key} with metadata and tags")
            except Exception as e:
                print(f"Error uploading {file}: {str(e)}")


def extract_pdf_content(pdf_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_output_dir = Path("output")
    output_dir = base_output_dir / f"extractedOpnSrc_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    content = {
        'text': [],
        'images': [],
        'tables': []
    }

    pdf = PdfReader(pdf_path)
    for page in pdf.pages:
        content['text'].append(page.extract_text())

    text_path = output_dir / "extracted_text.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content['text']))

    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            image_filename = f"image_page{page_num + 1}_{img_index + 1}.{base_image['ext']}"
            image_path = output_dir / image_filename
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
            content['images'].append(image_filename)

    try:
        tables = camelot.read_pdf(pdf_path, pages="all")
        for idx, table in enumerate(tables):
            table_path = output_dir / f"table_{idx + 1}.csv"
            table.df.to_csv(table_path, index=False)
            content['tables'].append(f"table_{idx + 1}.csv")
    except Exception as e:
        print(f"Error extracting tables: {e}")

    try:
        doc_converter = DocumentConverter()
        conversion_result = doc_converter.convert(pdf_path)

        markdown_content = conversion_result.document.export_to_markdown()

        markdown_path = output_dir / "extracted_content.md"
        with open(markdown_path, "w", encoding="utf-8") as md_file:
            md_file.write(markdown_content)

        print(f"Markdown file created at: {markdown_path}")

    except Exception as e:
        print(f"Error converting PDF to Markdown: {e}")

    # Upload extracted files to S3
    upload_files_to_s3(str(output_dir))

    return content, output_dir


# Specify the input PDF path
pdf_path = "C:/PDF to be Extracted/MergedPDF.pdf"

# Extract content and upload to S3
content, output_directory = extract_pdf_content(pdf_path)
print(f"Content extracted to: {output_directory} and uploaded to S3")
