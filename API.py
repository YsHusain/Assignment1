from fastapi import FastAPI, File, UploadFile, HTTPException
from pathlib import Path
import tempfile
import os
from typing import Dict
import shutil

app = FastAPI()

# Import your existing function
from ExtractPDF import extract_pdf_content

@app.post("/process-pdf/opensource")
async def process_pdf_opensource(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Create temporary file to store uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # Process the PDF using your existing function
        content, output_dir = extract_pdf_content(temp_path)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return {
            "filename": file.filename,
            "extracted_content": {
                "text_count": len(content['text']),
                "images_count": len(content['images']),
                "tables_count": len(content['tables']),
                "output_directory": str(output_dir)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


