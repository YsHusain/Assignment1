import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Your Diffbot API token (Consider loading from environment variables)
api_token = os.getenv('DIFFBOT_API_TOKEN', 'your_default_token')  # Loading from environment variable
if api_token == 'your_default_token':
    logging.warning("API token is using the default. Please set the environment variable.")

# URL to scrape
url = 'https://books.toscrape.com/'

# Diffbot API endpoint
api_endpoint = f'https://api.diffbot.com/v3/article?token={api_token}&url={url}'

# Sending the request to Diffbot API
response = requests.get(api_endpoint)

# Check if the response is successful
if response.status_code == 200:
    data = response.json()
    
    # Extracting the article content and image URLs
    article_content = data.get('objects', [])[0].get('text', 'No article content found.')
    images = data.get('objects', [])[0].get('images', [])
    
    # Create the Markdown content
    md_content = "# Article from Books to Scrape\n\n"
    md_content += "## Content\n\n"
    md_content += article_content + "\n\n"

    # Directory to store images
    image_dir = "downloaded_images"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    # Download and save images  
    for idx, image in enumerate(images, 1):
        image_url = image.get('url')
        if image_url:
            try:
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    extension = image_url.split('.')[-1]
                    filename = f"image_{idx}.{extension}"
                    filepath = os.path.join(image_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    md_content += f"![Image {idx}]({filepath})\n"
                else:
                    logging.warning(f"Failed to download image {idx} from {image_url}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error downloading image {idx}: {e}")

    # Save the Markdown content to a file
    with open('converted_article.md', 'w', encoding='utf-8') as f:
        f.write(md_content)

    logging.info("Article converted successfully and saved to 'converted_article.md'")
else:
    logging.error(f"API request failed with status code {response.status_code}")
