
# import os
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import FileResponse
# from pydantic import BaseModel
# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime
# from urllib.parse import urljoin
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse

# # Initialize FastAPI app
# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Diffbot API token
# API_TOKEN = 'da8d9ca627aa4fe622b5b0c45f08105c'

# # Directory to store images
# IMAGE_DIR = "downloaded_images"
# if not os.path.exists(IMAGE_DIR):
#     os.makedirs(IMAGE_DIR)

# class URLRequest(BaseModel):
#     url: str

# @app.post("/scrape-open-source/")
# async def scrape_open_source(request: URLRequest):
#     """Scrape website using BeautifulSoup"""
#     try:
#         # Add more robust headers
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#             'Accept-Language': 'en-US,en;q=0.5',
#             'Connection': 'keep-alive',
#         }
        
#         print(f"Fetching URL: {request.url}")  # Debug print
        
#         # Fetch the webpage with a timeout
#         response = requests.get(request.url, headers=headers, timeout=10)
#         response.raise_for_status()

#         print("Response received, parsing content...")  # Debug print
        
#         # Parse the webpage
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Extract content
#         content = {
#             'title': soup.title.string if soup.title else "No title found",
#             'paragraphs': [],
#             'links': [],
#             'images': []
#         }

#         # Extract paragraphs (more robust)
#         for p in soup.find_all(['p', 'div', 'article']):
#             text = p.get_text().strip()
#             if text and len(text) > 20:  # Only add substantial paragraphs
#                 content['paragraphs'].append(text)

#         # Extract links
#         for a in soup.find_all('a', href=True):
#             href = a['href']
#             text = a.get_text().strip() or href
#             if href.startswith(('http', 'https')):
#                 content['links'].append({
#                     'text': text[:100],  # Limit text length
#                     'url': href
#                 })

#         # Extract images
#         for img in soup.find_all('img', src=True):
#             src = img['src']
#             if not src.startswith(('http', 'https')):
#                 src = urljoin(request.url, src)
#             alt = img.get('alt', 'No description available')
#             content['images'].append({
#                 'src': src,
#                 'alt': alt[:100]  # Limit alt text length
#             })

#         print(f"Content extracted: {len(content['paragraphs'])} paragraphs, {len(content['links'])} links, {len(content['images'])} images")  # Debug print

#         # Limit the amount of content to prevent overload
#         content['paragraphs'] = content['paragraphs'][:20]  # Limit to 20 paragraphs
#         content['links'] = content['links'][:20]  # Limit to 20 links
#         content['images'] = content['images'][:10]  # Limit to 10 images

#         return JSONResponse(content)
        
#     except requests.RequestException as e:
#         print(f"Request error: {str(e)}")  # Debug print
#         raise HTTPException(status_code=500, detail=f"Error fetching URL: {str(e)}")
#     except Exception as e:
#         print(f"Processing error: {str(e)}")  # Debug print
#         raise HTTPException(status_code=500, detail=f"Error processing content: {str(e)}")




# @app.post("/scrape_article-enterprise/")
# async def scrape_article_enterprise(request: URLRequest):
#     """Scrape article using Diffbot API"""
#     try:
#         api_endpoint = f'https://api.diffbot.com/v3/article?token={API_TOKEN}&url={request.url}'
#         response = requests.get(api_endpoint)
        
#         if response.status_code != 200:
#             raise HTTPException(status_code=response.status_code, detail="Failed to fetch article")
            
#         data = response.json()
#         if not data.get('objects'):
#             raise HTTPException(status_code=404, detail="No content found")
            
#         article = data['objects'][0]
        
#         # Create markdown content
#         md_content = "# Article Content\n\n"
        
#         if article.get('title'):
#             md_content += f"## {article['title']}\n\n"
            
#         if article.get('text'):
#             md_content += article['text'] + "\n\n"
            
#         if article.get('images'):
#             md_content += "## Images\n\n"
#             for img in article['images']:
#                 if img.get('url'):
#                     md_content += f"![{img.get('title', 'Image')}]({img['url']})\n\n"
                    
#         # Save to file
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"article_content_{timestamp}.md"
        
#         with open(filename, 'w', encoding='utf-8') as f:
#             f.write(md_content)
            
#         return FileResponse(filename, media_type='text/markdown', filename=filename)
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8080)

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import boto3
import json
from dotenv import load_dotenv

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

# Diffbot API token
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
                    # Determine image extension
                    img_ext = src.split('.')[-1].lower()
                    if img_ext not in ['jpg', 'jpeg', 'png', 'gif']:
                        img_ext = 'jpg'
                    
                    # Store image in S3
                    img_key = f"web_sources/open_source/extracted_images/{document_id}/image_{idx}.{img_ext}"
                    s3_client.put_object(
                        Bucket=AWS_S3_BUCKET_NAME,
                        Key=img_key,
                        Body=img_response.content,
                        ContentType=f'image/{img_ext}',
                        # ACL='public-read'
                    )
                    
                    # Add image to content with S3 URL
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
            ContentType='application/json',
            # ACL='public-read'
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

