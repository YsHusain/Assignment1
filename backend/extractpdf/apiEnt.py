from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
import tempfile
import shutil
import os
from datetime import datetime
from typing import Dict

# Import the enterprise processor class
from extract_pdf import ExtractTextTableInfoWithFiguresTablesRenditionsFromPDF

app = FastAPI()

@app.post("/process-pdf/enterprise")
async def process_pdf_enterprise(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Create temporary file to store uploaded PDF
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / "temp_input.pdf"
        
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process PDF using enterprise extractor
        processor = ExtractTextTableInfoWithFiguresTablesRenditionsFromPDF()
        output_path = processor.create_output_file_path()
        
        # Convert to markdown
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        markdown_output = f"output/enterprise_converted_{timestamp}.md"
        processor.convert_extracted_pdf_to_markdown(output_path, markdown_output)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return {
            "filename": file.filename,
            "output_zip": output_path,
            "markdown_output": markdown_output,
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}