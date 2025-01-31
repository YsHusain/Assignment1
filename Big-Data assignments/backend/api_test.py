import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import boto3
import json
from dotenv import load_dotenv
import tempfile
import shutil
from pathlib import Path
from typing import Dict

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extractpdf.extract_pdf import ExtractTextTableInfoWithFiguresTablesRenditionsFromPDF
from extractpdf.ExtractPDF import extract_pdf_content

# Then import your modules


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
API_TOKEN = os.getenv("DIFFBOT_API_TOKEN")

class URLRequest(BaseModel):
    url: str

@app.post("/scrape-open-source/")
async def scrape_open_source(request: URLRequest):
    """Scrape website using BeautifulSoup"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        print(f"Fetching URL: {request.url}")
        
        response = requests.get(request.url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print("Response received, parsing content...")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Generate unique document ID
        document_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Extract content
        content = {
            'title': soup.title.string if soup.title else "No title found",
            'paragraphs': [],
            'links': [],
            'images': []
        }

        # Extract paragraphs
        for p in soup.find_all(['p', 'div', 'article']):
            text = p.get_text().strip()
            if text and len(text) > 20:
                content['paragraphs'].append(text)

        # Extract links
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text().strip() or href
            if href.startswith(('http', 'https')):
                content['links'].append({
                    'text': text[:100],
                    'url': href
                })

        # Extract and store images
        for idx, img in enumerate(soup.find_all('img', src=True)):
            src = img['src']
            if not src.startswith(('http', 'https')):
                src = urljoin(request.url, src)
            
            try:
                img_response = requests.get(src, headers=headers, timeout=10)
                if img_response.status_code == 200:
                    img_ext = src.split('.')[-1].lower()
                    if img_ext not in ['jpg', 'jpeg', 'png', 'gif']:
                        img_ext = 'jpg'
                    
                    img_key = f"web_sources/open_source/extracted_images/{document_id}/image_{idx}.{img_ext}"
                    s3_client.put_object(
                        Bucket=AWS_S3_BUCKET_NAME,
                        Key=img_key,
                        Body=img_response.content,
                        ContentType=f'image/{img_ext}'
                    )
                    
                    content['images'].append({
                        'src': f"https://{AWS_S3_BUCKET_NAME}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{img_key}",
                        'alt': img.get('alt', f'Image {idx + 1}')
                    })
            except Exception as e:
                print(f"Error processing image {src}: {e}")

        # Store content in S3
        content_key = f"web_sources/open_source/extracted_markdown/{document_id}/content.json"
        s3_client.put_object(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=content_key,
            Body=json.dumps(content),
            ContentType='application/json'
        )

        # Limit content for response
        content['paragraphs'] = content['paragraphs'][:20]
        content['links'] = content['links'][:20]
        content['images'] = content['images'][:10]

        return JSONResponse(content)
        
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching URL: {str(e)}")
    except Exception as e:
        print(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing content: {str(e)}")

@app.post("/scrape-article-enterprise/")
async def scrape_article_enterprise(request: URLRequest):
    """Scrape article using Diffbot API"""
    try:
        document_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        api_endpoint = f'https://api.diffbot.com/v3/article?token={API_TOKEN}&url={request.url}'
        response = requests.get(api_endpoint)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch article")
            
        data = response.json()
        if not data.get('objects'):
            raise HTTPException(status_code=404, detail="No content found")
            
        article = data['objects'][0]
        
        content = {
            'title': article.get('title', ''),
            'paragraphs': article.get('text', '').split('\n'),
            'links': [],
            'images': []
        }

        if 'links' in article:
            content['links'] = [
                {
                    'text': link.get('anchor', ''),
                    'url': link.get('href', '')
                }
                for link in article.get('links', [])
                if link.get('href') and link.get('anchor')
            ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        for idx, img in enumerate(article.get('images', [])):
            if img.get('url'):
                try:
                    img_response = requests.get(img['url'], headers=headers, timeout=10)
                    if img_response.status_code == 200:
                        content_type = img_response.headers.get('content-type', '')
                        if 'png' in content_type:
                            img_ext = 'png'
                        elif 'gif' in content_type:
                            img_ext = 'gif'
                        else:
                            img_ext = 'jpg'
                        
                        img_key = f"web_sources/enterprise/extracted_images/{document_id}/image_{idx}.{img_ext}"
                        
                        s3_client.put_object(
                            Bucket=AWS_S3_BUCKET_NAME,
                            Key=img_key,
                            Body=img_response.content,
                            ContentType=f'image/{img_ext}'
                        )
                        
                        content['images'].append({
                            'src': f"https://{AWS_S3_BUCKET_NAME}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{img_key}",
                            'alt': img.get('title', ''),
                            'caption': img.get('caption', '')
                        })
                except Exception as e:
                    print(f"Error processing image {img['url']}: {e}")
                    continue

        content_key = f"web_sources/enterprise/extracted_markdown/{document_id}/content.json"
        s3_client.put_object(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=content_key,
            Body=json.dumps(content),
            ContentType='application/json'
        )

        return JSONResponse(content)
        
    except Exception as e:
        print(f"Error in enterprise scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-pdf/enterprise")
async def process_pdf_enterprise(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / "temp_input.pdf"
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        processor = ExtractTextTableInfoWithFiguresTablesRenditionsFromPDF()
        output_path = processor.create_output_file_path()
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        markdown_output = f"output/enterprise_converted_{timestamp}.md"
        processor.convert_extracted_pdf_to_markdown(output_path, markdown_output)
        
        return {
            "filename": file.filename,
            "output_zip": output_path,
            "markdown_output": markdown_output,
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/process-pdf/opensource")
async def process_pdf_opensource(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        content, output_dir = extract_pdf_content(temp_path)
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)