# @app.post("/scrape_article-enterprise/")
# async def scrape_article_enterprise(request: URLRequest):
#     """Scrape article using Diffbot API"""
#     try:
#         document_id = datetime.now().strftime("%Y%m%d_%H%M%S")
#         api_endpoint = f'https://api.diffbot.com/v3/article?token={API_TOKEN}&url={request.url}'
#         response = requests.get(api_endpoint)
        
#         if response.status_code != 200:
#             raise HTTPException(status_code=response.status_code, detail="Failed to fetch article")
            
#         data = response.json()
#         if not data.get('objects'):
#             raise HTTPException(status_code=404, detail="No content found")
            
#         article = data['objects'][0]
        
#         # Prepare content for storage
#         content = {
#             'title': article.get('title', ''),
#             'text': article.get('text', ''),
#             'images': []
#         }

#         # Process and store images
#         for idx, img in enumerate(article.get('images', [])):
#             if img.get('url'):
#                 try:
#                     img_response = requests.get(img['url'])
#                     if img_response.status_code == 200:
#                         img_ext = img['url'].split('.')[-1].lower()
#                         if img_ext not in ['jpg', 'jpeg', 'png', 'gif']:
#                             img_ext = 'jpg'
                        
#                         img_key = f"web_sources/enterprise/extracted_images/{document_id}/image_{idx}.{img_ext}"
#                         s3_client.put_object(
#                             Bucket=AWS_S3_BUCKET_NAME,
#                             Key=img_key,
#                             Body=img_response.content,
#                             ContentType=f'image/{img_ext}',
#                             # ACL='public-read'
#                         )
                        
#                         content['images'].append({
#                             'src': f"https://{AWS_S3_BUCKET_NAME}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{img_key}",
#                             'title': img.get('title', f'Image {idx + 1}')
#                         })
#                 except Exception as e:
#                     print(f"Error processing image {img['url']}: {e}")

#         # Store content in S3
#         content_key = f"web_sources/enterprise/extracted_markdown/{document_id}/content.json"
#         s3_client.put_object(
#             Bucket=AWS_S3_BUCKET_NAME,
#             Key=content_key,
#             Body=json.dumps(content),
#             ContentType='application/json',
#             # ACL='public-read'
#         )

#         return JSONResponse(content)
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape_article-enterprise/")
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
        
        # Prepare content for storage
        content = {
            'title': article.get('title', ''),
            'paragraphs': article.get('text', '').split('\n'),  # Split text into paragraphs
            'links': [],  # Initialize links list
            'images': []
        }

        # Extract links if available
        if 'links' in article:
            content['links'] = [
                {
                    'text': link.get('anchor', ''),
                    'url': link.get('href', '')
                }
                for link in article.get('links', [])
                if link.get('href') and link.get('anchor')
            ]

        # Process and store images
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        for idx, img in enumerate(article.get('images', [])):
            if img.get('url'):
                try:
                    img_response = requests.get(img['url'], headers=headers, timeout=10)
                    if img_response.status_code == 200:
                        # Determine image extension from URL or content type
                        content_type = img_response.headers.get('content-type', '')
                        if 'png' in content_type:
                            img_ext = 'png'
                        elif 'gif' in content_type:
                            img_ext = 'gif'
                        else:
                            img_ext = 'jpg'  # default to jpg
                        
                        # Generate image key
                        img_key = f"web_sources/enterprise/extracted_images/{document_id}/image_{idx}.{img_ext}"
                        
                        # Store image in S3
                        s3_client.put_object(
                            Bucket=AWS_S3_BUCKET_NAME,
                            Key=img_key,
                            Body=img_response.content,
                            ContentType=f'image/{img_ext}'
                        )
                        
                        # Add image to content with S3 URL
                        content['images'].append({
                            'src': f"https://{AWS_S3_BUCKET_NAME}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{img_key}",
                            'alt': img.get('title', ''),
                            'caption': img.get('caption', '')
                        })
                        print(f"Successfully stored image {idx + 1}")
                except Exception as e:
                    print(f"Error processing image {img['url']}: {e}")
                    continue

        # Store content in S3
        content_key = f"web_sources/enterprise/extracted_markdown/{document_id}/content.json"
        s3_client.put_object(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=content_key,
            Body=json.dumps(content),
            ContentType='application/json'
        )

        print(f"Processed content with {len(content['images'])} images")
        return JSONResponse(content)
        
    except Exception as e:
        print(f"Error in enterprise scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)