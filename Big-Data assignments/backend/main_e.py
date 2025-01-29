import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from datetime import datetime

# Initialize the FastAPI app
app = FastAPI()

# Your Diffbot API token
api_token = 'da8d9ca627aa4fe622b5b0c45f08105c'

# Directory to store images
image_dir = "downloaded_images"
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

# Define the input model for receiving URL data
class URLRequest(BaseModel):
    url: str

@app.post("/scrape_article/")
async def scrape_article(request: URLRequest):
    url = request.url

    # Diffbot API endpoint
    api_endpoint = f'https://api.diffbot.com/v3/article?token={api_token}&url={url}'
    
    # Sending the request to Diffbot API
    response = requests.get(api_endpoint)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch article content")

    data = response.json()
    
    # Extracting article content and images
    article_content = data.get('objects', [])[0].get('text', '')
    images = data.get('objects', [])[0].get('images', [])
    
    # Create Markdown content
    md_content = "# Article Content\n\n"
    md_content += "## Content\n\n"
    md_content += article_content + "\n\n"

    # Add images to Markdown content
    if images:
        md_content += "## Images\n\n"
        for idx, image in enumerate(images):
            image_url = image.get('url')
            alt_text = image.get('title', f'Image {idx + 1}')
            try:
                # Get the image
                img_response = requests.get(image_url, stream=True)
                if img_response.status_code == 200:
                    # Determine the image file extension
                    content_type = img_response.headers.get('Content-Type')
                    if content_type and 'image' in content_type:
                        image_extension = content_type.split('/')[-1]
                        image_filename = f"image_{idx + 1}.{image_extension}"
                        image_path = os.path.join(image_dir, image_filename)
                        
                        # Save the image
                        with open(image_path, 'wb') as img_file:
                            img_file.write(img_response.content)
                        
                        # Add the image reference to Markdown
                        md_content += f"![{alt_text}]({image_path})\n\n"
                    else:
                        md_content += f"![{alt_text}]({image_url})\n\n"  # Fallback to URL
                else:
                    md_content += f"![{alt_text}]({image_url})\n\n"  # Fallback to URL
            except Exception as e:
                md_content += f"![{alt_text}]({image_url})\n\n"  # Fallback to URL

    # Generate a unique filename using the current date and time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    md_filename = f"scraped_article_{timestamp}.md"
    
    # Save the Markdown content to a file
    with open(md_filename, 'w') as md_file:
        md_file.write(md_content)
    
    return {"message": "Markdown file created successfully!", "file_name": md_filename}

# Run the FastAPI app using Uvicorn (in terminal)
# uvicorn script_name:app --reload
