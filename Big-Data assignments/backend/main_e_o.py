import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

from typing import List, Optional
from fastapi import Query 


import boto3

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")


PORT = int(os.getenv("PORT", 8080))
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Diffbot API token
API_TOKEN = 'da8d9ca627aa4fe622b5b0c45f08105c'

# Directory to store images
IMAGE_DIR = "downloaded_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Define the input model for receiving URL data
class URLRequest(BaseModel):
    url: str

def upload_to_s3(content, key, content_type='text/plain'):
    """Upload content to S3"""
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=content,
            ContentType=content_type,
            ACL='public-read'
        )
        return f"https://{BUCKET_NAME}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{key}"
    except Exception as e:
        print(f"S3 Upload Error: {str(e)}")
        return None
    
def save_image_to_s3(img_url, headers, session_id, source_type):
    """Save image to S3 and return the URL"""
    try:
        img_response = requests.get(img_url, headers=headers)
        img_response.raise_for_status()

        # Get image extension
        img_name = os.path.basename(img_url.split('?')[0]) or "image.jpg"
        img_ext = img_name.split('.')[-1].lower()

        # Generate S3 key
        s3_key = f"web_sources/{source_type}/extracted_images/{session_id}_{img_name}"
        
        # Upload to S3
        img_url = upload_to_s3(
            img_response.content,
            s3_key,
            f'image/{img_ext}'
        )
        
        return img_url
    except Exception as e:
        print(f"Error saving image {img_url}: {e}")
        return None

def save_image(img_url, headers, image_folder, md_file):
    """Save an image from a URL to the specified folder and log in the markdown file."""
    try:
        img_response = requests.get(img_url, headers=headers)
        img_response.raise_for_status()

        # Extract image name from URL or use a default name
        img_name = os.path.basename(img_url.split('?')[0]) or "image.jpg"

        # Ensure the image folder exists
        os.makedirs(image_folder, exist_ok=True)

        # Save the image locally
        img_path = os.path.join(image_folder, img_name)
        with open(img_path, 'wb') as f:
            f.write(img_response.content)

        # Write the markdown image reference with relative path
        md_file.write(f"![{img_name}]({image_folder}/{img_name})\n")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image {img_url}: {e}")



# Function to scrape websites using BeautifulSoup
def scrape_website(url):
    """Scrape the given website for text, hyperlinks, images, tables, and charts, saving to a markdown file."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        md_filename = "scraped_output.md"
        with open(md_filename, "w", encoding="utf-8") as md_file:
            md_file.write(f"# Scraped Data from {url}\n\n")
            page_title = soup.title.string if soup.title else "No title found"
            md_file.write(f"## Page Title\n\n{page_title}\n\n")

            md_file.write("## Hyperlinks on the page:\n\n")
            for link in soup.find_all('a', href=True):
                md_file.write(f"- [{link['href']}]({link['href']})\n")

            md_file.write("\n## Paragraphs on the page:\n\n")
            for paragraph in soup.find_all('p'):
                md_file.write(f"{paragraph.text.strip()}\n\n")

            md_file.write("\n## Images on the page:\n\n")
            image_folder = IMAGE_DIR
            os.makedirs(image_folder, exist_ok=True)
            for img in soup.find_all('img'):
                img_url = img.get('src')
                if img_url:
                    full_img_url = urljoin(url, img_url)
                    save_image(full_img_url, headers, image_folder, md_file)

            md_file.write("\nScraping completed!\n")
        return md_filename
    except requests.exceptions.RequestException as e:
        print("Error fetching the website:", e)
        return None


# Endpoint to scrape an open-source website (URL input required)
@app.post("/scrape-open-source/")
async def scrape_open_source(request: URLRequest):
    """Scrape the provided website, generate the file, and return the file."""
    file_name = scrape_website(request.url)
    if file_name:
        file_path = os.path.join(os.getcwd(), file_name)
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    else:
        raise HTTPException(status_code=400, detail="Error scraping the website.")


# Endpoint to scrape an article via Diffbot API (Enterprise)
@app.post("/scrape_article-enterprise/")
async def scrape_article(request: URLRequest):
    url = request.url

    # Diffbot API call to fetch article
    api_endpoint = f'https://api.diffbot.com/v3/article?token={API_TOKEN}&url={url}'
    response = requests.get(api_endpoint)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch article content")

    data = response.json()

    # Extract article content and images
    article_content = data.get('objects', [])[0].get('text', '')
    images = data.get('objects', [])[0].get('images', [])

    # Generate Markdown content
    md_content = "# Article Content\n\n"
    md_content += "## Content\n\n"
    md_content += article_content + "\n\n"

    # Add images to Markdown content
    image_folder = 'downloaded_images'
    os.makedirs(image_folder, exist_ok=True)
    
    if images:
        md_content += "## Images\n\n"
        for idx, image in enumerate(images):
            image_url = image.get('url')
            alt_text = image.get('title', f'Image {idx + 1}')

            try:
                # Attempt to download and save image locally
                img_response = requests.get(image_url)
                img_response.raise_for_status()

                image_extension = image_url.split('.')[-1]
                image_filename = f"image_{idx + 1}.{image_extension}"
                image_path = os.path.join(image_folder, image_filename)

                with open(image_path, 'wb') as img_file:
                    img_file.write(img_response.content)

                # Add image to Markdown content with local path
                md_content += f"![{alt_text}]({image_path})\n\n"
            except requests.exceptions.RequestException as e:
                print(f"Error downloading image {image_url}: {e}")
                md_content += f"![{alt_text}]({image_url})\n\n"  # Fallback to URL if download fails

    # Generate a unique filename using the current date and time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    md_filename = f"scraped_article_{timestamp}.md"

    # Save the Markdown content to a file
    with open(md_filename, 'w', encoding='utf-8') as md_file:
        md_file.write(md_content)

    # Return the generated Markdown file as a download
    return FileResponse(md_filename, media_type='application/octet-stream', filename=md_filename)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)




