

# from PyPDF2 import PdfReader
# import fitz
# import pandas as pd
# import camelot
# import os
# from datetime import datetime
# from docling.document_converter import DocumentConverter 
# from pathlib import Path

# def extract_pdf_content(pdf_path):
#     # Create timestamped output directory
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     base_output_dir = Path("output")  # Base output directory
#     output_dir = base_output_dir / f"extractedOpnSrc_{timestamp}"  # Create unique subdirectory
#     output_dir.mkdir(parents=True, exist_ok=True)
    
#     # Initialize dictionary to store all extracted content
#     content = {
#         'text': [],
#         'images': [],
#         'tables': []
#     }
    
#     # Extract text using PyPDF2
#     pdf = PdfReader(pdf_path)
#     for page in pdf.pages:
#         content['text'].append(page.extract_text())
    
#     # Save text
#     text_path = output_dir / "extracted_text.txt"
#     with open(text_path, "w", encoding="utf-8") as f:
#         f.write("\n".join(content['text']))
    
#     # Extract and save images using PyMuPDF
#     doc = fitz.open(pdf_path)
#     for page_num in range(len(doc)):
#         page = doc[page_num]
#         images = page.get_images(full=True)
        
#         for img_index, img in enumerate(images):
#             xref = img[0]
#             base_image = doc.extract_image(xref)
#             image_bytes = base_image["image"]
            
#             # Save image in output directory
#             image_filename = f"image_page{page_num + 1}_{img_index + 1}.{base_image['ext']}"
#             image_path = output_dir / image_filename
#             with open(image_path, "wb") as image_file:
#                 image_file.write(image_bytes)
#             content['images'].append(image_filename)
    
#     # Extract and save tables using Camelot
#     try:
#         tables = camelot.read_pdf(pdf_path, pages="all")
#         for idx, table in enumerate(tables):
#             table_path = output_dir / f"table_{idx + 1}.csv"
#             table.df.to_csv(table_path, index=False)
#             content['tables'].append(f"table_{idx + 1}.csv")
#     except Exception as e:
#         print(f"Error extracting tables: {e}")
    
#     # Convert PDF to Markdown format using Docling's DocumentConverter
#     try:
#         doc_converter = DocumentConverter()
#         conversion_result = doc_converter.convert(pdf_path)
        
#         # Export the converted document to Markdown format
#         markdown_content = conversion_result.document.export_to_markdown()
        
#         # Save the Markdown file
#         markdown_path = output_dir / "extracted_content.md"
#         with open(markdown_path, "w", encoding="utf-8") as md_file:
#             md_file.write(markdown_content)
        
#         print(f"Markdown file created at: {markdown_path}")
    
#     except Exception as e:
#         print(f"Error converting PDF to Markdown: {e}")
    
#     return content, output_dir

# # Specify the input PDF path
# pdf_path = "C:/PDF to be Extracted/MergedPDF.pdf"

# # Extract content
# content, output_directory = extract_pdf_content(pdf_path)
# print(f"Content extracted to: {output_directory}")
# print("Test")

import os
import PyPDF2
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime

def extract_pdf_content(pdf_path):
    try:
        # Create output directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"output/opensource_pdf_{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize content dictionary
        content = {
            'text': [],
            'images': [],
            'tables': []
        }

        # Extract text using PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                content['text'].append(page.extract_text())

        # Extract images using PyMuPDF
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Save image
                image_path = output_dir / f"image_p{page_num + 1}_{img_index + 1}.png"
                with open(image_path, 'wb') as img_file:
                    img_file.write(image_bytes)
                content['images'].append(str(image_path))

        return content, str(output_dir)

    except Exception as e:
        print(f"Error extracting PDF content: {str(e)}")
        raise